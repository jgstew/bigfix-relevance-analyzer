"""Judge one analysis, or a whole file, against pre-commit-shaped rules.

:mod:`~bigfix_relevance_analyzer.analyzer` and
:mod:`~bigfix_relevance_analyzer.complexity` answer "what is true of this
statement"; this module answers "should a commit be blocked over it". Kept
separate so a caller that only wants the facts -- an editor hover, an MCP
server -- never pays for a threshold it did not ask for, and so a hook, CI,
and any other consumer share one verdict instead of each reimplementing it.

Like the rest of the package, this is print-free and never raises on bad
content: a file that fails to read, or a statement that fails to parse, is
itself something to report, not something to crash over.

    from bigfix_relevance_analyzer.lint import LintConfig, lint_paths

    findings = lint_paths(changed_paths, LintConfig(max_score=350))
    for finding in findings:
        print(finding)
    if any(f.severity is Severity.ERROR for f in findings):
        raise SystemExit(1)

Every rule is listed in :data:`RULES`; all but two are always on. The main ones:

- ``parse-error`` / ``error-token`` -- the statement is broken. Always an
  error; nothing to configure.
- ``unbound-it`` -- an ``it`` with no context to bind to. Always an error:
  it means the reference is meaningless in the engine, not merely unusual.
- ``type-error`` -- any other
  :attr:`~bigfix_relevance_analyzer.typecheck.CheckResult.diagnostics` the
  type checker reported (a type mismatch, a non-boolean ``whose`` filter, a
  tuple index out of range, ...). Always an error: these come from checking
  the parsed tree against the real inspector tables, not a heuristic, so a
  genuine type mismatch is as concrete a defect as a parse error. The
  ``used-without-context`` diagnostic is excluded here -- it is the checker's
  own independent detection of the same unbound ``it`` the ``unbound-it``
  rule above already reports, and including both would report one root cause
  twice.
- ``singular-required`` -- a plural operand where the engine requires a
  singular, which it refuses before evaluating anything. Always an error, and
  the one error that carries a fix: `unique value of`, or the singular
  spelling of a plural aggregate. Its own rule rather than ``type-error`` so a
  repo can turn the fix off by name and keep these as plain failures.
- ``mixed-dialect`` -- inspectors exclusive to client relevance and to session
  relevance in one statement, so no engine can evaluate it. Always an error:
  unlike ``unknown-inspector``, this is not a gap in the snapshot but two
  halves of it that exclude each other. See the rule's rationale in
  :data:`RULES` for why the two halves are not equally strong evidence.
- ``unknown-inspector`` -- a name no dump defines, or a bare world reference
  the dumps know only with a direct object (the checker's
  ``world-property-not-defined``). Always a warning, never an error by
  default, because the dumps do not cover every platform, product version, or
  evaluation context -- a name absent from them, or absent from the position
  it was written in, is a lead, not proof of a typo. Proxy agent inspectors
  are the standing example: ``devices`` is a top-level plural there, and the
  dumps record only the grub ``device of <grub file location>``.
- ``non-unique-risk`` -- a property written singular where more than one value
  may come back: over an object that may be plural
  (``singular-over-plural-object``), because the tables record the property
  itself as multivalued (``singular-of-multivalued-property``), or because a
  ``whose`` filter was asserted to match exactly one
  (``singular-of-filtered-collection``). A warning, not an error: the
  expression types cleanly, and the author may know exactly one value exists.
  See the rule's rationale in :data:`RULES` for the exemptions.
- ``complexity`` / ``evaluation-cost`` -- :attr:`RelevanceComplexity.score`
  and ``.evaluation_cost`` past a ceiling. On by default, at a generous
  built-in ceiling (:data:`DEFAULT_MAX_SCORE`, :data:`DEFAULT_MAX_EVALUATION_COST`)
  chosen to sit well above ordinary content and catch only the genuinely
  extreme -- content that legitimately needs to be this complex should raise
  :attr:`LintConfig.max_score` / ``.max_evaluation_cost`` rather than stay
  silent about it. Pass ``None`` for either (via the library API; there is no
  CLI spelling for it) to disable the rule entirely.
- ``file-error`` -- a path given to :func:`lint_file` / :func:`lint_paths` that
  does not exist, could not be read, or has a suffix no extractor reads.
  Always an error: it yields no sites, so left unreported it is
  indistinguishable from a clean file, and a typo'd path in a hook would pass
  CI having linted nothing. An existing directory is
  exempt -- a path is taken literally and only :func:`lint_directory` recurses.
- ``unterminated-substitution`` -- an ActionScript `{` with anything after it
  on its line and no `}` to close it there, which fails the action (issue 52).
  Always an error. Unlike every rule above, it is about the ActionScript
  around the relevance, found while extracting it, so its finding has no
  site.
- ``unterminated-processing-instruction`` / ``unterminated-code-fence`` /
  ``xml-parse-error`` -- the other problems met while extracting: a
  `<?Relevance` with no `?>` (error), a relevance-tagged markdown fence never
  closed (warning: the markdown is valid, but its relevance went unread), and a
  BES file that is not well-formed XML (error). Like the rule above, each
  means relevance that was never linted, so each finding has no site.
- ``max-depth-exceeded`` -- only from :func:`lint_directory`: a directory tree
  deeper than its ``max_depth`` was not fully walked. Always an error, because
  a limit this generous (6 levels, by default) being hit at all is itself
  worth a human's attention, and a silently truncated walk would look
  identical to a clean, fully-scanned one.

Deliberately not a rule here: :attr:`RelevanceAnalysis.missing_platforms` --
absence from the dumps is not proof of lack of support, so it stays a fact a
caller can read off the analysis directly rather than a finding this module
asserts an opinion about.

The keys of :data:`RULES` are a downstream vocabulary, not an internal one:
`pre-commit-bigfix`'s hook maps each to one of its own ``E6xx``/``W6xx`` codes,
and a repo's config disables rules by name. Adding, renaming or removing a code
is therefore a minor-version event with a consumer to update, not a detail --
that hook has a test that fails when a code here has no mapping there.

:func:`lint_paths` and :func:`lint_file` never expand a directory argument --
a path is taken literally, exactly like the extractor they wrap. Only
:func:`lint_directory` recurses, and only when a caller asks it to (both CLIs
reach for it solely when given zero path arguments, so an explicit ``.`` still
behaves like any other literal path).
"""

from __future__ import annotations

import enum
import functools
import heapq
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

from bigfix_relevance_analyzer._actionscript_keywords import ACTIONSCRIPT_KEYWORDS
from bigfix_relevance_analyzer._serialize import _as_path, _path
from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.extract import (
    _RECOGNIZED_SUFFIXES,
    RelevanceSite,
    _extract_data,
    _extract_file,
    _ExtractionProblem,
    _is_recognized,
)
from bigfix_relevance_analyzer.nodes import Node, Of, Reference
from bigfix_relevance_analyzer.tokenizer import TokenKind
from bigfix_relevance_analyzer.typecheck import (
    _UNIQUE_VALUE,
    SINGULAR_REQUIRED,
    Plurality,
    TypeDiagnostic,
    _is_aggregate,
)

if TYPE_CHECKING:
    from bigfix_relevance_analyzer.autofix import AutofixResult

__all__ = [
    "DEFAULT_MAX_DEPTH",
    "DEFAULT_MAX_EVALUATION_COST",
    "DEFAULT_MAX_SCORE",
    "DEFAULT_SEVERITIES",
    "RULES",
    "Finding",
    "LintConfig",
    "LintRule",
    "Severity",
    "counts",
    "lint_analysis",
    "lint_directory",
    "lint_file",
    "lint_paths",
    "lint_paths_to_dict",
    "lint_text",
    "rules",
]

DEFAULT_MAX_DEPTH = 6
"""How many directory levels below a :func:`lint_directory` root to descend.

The root itself is depth 0, so is a file directly inside it; each subdirectory
adds one. Chosen as a generous default rather than an unbounded walk, and
never exceeded silently -- see the ``max-depth-exceeded`` rule above.
"""

DEFAULT_MAX_SCORE = 550.0
"""The built-in ceiling for the ``complexity`` rule.

Chosen to sit well above ordinary content -- the package's own pinned test
statements score in the single digits to the mid-30s, and even a statement
with real nesting and several filters lands well under this -- while still
catching a statement that is genuinely, unusually complex. Raise
:attr:`LintConfig.max_score` for content that legitimately needs to be this
elaborate; pass ``None`` via the library API to disable the rule entirely.
"""

DEFAULT_MAX_EVALUATION_COST = 50.0
"""The built-in ceiling for the ``evaluation-cost`` rule.

Evaluation cost is summed from a small number of fixed per-occurrence tiers
(1, 3, 6, or 12 -- see :mod:`~bigfix_relevance_analyzer.complexity`), so this
ceiling tolerates several costly-inspector calls in one statement before
firing. Raise :attr:`LintConfig.max_evaluation_cost` for content that
legitimately needs them; pass ``None`` via the library API to disable the
rule entirely.
"""

_SKIP_DIR_NAMES = frozenset({"__pycache__", "node_modules", "dist", "build", "venv", "env"})
"""Directory names :func:`lint_directory` never descends into, by name alone.

Plus, unconditionally, any directory whose name starts with ``.`` (``.git``,
``.venv``, ``.mypy_cache``, ``.pytest_cache``, ``.ruff_cache``, ``.tox``, ...) --
common enough as a class that a single rule covers all of them without its own
entry per tool. Not ``.gitignore``-aware: that would mean depending on a `git`
binary and a repository being present, which this stdlib-only package does not
assume either of.
"""


class Severity(enum.Enum):
    """How a finding should count against a commit."""

    ERROR = "error"
    WARNING = "warning"
    IGNORE = "ignore"
    """Configured off. A finding at this severity is dropped, not emitted."""


@dataclass(frozen=True, slots=True)
class LintRule:
    """One rule, with the wording every consumer should explain it in.

    The rules were always documented -- in this module's docstring, in prose, for
    a human reading the source. This is the same explanation in a form a hook,
    a CI log, an editor hover, or an MCP server can serve, so that a finding
    means the same thing wherever it surfaces instead of each consumer
    inventing a description from the code alone.

    A :class:`Finding` carries only its :attr:`~Finding.code`; a consumer joins
    on it. That keeps the prose out of every finding, where it would repeat
    verbatim and dominate the payload of a large run.
    """

    code: str
    """Matches :attr:`Finding.code`, and this rule's key in :data:`RULES`."""

    default_severity: Severity
    """What it reports at when :attr:`LintConfig.severities` overrides nothing."""

    summary: str
    """One line: what fired. Sized for a table cell or a hover, so no trailing period."""

    rationale: str
    """Why the rule exists, and why it defaults the way it does. Full sentences."""

    gated: bool
    """Whether the rule is controlled by a numeric ceiling rather than being
    unconditionally on.

    Deliberately not called ``configurable``: *every* rule's severity is
    configurable through :attr:`LintConfig.severities`, so that name would be
    true of all of them and distinguish nothing. What these two have that the
    others do not is a ceiling with its own default, tunable independently of
    severity -- they still report by default, just only past that ceiling.
    """

    threshold: str | None = None
    """The :class:`LintConfig` field that carries a :attr:`gated` rule's ceiling.

    ``None`` for every rule that is always on with no ceiling to tune, so a
    consumer can render "raise ``max_score`` to relax this" without a lookup
    table of its own.
    """

    def to_dict(self) -> dict[str, Any]:
        """This rule as JSON-serializable plain data."""
        return {
            "code": self.code,
            "default_severity": self.default_severity.value,
            "summary": self.summary,
            "rationale": self.rationale,
            "gated": self.gated,
            "threshold": self.threshold,
        }


def _names(phrases: tuple[str, ...]) -> str:
    """`` `a` is `` / `` `a`, `b` are ``, for a clause that reads as English."""
    quoted = ", ".join(f"`{phrase}`" for phrase in phrases)
    return f"{quoted} {'is' if len(phrases) == 1 else 'are'}"


def _rule(
    code: str,
    default_severity: Severity,
    summary: str,
    rationale: str,
    *,
    threshold: str | None = None,
) -> tuple[str, LintRule]:
    return code, LintRule(
        code=code,
        default_severity=default_severity,
        summary=summary,
        rationale=rationale,
        gated=threshold is not None,
        threshold=threshold,
    )


#: Every rule this module can report. The rationales are the module docstring's
#: own rule list, moved here so there is one copy rather than a prose one
#: for humans and an implicit one for consumers.
RULES: Mapping[str, LintRule] = MappingProxyType(
    dict(
        (
            _rule(
                "parse-error",
                Severity.ERROR,
                "the statement could not be parsed",
                "The statement is broken, so nothing further can be concluded about it. "
                "Always an error, with nothing to configure.",
            ),
            _rule(
                "error-token",
                Severity.ERROR,
                "the statement contains text that could not be lexed",
                "Text the tokenizer could not read at all, which means the statement is "
                "broken even where it parsed around it. Always an error, with nothing to "
                "configure.",
            ),
            _rule(
                "unbound-it",
                Severity.ERROR,
                "`it` is used where there is no context to bind it to",
                "An unbound `it` is meaningless to the engine, not merely unusual, so this "
                "is always an error. Note that `of` binds `it` as well as `whose` does -- "
                "the runtime's own message claims otherwise and is wrong.",
            ),
            _rule(
                "type-error",
                Severity.ERROR,
                "the type checker reported a problem beyond an unbound `it`",
                "A type mismatch, a non-boolean `whose` filter, a tuple index out of range, "
                "and the rest of the type checker's diagnostic catalog -- these come from "
                "checking the parsed tree against the real inspector tables, not a "
                "heuristic, so a genuine type error is as concrete a defect as a parse "
                "error. Always an error, with nothing to configure.",
            ),
            _rule(
                "singular-required",
                Severity.ERROR,
                "a plural where the engine requires a single value",
                "An operator, or `|`, handed an operand that may be several values. The "
                "engine refuses it before evaluating anything -- `A singular expression "
                "is required.` -- so the statement can never run, which makes this an "
                "error. The fix is `unique value of` around the operand, or the singular "
                "spelling of a plural aggregate (`concatenations` -> `concatenation`): "
                "either runs whenever there is one distinct value, and fails on none or "
                "several just as the singular spelling would. The fix is refused where "
                "it would add a problem, such as a type `unique value of` does not take. "
                "Never applied to an ActionScript `{...}` substitution, which joins a "
                "plural rather than refusing it (see `plural-substitution`). Reported as "
                "`type-error` before this rule existed, so moving to it lowers a repo's "
                "`type-error` count by exactly these.",
            ),
            _rule(
                "site-type-mismatch",
                Severity.ERROR,
                "the value does not fit the kind of site it was extracted from",
                "Only extraction knows this: the same expression is correct in one slot "
                "and broken in another, so this is the one rule that reads the "
                "`RelevanceSite` rather than the statement alone -- and it is silent for "
                "a caller that lints bare text, which has no slot. Three slots constrain "
                "their value and are checked. A `<Relevance>` element decides "
                "applicability, so a clause that is not a boolean makes the content "
                "unable to apply anywhere. An `if`/`elseif`/`continue if` condition "
                "branches on its answer, takes one value, and -- confirmed by testing "
                "against a live client -- accepts a `boolean` or a `string` but nothing "
                "else. An ordinary ActionScript `{...}` substitution is not checked "
                "here: it accepts any type and joins a plural value rather than "
                "rejecting it, which `plural-substitution` reports. An error, not a "
                "warning, because neither is a risk the author may have ruled out -- the "
                "content cannot work. Positive evidence only, as everywhere else: an "
                "undetermined type or plurality is not a finding, and neither is a value "
                "some other rule already faulted. Analysis properties are deliberately "
                "unlisted, being legitimately plural and of any renderable type.",
            ),
            _rule(
                "plural-substitution",
                Severity.WARNING,
                "an ordinary ActionScript substitution's value may be more than one value",
                "A `run`/`wait`/`parameter` `{...}` substitution does not reject a "
                "plural: confirmed with real actions on a BES client, it joins every "
                'value with no separator -- `{("a";"b")}` substitutes `ab`, and no '
                "values at all substitute the empty string. So the content runs, but "
                "probably not as meant, which makes this a warning rather than "
                '`site-type-mismatch`\'s error. The fix is `concatenation "<sep>" of '
                "(...)` when several values are possible, or a tighter filter when "
                "exactly one is meant -- never `unique value of`, which errors on zero "
                "values and on two distinct ones, both of which substitute fine as "
                "written. A plural spelling that cannot answer more than one value is "
                "not a finding: an aggregate like `concatenations` or `maxima` applied "
                "to the whole value, and `tuple string items <n>` of such a value. "
                "`if`/`elseif`/`continue if` conditions were not part of that "
                "experiment and stay with `site-type-mismatch`.",
            ),
            _rule(
                "actionscript-keyword",
                Severity.ERROR,
                "an ActionScript command word used as a relevance name",
                "Usually an ActionScript line pasted or doubled into relevance, as in "
                '`elseif {elseif (exists package "glibc" ...)}`. The words come from '
                "the console's ActionScript grammar, minus every inspector name in any "
                "dialect (`parameter`, `setting`, `wait` and `set` are everyday "
                "relevance) and minus relevance's own grammar words (`if`, `else`, "
                "already parse errors). Every remaining word answers `The operator "
                '"<word>" is not defined.` on every client platform and qna version '
                "tested and in session relevance, so unlike `unknown-inspector` this is "
                "not a gap in the dumps: an error, and the word is not reported again "
                "as an unknown inspector.",
            ),
            _rule(
                "unknown-inspector",
                Severity.WARNING,
                "a name no inspector dump defines, at all or in the position it was written",
                "The most actionable single signal for a typo, but not proof of one: the "
                "dumps do not cover every platform, product version, or evaluation "
                "context, so a name absent from them is a lead rather than a fault. Two "
                "checker findings land here: a name in no dump at all, and a bare world "
                "reference the dumps know only with a direct object (proxy agent "
                "inspectors define top-level names like `devices` that the dumps record "
                "only as grub's `device of <grub file location>`). Always a warning, "
                "never an error by default.",
            ),
            _rule(
                "non-renderable-substitution",
                Severity.WARNING,
                "an ordinary ActionScript substitution's value is an opaque object with "
                "no text form",
                "A `run`/`wait`/`parameter` substitution embeds whatever its relevance "
                "answers with as text, and most types manage that fine -- a `boolean`, "
                "an `integer`, a `version`, even a `folder` (via its pathname). A "
                "curated handful genuinely can't: the whole `bes *` object family, "
                "`dmi *`/`smbios *` structs, `xml dom *`, `active directory *` objects, "
                "`sqlite *`, and bare objects like `dictionary`, `registry`, `process`, "
                "`socket`, `connection`. Unlike `site-type-mismatch`'s requirement on an "
                "`if`/`elseif`/`continue if` condition, nobody has run a real "
                "substitution with one of these and watched it fail -- this is the "
                "reasoning that an opaque object has no text form, not a live-engine "
                "confirmation, which is why it is a warning rather than that rule's "
                "hard error. Positive evidence only: a value that might resolve to a "
                "renderable type in one branch is not flagged.",
            ),
            _rule(
                "mixed-dialect",
                Severity.ERROR,
                "inspectors exclusive to client relevance and to session relevance in "
                "one statement",
                "Client relevance is evaluated by the BES Client on an endpoint and "
                "session relevance by the root server, so a statement needing "
                "inspectors from both is not a question either one can be asked -- "
                '`(exists files of folders "/") AND (exists bes computers)` has no '
                "engine. An error rather than a warning because, unlike "
                "`unknown-inspector`, this is not a gap in the snapshot: both halves "
                "are in it and they exclude each other. The evidence is not quite "
                "symmetric -- the client dumps are verified complete for the five "
                "sampled platforms against the engine's own `number of <category>`, "
                "while the session surface is sampled from the console, Web Reports "
                "and the REST API but not the WebUI or the Fixlet Debugger, so a name "
                "that looks client-only is the weaker half of the pair. Reported at "
                "error severity by deliberate choice rather than by symmetry of "
                "evidence; no site in `tests/examples/` triggers it.",
            ),
            _rule(
                "non-unique-risk",
                Severity.WARNING,
                "a property written singular where more than one value may come back",
                "Three sibling diagnostics land here. `value of results ...` writes the "
                "singular form over an *object* that may be plural, and `file of folder "
                "...` writes the singular form of a *property* the tables record as "
                "multivalued -- either way the written form settles the expression as "
                "singular, so the static singularity rule does not apply, and what "
                "remains is a runtime complaint: `Singular expression refers to "
                "non-unique object.` if several values exist, `... to nonexistent "
                "object.` if none do. Plural relevance is the best practice where a "
                "singular is not required. Collapsing is sometimes the point, so these "
                "cases are exempt: an aggregate (`unique value of`, `concatenation of`, "
                "`maximum of` ...), a value flowing into a position that requires a "
                "singular, and anything under an `|` error fallback, where the author "
                "has already answered for it -- and the property-side diagnostic is "
                "additionally quiet inside a `whose` predicate (elements are handled "
                "one at a time there), under `exists` (confirmed in qna: `exists "
                'file of folder "/"` answers True, no error, however many files '
                "exist), and in a tuple element, where "
                "plurality changes the meaning. What is left is a collapse nothing "
                "guards, and it is a warning rather than an error because the author "
                "may still know exactly one value exists. The third diagnostic, "
                "`value whose (...) of <key>` asserting that a *filter* matches one, "
                "is exempt only under a direct `exists`: it survives a singular "
                "context, where the other two are forgiven, because a filter always "
                "had a safe spelling available (`exists values whose (... and ...) of "
                "<key>`) and because the collapse is silent -- confirmed in qna, a "
                "filter over 49 folders that 47 satisfy answers 0 once a singular "
                "spelling inside it collapses, dropping every element that raised.",
            ),
            _rule(
                "plural-preferred",
                Severity.WARNING,
                "a singular spelling mid-chain, where the plural reads safer",
                "The sibling of `non-unique-risk`, reported where that hazard cannot "
                'fire. `pathname of file "x.bes" whose (...) of folder "c:\\\\"` cannot '
                "match twice -- a folder holds one file of a given name -- but it "
                "writes a filter on a singular spelling mid-chain, which is the habit "
                "that makes the same shape raise wherever the name is dropped, and it "
                "still raises `Singular expression refers to nonexistent object.` when "
                "the filter matches nothing, where the plural spelling answers 0. "
                "The same habit without a filter is reported too, wherever a plural "
                'is built from the singular: `exists values of setting "x" of client` '
                "raises the same error when the setting is absent, and `exists` does "
                "not hide it -- the plural property distributes over the singular's "
                'error (confirmed in qna; `settings "x"` answers False). A direct '
                '`exists` over the singular (`exists setting "x" of client`, or a '
                "filtered form) answers False today and is reported anyway, since it "
                "errors again the moment the `exists` is dropped while the relevance is "
                "expanded. Quiet left of an `|`, where the error is what trips the "
                'fallback, and on a root spelling such as `folder "/tmp"`. '
                "Best practice is to stay plural for as long as the chain runs and "
                "collapse once at the end, with `unique value of` where a singular is "
                'actually required: `unique value of pathnames of files "x.bes" whose '
                '(...) of folders "c:\\\\"`. A warning, and a separate rule from '
                "`non-unique-risk` so that silencing this shape does not also silence "
                "the collapses that error on several rather than on none.",
            ),
            _rule(
                "version-truncating-compare",
                Severity.WARNING,
                "a version comparison that truncates to the shorter operand's components",
                "A version comparison only compares as many components as the *shorter* "
                'side has, so the engine calls `version "1.2.3"` and `version "1.2"` '
                "equal -- deliberate engine behavior, and the reason a truncating `=` "
                "works as a prefix match. Applied to the ordering operators it is "
                "harmless for half of them and a gotcha for the other half: on a 14.6.1 "
                'host, `version of operating system > version "14"` answers `False`, so '
                'a fixlet gating on "newer than 14" excludes exactly the machines it was '
                "written for -- without erroring, which is why nothing downstream "
                "notices. Only the operators that flip at equality in the direction of "
                "the dropped tail are reported, so the common and correct `>= version "
                '"5.1"` idiom is left alone. The fix is `pad of` on both sides, which is '
                "defined in every captured source. A warning, not an error, both "
                "because the statement is well-formed and because the truncating "
                "behavior is sometimes exactly what the author wanted.",
            ),
            _rule(
                "version-like-string-compare",
                Severity.WARNING,
                "two version-looking strings compared as strings, not as versions",
                "With no `version` on either side the engine compares string literals "
                'lexicographically, so `"2.10.1" > "2.3.3"` is `False` -- the opposite '
                "of what anyone writing it intends. It needs only one component to cross "
                "a digit-width boundary, which `1.9` to `1.10` does, and that is exactly "
                "where a version comparison matters. Adding `as version` to either side "
                "is enough: one typed operand coerces the other. Reported only for "
                "dotted-numeric literals on both sides, so ordinary string comparisons "
                "are untouched.",
            ),
            _rule(
                "complexity",
                Severity.ERROR,
                "the complexity score is above the ceiling",
                "On by default at a generous built-in ceiling (`DEFAULT_MAX_SCORE`) chosen "
                "to sit well above ordinary content and catch only the genuinely extreme. "
                "Content that legitimately needs to be this complex should raise "
                "`max_score` rather than stay silent about it; pass `None` via the library "
                "API to disable the rule entirely.",
                threshold="max_score",
            ),
            _rule(
                "evaluation-cost",
                Severity.ERROR,
                "the evaluation cost is above the ceiling",
                "On by default at a generous built-in ceiling (`DEFAULT_MAX_EVALUATION_COST`), "
                "for the same reason as the complexity ceiling: content that legitimately "
                "needs to run this expensively should raise `max_evaluation_cost` rather "
                "than stay silent about it; pass `None` via the library API to disable the "
                "rule entirely.",
                threshold="max_evaluation_cost",
            ),
            _rule(
                "file-error",
                Severity.ERROR,
                "a path given to the linter does not exist, could not be read, "
                "or is a file type it does not lint",
                "A path that is not there yields no sites, which reads exactly like a clean "
                "file unless it is reported -- so a misspelled path in a pre-commit hook would "
                "otherwise pass CI having linted nothing. Always an error: the caller named "
                "this file, so failing to read it is a fault in the run rather than an opinion "
                "about content. An existing *directory* is not a file error; it is skipped, "
                "because a path here is taken literally and only :func:`lint_directory` "
                "recurses.",
            ),
            _rule(
                "unterminated-substitution",
                Severity.ERROR,
                "an ActionScript `{` is not closed on its line, so the action fails there",
                "The action engine substitutes relevance line by line, so a `}` on a later "
                "line never closes a `{`. A `{` that is its line's last character is written "
                "literally (`try {`); one with anything after it, even trailing whitespace, "
                "fails the action -- confirmed with real actions, inside `createfile until` "
                "bodies and outside them (issue 52). Always an error: no statement is "
                "extracted from the line, so it would otherwise lint clean. There is no "
                "autofix, because closing it with `}` and escaping it as `{{` mean different "
                "things and only the author knows which was meant.",
            ),
            _rule(
                "unterminated-processing-instruction",
                Severity.ERROR,
                "a `<?Relevance` has no closing `?>`, so its relevance was not linted",
                "A processing instruction may span lines, but it has to close: with no `?>` "
                "after it in the document -- or, in a BES `<Description>`, before "
                "`</Description>` -- there is no statement to extract, and the file would "
                "otherwise lint clean with relevance in it that nobody checked. An error for "
                "the same reason as `file-error`: a silent pass over content that was never "
                "read.",
            ),
            _rule(
                "unterminated-code-fence",
                Severity.WARNING,
                "a relevance code fence in markdown is never closed, so its relevance was "
                "not linted",
                "Only fences tagged `relevance`, `client_relevance` or `session_relevance`. "
                "CommonMark runs an unclosed fence to the end of the document, so the markdown "
                "itself is valid and renders, which is why this is a warning rather than an "
                "error -- but the relevance in it is never extracted, so it is never checked.",
            ),
            _rule(
                "xml-parse-error",
                Severity.ERROR,
                "a BES XML file does not parse, so nothing in it was linted",
                "Reported at the line the XML parser stopped on. Checking documents against "
                "the BES schema is not this package's job, but a file that is not well-formed "
                "XML yields no sites at all, which would otherwise read exactly like a clean "
                "file.",
            ),
            _rule(
                "max-depth-exceeded",
                Severity.ERROR,
                "a directory tree was deeper than the walk's limit, so it was not fully scanned",
                "Reported only by :func:`lint_directory`. Always an error, because a limit "
                "this generous being reached at all deserves a human's attention, and a "
                "silently truncated walk would look identical to a clean, complete one.",
            ),
        )
    )
)


def rules() -> tuple[LintRule, ...]:
    """Every rule, in the order a rule list should render them.

    Errors before warnings, because the question a reader brings to a rule list
    is what will block a commit; alphabetical within a severity, so the order
    never depends on where an entry happens to sit in :data:`RULES`.
    """
    ranked = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.IGNORE: 2}
    return tuple(
        sorted(RULES.values(), key=lambda rule: (ranked[rule.default_severity], rule.code))
    )


#: Severity a rule reports at when :attr:`LintConfig.severities` says nothing
#: about it. Keyed by :attr:`Finding.code`. Derived from :data:`RULES` so the
#: two cannot disagree -- this was a second hand-maintained literal once.
DEFAULT_SEVERITIES: Mapping[str, Severity] = MappingProxyType(
    {code: rule.default_severity for code, rule in RULES.items()}
)


@dataclass(frozen=True, slots=True)
class TextSpan:
    """Which characters of the analysed statement a :class:`Finding` is about.

    0-based offsets, end exclusive, into the text that was analysed: a site's
    :attr:`~bigfix_relevance_analyzer.extract.RelevanceSite.text` when the
    finding came from extraction, else the bare statement (stripped, as
    :func:`lint_text` analyses it). Relative to the statement, never to a file,
    so a span stays right when the statement moves and is independent of how
    the file was decoded. Turning one into a file position is the consumer's
    job; :mod:`bigfix_relevance_analyzer.lsp.positions` does it for an editor.

    ``start == end`` is a point between characters: a parse error at the end
    of the statement, where there is no character to cover.

    Deliberately not :class:`~bigfix_relevance_analyzer.nodes.Span`, whose line
    and column are relative to the statement too and would read as a file
    position on a finding that carries a file path.
    """

    start: int
    end: int

    message: str | None = None
    """What to say about this span alone, when the finding's own message covers
    several. Only ``unknown-inspector`` sets it: one span per use of each
    unknown name, each saying which name and offering that name's leads, where
    the finding's message lists every name and all their leads together.
    ``None`` means the finding's message is the one to show."""

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "message": self.message}


@dataclass(frozen=True, slots=True)
class Finding:
    """One thing worth a commit's attention, already worded to stand alone."""

    code: str
    """Which rule fired -- see the keys of :data:`DEFAULT_SEVERITIES`."""

    severity: Severity

    message: str
    """One line, already including whatever detail explains *why*."""

    path: Path | None
    """The file this came from, or ``None`` for a bare :func:`lint_analysis` call."""

    line: int
    """1-based line, absolute in ``path`` when one is set; else relative to the text."""

    site: RelevanceSite | None = None
    """The extraction site this analysis came from, when there was one."""

    suggestions: tuple[str, ...] = ()
    """Names the reported one may have been meant to be, best first.

    Only ever populated for ``unknown-inspector``, and only when
    :attr:`LintConfig.suggest` asked for it -- see that flag for why it is not
    the default. Empty rather than ``None`` on every other rule, so a consumer
    reads one type for every finding instead of special-casing six of seven
    codes.

    The same names appear in :attr:`message`. That duplication is deliberate,
    for the same reason :meth:`to_dict` repeats the rendered line under
    ``text``: a human wants the sentence, and a program should not have to
    parse prose back out of it.
    """

    autofix: AutofixResult | None = None
    """The whole statement with every safe fix applied, on a finding a fix
    resolves.

    Deliberately the *site's* result rather than this finding's own edit:
    fixes cascade and interact, so the only rewrite worth offering is the one
    worked out over all of them at once. Every fixable finding from the same
    site therefore carries the same result -- a hook swaps the site's text for
    :attr:`~bigfix_relevance_analyzer.autofix.AutofixResult.fixed` once, not
    once per finding. ``None`` on every other finding, and on a fixable one
    whose fix the guard refused, so ``is not None`` means there is a fixed
    version to offer.
    """

    spans: tuple[TextSpan, ...] = ()
    """The characters of the statement this finding is about, when it knows.

    See :class:`TextSpan` for what the offsets are into. Empty means the
    finding is about the statement as a whole -- ``complexity``,
    ``mixed-dialect``, a substitution's slot -- or about the file around it
    (an unterminated fence, say), and a consumer should fall back to
    :attr:`line`. One span for most rules: the token, ``it``, or expression
    the rule is about. ``unknown-inspector`` stays one finding per statement
    but has a span for every use of every name it reports, in source order.

    Where there is a span, :attr:`line` is the line it starts on, except for
    ``unknown-inspector``, which reports the statement's first line.
    """

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}" if self.path is not None else f"line {self.line}"
        return f"{where}: {self.severity.value} [{self.code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """This finding as JSON-serializable plain data.

        ``text`` is ``str(self)`` -- the one-line, grep-able rendering both CLIs
        print. It is included because every consumer wants it and none should
        have to reproduce the format, which is a real API despite looking like
        a detail: a hook's output is diffed and parsed downstream.

        Deliberately absent: the rule's ``summary`` and ``rationale``. Those
        live once in :data:`RULES`, keyed by :attr:`code`, and a consumer joins
        on it. Inlining two sentences into every finding would multiply the size
        of a lint payload over a large repo for text that repeats verbatim.
        """
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "path": _path(self.path),
            "line": self.line,
            "site": None if self.site is None else self.site.to_dict(),
            "suggestions": list(self.suggestions),
            "autofix": None if self.autofix is None else self.autofix.to_dict(),
            "text": str(self),
            "spans": [span.to_dict() for span in self.spans],
        }


@dataclass(frozen=True, slots=True)
class LintConfig:
    """What to gate on. See the module docstring for what each rule does by default."""

    max_score: float | None = DEFAULT_MAX_SCORE
    """Ceiling for the ``complexity`` rule. ``None`` disables it entirely."""

    max_evaluation_cost: float | None = DEFAULT_MAX_EVALUATION_COST
    """Ceiling for the ``evaluation-cost`` rule. ``None`` disables it entirely."""

    severities: Mapping[str, Severity] = field(default_factory=dict)
    """Per-code overrides of :data:`DEFAULT_SEVERITIES`. Unlisted codes keep their default."""

    dialect: Dialect | None = None
    """Force the dialect instead of trusting extraction or classifying the text."""

    platform: str | None = None

    suggest: bool = False
    """Whether to attach "did you mean" candidates to ``unknown-inspector``.

    Off by default because it is not free and the rule it helps is the most
    frequent one: unknown names are *common* in a repo running newer inspectors
    than the snapshot, which is precisely why the rule is a warning rather than
    an error. Fuzzy matching costs milliseconds per name, so a few thousand
    sites would add real latency to a pre-commit hook for a finding that blocks
    nothing.

    Worth turning on for an interactive consumer -- an editor, or an MCP server
    handing findings to a model -- where one extra millisecond buys a lead the
    reader would otherwise have to go and look up. See
    :func:`~bigfix_relevance_analyzer.inspectors.suggest`.
    """

    def severity_for(self, code: str) -> Severity:
        return self.severities.get(code, DEFAULT_SEVERITIES.get(code, Severity.WARNING))


def counts(findings: Iterable[Finding]) -> Mapping[str, int]:
    """How many findings at each reportable severity, zeros included.

    The one piece of arithmetic every consumer of this module repeats, and the
    piece they must agree on: whether a run passed is
    ``counts(findings)["error"] == 0``, and both CLIs here decide it that way.
    A caller with a stricter policy -- ``--fail-on-warning`` -- layers it on top
    of these numbers rather than recounting them.

    :attr:`Severity.IGNORE` gets no key. A finding at that severity is dropped
    before it is ever built, so a key for it would read zero forever and imply
    the linter had looked for something and found none of it.
    """
    tallies = {Severity.ERROR.value: 0, Severity.WARNING.value: 0}
    for finding in findings:
        if finding.severity is not Severity.IGNORE:
            tallies[finding.severity.value] += 1
    return tallies


def _passed(tallies: Mapping[str, int]) -> bool:
    """The default gate, from :func:`counts`: nothing at error severity.

    Takes the tallies rather than the findings so a caller that also prints
    them counts once -- see :func:`counts` for why both CLIs share this.
    """
    return tallies[Severity.ERROR.value] == 0


def _findings_dict(findings: Iterable[Finding]) -> dict[str, Any]:
    """The ``findings``/``counts``/``ok`` envelope every JSON output here shares.

    See :func:`lint_paths_to_dict` for why it is the envelope and not just the
    list.
    """
    listed = tuple(findings)
    tallies = counts(listed)
    return {
        "findings": [finding.to_dict() for finding in listed],
        "counts": dict(tallies),
        "ok": _passed(tallies),
    }


def _finding(
    config: LintConfig,
    code: str,
    message: str,
    *,
    path: Path | None,
    line: int,
    site: RelevanceSite | None = None,
    suggestions: tuple[str, ...] = (),
    autofix: AutofixResult | None = None,
    spans: tuple[TextSpan, ...] = (),
) -> Finding | None:
    """A :class:`Finding` at ``code``'s configured severity, or ``None`` when
    that severity is :attr:`Severity.IGNORE` -- an ignored finding is never
    built at all (see :func:`counts`)."""
    severity = config.severity_for(code)
    if severity is Severity.IGNORE:
        return None
    return Finding(
        code=code,
        severity=severity,
        message=message,
        path=path,
        line=line,
        site=site,
        suggestions=suggestions,
        autofix=autofix,
        spans=spans,
    )


def _complexity_detail(report: RelevanceAnalysis, limit: int = 3) -> str:
    metrics = report.complexity
    parts = []
    for name, _weighted in metrics.contributions[:limit]:
        raw = getattr(metrics, name, None)
        parts.append(f"{name}={raw}" if raw is not None else name)
    return ", ".join(parts)


def _site_dialect(site: RelevanceSite, forced: Dialect | None) -> Dialect | None:
    # A site the extractor already classified is a stronger signal than
    # re-classifying the bare fragment: a forced dialect (--dialect) still
    # wins, but otherwise trust extraction's read of the surrounding document
    # over guessing from the statement alone.
    return forced if forced is not None else (site.dialect if is_definite(site.dialect) else None)


# Checker diagnostics that are not `type-error`. The checker reports what the
# engine would say; this layer decides how much it matters, and a runtime risk
# the author may have ruled out is not the same as a static type error.
_CHECK_RULES: Final = {
    "singular-over-plural-object": "non-unique-risk",
    "singular-of-multivalued-property": "non-unique-risk",
    # Same warning, and the one the checker keeps standing under a singular
    # context, because a `whose` filter had a safe spelling available.
    "singular-of-filtered-collection": "non-unique-risk",
    # Not a risk at all -- a shape. Its own rule so that the hazard rule stays
    # about hazards, and so a repo that does not want the style note can
    # silence it without silencing the errors-at-evaluation ones.
    "filtered-singular-spelling": "plural-preferred",
    # The same habit without a filter: a singular spelling mid-chain where a
    # plural is being built. Same rule, same rationale.
    "singular-spelling-mid-chain": "plural-preferred",
    # The engine's up-front `A singular expression is required.`. An error like
    # `type-error`, but its own rule because it carries a fix a repo may want
    # off by name.
    **dict.fromkeys(SINGULAR_REQUIRED, "singular-required"),
    # Version comparison. Their own rules rather than `type-error`, because the
    # statement type-checks: the engine answers it, and the answer is wrong.
    # Separate from each other so a repo can silence the stylistic prefix-match
    # reading of `=` without also silencing the string-compare defect.
    "version-truncating-compare": "version-truncating-compare",
    "version-like-string-compare": "version-like-string-compare",
    # A bare world reference the dumps know only with a direct object -- the
    # same epistemic state as a name no dump defines (the snapshot has no row
    # for *this position*, and the snapshot is known-incomplete), so it lands
    # on the same rule. Proxy agent inspectors are the motivating case:
    # `devices` is a top-level plural there, and collides with the captured
    # `device of <grub file location>`.
    "world-property-not-defined": "unknown-inspector",
}


def _fix_applied(diagnostic: TypeDiagnostic, fixed: AutofixResult | None) -> bool:
    """Whether the site's fixed text includes ``diagnostic``'s own fix.

    The site's result is one rewrite over every fix, so a fix the guard
    refused can sit beside one it applied. Each composed edit is against the
    original, as the fix's range is, so the fix was applied when an edit
    overlaps that range -- overlap rather than containment, because a
    respelling's range may run on into whitespace the edit trimmed off --
    unless the edit is a `unique value of` wrap that kept this range verbatim
    inside it, which is some other fix's.
    """
    from bigfix_relevance_analyzer.autofix import _kept

    fix = diagnostic.fix
    if fix is None or fixed is None:
        return False
    for edit in fixed.edits:
        if not (edit.start < fix.end and fix.start < edit.end):
            continue
        own = (edit.start, edit.end) == (fix.start, fix.end)
        if not own and _kept(edit, fixed.original) is not None:
            continue
        return True
    return False


def _with_fix(diagnostic: TypeDiagnostic, applied: bool) -> str:
    """``diagnostic``'s message, plus what its fix did when it was ``applied``.

    Only for the :data:`SINGULAR_REQUIRED` codes, where the rewrite is the
    point of the finding. Plain on purpose: no advice about a tighter index,
    which belongs to a non-unique failure if `unique value of` ever hits one.
    """
    fix = diagnostic.fix
    if fix is None or not applied or diagnostic.code not in SINGULAR_REQUIRED:
        return diagnostic.message
    if fix.replacement.startswith(_UNIQUE_VALUE):
        done = "wrapped in `unique value of`"
    else:
        done = f"respelled `{fix.expected}` as `{fix.replacement}`"
    return f"{diagnostic.message}; {done}: this position requires a single value"


def _rule_for(check_code: str) -> str:
    """The lint rule a checker diagnostic code reports under; see :data:`_CHECK_RULES`."""
    return _CHECK_RULES.get(check_code, "type-error")


# What each kind of site requires of the value it holds. Only the slots the
# engine genuinely constrains are listed: an applicability clause decides yes
# or no, and an `if`/`elseif`/`continue if` condition needs an answer to
# branch on and only accepts a `boolean` or a `string`. An ordinary
# ActionScript substitution is deliberately absent: confirmed with real
# actions (#68), it accepts any renderable type and joins a plural value
# rather than rejecting it -- a risk `_plural_substitution` reports as a
# warning, not a requirement this table could fail. An analysis
# property may legitimately be plural and of any renderable type, a `.rel`
# file or a markdown block is not a slot at all, and the remaining contexts
# have not been confirmed -- an unlisted kind is judged on nothing.
#
# The required-type axis is always a set, even where exactly one name would
# do: one representation for `_slot_mismatch` to check, rather than a
# single-name shape and a set shape both needing their own branch.
_SLOT_REQUIREMENTS: Final = {
    "relevance": ("singular", frozenset({"boolean"})),
    "actionscript-condition": ("singular", frozenset({"boolean", "string"})),
}


def _slot_mismatch(site: RelevanceSite | None, report: RelevanceAnalysis) -> str | None:
    """How ``report``'s value fails the slot ``site`` came out of, if it does.

    Positive evidence only, the discipline the checker follows everywhere --
    but *per axis*, because plurality and type are established separately. A
    value the checker could not type may still be one it is certain is plural,
    since plurality is settled by the written spelling: `concatenation ", " of
    (...) of (<plural>)` answers once per element whatever those elements turn
    out to be. Gating the plurality check on the type being known lost the only
    real instance in a 160,249-site corpus.

    A value already ruled out -- an empty type set, meaning every candidate was
    eliminated -- is skipped on both axes, because some other rule has already
    faulted it and this would be one problem told twice.

    Both axes are evaluated before either is reported, because a value can
    fail both at once, and the type failure is the one worth naming: shipped
    content proves that a plurality finding alone reads as an instruction --
    "collapse it" -- that a reader follows to a respelling still not the
    required type. `AutomaticComputerGroups/VM - Hyper-V.bes` was exactly
    this, `unique values whose (...) of (dmis; smbioses; bioses)` over a
    `SearchComponentRelevance/Relevance` slot, which needs a `boolean`: the
    respelling that clears the plurality complaint, `unique value of
    <plural>`, is still a version string, not a `boolean`, and only `exists`
    over the plural form actually answers the slot's question. The type
    problem does not depend on the plurality one -- it does not go away when
    the value is singular -- so it is worth stating whichever finding
    literally fired first.
    """
    if site is None or report.check is None:
        return None
    requirement = _SLOT_REQUIREMENTS.get(site.kind)
    if requirement is None:
        return None
    plurality, required_types = requirement
    value = report.check.value
    if value.types is not None and not value.types:
        return None

    is_plural = plurality == "singular" and value.plurality is Plurality.PLURAL
    if (
        required_types is not None
        and (known_types := value.types) is not None
        and known_types.isdisjoint(required_types)
    ):
        rendered = " or ".join(f"`{name}`" for name in sorted(known_types))
        wanted = sorted(required_types)
        requirement_phrase = (
            f"a `{wanted[0]}`" if len(wanted) == 1 else " or ".join(f"`{name}`" for name in wanted)
        )
        message = f"{site.context} must be {requirement_phrase}; this is {rendered}"
        if is_plural:
            # Naming both, not just the type: a reader who only collapses the
            # plurality -- exactly the fix the other message on its own
            # suggests -- still has not produced an acceptable type, and needs
            # to know that before trying it.
            message += (
                ", and plural -- respelling it singular does not change the type; "
                "`exists` answers the slot directly"
            )
        return message

    if is_plural:
        return (
            f"{site.context} takes one value; this is plural -- "
            "an aggregate such as `unique value of` collapses it"
        )
    return None


# `tuple string items <n>` of one string answers at most one value: confirmed
# in QnA, `number of tuple string items 0 of concatenations ", " of ("a";"b")`
# is 1 (and 0 over no values).
_TUPLE_STRING_ITEMS: Final = frozenset({"tuple string item", "tuple string items"})


def _at_most_one_value(node: Node) -> bool:
    """Whether ``node``, though perhaps spelled plural, cannot answer more than one value.

    Narrow and syntactic on purpose, covering the shapes shipped content uses:
    an aggregate applied to the whole value (`concatenations ", " of X`) and
    `tuple string items <n>` of such a value. An aggregate *distributed* over
    a plural -- `(concatenations ", " of it) of ("a";"b")`, a property `Of`
    whose own object is `it` -- answers once per element (2, in QnA), so only
    a bare `Reference` as the property counts. `unique values` is not an
    aggregate in this sense: it answers once per distinct value.
    """
    if not isinstance(node, Of) or not isinstance(node.prop, Reference):
        return False
    phrase = node.prop.phrase
    if phrase in _TUPLE_STRING_ITEMS:
        return _at_most_one_value(node.obj)
    return phrase not in {"unique value", "unique values"} and _is_aggregate(phrase)


def _plural_substitution(site: RelevanceSite | None, report: RelevanceAnalysis) -> str | None:
    """Whether an ordinary substitution's value may be more than one value.

    Positive evidence only, as in `_slot_mismatch`: the checker has to be sure
    the value is plural, and a value some other rule already ruled out (an
    empty type set) is skipped.
    """
    if site is None or site.kind != "actionscript-substitution" or report.check is None:
        return None
    value = report.check.value
    if value.plurality is not Plurality.PLURAL or (value.types is not None and not value.types):
        return None
    if report.node is not None and _at_most_one_value(report.node):
        return None
    return (
        f"{site.context} is plural: the values are joined with no separator "
        '(`("a";"b")` gives `ab`, no values give an empty string) -- use '
        '`concatenation "<sep>" of (...)` if more than one is possible, or a tighter '
        "filter if exactly one is meant"
    )


# Object types with no meaningful text form when substituted -- curated by
# name pattern, not derived from the dumps' cast table. The cast table only
# records a `<T> as string` row where something else in the dumps sampled
# one, so most scalars have no row at all despite obviously rendering fine
# (`utf8 string`, every `... with multiplicity` element type); deriving from
# it would flag the common case, not the rare one. Confirmed directly on two
# of the bare entries below, unrelated to anything else in this codebase's
# history:
#
#     Q: "x" & (processes as string)
#     E: The operator "string" is not defined.
#     Q: "x" & (dictionaries of files "/etc/hosts" as string)
#     E: The operator "string" is not defined.
#
# and that an object *not* on this list, `folder`, does render -- via its
# pathname, confirmed the same way:
#
#     Q: "x" & (folder "/tmp" as string)
#     A: x/tmp
#
# so the list stays narrow and deliberate. This is inference, not a
# live-confirmed engine fact the way the `actionscript-condition` type
# requirement above is -- see `non-renderable-substitution` in `RULES` for
# why that keeps it a warning rather than a `site-type-mismatch` error.
_NON_RENDERABLE_TYPE_PREFIXES: Final = (
    "bes ",
    "dmi ",
    "smbios ",
    "xml dom ",
    "active directory ",
    "sqlite ",
)
_NON_RENDERABLE_TYPES: Final = frozenset(
    {
        "wmi object",
        "registry",
        "socket",
        "connection",
        "process",
        "security descriptor",
        "security database",
        "array",
        "dictionary",
        "nothing",
    }
)


def _is_non_renderable(name: str) -> bool:
    return name in _NON_RENDERABLE_TYPES or name.startswith(_NON_RENDERABLE_TYPE_PREFIXES)


def _non_renderable_substitution(
    site: RelevanceSite | None, report: RelevanceAnalysis
) -> str | None:
    """Whether an ordinary substitution's value is an opaque object.

    Gated to `"actionscript-substitution"` alone: an `if`/`elseif`/`continue
    if` condition already has its own, stricter, confirmed requirement in
    `_slot_mismatch`, and a `<Relevance>` element's boolean requirement rules
    this out on its own axis.

    Positive evidence only, same discipline as `_slot_mismatch`: flags only
    when *every* possible type is on the blocklist, so a value that might
    resolve to a renderable type in one branch and an opaque one in another
    is left alone.
    """
    if site is None or site.kind != "actionscript-substitution" or report.check is None:
        return None
    types = report.check.value.types
    if not types or not all(_is_non_renderable(name) for name in types):
        return None
    rendered = " or ".join(f"`{name}`" for name in sorted(types))
    return f"{site.context} substitutes {rendered}, which has no string representation to embed"


def _unknown_message(names: tuple[str, ...], leads: tuple[str, ...]) -> str:
    """``unknown-inspector``'s wording, for a statement's names or for one of them."""
    message = "no dump defines " + ", ".join(f"`{name}`" for name in names)
    if not leads:
        return message
    quoted = [f"`{lead}`" for lead in leads]
    # "a, b or c" rather than "a or b or c" -- three `or`s in one clause reads
    # as a parser bug rather than a list.
    offered = quoted[0] if len(quoted) == 1 else f"{', '.join(quoted[:-1])} or {quoted[-1]}"
    return f"{message} -- did you mean {offered}?"


def _parse_error_span(report: RelevanceAnalysis, offset: int) -> TextSpan:
    """The token a parse error points at, or the empty span at ``offset``
    when none starts there -- the end of the statement, typically."""
    for token in report.tokens:
        if token.offset == offset and not token.is_trivia():
            return TextSpan(offset, offset + len(token.text))
    return TextSpan(offset, offset)


def _name_span(report: RelevanceAnalysis, reference: Reference) -> TextSpan:
    """Where ``reference``'s name is written, without its index argument.

    A reference's own span takes in the argument -- ``bogus "x"`` -- but the
    name is what a name rule is about. The name ends with its last word
    before the argument, which tokens say exactly, wherever comments or
    parentheses sit.
    """
    span = reference.span
    if reference.index is None:
        return TextSpan(span.start, span.end)
    stop = reference.index.span.start
    end = max(
        (
            token.offset + len(token.text)
            for token in report.tokens
            if token.kind is TokenKind.WORD and span.start <= token.offset < stop
        ),
        default=span.end,
    )
    return TextSpan(span.start, end)


def lint_analysis(
    report: RelevanceAnalysis,
    config: LintConfig,
    *,
    path: Path | None = None,
    base_line: int = 1,
    site: RelevanceSite | None = None,
) -> tuple[Finding, ...]:
    """Judge one already-computed analysis. The building block every other entry point uses.

    ``base_line`` is where the analysed text starts in its source file (1 for a
    bare statement, or a :class:`~bigfix_relevance_analyzer.extract.RelevanceSite`'s
    ``line`` when this analysis came from extraction); positions inside the
    text are 1-based and relative to it, so the absolute line is
    ``base_line + relative_line - 1``.
    """
    findings: list[Finding] = []

    def emit(
        code: str,
        message: str,
        line: int,
        suggestions: tuple[str, ...] = (),
        autofix: AutofixResult | None = None,
        spans: tuple[TextSpan, ...] = (),
    ) -> None:
        finding = _finding(
            config,
            code,
            message,
            path=path,
            line=base_line + line - 1,
            site=site,
            suggestions=suggestions,
            autofix=autofix,
            spans=spans,
        )
        if finding is not None:
            findings.append(finding)

    if report.parse_error is not None:
        error = report.parse_error
        emit(
            "parse-error",
            f"col {error.column}: {error.message}",
            error.line,
            spans=(_parse_error_span(report, error.offset),),
        )

    for token in report.error_tokens:
        emit(
            "error-token",
            f"unlexable text {token.text!r}",
            token.line,
            spans=(TextSpan(token.offset, token.offset + len(token.text)),),
        )

    for binding in report.unbound_its:
        span = binding.it.span
        emit(
            "unbound-it",
            "`it` used with no context to bind to",
            span.line,
            spans=(TextSpan(span.start, span.end),),
        )

    if report.check is not None:
        # Worked out once for the site, and only when something could use it.
        fixed = (
            report.autofix()
            if any(diagnostic.fix is not None for diagnostic in report.check.diagnostics)
            else None
        )
        site_fix = fixed if fixed is not None and fixed.changed else None
        for diagnostic in report.check.diagnostics:
            # `used-without-context` is the checker's own independent detection
            # of the same unbound `it` the loop above already reports -- see
            # the module docstring's `type-error` entry. Skipping it here
            # keeps one root cause from becoming two findings.
            if diagnostic.code == "used-without-context":
                continue
            applied = _fix_applied(diagnostic, site_fix)
            emit(
                _rule_for(diagnostic.code),
                _with_fix(diagnostic, applied),
                diagnostic.span.line,
                autofix=site_fix if applied else None,
                spans=(TextSpan(diagnostic.span.start, diagnostic.span.end),),
            )

    # Statement-level, like `unknown-inspector` below: the mismatch is between
    # the value as a whole and the slot, so it has no span of its own and lands
    # on the statement's first line.
    mismatch = _slot_mismatch(site, report)
    if mismatch is not None:
        emit("site-type-mismatch", mismatch, 1)

    plural = _plural_substitution(site, report)
    if plural is not None:
        emit("plural-substitution", plural, 1)

    non_renderable = _non_renderable_substitution(site, report)
    if non_renderable is not None:
        emit("non-renderable-substitution", non_renderable, 1)

    # Statement-level too, and before `unknown-inspector`: when a statement is
    # in neither dialect, that is the more useful thing to read first.
    if report.resolved_dialect is Dialect.UNCERTAIN:
        client_only = report.references_only_in(Dialect.CLIENT)
        session_only = report.references_only_in(Dialect.SESSION)
        emit(
            "mixed-dialect",
            f"{_names(client_only)} client relevance only, "
            f"{_names(session_only)} session relevance only",
            1,
        )

    # Matched on the parsed phrase, so only a whole name counts: `run` is a
    # keyword, the `run` in a longer inspector phrase is not.
    # One finding per word, on the line of its first use. The parser has
    # already lowercased the phrase, so `ElseIf` matches too.
    keyword_uses: dict[str, Reference] = {}
    for entry in report.references:
        word = entry.reference.phrase
        if word in ACTIONSCRIPT_KEYWORDS:
            keyword_uses.setdefault(word, entry.reference)
    for word, reference in keyword_uses.items():
        emit(
            "actionscript-keyword",
            f"ActionScript keyword `{word}` inside a relevance expression",
            reference.span.line,
            spans=(_name_span(report, reference),),
        )

    unknown = tuple(name for name in report.unknown_references if name not in keyword_uses)
    if unknown:
        # Imported here rather than at module scope: `inspectors` is only needed
        # on this one opt-in branch, and `lint` is otherwise reachable without
        # paying for the search index at all.
        name_leads: dict[str, tuple[str, ...]] = dict.fromkeys(unknown, ())
        if config.suggest:
            from bigfix_relevance_analyzer.inspectors import suggest as _suggest

            dialect = config.dialect or (report.dialect if not report.dialect_assumed else None)
            name_leads = {name: _suggest(name, dialect=dialect) for name in unknown}
        leads = tuple(dict.fromkeys(lead for name in unknown for lead in name_leads[name]))
        # Every use of every name, in source order: one finding still (the
        # hook counts findings), but an editor underlines each use, and each
        # span carries the message for its own name and its own leads, so a
        # consumer never has to take the finding's message apart.
        uses: list[TextSpan] = []
        for entry in report.references:
            phrase = entry.reference.phrase
            if phrase in name_leads:
                written = _name_span(report, entry.reference)
                message = _unknown_message((phrase,), name_leads[phrase])
                uses.append(TextSpan(written.start, written.end, message))
        # The finding itself is statement-level for its line: relative line 1,
        # which `emit` offsets by `base_line`. Passing `base_line` itself here
        # double-counted the offset for extracted sites (line 15 of an 11-line
        # file).
        emit("unknown-inspector", _unknown_message(unknown, leads), 1, leads, spans=tuple(uses))

    if config.max_score is not None and report.complexity.score > config.max_score:
        detail = _complexity_detail(report)
        suffix = f" ({detail})" if detail else ""
        emit(
            "complexity",
            f"score {report.complexity.score:.3g} > {config.max_score:.3g}{suffix}",
            1,
        )

    if (
        config.max_evaluation_cost is not None
        and report.complexity.evaluation_cost > config.max_evaluation_cost
    ):
        inspectors = ", ".join(report.complexity.costly_inspectors)
        suffix = f" ({inspectors})" if inspectors else ""
        emit(
            "evaluation-cost",
            f"cost {report.complexity.evaluation_cost:.3g} > "
            f"{config.max_evaluation_cost:.3g}{suffix}",
            1,
        )

    return tuple(findings)


def _file_error(path: Path, detail: str, config: LintConfig) -> tuple[Finding, ...]:
    """One ``file-error`` finding about ``path`` itself, honouring its severity."""
    finding = _finding(config, "file-error", f"cannot lint: {detail}", path=path, line=1)
    return () if finding is None else (finding,)


_ANALYSIS_CACHE_SIZE: Final = 2048
"""How many distinct statements one process keeps analyses for.

Relevance is boilerplate-heavy. Across a real content repository 88% of
extracted statements are byte-identical to another one -- `/* Windows Only */
windows of operating system` alone appears over six thousand times -- and a
lint run walks every file in one process. Measured over 400 real `.bes` files:
3.07s without this, 0.26s with it, at a 94.8% hit rate.

2048 covers the distinct statements in that corpus with room to spare, at
roughly 7 KiB per entry -- about 14 MB if it ever fills. Bounded rather than
unbounded because `lint_paths` is also reachable from a long-running process.
"""

_analyze_cached = functools.lru_cache(maxsize=_ANALYSIS_CACHE_SIZE)(analyze)
"""`analyze`, memoized on its arguments, for the duration of the process.

Safe because a :class:`~bigfix_relevance_analyzer.analyzer.RelevanceAnalysis`
describes the *statement* and nothing else: it is frozen, it has no ``__dict__``
to accumulate caller state in, its derived properties recompute rather than
memoize, and everything positional a finding needs -- ``path``, ``base_line``,
``site`` -- reaches :func:`lint_analysis` as its own arguments rather than
through the report. ``test_two_identical_statements_still_report_their_own_positions``
is what holds that line.

Deliberately the *wrapped function* rather than a hand-written key. `analyze`
takes a keyword-only ``probe_kind`` as well as text, dialect and platform; a
key listing only the first three would quietly serve one probe kind's answer
for another, and would need remembering again for every parameter added later.
Wrapping keys on the arguments actually passed, so it cannot drift.
"""


def lint_file(path: str | bytes | os.PathLike[str], config: LintConfig) -> tuple[Finding, ...]:
    """Extract and judge every relevance site in one file.

    The path is taken as named on purpose, so anything that stops it being
    linted is reported rather than skipped, under ``file-error``: a missing
    path, an unreadable one, and a file type
    :func:`~bigfix_relevance_analyzer.extract.extract_relevance_from_file` does
    not recognize. Each of those yields no sites, and none may look like a
    clean file. The one path that stays silent is an existing directory: only
    :func:`lint_directory` descends, so a directory argument is a no-op here by
    design rather than a failure to read something.
    """
    return _lint_file(_as_path(path), config, explicit=True)


def _lint_file(file_path: Path, config: LintConfig, *, explicit: bool) -> tuple[Finding, ...]:
    """:func:`lint_file`, or the directory walk's quieter version of it."""
    blocked = _unlintable(file_path, config, explicit=explicit)
    if blocked is not None:
        return blocked
    try:
        sites, problems = _extract_file(file_path)
    except OSError as error:
        return _file_error(file_path, error.strerror or str(error), config)
    return _lint_extracted(file_path, sites, problems, config)


def _unlintable(
    file_path: Path, config: LintConfig, *, explicit: bool
) -> tuple[Finding, ...] | None:
    """What to report instead of linting ``file_path``, or ``None`` to go ahead.

    Asked before extraction, from the name and the filesystem entry alone: an
    unrecognized suffix never reaches the filesystem in the extractor, so a
    missing `notes.txt` would otherwise raise nothing to notice.

    Not ``is_file()``: that is true only of a *regular* file, so a piped
    `/dev/stdin` -- a FIFO that reads fine -- came out as `no such file`.

    An unrecognized type is reported only for a path named ``explicitly``. The
    directory walk meets every `.py` and `.json` in a repository, and skipping
    those is its job; a named path is a statement that it should be linted, so
    `0 errors in 1 file` over a file nothing read would be a false pass (#16).
    """
    if file_path.is_dir():
        return ()
    if not file_path.exists():
        return _file_error(file_path, "no such file", config)
    if not _is_recognized(file_path):
        if not explicit:
            return ()
        expected = ", ".join(_RECOGNIZED_SUFFIXES)
        return _file_error(
            file_path, f"unrecognised file type; nothing was linted (expected {expected})", config
        )
    return None


SiteJudge = Callable[[Path | None, RelevanceSite, LintConfig], tuple[Finding, ...]]
"""How one extracted site becomes findings: :func:`_judge_site`, or a caller's
wrapper around it (the language server caches per site)."""


def _judge_site(
    file_path: Path | None, site: RelevanceSite, config: LintConfig
) -> tuple[Finding, ...]:
    """Every finding for one extracted site of ``file_path``."""
    report = _analyze_site(site, config)
    return lint_analysis(report, config, path=file_path, base_line=site.line, site=site)


def _lint_sites(
    file_path: Path,
    sites: Iterable[RelevanceSite],
    config: LintConfig,
    judge: SiteJudge = _judge_site,
) -> tuple[Finding, ...]:
    """Judge sites already extracted from ``file_path``: :func:`lint_file`'s second half."""
    findings: list[Finding] = []
    for site in sites:
        findings.extend(judge(file_path, site, config))
    return tuple(findings)


def _problem_findings(
    file_path: Path, problems: Iterable[_ExtractionProblem], config: LintConfig
) -> tuple[Finding, ...]:
    """One finding per problem the extractor met in ``file_path``. None has a
    site: the problem is that no statement could be extracted there."""
    findings = (
        _finding(config, problem.code, problem.message, path=file_path, line=problem.line)
        for problem in problems
    )
    return tuple(finding for finding in findings if finding is not None)


def _lint_extracted(
    file_path: Path,
    sites: Iterable[RelevanceSite],
    problems: Iterable[_ExtractionProblem],
    config: LintConfig,
    judge: SiteJudge = _judge_site,
) -> tuple[Finding, ...]:
    """Every finding for one extracted file, sites and problems together.

    Problem findings are merged in by line rather than the whole list sorted:
    a site's findings keep the order they always had, even where a multi-line
    statement reports a line past the next site's.
    """
    return tuple(
        heapq.merge(
            _problem_findings(file_path, problems, config),
            _lint_sites(file_path, sites, config, judge),
            key=lambda finding: finding.line,
        )
    )


def _lint_data(
    file_path: Path, data: bytes, config: LintConfig, judge: SiteJudge = _judge_site
) -> tuple[Finding, ...]:
    """:func:`lint_file` over ``data`` instead of the file's contents on disk.

    ``file_path`` only names the content -- its suffix picks the extractor,
    and findings carry it -- and is never opened, so it need not exist. An
    unrecognized suffix yields no findings rather than a ``file-error``: the
    caller chose to hand this content over, it did not name a path to lint.
    """
    if not _is_recognized(file_path):
        return ()
    sites, problems = _extract_data(file_path, data)
    return _lint_extracted(file_path, sites, problems, config, judge)


def lint_text(text: str, config: LintConfig) -> tuple[Finding, ...]:
    """Judge one bare relevance statement, given as text rather than in a file.

    Analysed in ``config.dialect`` when one is forced (classified otherwise)
    and ``config.platform``, through the same cache a file's sites use.
    Findings carry no path. What is analysed is ``text.strip()``, and both
    positions are relative to that: lines count from its first line, and
    :attr:`Finding.spans` are offsets into it -- so for an indented or
    blank-led ``text``, index ``text.strip()``, not ``text``.
    """
    return lint_analysis(_analyze_text(text, config), config)


def _analyze_text(text: str, config: LintConfig) -> RelevanceAnalysis:
    """The analysis :func:`lint_text` judges, for a caller that renders it too."""
    return _analyze_cached(text.strip(), config.dialect, config.platform)


def _analyze_site(site: RelevanceSite, config: LintConfig) -> RelevanceAnalysis:
    """Analyse one extracted site the way linting it does: in the site's own
    dialect unless one is forced, through the shared analysis cache."""
    return _analyze_cached(site.text, _site_dialect(site, config.dialect), config.platform)


def lint_paths(
    paths: Iterable[str | bytes | os.PathLike[str]], config: LintConfig
) -> tuple[Finding, ...]:
    """:func:`lint_file` over many paths, in order, reporting ones that error out.

    A path that could not be read does not stop the run: it becomes a
    ``file-error`` finding and the remaining paths are linted as usual.

    Each path is taken literally -- a directory here is not descended into; use
    :func:`lint_directory` for that.
    """
    findings: list[Finding] = []
    for path in paths:
        findings.extend(lint_file(path, config))
    return tuple(findings)


def lint_paths_to_dict(
    paths: Iterable[str | bytes | os.PathLike[str]], config: LintConfig
) -> dict[str, Any]:
    """:func:`lint_paths` as JSON-serializable plain data, with the verdict.

    The envelope, not just the list: ``counts`` and ``ok`` are the pass/fail
    arithmetic every consumer would otherwise redo, and ``ok`` is the same
    verdict both CLIs in this package exit on. A caller wanting a stricter
    policy still has the numbers -- ``ok`` answers "did anything error", which
    is the default gate, and ``counts["warning"]`` is there for a repo that
    treats warnings as failures too.

    Findings keep :func:`lint_paths`'s order -- per path, then per site within
    it -- because that is the order a human reads a file in, and sorting by
    severity instead would scatter one file's findings across the report.
    """
    return _findings_dict(lint_paths(paths, config))


def _walk_files(root: Path, max_depth: int) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    """Discover files under ``root`` up to ``max_depth`` levels deep.

    Returns ``(files, exceeded)``: every file found (default-excluded directories
    pruned), and every directory that was *not* descended into because doing so
    would have gone past ``max_depth``. Sorted within each directory for a
    deterministic order across runs and platforms. Does no linting itself --
    that stays in :func:`lint_directory`, which turns ``exceeded`` into findings.
    """
    if root.is_file():
        return (root,), ()
    if not root.is_dir():
        return (), ()

    files: list[Path] = []
    exceeded: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel = current.relative_to(root)
        depth = 0 if rel == Path() else len(rel.parts)

        dirnames[:] = sorted(
            name for name in dirnames if name not in _SKIP_DIR_NAMES and not name.startswith(".")
        )

        if depth >= max_depth and dirnames:
            exceeded.extend(current / name for name in dirnames)
            dirnames[:] = []  # stop os.walk from descending into them

        files.extend(current / name for name in sorted(filenames))

    return tuple(files), tuple(exceeded)


def lint_directory(
    root: str | bytes | os.PathLike[str],
    config: LintConfig,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> tuple[Finding, ...]:
    """Walk ``root`` and :func:`lint_file` everything found under it.

    The only entry point that recurses into a directory -- :func:`lint_paths`
    and :func:`lint_file` take a path exactly as given. Both CLIs reach for this
    solely when given zero path arguments, so passing a directory explicitly
    keeps behaving like any other literal path; this is the "walk `.`" behind a
    bare invocation, not a general directory-expansion feature.

    A branch deeper than ``max_depth`` is not silently dropped: each directory
    where descent stopped is reported as its own ``max-depth-exceeded`` finding,
    same as any other rule in this module, and everything below it is skipped.
    """
    root_path = _as_path(root)
    files, exceeded = _walk_files(root_path, max_depth)
    findings = list(_depth_findings(root_path, exceeded, max_depth, config))
    for file_path in files:
        findings.extend(_lint_file(file_path, config, explicit=False))
    return tuple(findings)


def _depth_findings(
    root: Path, exceeded: Iterable[Path], max_depth: int, config: LintConfig
) -> tuple[Finding, ...]:
    """One ``max-depth-exceeded`` finding per directory :func:`_walk_files` stopped at."""
    findings = (
        _finding(
            config,
            "max-depth-exceeded",
            f"more than {max_depth} directory levels below {root}; not descending into {directory}",
            path=directory,
            line=1,
        )
        for directory in exceeded
    )
    return tuple(finding for finding in findings if finding is not None)
