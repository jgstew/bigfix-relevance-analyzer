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

Nine rules, seven of them always on and two tunable:

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
- ``unknown-inspector`` -- a name no dump defines. Always a warning, never an
  error by default, because the dumps do not cover every platform or product
  version -- a name absent from them is a lead, not proof of a typo.
- ``non-unique-risk`` -- a property written singular where more than one value
  may come back, either over an object that may be plural
  (``singular-over-plural-object``) or because the tables record the property
  itself as multivalued (``singular-of-multivalued-property``). A warning, not
  an error: the expression types cleanly, and the author may know exactly one
  value exists. See the rule's rationale in :data:`RULES` for the exemptions.
- ``complexity`` / ``evaluation-cost`` -- :attr:`RelevanceComplexity.score`
  and ``.evaluation_cost`` past a ceiling. On by default, at a generous
  built-in ceiling (:data:`DEFAULT_MAX_SCORE`, :data:`DEFAULT_MAX_EVALUATION_COST`)
  chosen to sit well above ordinary content and catch only the genuinely
  extreme -- content that legitimately needs to be this complex should raise
  :attr:`LintConfig.max_score` / ``.max_evaluation_cost`` rather than stay
  silent about it. Pass ``None`` for either (via the library API; there is no
  CLI spelling for it) to disable the rule entirely.
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
#: own seven-rule list, moved here so there is one copy rather than a prose one
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
                "unknown-inspector",
                Severity.WARNING,
                "a name no inspector dump defines",
                "The most actionable single signal for a typo, but not proof of one: the "
                "dumps do not cover every platform or product version, so a name absent "
                "from them is a lead rather than a fault. Always a warning, never an error "
                "by default.",
            ),
            _rule(
                "non-unique-risk",
                Severity.WARNING,
                "a property written singular where more than one value may come back",
                "Two sibling diagnostics land here. `value of results ...` writes the "
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
                "may still know exactly one value exists.",
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
}


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
        emit("unknown-inspector", message, base_line, leads)

    if config.max_score is not None and report.complexity.score > config.max_score:
        detail = _complexity_detail(report)
        suffix = f" ({detail})" if detail else ""
        emit(
            "complexity",
            f"score {report.complexity.score:.3g} > {config.max_score:.3g}{suffix}",
            base_line,
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
            base_line,
        )

    return tuple(findings)


def lint_file(path: str | bytes | os.PathLike[str], config: LintConfig) -> tuple[Finding, ...]:
    """Extract and judge every relevance site in one file.

    A file type :func:`~bigfix_relevance_analyzer.extract.extract_relevance_from_file`
    does not recognize yields no sites and, therefore, no findings -- the same
    "unknown, skip" policy the extractor itself uses.
    """
    file_path = Path(os.fsdecode(path))
    try:
        sites = extract_relevance_from_file(file_path)
    except OSError:
        return ()

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
    """:func:`lint_file` over many paths, in order, skipping ones that error out.

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
