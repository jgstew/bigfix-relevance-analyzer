"""Every analysis this package offers, run over one relevance statement.

The other modules each answer one question -- which dialect is this, does it
parse, what does it evaluate to, where can it run, what does it cost. A
consumer that wants all of them (an editor hover, a pre-commit report, an MCP
server answering "tell me about this relevance") otherwise has to wire them
together itself, in the right order, and know which results are only available
once the statement parses. This module is that wiring, done once.

Nothing here evaluates relevance. Types and platforms come from the inspector
tables, and :attr:`RelevanceAnalysis.levels` is probe *text* for an evaluator
the caller supplies; see :mod:`~bigfix_relevance_analyzer.breakdown`.

It is also print-free, like the rest of the package -- rendering lives in
``__main__``, so importing this inside a stdio MCP server stays safe.

    from bigfix_relevance_analyzer import analyze_relevance

    report = analyze_relevance('exists file "C:\\\\foo.txt"')
    print(report.dialect, report.check.value.plurality if report.check else None)
    print(report.complexity.score)

Analysis never raises on bad input: a statement that does not lex or parse
comes back with :attr:`RelevanceAnalysis.error` set and the tree-dependent
fields empty, because the callers this exists for -- editors, hooks -- are
handed broken text constantly and a half-written statement is the normal case,
not an exceptional one. What *is* still reported for such a statement is
everything that does not need a tree: the dialect, the token stream with its
error tokens positioned, and the complexity metrics, which are lexical.
"""

from __future__ import annotations

import functools
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from bigfix_relevance_analyzer import grammar, inspectors
from bigfix_relevance_analyzer._serialize import _enum, _position, _span
from bigfix_relevance_analyzer.binding import ItBinding, resolve_it_bindings
from bigfix_relevance_analyzer.breakdown import Level, ProbeKind, breakdown_probes
from bigfix_relevance_analyzer.complexity import (
    CostRule,
    RelevanceComplexity,
    _analyze_lexed,
    cost_rules_for,
)
from bigfix_relevance_analyzer.dialect import Dialect, classify_relevance_dialect, is_definite
from bigfix_relevance_analyzer.nodes import (
    Binary,
    Cast,
    Node,
    Reference,
    Unary,
    to_mermaid,
    to_sexpr,
    tree_depth,
    walk,
)
from bigfix_relevance_analyzer.parser import ParseError, _try_parse_lexed
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind, _lex
from bigfix_relevance_analyzer.typecheck import CheckResult, TypeEnvironment, check

if TYPE_CHECKING:
    from bigfix_relevance_analyzer.autofix import AutofixResult, Guard

__all__ = [
    "ReferenceReport",
    "RelevanceAnalysis",
    "analyze",
    "client_platforms",
]


@dataclass(frozen=True, slots=True)
class ReferenceReport:
    """One name in the statement, and what the inspector tables say about it."""

    reference: Reference
    """The node itself; its :attr:`~bigfix_relevance_analyzer.nodes.Span` is
    where to point a message."""

    matches: tuple[inspectors.Inspector, ...]
    """Every table row with this name, in any dialect or platform."""

    visible: tuple[inspectors.Inspector, ...]
    """The subset of :attr:`matches` the analysed environment can see.

    Empty alongside a non-empty :attr:`matches` means the name is real but not
    reachable as written here -- a session inspector used in client relevance,
    or a Windows one under ``--platform macos``.
    """

    narrowed: tuple[inspectors.Inspector, ...] = ()
    """The rows the checker actually resolved this occurrence to.

    :attr:`matches` and :attr:`visible` both answer "what could this name be",
    which for an overloaded name is a much larger question than "what is it
    here". `keys` is nineteen properties across json, yaml, registry, metabase
    and plugin stores; `keys of <registry key>` is one of them. The checker has
    always narrowed -- see
    :func:`~bigfix_relevance_analyzer.typecheck.resolve_property` -- and this
    is that answer, carried out of the walk rather than recomputed bare.

    Empty when the walk did not resolve this occurrence at all, and also when
    it resolved to nothing: both fall back to the wider sets, because a name
    that exists somewhere is more useful to show than a blank. Which of the
    two happened is what :attr:`known` and the checker's diagnostics say.
    """

    @property
    def phrase(self) -> str:
        """The case-folded, space-normalized name, e.g. ``operating system``."""
        return self.reference.phrase

    @property
    def known(self) -> bool:
        """Whether any dump defines this name at all."""
        return bool(self.matches)

    @property
    def resolved(self) -> tuple[inspectors.Inspector, ...]:
        """What to report, narrowest answer first.

        The rows this occurrence resolved to, else the ones the environment can
        see, else every row with the name. Falling back is deliberate at both
        steps. A name that exists but is out of scope -- or one whose direct
        object rules every overload out -- is a more useful thing to show than
        nothing, and :attr:`known`, :attr:`visible` and the checker's
        diagnostics are what distinguish the cases.
        """
        return self.narrowed or self.visible or self.matches

    @property
    def dialects(self) -> frozenset[Dialect]:
        """Which dialects define this name, over *every* row rather than the
        narrowed or visible ones.

        Deliberately read from :attr:`matches`: the question is what the tables
        know about the name, which cannot depend on the environment the lookup
        already filtered by, or the answer would just restate the environment.
        """
        if self.matches is inspectors.lookup(self.phrase):
            return inspectors._dialects_of_name(self.phrase)  # the usual case, cached
        return inspectors._dialects_of(self.matches)

    @property
    def return_types(self) -> tuple[str, ...]:
        """The distinct types this name can evaluate to, sorted."""
        return inspectors._return_types_of(self.resolved)

    @property
    def platforms(self) -> frozenset[str]:
        """Evaluation contexts defining any resolved row -- client platforms by
        name, session surfaces as ``session:<context>``."""
        return inspectors._contexts_of(self.resolved)


@dataclass(frozen=True, slots=True)
class RelevanceAnalysis:
    """Everything known about one statement. Built by :func:`analyze`."""

    text: str
    """The statement as given, verbatim."""

    classified_dialect: Dialect | None
    """What :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`
    concluded, or ``None`` when the text carries no evidence either way."""

    requested_dialect: Dialect | None
    """The dialect the caller forced, if any."""

    environment: TypeEnvironment
    """The dialect and platform every lookup ran against."""

    tokens: tuple[Token, ...]
    """The full token stream, trivia included, so a caller can re-render it."""

    parse_error: ParseError | None
    """Why parsing failed, positioned, or ``None`` when it succeeded."""

    node: Node | None
    """The root of the tree, or ``None`` when :attr:`parse_error` is set."""

    check: CheckResult | None
    """The type-check result, or ``None`` when there is no tree to check."""

    references: tuple[ReferenceReport, ...]
    """One per :class:`~bigfix_relevance_analyzer.nodes.Reference`, in the order
    the walk found them."""

    it_bindings: tuple[ItBinding, ...]
    """Every ``it``, with what it refers to. An entry whose
    :attr:`~bigfix_relevance_analyzer.binding.ItBinding.context` is ``None`` is
    an error the type checker also reports."""

    levels: tuple[Level, ...]
    """Breakdown probes, one per measurable level. Text, not results."""

    complexity: RelevanceComplexity
    """Readability and evaluation-cost metrics. Present even for text that does
    not parse, because they are counted lexically."""

    cost_rules: tuple[CostRule, ...]
    """The heavy-inspector rules this statement matched, in table order."""

    _form_dialect: Dialect | None = field(default=None, repr=False, compare=False)
    """The one dialect the forms written leave, when the names alone say
    :attr:`~bigfix_relevance_analyzer.dialect.Dialect.BOTH`; else ``None``.

    Worked out by :func:`analyze` while the tree it checked is alive, because
    the checks it reads are keyed by ``id()`` (#141). Stored as the answer, so
    an analysis returned from a worker pool keeps it.
    """

    @property
    def dialect(self) -> Dialect:
        """The dialect analysis actually ran as."""
        return self.environment.dialect

    @property
    def resolved_dialect(self) -> Dialect | None:
        """Which dialect every resolved reference's own table facts settle on.

        :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`
        runs on raw text, before parsing, and is deliberately blind to common
        English words such as ``file`` -- see its module docstring -- because
        in unparsed text those are too collision-prone to trust. Once the
        statement has parsed, that risk is gone: a :class:`ReferenceReport`'s
        :attr:`~ReferenceReport.matches` are inspector-table rows resolved by
        name, not a guess about a word in prose, so ``files`` or ``folders``
        being client-only is real evidence a text classifier could never use.

        Computed as the intersection, across every reference with at least one
        known match, of the dialects that reference's rows are defined in --
        the same "valid in every dialect this could be" reasoning
        :func:`~bigfix_relevance_analyzer.dialect.classify_relevance_dialect`
        cannot apply without a parse tree. An unknown name (no match at all)
        contributes no evidence either way.

        Names alone are not the whole answer, because one name can be two
        inspectors: ``operating system of <bes computer>`` is session, while
        ``operating system`` with no direct object is client only. So when the
        names say BOTH, the statement is checked as each dialect and the forms
        it is actually written in decide, with the types they produce: a
        dialect is ruled out when a known reference resolves to no row in it.
        That is usually the form (no direct object), but can be a type only one
        dialect's tables give a property: ``name of current analysis`` is
        SESSION, because client's ``current analysis`` is a ``fixlet``, which
        has no ``name``. ``name of operating system`` is
        therefore CLIENT, and so is ``nme of operating system``, its unknown
        name proving nothing. If that rules out one dialect, the other is the
        answer; if it rules out neither, or both, the answer stays BOTH --
        never an empty or contradictory one, which only names can establish.
        The checks run with no platform, so neither the dialect analysis ran
        as nor a ``platform`` argument changes this answer.

        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.CLIENT` or
        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.SESSION` means every
        resolved reference supports that dialect and not both dialects at
        once. :attr:`~bigfix_relevance_analyzer.dialect.Dialect.BOTH` means
        every resolved reference supports both -- provable here in a way the
        text classifier's own docstring says it cannot be, because a parse
        tree already exists by this point. A statement with *no* references
        at all is BOTH for the same reason, vacuously: literals, casts and
        operators are the universal core of the language, identical on every
        engine sampled -- see the ``universal-relevance`` reference document
        -- so there is nothing left in it that could be dialect-specific.
        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN` means the
        references contradict each other: some resolve only in client
        relevance, others only in session, so this statement cannot be valid
        as either. ``None`` means nothing parsed, or the statement has at
        least one reference and none of them resolved to a known name.
        """
        named = self._named_dialect
        if named is Dialect.BOTH and self._form_dialect is not None:
            return self._form_dialect
        return named

    @property
    def _named_dialect(self) -> Dialect | None:
        """:attr:`resolved_dialect` from the names alone, before their forms narrow it."""
        if self.node is None:
            return None
        return _dialect_of_names(self.references)

    def references_only_in(self, dialect: Dialect) -> tuple[str, ...]:
        """Names whose every known row is defined in ``dialect`` and no other.

        The two halves of a :attr:`resolved_dialect` of
        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN`, so a
        report can name what actually contradicts what rather than saying only
        that something does. Empty for an unknown name, which proves nothing in
        either direction.
        """
        return tuple(
            sorted(
                {
                    reference.phrase
                    for reference in self.references
                    if reference.dialects == frozenset({dialect})
                }
            )
        )

    @property
    def dialect_assumed(self) -> bool:
        """Whether :attr:`dialect` is a fallback rather than a finding.

        False when the caller forced a dialect, when the pre-parse text
        classifier reached a verdict, or when :attr:`resolved_dialect` -- the
        reference table's own post-parse evidence -- settles on one specific
        dialect by itself. True when none of the three determined anything, so
        every dialect-dependent conclusion below is conditional on a guess,
        which a report should say out loud.

        Also true when :attr:`resolved_dialect` is
        :attr:`~bigfix_relevance_analyzer.dialect.Dialect.UNCERTAIN`, whatever
        the classifier said. A statement using inspectors exclusive to both
        dialects *has* no dialect, so there is nothing for a verdict to be
        right about, and the classifier reaching one only means it saw half the
        evidence: `(exists files of folders "/") AND (exists bes computers)`
        classifies as session on the strength of the `bes ` prefix, while the
        client-only `files` and `folders` are words the text classifier is
        deliberately blind to. Analysis still has to run as *some* dialect, but
        reporting that pick as a conclusion would state a fact that is not one.
        A forced dialect is exempt: the caller said so, and the tables do not
        get a vote on what the caller meant.
        """
        if self.requested_dialect is not None:
            return False
        if self.resolved_dialect is Dialect.UNCERTAIN:
            return True
        if self.classified_dialect is not None:
            return False
        return not is_definite(self.resolved_dialect)

    @property
    def parsed(self) -> bool:
        """Whether the statement parsed."""
        return self.node is not None

    @property
    def valid(self) -> bool:
        """Whether it parsed *and* the tables found nothing wrong with it.

        Not proof that it runs: the tables are dumps of what some engines
        reported, so a clean result on an inspector no dump covers means
        "nothing contradicts this", not "this is correct".
        """
        return self.node is not None and self.check is not None and self.check.ok

    @property
    def error_tokens(self) -> tuple[Token, ...]:
        """Text the tokenizer could not lex. Non-empty means broken input."""
        return tuple(token for token in self.tokens if token.kind is TokenKind.ERROR)

    @property
    def code_tokens(self) -> tuple[Token, ...]:
        """The tokens that carry meaning: no whitespace, no comments."""
        return tuple(token for token in self.tokens if not token.is_trivia())

    @property
    def token_kinds(self) -> dict[str, int]:
        """How many tokens of each lexical kind, trivia included."""
        counts: dict[str, int] = {}
        for token in self.tokens:
            counts[token.kind.value] = counts.get(token.kind.value, 0) + 1
        return counts

    @property
    def nodes(self) -> tuple[Node, ...]:
        """Every node in the tree, parents first. Empty when it did not parse."""
        return () if self.node is None else tuple(walk(self.node))

    @property
    def node_kinds(self) -> dict[str, int]:
        """How many nodes of each class, keyed by class name."""
        counts: dict[str, int] = {}
        for item in self.nodes:
            name = type(item).__name__
            counts[name] = counts.get(name, 0) + 1
        return dict(sorted(counts.items()))

    @property
    def tree_depth(self) -> int:
        """The height of the tree; 0 when it did not parse."""
        return 0 if self.node is None else tree_depth(self.node)

    @property
    def sexpr(self) -> str | None:
        """The tree as an S-expression, the corpus's own notation."""
        return None if self.node is None else to_sexpr(self.node)

    @property
    def mermaid(self) -> str | None:
        """The tree as a Mermaid ``flowchart``, via
        :func:`~bigfix_relevance_analyzer.nodes.to_mermaid` -- a real graph
        of the parsed structure, not a description of one. ``None`` when it
        did not parse.
        """
        return None if self.node is None else to_mermaid(self.node)

    @property
    def platforms(self) -> frozenset[str]:
        """The evaluation contexts the statement as a whole can run on.

        Client platforms by their bare name and session surfaces as
        ``session:<context>``; both dialects are on the one axis, so a
        statement every dialect defines says so here. Empty when there is no
        tree to check.
        """
        return frozenset() if self.check is None else self.check.platforms

    @property
    def missing_platforms(self) -> frozenset[str]:
        """Contexts in play that this statement is *not* viable on.

        Reported, never enforced: a platform absent from the dumps has not been
        proven unsupported, only never observed.
        """
        return self.environment.universe - self.platforms

    @property
    def unknown_references(self) -> tuple[str, ...]:
        """Names no dump defines, sorted and de-duplicated.

        The most actionable single signal here for a typo, but not proof of
        one: the dumps do not cover every platform or product version.
        """
        return tuple(sorted({report.phrase for report in self.references if not report.known}))

    @property
    def unbound_its(self) -> tuple[ItBinding, ...]:
        """Occurrences of ``it`` with no context to bind to."""
        return tuple(entry for entry in self.it_bindings if entry.context is None)

    def autofix(self, *, guard: Guard = "warnings", max_rounds: int | None = None) -> AutofixResult:
        """This statement with every safe fix applied, as one final result.

        Re-analyses under the same requested dialect and platform this
        analysis ran with. See :func:`~bigfix_relevance_analyzer.autofix.autofix`
        for what "safe" means, and for ``guard`` and ``max_rounds``. Not
        memoized: this object is frozen, and a statement with nothing to fix
        -- the common case -- costs one pass over its diagnostics.
        """
        # Imported here: `autofix` builds on this module.
        from bigfix_relevance_analyzer.autofix import DEFAULT_MAX_ROUNDS, _autofix

        return _autofix(
            self,
            self.requested_dialect,
            self.environment.platform,
            guard,
            DEFAULT_MAX_ROUNDS if max_rounds is None else max_rounds,
        )

    def to_dict(self, *, mermaid: bool = False) -> dict[str, Any]:
        """The whole analysis as JSON-serializable plain data.

        For consumers across a wire -- an MCP server, a report file -- that
        cannot hold the node objects. Lossy by design: nodes become source
        text and S-expressions, enums become their values.

        ``mermaid`` adds the parse tree's flowchart under ``parse.mermaid``.
        Off by default for the same reason the CLI's ``--mermaid`` flag is
        opt-in: a line per box and per edge dwarfs the rest of the payload on
        a real statement, and the S-expression already carries the same tree.
        """
        report: dict[str, Any] = {
            "text": self.text,
            "dialect": {
                "classified": _enum(self.classified_dialect),
                "resolved": _enum(self.resolved_dialect),
                "requested": _enum(self.requested_dialect),
                "effective": self.dialect.value,
                "assumed": self.dialect_assumed,
            },
            "lexing": {
                "tokens": len(self.tokens),
                "code_tokens": len(self.code_tokens),
                "by_kind": self.token_kinds,
                "errors": [{"text": token.text, **_position(token)} for token in self.error_tokens],
            },
            "parse": {
                "ok": self.parsed,
                "error": None if self.parse_error is None else self.parse_error.to_dict(),
                "sexpr": self.sexpr,
                **({"mermaid": self.mermaid} if mermaid else {}),
                "node_count": len(self.nodes),
                "tree_depth": self.tree_depth,
                "node_kinds": self.node_kinds,
            },
            # `cost_rules` is grafted on here rather than living on
            # `RelevanceComplexity`, because a rule's cost depends on the
            # dialect being evaluated and only this object knows one.
            "complexity": {
                **self.complexity.to_dict(),
                "cost_rules": [
                    {
                        "label": rule.label,
                        "cost": rule.cost_for(self.dialect),
                        "why": rule.why,
                    }
                    for rule in self.cost_rules
                ],
            },
        }
        if self.check is not None:
            report["types"] = self.check.to_dict()
        report["platforms"] = {
            "viable": sorted(self.platforms),
            "universe": sorted(self.environment.universe),
            "missing": sorted(self.missing_platforms),
        }
        report["references"] = [
            {
                "phrase": report_entry.phrase,
                **_span(report_entry.reference.span),
                "known": report_entry.known,
                "visible_here": bool(report_entry.visible),
                "signatures": list(inspectors._signatures_of(report_entry.resolved)),
                "return_types": list(report_entry.return_types),
                "platforms": sorted(report_entry.platforms & self.environment.universe),
            }
            for report_entry in self.references
        ]
        report["unknown_references"] = list(self.unknown_references)
        # Inline, and staying that way: rendering a binding's `context` needs
        # the source text, which an `ItBinding` does not own. A
        # `to_dict(text=...)` would be a worse API than none at all.
        report["it_bindings"] = [
            {
                **_span(entry.it.span),
                "binder": _enum(entry.binder),
                "context": (
                    None
                    if entry.context is None
                    else self.text[entry.context.span.start : entry.context.span.end]
                ),
                "bound": entry.context is not None,
            }
            for entry in self.it_bindings
        ]
        report["levels"] = [level.to_dict() for level in self.levels]
        # `None` rather than an unchanged result: the question a consumer asks
        # is "is there a fixed version to offer", and no is the common answer.
        fixed = self.autofix()
        report["autofix"] = fixed.to_dict() if fixed.changed else None
        return report


def _dialect_of_names(references: tuple[ReferenceReport, ...]) -> Dialect | None:
    """The dialects every known name is defined in, as one :class:`Dialect`.

    See :attr:`RelevanceAnalysis.resolved_dialect`, which this is the first
    half of.
    """
    if not references:
        return Dialect.BOTH  # only core syntax used -- no inspectors to disagree
    supported: frozenset[Dialect] | None = None
    for reference in references:
        found = reference.dialects
        if not found:
            continue  # an unknown name, or one with no dialect at all
        supported = found if supported is None else supported & found
    if supported is None:
        return None
    if supported == {Dialect.CLIENT, Dialect.SESSION}:
        return Dialect.BOTH
    if supported == {Dialect.CLIENT}:
        return Dialect.CLIENT
    if supported == {Dialect.SESSION}:
        return Dialect.SESSION
    return Dialect.UNCERTAIN  # empty intersection: genuinely contradictory


def _rules_out(checked: CheckResult, references: tuple[ReferenceReport, ...]) -> bool:
    """Whether some known reference resolved to no row at all in ``checked``.

    Absent is not empty: a reference the walk never reached proves nothing.
    """
    return any(
        not checked.resolutions[key]
        for reference in references
        if reference.known and (key := id(reference.reference)) in checked.resolutions
    )


@functools.cache
def _in_both_dialects(name: str, kind: inspectors.InspectorKind | None = None) -> bool:
    """Whether every table row named ``name`` is defined in both dialects."""
    return all(
        Dialect.CLIENT in entry.dialects and Dialect.SESSION in entry.dialects
        for entry in inspectors.lookup(name, kind=kind)
    )


def _both_fit(
    node: Node, references: tuple[ReferenceReport, ...], checked: CheckResult | None
) -> bool:
    """Whether checking ``node`` as the other dialect cannot rule either out.

    The checker reads dialect-filtered rows in four places: references,
    casts, and binary and unary operators. ``checked`` ran as one dialect with
    no platform. If every known reference resolved there, to rows all defined
    in both dialects, and every cast and operator is the same in both, the
    other dialect sees at least those rows, so it resolves each reference to
    at least as much, and neither dialect is ruled out: the answer is BOTH
    without a second check. With no such check (a platform narrowed it), every
    row a reference could reach has to be in both instead.
    """
    for reference in references:
        if not reference.known:
            continue
        if checked is None:
            if not _in_both_dialects(reference.phrase):
                return False
            continue
        rows = checked.resolutions.get(id(reference.reference))
        if not rows or not all(
            Dialect.CLIENT in entry.dialects and Dialect.SESSION in entry.dialects for entry in rows
        ):
            return False  # absent, ruled out here, or resolved to one dialect's row
    for item in walk(node):
        if isinstance(item, Cast):
            neutral = _in_both_dialects(item.target, inspectors.InspectorKind.CAST)
        elif isinstance(item, Binary):
            form = grammar.CANONICAL_BINARY.get(item.op)
            neutral = form is None or _in_both_dialects(
                form.operator, inspectors.InspectorKind.BINARY_OPERATOR
            )
        elif isinstance(item, Unary):
            neutral = item.op == "not" or _in_both_dialects(
                item.op, inspectors.InspectorKind.UNARY_OPERATOR
            )
        else:
            continue
        if not neutral:
            return False
    return True


def analyze_to_dict(
    text: str,
    dialect: Dialect | None = None,
    platform: str | None = None,
    *,
    probe_kind: ProbeKind = ProbeKind.COUNT,
    mermaid: bool = False,
) -> dict[str, Any]:
    """:func:`analyze` then :meth:`RelevanceAnalysis.to_dict`, in one call.

    For a caller that only ever wanted the payload -- an MCP tool body, a
    report writer -- and would otherwise write the same two-step every time.
    Nothing is added and nothing is withheld; see :meth:`RelevanceAnalysis.to_dict`
    for what the keys mean and :mod:`bigfix_relevance_analyzer._serialize` for
    the conventions they follow.
    """
    return analyze(text, dialect, platform, probe_kind=probe_kind).to_dict(mermaid=mermaid)


def analyze(
    text: str,
    dialect: Dialect | None = None,
    platform: str | None = None,
    *,
    probe_kind: ProbeKind = ProbeKind.COUNT,
) -> RelevanceAnalysis:
    """Run every analysis over ``text`` and return the results together.

    ``dialect`` forces the dialect instead of classifying it -- pass the
    :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.dialect` extraction
    already worked out, rather than having it guessed a second time from a
    fragment out of context. When it is ``None`` and classification is
    undetermined, client is assumed and :attr:`RelevanceAnalysis.dialect_assumed`
    says so.

    ``platform`` narrows client lookups to one platform. Leaving it out keeps
    every platform in play and lets narrowing do the work, which is what makes
    :attr:`RelevanceAnalysis.platforms` meaningful.

    Never raises for bad relevance: see the module docstring.
    """
    return _analyze(text, dialect, platform, probe_kind=probe_kind)[0]


def _analyze(
    text: str,
    dialect: Dialect | None = None,
    platform: str | None = None,
    *,
    probe_kind: ProbeKind = ProbeKind.COUNT,
    all_checks: bool = False,
) -> tuple[RelevanceAnalysis, Mapping[Dialect, CheckResult]]:
    """:func:`analyze`, plus the checks it ran as each dialect with no platform.

    The checks are filled when the names say BOTH and checking again could
    tell the dialects apart, and empty otherwise. ``all_checks`` fills them
    whenever the names say BOTH, which is what
    :func:`~bigfix_relevance_analyzer.dialect.dialect_fit` needs: it reuses
    them rather than checking twice more. They stay out of the analysis itself
    because their ``id()`` keys mean nothing once it is copied.
    """
    classified = classify_relevance_dialect(text)
    effective = dialect or classified or Dialect.CLIENT
    environment = TypeEnvironment.create(effective, platform)

    # Lex once and hand the same stream to everything below. Each of the three
    # layers takes `str` at its public entry point and used to lex again behind
    # it, which made this function scan the input four times for one answer.
    lexed = _lex(text)
    parsed = _try_parse_lexed(text, lexed.code)
    node = parsed.node

    references: tuple[ReferenceReport, ...] = ()
    it_bindings: tuple[ItBinding, ...] = ()
    levels: tuple[Level, ...] = ()
    checked: CheckResult | None = None
    dialect_checks: Mapping[Dialect, CheckResult] = MappingProxyType({})
    form_dialect: Dialect | None = None
    if node is not None:
        checked = check(node, environment, source=text)
        references = tuple(
            ReferenceReport(
                reference=item,
                matches=(matches := inspectors.lookup(item.phrase)),
                visible=tuple(entry for entry in matches if environment.visible(entry)),
                narrowed=checked.resolutions.get(id(item), ()),
            )
            for item in walk(node)
            if isinstance(item, Reference)
        )
        it_bindings = resolve_it_bindings(node)
        levels = breakdown_probes(text, node, kind=probe_kind)
        # No references is BOTH whatever the checks say; only dialect_fit,
        # which wants each dialect's verdict, checks those again.
        if _dialect_of_names(references) is Dialect.BOTH and (
            all_checks
            or (
                references
                and not _both_fit(node, references, checked if platform is None else None)
            )
        ):
            # One name can be two inspectors (#141); which rows each reference
            # resolves to in each dialect decides. No platform, so platform
            # narrowing cannot rule a dialect out: reuse the check above only
            # when it already ran that way.
            dialect_checks = MappingProxyType(
                {
                    each: checked
                    if each is effective and platform is None
                    else check(node, TypeEnvironment.create(each, None), source=text)
                    for each in (Dialect.CLIENT, Dialect.SESSION)
                }
            )
            fits = [d for d, c in dialect_checks.items() if not _rules_out(c, references)]
            form_dialect = fits[0] if len(fits) == 1 else None

    complexity = _analyze_lexed(lexed.code, effective)
    analysis = RelevanceAnalysis(
        text=text,
        classified_dialect=classified,
        requested_dialect=dialect,
        environment=environment,
        tokens=lexed.tokens,
        parse_error=parsed.error,
        node=node,
        check=checked,
        references=references,
        it_bindings=it_bindings,
        levels=levels,
        complexity=complexity,
        # The rules the complexity pass already matched, rather than a second
        # pattern pass over the same words: labels are unique, and a rule
        # contributes cost exactly when its pattern matches.
        cost_rules=tuple(
            rule for rule in cost_rules_for(effective) if rule.label in complexity.costly_inspectors
        ),
        _form_dialect=form_dialect,
    )
    return analysis, dialect_checks


def client_platforms(analysis: RelevanceAnalysis) -> tuple[str, ...]:
    """The client platforms ``analysis``'s statement can run on, sorted.

    :attr:`~bigfix_relevance_analyzer.typecheck.RelevanceValue.client_platforms`
    of its type check, for a caller that starts from the analysis: session
    environments are left out, since no endpoint can match one. Empty when the
    text did not parse, so there was nothing to check.
    """
    return () if analysis.check is None else analysis.check.value.client_platforms
