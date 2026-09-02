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

Eleven rules, nine of them always on and two tunable:

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
  does not exist or could not be read. Always an error: it yields no sites, so
  left unreported it is indistinguishable from a clean file, and a typo'd path
  in a hook would pass CI having linted nothing. An existing directory is
  exempt -- a path is taken literally and only :func:`lint_directory` recurses.
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
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from bigfix_relevance_analyzer._serialize import _path
from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.extract import RelevanceSite, extract_relevance_from_file
from bigfix_relevance_analyzer.typecheck import Plurality

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
                "site-type-mismatch",
                Severity.ERROR,
                "the value does not fit the kind of site it was extracted from",
                "Only extraction knows this: the same expression is correct in one slot "
                "and broken in another, so this is the one rule that reads the "
                "`RelevanceSite` rather than the statement alone -- and it is silent for "
                "a caller that lints bare text, which has no slot. Two slots constrain "
                "their value and are checked. A `<Relevance>` element decides "
                "applicability, so a clause that is not a boolean makes the content "
                "unable to apply anywhere. An ActionScript `{...}` substitution has one "
                "hole to fill, so a plural value has no single answer to put in it; a "
                "boolean is fine there and coerces to a string, which shipped content "
                "relies on heavily. An error, not a warning, because neither is a risk "
                "the author may have ruled out -- the content cannot work. Positive "
                "evidence only, as everywhere else: an undetermined type or plurality is "
                "not a finding, and neither is a value some other rule already faulted. "
                "Analysis properties are deliberately unlisted, being legitimately "
                "plural and of any renderable type.",
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
                "a `whose` filter written on a singular spelling, where the plural reads safer",
                "The sibling of `non-unique-risk`, reported where that hazard cannot "
                'fire. `pathname of file "x.bes" whose (...) of folder "c:\\\\"` cannot '
                "match twice -- a folder holds one file of a given name -- but it "
                "writes a filter on a singular spelling mid-chain, which is the habit "
                "that makes the same shape raise wherever the name is dropped, and it "
                "still raises `Singular expression refers to nonexistent object.` when "
                "the filter matches nothing, where the plural spelling answers 0. "
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
                "a path given to the linter does not exist or could not be read",
                "A path that is not there yields no sites, which reads exactly like a clean "
                "file unless it is reported -- so a misspelled path in a pre-commit hook would "
                "otherwise pass CI having linted nothing. Always an error: the caller named "
                "this file, so failing to read it is a fault in the run rather than an opinion "
                "about content. An existing *directory* is not a file error; it is skipped, "
                "because a path here is taken literally and only :func:`lint_directory` "
                "recurses.",
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
            "text": str(self),
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


def _complexity_detail(report: RelevanceAnalysis, limit: int = 3) -> str:
    metrics = report.complexity
    parts = []
    for name, _weighted in metrics.contributions[:limit]:
        raw = getattr(metrics, name, None)
        parts.append(f"{name}={raw}" if raw is not None else name)
    return ", ".join(parts)


def _site_dialect(site: RelevanceSite, forced: Dialect | None) -> Dialect | None:
    # A site the extractor already classified is a stronger signal than
    # re-classifying the bare fragment -- mirrors __main__._analyze_site.
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


# What each kind of site requires of the value it holds. Only the two slots the
# engine genuinely constrains are listed: an applicability clause decides yes or
# no, and an ActionScript substitution has one hole to fill. An analysis
# property may legitimately be plural and may be any renderable type, a
# `.rel` file or a markdown block is not a slot at all, and the remaining
# contexts have not been confirmed -- an unlisted kind is judged on nothing.
_SLOT_REQUIREMENTS: Final = {
    "relevance": ("singular", "boolean"),
    "actionscript-substitution": ("singular", None),
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
    """
    if site is None or report.check is None:
        return None
    requirement = _SLOT_REQUIREMENTS.get(site.kind)
    if requirement is None:
        return None
    plurality, required_type = requirement
    value = report.check.value
    if value.types is not None and not value.types:
        return None

    if plurality == "singular" and value.plurality is Plurality.PLURAL:
        return (
            f"{site.context} takes one value; this is plural -- "
            "an aggregate such as `unique value of` collapses it"
        )
    if required_type is not None and value.types is not None and required_type not in value.types:
        rendered = " or ".join(f"`{name}`" for name in sorted(value.types))
        return f"{site.context} must be a `{required_type}`; this is {rendered}"
    return None


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

    def emit(code: str, message: str, line: int, suggestions: tuple[str, ...] = ()) -> None:
        severity = config.severity_for(code)
        if severity is Severity.IGNORE:
            return
        findings.append(
            Finding(
                code=code,
                severity=severity,
                message=message,
                path=path,
                line=base_line + line - 1,
                site=site,
                suggestions=suggestions,
            )
        )

    if report.parse_error is not None:
        error = report.parse_error
        emit("parse-error", f"col {error.column}: {error.message}", error.line)

    for token in report.error_tokens:
        emit("error-token", f"unlexable text {token.text!r}", token.line)

    for binding in report.unbound_its:
        emit("unbound-it", "`it` used with no context to bind to", binding.it.span.line)

    if report.check is not None:
        for diagnostic in report.check.diagnostics:
            # `used-without-context` is the checker's own independent detection
            # of the same unbound `it` the loop above already reports -- see
            # the module docstring's `type-error` entry. Skipping it here
            # keeps one root cause from becoming two findings.
            if diagnostic.code == "used-without-context":
                continue
            emit(
                _CHECK_RULES.get(diagnostic.code, "type-error"),
                diagnostic.message,
                diagnostic.span.line,
            )

    # Statement-level, like `unknown-inspector` below: the mismatch is between
    # the value as a whole and the slot, so it has no span of its own and lands
    # on the statement's first line.
    mismatch = _slot_mismatch(site, report)
    if mismatch is not None:
        emit("site-type-mismatch", mismatch, 1)

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

    if report.unknown_references:
        names = ", ".join(f"`{name}`" for name in report.unknown_references)
        message = f"no dump defines {names}"
        # Imported here rather than at module scope: `inspectors` is only needed
        # on this one opt-in branch, and `lint` is otherwise reachable without
        # paying for the search index at all.
        leads: tuple[str, ...] = ()
        if config.suggest:
            from bigfix_relevance_analyzer.inspectors import suggest as _suggest

            dialect = config.dialect or (report.dialect if not report.dialect_assumed else None)
            leads = tuple(
                dict.fromkeys(
                    lead
                    for name in report.unknown_references
                    for lead in _suggest(name, dialect=dialect)
                )
            )
            if leads:
                quoted = [f"`{lead}`" for lead in leads]
                # "a, b or c" rather than "a or b or c" -- three `or`s in one
                # clause reads as a parser bug rather than a list.
                offered = (
                    quoted[0] if len(quoted) == 1 else f"{', '.join(quoted[:-1])} or {quoted[-1]}"
                )
                message = f"{message} -- did you mean {offered}?"
        # Statement-level findings carry no span, so they land on the
        # statement's first line -- relative line 1, which `emit` offsets by
        # `base_line`. Passing `base_line` itself here double-counted the
        # offset for extracted sites (line 15 of an 11-line file).
        emit("unknown-inspector", message, 1, leads)

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
    severity = config.severity_for("file-error")
    if severity is Severity.IGNORE:
        return ()
    return (
        Finding(
            code="file-error",
            severity=severity,
            message=f"cannot lint: {detail}",
            path=path,
            line=1,
        ),
    )


def lint_file(path: str | bytes | os.PathLike[str], config: LintConfig) -> tuple[Finding, ...]:
    """Extract and judge every relevance site in one file.

    A file type :func:`~bigfix_relevance_analyzer.extract.extract_relevance_from_file`
    does not recognize yields no sites and, therefore, no findings -- the same
    "unknown, skip" policy the extractor itself uses.

    A path that is not a readable file is reported rather than skipped, under
    ``file-error`` -- a missing file yields no sites either, and the two must
    not look alike. The one path that stays silent is an existing directory:
    only :func:`lint_directory` descends, so a directory argument is a no-op
    here by design rather than a failure to read something.
    """
    file_path = Path(os.fsdecode(path))
    # Asked before extraction, not instead of it: a suffix the extractor does
    # not recognize never touches the filesystem, so a missing `notes.txt`
    # would otherwise raise nothing to notice.
    if not file_path.is_file():
        if file_path.is_dir():
            return ()
        return _file_error(file_path, "no such file", config)

    try:
        sites = extract_relevance_from_file(file_path)
    except OSError as error:
        return _file_error(file_path, error.strerror or str(error), config)

    findings: list[Finding] = []
    for site in sites:
        dialect = _site_dialect(site, config.dialect)
        report = analyze(site.text, dialect, config.platform)
        findings.extend(
            lint_analysis(report, config, path=file_path, base_line=site.line, site=site)
        )
    return tuple(findings)


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
    findings = lint_paths(paths, config)
    tallies = counts(findings)
    return {
        "findings": [finding.to_dict() for finding in findings],
        "counts": dict(tallies),
        "ok": tallies[Severity.ERROR.value] == 0,
    }


def _walk(root: Path, max_depth: int) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
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
    root_path = Path(os.fsdecode(root))
    files, exceeded = _walk(root_path, max_depth)

    findings: list[Finding] = []
    for directory in exceeded:
        severity = config.severity_for("max-depth-exceeded")
        if severity is not Severity.IGNORE:
            findings.append(
                Finding(
                    code="max-depth-exceeded",
                    severity=severity,
                    message=(
                        f"more than {max_depth} directory levels below {root_path}; "
                        f"not descending into {directory}"
                    ),
                    path=directory,
                    line=1,
                )
            )
    for file_path in files:
        findings.extend(lint_file(file_path, config))
    return tuple(findings)
