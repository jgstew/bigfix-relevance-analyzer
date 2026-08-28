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

Six rules, three of them always on and three opt-in:

- ``parse-error`` / ``error-token`` -- the statement is broken. Always an
  error; nothing to configure.
- ``unbound-it`` -- an ``it`` with no context to bind to. Always an error:
  it means the reference is meaningless in the engine, not merely unusual.
- ``unknown-inspector`` -- a name no dump defines. Always a warning, never an
  error by default, because the dumps do not cover every platform or product
  version -- a name absent from them is a lead, not proof of a typo.
- ``complexity`` / ``evaluation-cost`` -- :attr:`RelevanceComplexity.score`
  and ``.evaluation_cost`` past a caller-supplied ceiling. Silent unless
  :attr:`LintConfig.max_score` / ``.max_evaluation_cost`` is set, because a
  baked-in number would fail every existing repo on day one; the ceiling is
  the adopting repo's ratchet to set, not this package's to assume.

Deliberately not a rule here: :attr:`RelevanceAnalysis.missing_platforms`
(absence from the dumps is not proof of lack of support) and any
:attr:`~bigfix_relevance_analyzer.typecheck.CheckResult.diagnostics` beyond
unbound ``it`` (too noisy for a default until the type layer has more
mileage). A caller that wants either can still read them off the analysis
directly -- this module has no monopoly on the facts, only an opinion about
which of them should fail a commit by default.
"""

from __future__ import annotations

import enum
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from bigfix_relevance_analyzer.analyzer import RelevanceAnalysis, analyze
from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.extract import RelevanceSite, extract_relevance_from_file

__all__ = [
    "Finding",
    "LintConfig",
    "Severity",
    "lint_analysis",
    "lint_file",
    "lint_paths",
]


class Severity(enum.Enum):
    """How a finding should count against a commit."""

    ERROR = "error"
    WARNING = "warning"
    IGNORE = "ignore"
    """Configured off. A finding at this severity is dropped, not emitted."""


#: Severity a rule reports at when :attr:`LintConfig.severities` says nothing
#: about it. Keyed by :attr:`Finding.code`.
DEFAULT_SEVERITIES: Mapping[str, Severity] = {
    "parse-error": Severity.ERROR,
    "error-token": Severity.ERROR,
    "unbound-it": Severity.ERROR,
    "unknown-inspector": Severity.WARNING,
    "complexity": Severity.ERROR,
    "evaluation-cost": Severity.ERROR,
}


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

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}" if self.path is not None else f"line {self.line}"
        return f"{where}: {self.severity.value} [{self.code}] {self.message}"


@dataclass(frozen=True, slots=True)
class LintConfig:
    """What to gate on. Every threshold defaults to off -- see the module docstring."""

    max_score: float | None = None
    max_evaluation_cost: float | None = None
    severities: Mapping[str, Severity] = field(default_factory=dict)
    """Per-code overrides of :data:`DEFAULT_SEVERITIES`. Unlisted codes keep their default."""

    dialect: Dialect | None = None
    """Force the dialect instead of trusting extraction or classifying the text."""

    platform: str | None = None

    def severity_for(self, code: str) -> Severity:
        return self.severities.get(code, DEFAULT_SEVERITIES.get(code, Severity.WARNING))


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

    def emit(code: str, message: str, line: int) -> None:
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
            )
        )

    if report.parse_error is not None:
        error = report.parse_error
        emit("parse-error", f"col {error.column}: {error.message}", error.line)

    for token in report.error_tokens:
        emit("error-token", f"unlexable text {token.text!r}", token.line)

    for binding in report.unbound_its:
        emit("unbound-it", "`it` used with no context to bind to", binding.it.span.line)

    if report.unknown_references:
        names = ", ".join(f"`{name}`" for name in report.unknown_references)
        emit("unknown-inspector", f"no dump defines {names}", base_line)

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
    """:func:`lint_file` over many paths, in order, skipping ones that error out."""
    findings: list[Finding] = []
    for path in paths:
        findings.extend(lint_file(path, config))
    return tuple(findings)
