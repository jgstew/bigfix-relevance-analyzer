"""How expensive a relevance statement is, as a heuristic score.

The point is not to measure relevance precisely -- it is to give a pre-commit
hook something to threshold on, so that a statement which has grown into a
nested pile of ``whose`` filters, or which quietly hashes every file on a disk,
gets flagged for a human to look at. A :class:`RelevanceComplexity` carries the
individual metrics alongside the score so a warning can say *why* something
scored high, not just that it did.

Two axes, one score
-------------------
**Readability** is the token-shaped part: length, nesting depth, ``of`` chains,
``whose`` filters, conditional nesting, how many distinct names a reader has to
hold at once. Where a construct can both pile up and nest, it is counted twice
-- once flat, once by depth -- because those are not the same cost. Three
``if``\\ s in a row read linearly; three nested inside each other's branches do
not, and only the depth metric can tell them apart.

**Evaluation cost** is what the statement does to the engine evaluating it, and
it does not follow from size. ``exists descendants of folder "C:\\"`` is eight
tokens and walks an entire disk, on every evaluation cycle, on every endpoint.
:data:`COST_RULES` is the table of inspector families known to be heavy, and
they are deliberately not weighted equally -- hashing a file is not the same
order of expense as reading a few lines from one.

Each rule declares which dialects it applies to *and* how much it costs in
each, which is a per-rule question rather than a split of the table. Applying
to both dialects does not mean costing the same in both: session relevance
cannot read a file at all, so ``sha1 of <string>`` is real work but nowhere
near ``sha1 of <file>`` on a client, and the ``hashing`` rule charges each
accordingly. ``wmi`` exists only on a Windows client, and ``results of <bes
fixlet>`` only on the server, so neither is charged against the other dialect at
all. Pass ``dialect`` to :func:`analyze` to get this scoping; without one,
nothing is excluded and each rule charges its worst case.

Both feed :attr:`RelevanceComplexity.score`. A consumer that wants one axis
alone can read :attr:`RelevanceComplexity.evaluation_cost` directly, or set
:data:`WEIGHT_EVALUATION_COST` to zero.

Counting happens over the token stream from
:mod:`bigfix_relevance_analyzer.tokenizer`, never over raw text. That is what
keeps a comment mentioning ``whose``, or the word ``and`` inside a string
literal, from inflating the score: only text that will actually evaluate counts,
the same discipline :mod:`bigfix_relevance_analyzer.dialect` applies.

What the metrics are not
------------------------
They are heuristics, and the tokenizer deliberately does not bind multi-word
inspector names (see its docstring), so the counts are position-blind: the
``of`` in the inspector name ``day of month`` counts as an ``of``, and a name
containing ``and`` counts as a boolean operator. For a *scorer* that is fine --
a statement using such names really is denser to read -- but nothing here should
be mistaken for a parse.

The weights are provisional. They are module-level constants so they can be
tuned against a real corpus without touching the counting, and no test pins an
absolute score, only orderings.

Where the cost table comes from
-------------------------------
The client-side families are taken from ``jgstew/besapi``'s
``examples/fixlet_add_mime_field.py``, which finds custom content whose
relevance is slow enough to deserve an explicit evaluation period. Every name a
rule matches on is checked against the inspector dumps by
:attr:`CostRule.anchors`, and each rule's :attr:`CostRule.dialects` has to agree
with where those names are actually defined, so the table is grounded in what
BigFix defines rather than in recollection.

Two things are *not* grounded that way, and are marked as such where they are
written down. The **tiers** are a judgement call, not a measurement -- see the
comment above :data:`COST_EXTREME`. And the **session-only rules** are a seed
rather than a survey: there is no curated equivalent of the besapi list for the
server side, so they cover the constructs whose expansion the dumps make plain
(the result matrix, applicability) and nothing more. Expect to add to them.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.tokenizer import GRAMMAR_WORDS, TokenKind, code_tokens

__all__ = [
    "BOTH_DIALECTS",
    "COST_EXTREME",
    "COST_HIGH",
    "COST_LOW",
    "COST_MODERATE",
    "COST_RULES",
    "DEPTH_EXPONENT",
    "CostRule",
    "RelevanceComplexity",
    "analyze",
    "cost_rules_for",
    "depth_cost",
    "evaluation_cost_rules",
    "score",
]

# ---------------------------------------------------------------------------
# Weights. Provisional -- see the module docstring.
# ---------------------------------------------------------------------------

DEPTH_EXPONENT = 1.5
"""How sharply nesting is charged, above linear.

Nine levels of nesting is worse than three times three levels: every enclosing
condition is one more thing a reader holds at once, so the cost compounds. This
raises depth to a power rather than multiplying it. Kept mild -- ``1 ** n == 1``
means unnested code is unaffected, and shallow nesting barely moves -- so it
only bites where nesting is genuinely deep.

Applied to parenthesis and conditional depth, but deliberately **not** to
``of`` chains: see :data:`WEIGHT_MAX_OF_CHAIN`.
"""


def depth_cost(depth: int, weight: float) -> float:
    """Charge ``depth`` levels of nesting at ``weight``, slightly above linearly."""
    # math.pow rather than `**`: the builtin is typed as returning Any, since a
    # negative base with a fractional exponent yields a complex number.
    return weight * math.pow(depth, DEPTH_EXPONENT)


WEIGHT_TOKEN = 1.0
"""Baseline: longer statements are harder, all else equal."""

WEIGHT_PAREN_DEPTH = 3.0
"""Nesting depth, the single strongest readability signal. Charged by
:func:`depth_cost`, so it compounds rather than scaling linearly."""

WEIGHT_BOOLEAN_OPERATOR = 2.0
WEIGHT_OF = 1.0
WEIGHT_MAX_OF_CHAIN = 2.0
"""A long unbroken `of` chain costs more than the same `of`s spread out.

Charged **linearly**, unlike the other depth metrics. Chaining properties is
simply how relevance is written -- ``names of processes of it`` is idiomatic,
not a smell -- so compounding it the way :data:`DEPTH_EXPONENT` compounds
parentheses would flag ordinary code as complex.
"""

WEIGHT_WHOSE_CLAUSE = 5.0
"""A `whose` filter introduces a second scope with its own `it`."""

WEIGHT_CONDITIONAL = 1.0
"""Each `if`. Small: a run of unnested conditionals reads linearly."""

WEIGHT_CONDITIONAL_DEPTH = 3.0
"""Nesting of conditionals, which is what actually costs a reader.

Deliberately several times :data:`WEIGHT_CONDITIONAL`: holding one branch in
mind is cheap, holding a branch inside another branch is not. Charged by
:func:`depth_cost`, so deep nesting compounds.
"""

WEIGHT_ITERATION_KEYWORD = 1.0
WEIGHT_SEMICOLON_CLAUSE = 2.0
WEIGHT_STRING_LITERAL = 0.5
WEIGHT_UNIQUE_IDENTIFIER = 1.0
"""Distinct names to hold in your head, as opposed to repeated ones."""

WEIGHT_ERROR_TOKEN = 5.0
"""Unlexable text: the statement is broken, which is worth surfacing."""

WEIGHT_EVALUATION_COST = 1.0
"""How much :attr:`RelevanceComplexity.evaluation_cost` contributes to the score.

Set this to 0.0 to score readability alone, or raise it to make the client's
evaluation loop the dominant concern.
"""

# ---------------------------------------------------------------------------
# Evaluation cost
# ---------------------------------------------------------------------------
#
# Readability and evaluation cost are different axes. A short statement can be
# ruinous on the client -- `exists descendants of folder "C:\"` is eight tokens
# and walks an entire disk -- so token counting alone will never flag the
# statements that actually hurt an endpoint.
#
# Which inspectors are heavy comes from the candidate list in jgstew/besapi's
# `examples/fixlet_add_mime_field.py`, a script that finds custom content whose
# relevance is slow enough to deserve an explicit evaluation period. The names
# in each pattern are then checked against the QnA dumps by the `anchors` field,
# so a rule cannot drift onto an inspector that does not exist.
#
# The *tiers* are a judgement call, not a benchmark: nobody has timed these on
# an endpoint here. They encode the ordering that BigFix performance guidance
# has long agreed on -- hashing a file and walking a directory tree cost more
# than reading a few lines -- and they are module-level constants precisely so
# they can be re-scaled once someone does measure.

COST_EXTREME = 12.0
"""Unbounded work: hashing whole files, walking a directory tree, WMI."""

COST_HIGH = 6.0
"""Enumerating a large or slow provider: the registry, AD, an event log."""

COST_MODERATE = 3.0
"""Real I/O, but bounded: reading a file's lines, an xpath, a stat sweep."""

COST_LOW = 1.0
"""A single bounded lookup: one field, one string -- no traversal, no sweep."""


CLIENT_ONLY = frozenset({Dialect.CLIENT})
SESSION_ONLY = frozenset({Dialect.SESSION})
BOTH_DIALECTS = frozenset({Dialect.CLIENT, Dialect.SESSION})
"""Convenience sets for :func:`uniform_cost`, not a partition of the table."""


def uniform_cost(cost: float, dialects: frozenset[Dialect]) -> tuple[tuple[Dialect, float], ...]:
    """Build a :attr:`CostRule.costs` table charging ``cost`` in every dialect given.

    Most rules cost the same wherever they apply, and this is the constructor
    for those. A rule whose cost genuinely differs by dialect -- see ``hashing``
    and ``modification time`` in :data:`COST_RULES` for why that happens --
    builds its ``costs`` tuple directly instead.
    """
    return tuple((dialect, cost) for dialect in sorted(dialects, key=lambda d: d.value))


@dataclass(frozen=True, slots=True)
class CostRule:
    """One family of inspectors that is expensive to evaluate."""

    label: str
    """Short name for the family, e.g. ``hashing``. Unique across the table."""

    costs: tuple[tuple[Dialect, float], ...]
    """What one occurrence costs, per dialect this rule applies to.

    The single source of truth for both "which dialects" and "how much": a
    dialect not present here is a dialect this rule does not charge for. Build
    this with :func:`uniform_cost` when the cost does not depend on dialect,
    which is most rules -- ``wmi`` exists only on a Windows client, so its rule
    is not charged against session relevance that merely happens to say the
    word, but the client cost does not vary by *how* it is heavy.

    It is not always uniform, though. ``sha1 of <file>`` exists on the client
    and reads the whole file; session relevance has no ``<file>`` variant at
    all, only ``sha1 of <string>`` and ``sha1 of <x509 certificate>``, so its
    ceiling is real but far lower -- see the two costs on that rule below.

    A test checks the dialects present here against :attr:`anchors` in the
    dumps, so a rule cannot claim applicability to a dialect that does not
    define the inspectors it names. The specific *cost* split when one exists
    is not machine-checked the same way -- it is a documented judgement call,
    same as the tier constants themselves.
    """

    pattern: re.Pattern[str]
    """Matched against runs of adjacent code words; see :func:`_word_runs`."""

    why: str
    """One line on what the engine actually does. Shown in a hook's warning."""

    example: str
    """Relevance this rule must match. Pinned by a test, so it cannot go stale."""

    anchors: tuple[str, ...] = ()
    """Inspector names this rule is about, each verified against the QnA dumps."""

    @property
    def dialects(self) -> frozenset[Dialect]:
        """Which engines this rule applies to at all, at any cost."""
        return frozenset(dialect for dialect, _cost in self.costs)

    def cost_for(self, dialect: Dialect | None) -> float:
        """What one occurrence costs when evaluated as ``dialect``.

        Zero for a dialect this rule does not apply to. An indefinite dialect
        (``None``, :attr:`Dialect.UNCERTAIN`, :attr:`Dialect.BOTH`) gets the
        worst case across every dialect the rule applies to: with no evidence
        to exclude anything, charging too much is closer to harmless than
        charging too little, the same reasoning :func:`cost_rules_for` uses to
        keep every rule in play rather than none.
        """
        table = dict(self.costs)
        if is_definite(dialect):
            return table.get(dialect, 0.0)
        return max(table.values())


COST_RULES: tuple[CostRule, ...] = (
    # Asymmetric: session relevance cannot read a file at all, so it has no
    # `sha1 of <file>` -- only `sha1 of <string>` and `sha1 of <x509
    # certificate>`. Real cost, much lower ceiling.
    CostRule(
        label="hashing",
        costs=((Dialect.CLIENT, COST_EXTREME), (Dialect.SESSION, COST_LOW)),
        pattern=re.compile(r"\b(?:md5|sha1|sha2?_?\d{3,4})s? of\b"),
        why=(
            "on the client this reads and digests a whole file; in session "
            "relevance it can only be a string or certificate, which is bounded"
        ),
        example='sha1 of file "/tmp/x" = "abc"',
        anchors=("sha1", "sha256", "md5"),
    ),
    CostRule(
        label="folder recursion",
        costs=uniform_cost(COST_EXTREME, CLIENT_ONLY),
        pattern=re.compile(r"\b(?:descendants? of|folders of folders?)\b"),
        why="walks an entire directory tree, which is unbounded on a large disk",
        example='exists descendants of folder "/opt"',
        anchors=("descendants", "folders"),
    ),
    CostRule(
        label="wmi query",
        costs=uniform_cost(COST_HIGH, CLIENT_ONLY),
        pattern=re.compile(r"\bwmi\b"),
        why="round-trips to the WMI provider, which is slow and can block",
        example='exists select objects "Name from Win32_Product" of wmi',
        anchors=("wmi",),
    ),
    CostRule(
        label="process image files",
        costs=uniform_cost(COST_HIGH, CLIENT_ONLY),
        pattern=re.compile(r"\bimage files? of processes\b"),
        why="opens the on-disk image of every running process",
        example="exists image files of processes",
        anchors=("processes",),
    ),
    CostRule(
        label="scheduled tasks",
        costs=uniform_cost(COST_HIGH, CLIENT_ONLY),
        pattern=re.compile(r"\bscheduled tasks?\b"),
        why="enumerates the task scheduler, which is slow to query",
        example='exists scheduled tasks whose (name of it = "x")',
        anchors=("scheduled tasks",),
    ),
    # A bare reference is cheap: the dumps carry `sample time of <active
    # directory group/local computer/local user>`, which only makes sense if
    # this is periodically-sampled, cached state rather than a live
    # domain-controller round trip on every evaluation. Client and session are
    # different operations here too -- client `active directory` is global,
    # session `active directory of <bes ldap directory>` targets one named
    # directory and returns a boolean -- but nothing says either is more
    # expensive than a cached read, so both get the same low cost.
    CostRule(
        label="active directory",
        costs=uniform_cost(COST_LOW, BOTH_DIALECTS),
        pattern=re.compile(r"\bactive director(?:y|ies)\b"),
        why="a periodically-sampled, cached read -- cheap on its own",
        example="exists active directory",
        anchors=("active directory",),
    ),
    # A different animal from the bare reference above: chaining into one of
    # these *unindexed* enumeration properties walks a whole collection --
    # users, groups -- that can be large on a big domain, unlike the cached
    # object the base rule covers. Indexed lookups (`logged on group <string>
    # of ...`) are a different, targeted operation and correctly do not match
    # here: the `<string>` index sits between the property name and `of`,
    # which ends the word run before `of` is reached -- see
    # `test_a_named_lookup_is_not_charged_as_enumeration`. Client-only: every
    # signature these anchors resolve to in the dumps is a client property.
    CostRule(
        label="active directory enumeration",
        costs=uniform_cost(COST_HIGH, CLIENT_ONLY),
        pattern=re.compile(
            r"\b(?:local users?|local groups?|logged on users?|logged on groups?|groups) of\b"
            r".*\bactive director(?:y|ies)\b"
        ),
        why="walks a whole collection of users or groups, which can be large on a big domain",
        example="exists local users of active directory",
        anchors=("local users", "local groups", "logged on users", "groups"),
    ),
    CostRule(
        label="active device enumeration",
        costs=uniform_cost(COST_MODERATE, CLIENT_ONLY),
        pattern=re.compile(r"\bactive devices?\b"),
        why="enumerates the device tree",
        example="exists active devices",
        anchors=("active devices",),
    ),
    CostRule(
        label="smbios enumeration",
        costs=uniform_cost(COST_MODERATE, CLIENT_ONLY),
        pattern=re.compile(r"\bsmbios\b"),
        why="reads and parses the SMBIOS tables",
        example="exists smbios",
        anchors=("smbios",),
    ),
    CostRule(
        label="event log",
        costs=uniform_cost(COST_HIGH, CLIENT_ONLY),
        pattern=re.compile(r"\brecords? of\b.*\bevent log\b|\bevent log\b"),
        why="scans an event log, which grows without bound",
        example="exists records of application event log",
        anchors=("event log",),
    ),
    CostRule(
        label="package database",
        costs=uniform_cost(COST_HIGH, CLIENT_ONLY),
        pattern=re.compile(
            r"\bpackages? of (?:rpm|debianpackagecache|rpmdatabase)\b"
            r"|\b(?:debian|winrt) packages?\b"
        ),
        why="queries the platform package database, which shells out or reads a large store",
        example="exists packages of rpm",
        anchors=("packages", "rpm"),
    ),
    CostRule(
        label="file line reading",
        costs=uniform_cost(COST_MODERATE, CLIENT_ONLY),
        pattern=re.compile(r"\blines? of file\b"),
        why="reads the file's contents; ruinous on a log that grows",
        example='exists lines of file "/var/log/x"',
        anchors=("lines",),
    ),
    # Asymmetric the other way from hashing: the client signatures
    # (`<filesystem object>`, `<symlink>`, `<volume>`) are a stat usually swept
    # across many files, while the session signatures (`<bes fixlet>`, `<bes
    # activation>`) are one metadata field on one object -- close to a plain
    # property read, not a sweep.
    CostRule(
        label="modification time",
        costs=((Dialect.CLIENT, COST_MODERATE), (Dialect.SESSION, COST_LOW)),
        pattern=re.compile(r"\bmodification times? of\b"),
        why=(
            "on the client this stats a filesystem object, usually swept across "
            "many files; in session relevance it is one field on a fixlet or "
            "activation"
        ),
        example="modification time of it",
        anchors=("modification time",),
    ),
    CostRule(
        label="xpath evaluation",
        costs=uniform_cost(COST_MODERATE, BOTH_DIALECTS),
        pattern=re.compile(r"\bxpaths?\b"),
        why="parses the document into a DOM before the expression runs",
        example='exists xpaths "//a" of xml document of file "/tmp/x"',
        anchors=("xpaths",),
    ),
    # -- session only ------------------------------------------------------
    #
    # Lower confidence than the client rules above: there is no curated
    # equivalent of the besapi candidate list for the server side, so this is a
    # seed rather than a survey. Both rules are here because the dumps show what
    # they expand to, not because anyone timed them.
    CostRule(
        label="result cross product",
        costs=uniform_cost(COST_EXTREME, SESSION_ONLY),
        pattern=re.compile(r"\bresults? of\b"),
        why=(
            "expands to the fixlet-by-computer result matrix; the dumps give "
            "`result <( bes computer, bes fixlet )>`, so this grows with the "
            "product of both, not the sum"
        ),
        example="number of results of bes fixlets",
        anchors=("results", "result"),
    ),
    CostRule(
        label="applicable computer expansion",
        costs=uniform_cost(COST_HIGH, SESSION_ONLY),
        pattern=re.compile(r"\bapplicable computers of\b"),
        why="evaluates applicability for every computer the fixlet reaches",
        example="number of applicable computers of bes fixlets",
        anchors=("applicable computers",),
    ),
)


def cost_rules_for(dialect: Dialect | None) -> tuple[CostRule, ...]:
    """The rules that apply to ``dialect``.

    An indefinite dialect -- ``None``, :attr:`Dialect.UNCERTAIN` or
    :attr:`Dialect.BOTH` -- excludes nothing, on the grounds that there is no
    evidence to exclude anything *with*. Over-charging is close to harmless in
    practice: a rule's pattern names inspectors the other engine does not
    define, so text from the wrong dialect rarely contains them.
    """
    if not is_definite(dialect):
        return COST_RULES
    return tuple(rule for rule in COST_RULES if dialect in rule.dialects)


def _word_runs(text: str) -> list[str]:
    """Normalized runs of adjacent code words, split at anything else.

    Cost patterns match against these rather than the raw text, which buys two
    things: an inspector named inside a string literal or a comment cannot be
    charged for, and a phrase cannot be matched across a punctuation boundary
    that would have separated it in the parse.
    """
    runs: list[str] = []
    current: list[str] = []
    for token in code_tokens(text):
        if token.kind is TokenKind.WORD:
            current.append(token.normalized)
        elif current:
            runs.append(" ".join(current))
            current = []
    if current:
        runs.append(" ".join(current))
    return runs


def evaluation_cost_rules(text: str, dialect: Dialect | None = None) -> tuple[CostRule, ...]:
    """Which cost rules ``text`` triggers, in table order, without duplicates."""
    runs = _word_runs(text)
    return tuple(
        rule for rule in cost_rules_for(dialect) if any(rule.pattern.search(run) for run in runs)
    )


def _evaluation_cost(runs: list[str], dialect: Dialect | None) -> tuple[float, tuple[str, ...]]:
    """Total cost of ``runs`` and the labels that contributed, in table order."""
    total = 0.0
    labels: list[str] = []
    for rule in cost_rules_for(dialect):
        occurrences = sum(len(rule.pattern.findall(run)) for run in runs)
        if occurrences:
            total += rule.cost_for(dialect) * occurrences
            labels.append(rule.label)
    return total, tuple(labels)


# Words treated as boolean operators when they appear as bare words.
_BOOLEAN_WORDS = frozenset({"and", "or", "not"})

# Words that name the implicit iteration subject.
_ITERATION_WORDS = frozenset({"it", "item", "items"})

# Words that introduce a filter clause.
_WHOSE_WORDS = frozenset({"whose", "whoses"})

# Punctuation that ends an `of` chain: a chain cannot cross a clause boundary.
_CHAIN_BREAKERS = frozenset({"(", ")", ";", ","})

# The word that opens a conditional. `then` and `else` are not counted: they
# cannot appear without an `if`, so counting them would only multiply the same
# signal.
_CONDITIONAL_WORD = "if"


@dataclass(frozen=True, slots=True)
class RelevanceComplexity:
    """Per-metric counts for one relevance statement, plus a weighted score."""

    token_count: int = 0
    """Tokens that carry meaning: whitespace and comments excluded."""

    max_paren_depth: int = 0
    boolean_operators: int = 0
    """Bare ``and`` / ``or`` / ``not`` words."""

    of_count: int = 0
    """Every ``of``, however it groups."""

    max_of_chain: int = 0
    """The most ``of``s in one clause, chains being broken by ``()``, ``;``, ``,``."""

    whose_clauses: int = 0
    iteration_keywords: int = 0
    """References to the implicit subject: ``it``, ``item``, ``items``."""

    conditional_branches: int = 0
    """Every ``if``, however it nests."""

    max_conditional_depth: int = 0
    """The deepest nesting of ``if`` inside another ``if``'s branch.

    A run of unnested conditionals, and an ``else if`` chain, both report 1: they
    read linearly. Two means one conditional sits inside another's branch.
    Inferred from parenthesis depth -- see :func:`analyze` -- because binding a
    branch to its ``if`` needs the parser this module does not have.
    """

    semicolon_clauses: int = 0
    """Number of ``;``-separated clauses, or 0 when there is no ``;`` at all."""

    string_literals: int = 0
    unique_identifiers: int = 0
    """Distinct words that are not grammar words, compared case-insensitively."""

    error_tokens: int = 0
    """Text the tokenizer could not lex. Non-zero means the statement is broken."""

    evaluation_cost: float = 0.0
    """What this costs the client to *evaluate*, as opposed to a human to read.

    The summed :attr:`CostRule.cost` of every heavy inspector occurrence; see
    :data:`COST_RULES`. Zero for relevance that uses none.
    """

    costly_inspectors: tuple[str, ...] = ()
    """The :attr:`CostRule.label` of each family charged for, in table order."""

    @property
    def score(self) -> float:
        """The weighted sum of every metric. Higher is worse.

        Readability and evaluation cost both feed this, so a short statement can
        still score high on the strength of one expensive inspector. A consumer
        that wants only one of the two axes can read
        :attr:`evaluation_cost` directly, or set
        :data:`WEIGHT_EVALUATION_COST` to 0.0.
        """
        return (
            WEIGHT_TOKEN * self.token_count
            + depth_cost(self.max_paren_depth, WEIGHT_PAREN_DEPTH)
            + WEIGHT_BOOLEAN_OPERATOR * self.boolean_operators
            + WEIGHT_OF * self.of_count
            # Linear on purpose -- see WEIGHT_MAX_OF_CHAIN.
            + WEIGHT_MAX_OF_CHAIN * self.max_of_chain
            + WEIGHT_WHOSE_CLAUSE * self.whose_clauses
            + WEIGHT_CONDITIONAL * self.conditional_branches
            + depth_cost(self.max_conditional_depth, WEIGHT_CONDITIONAL_DEPTH)
            + WEIGHT_ITERATION_KEYWORD * self.iteration_keywords
            + WEIGHT_SEMICOLON_CLAUSE * self.semicolon_clauses
            + WEIGHT_STRING_LITERAL * self.string_literals
            + WEIGHT_UNIQUE_IDENTIFIER * self.unique_identifiers
            + WEIGHT_ERROR_TOKEN * self.error_tokens
            + WEIGHT_EVALUATION_COST * self.evaluation_cost
        )


def analyze(text: str, dialect: Dialect | None = None) -> RelevanceComplexity:
    """Count every complexity metric for ``text`` in one pass.

    ``dialect`` scopes the evaluation-cost rules; pass a
    :attr:`RelevanceSite.dialect <bigfix_relevance_analyzer.extract.RelevanceSite.dialect>`
    when one is known, so client-only inspectors are not charged against session
    relevance. Leaving it out excludes nothing -- see :func:`cost_rules_for`.
    Readability metrics do not depend on it.

    Never raises. Malformed relevance is scored like anything else, with the
    unlexable part reported as :attr:`RelevanceComplexity.error_tokens`.
    """
    token_count = 0
    depth = 0
    max_depth = 0
    booleans = 0
    ofs = 0
    of_chain = 0
    max_of_chain = 0
    whoses = 0
    conditionals = 0
    max_conditional_depth = 0
    # Parenthesis depth of each `if` still considered open. An `if` at the same
    # depth as the one before it is a sibling or an `else if` chain link, not a
    # nesting, so the earlier one is popped first.
    open_conditionals: list[int] = []
    iterations = 0
    semicolons = 0
    strings = 0
    errors = 0
    identifiers: set[str] = set()
    runs: list[str] = []
    run: list[str] = []

    for token in code_tokens(text):
        token_count += 1
        word = token.normalized

        # Word runs for the cost patterns, built in the same pass. A run ends at
        # the first token that is not a word.
        if token.kind is TokenKind.WORD:
            run.append(word)
        elif run:
            runs.append(" ".join(run))
            run = []

        if token.kind is TokenKind.WORD:
            if word == "of":
                ofs += 1
                of_chain += 1
                max_of_chain = max(max_of_chain, of_chain)
                continue
            if word in _BOOLEAN_WORDS:
                booleans += 1
            elif word in _WHOSE_WORDS:
                whoses += 1
            elif word == _CONDITIONAL_WORD:
                conditionals += 1
                # Anything opened at this depth or shallower has closed: a
                # conditional only nests when it sits inside the parentheses of
                # another one's branch.
                while open_conditionals and open_conditionals[-1] >= depth:
                    open_conditionals.pop()
                open_conditionals.append(depth)
                max_conditional_depth = max(max_conditional_depth, len(open_conditionals))
            elif word in _ITERATION_WORDS:
                iterations += 1
            if word not in GRAMMAR_WORDS:
                identifiers.add(word)
        elif token.kind is TokenKind.STRING:
            strings += 1
        elif token.kind is TokenKind.ERROR:
            errors += 1
        elif token.kind is TokenKind.PUNCT:
            if word == "(":
                depth += 1
                max_depth = max(max_depth, depth)
            elif word == ")":
                # Clamped: unbalanced relevance must not push depth negative and
                # then hide real nesting that follows.
                depth = max(0, depth - 1)
            elif word == ";":
                semicolons += 1
            if word in _CHAIN_BREAKERS:
                of_chain = 0

    if run:
        runs.append(" ".join(run))
    cost, costly = _evaluation_cost(runs, dialect)

    return RelevanceComplexity(
        token_count=token_count,
        max_paren_depth=max_depth,
        boolean_operators=booleans,
        of_count=ofs,
        max_of_chain=max_of_chain,
        whose_clauses=whoses,
        conditional_branches=conditionals,
        max_conditional_depth=max_conditional_depth,
        iteration_keywords=iterations,
        semicolon_clauses=semicolons + 1 if semicolons else 0,
        string_literals=strings,
        unique_identifiers=len(identifiers),
        error_tokens=errors,
        evaluation_cost=cost,
        costly_inspectors=costly,
    )


def score(text: str, dialect: Dialect | None = None) -> float:
    """The complexity score for ``text``. Shorthand for ``analyze(text).score``."""
    return analyze(text, dialect).score
