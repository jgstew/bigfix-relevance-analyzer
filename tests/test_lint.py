"""Tests for the lint rule layer that a pre-commit hook consumes.

These pin the judgement layer (:mod:`bigfix_relevance_analyzer.lint`), not any
particular CLI wrapper: a rule is right when it fires on the statement it is
meant to catch and stays silent on everything else, independent of how a
caller renders or exits on the result.
"""

from __future__ import annotations

from pathlib import Path

from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    Severity,
    lint_analysis,
    lint_file,
    lint_paths,
)

CLIENT = 'exists file "C:\\foo.txt" whose (size of it > 100)'
BROKEN = 'exists file "unterminated'
UNBOUND_IT = "size of it"  # `it` with nothing to bind to
UNKNOWN_INSPECTOR = "totally bogus made up inspector"
BES_EXAMPLE = Path("tests/examples/mixed_context/task_with_client_and_session_relevance.bes")


def codes(findings: tuple[Finding, ...]) -> set[str]:
    return {f.code for f in findings}


# ---------------------------------------------------------------------------
# Individual rules, in isolation
# ---------------------------------------------------------------------------


def test_clean_statement_has_no_findings() -> None:
    report = analyze(CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert findings == ()


def test_parse_error_is_reported_as_error() -> None:
    # An unterminated string is both an unlexable ERROR token and a parse
    # failure -- the same root cause surfaced by two independent rules.
    report = analyze(BROKEN)
    findings = lint_analysis(report, LintConfig())
    assert codes(findings) == {"parse-error", "error-token"}
    assert all(f.severity is Severity.ERROR for f in findings)


def test_unbound_it_is_reported_as_error() -> None:
    report = analyze(UNBOUND_IT, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert "unbound-it" in codes(findings)
    unbound = next(f for f in findings if f.code == "unbound-it")
    assert unbound.severity is Severity.ERROR


def test_unknown_inspector_is_reported_as_warning() -> None:
    report = analyze(UNKNOWN_INSPECTOR, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert "unknown-inspector" in codes(findings)
    unknown = next(f for f in findings if f.code == "unknown-inspector")
    assert unknown.severity is Severity.WARNING


def test_complexity_is_silent_without_a_configured_threshold() -> None:
    # A nested, filtered statement that scores meaningfully above zero.
    report = analyze(
        'exists files whose (name of it starts with "bes" AND size of it > 0) '
        'of folders whose (name of it as lowercase as string != "") of folder "/tmp"'
    )
    assert report.complexity.score > 0
    findings = lint_analysis(report, LintConfig())
    assert "complexity" not in codes(findings)


def test_complexity_fires_when_score_exceeds_configured_max() -> None:
    report = analyze(CLIENT)
    threshold = report.complexity.score - 1
    findings = lint_analysis(report, LintConfig(max_score=threshold))
    assert "complexity" in codes(findings)
    finding = next(f for f in findings if f.code == "complexity")
    assert finding.severity is Severity.ERROR
    assert "score" in finding.message


def test_complexity_is_silent_when_score_is_under_configured_max() -> None:
    report = analyze(CLIENT)
    findings = lint_analysis(report, LintConfig(max_score=report.complexity.score + 1))
    assert "complexity" not in codes(findings)


def test_evaluation_cost_is_silent_without_a_configured_threshold() -> None:
    report = analyze('exists descendants of folder "C:\\"', Dialect.CLIENT)
    assert report.complexity.evaluation_cost > 0
    findings = lint_analysis(report, LintConfig())
    assert "evaluation-cost" not in codes(findings)


def test_evaluation_cost_fires_when_over_configured_max() -> None:
    report = analyze('exists descendants of folder "C:\\"', Dialect.CLIENT)
    threshold = report.complexity.evaluation_cost - 1
    findings = lint_analysis(report, LintConfig(max_evaluation_cost=threshold))
    assert "evaluation-cost" in codes(findings)
    finding = next(f for f in findings if f.code == "evaluation-cost")
    assert finding.severity is Severity.ERROR


def test_severity_override_can_promote_a_warning_to_an_error() -> None:
    report = analyze(UNKNOWN_INSPECTOR, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig(severities={"unknown-inspector": Severity.ERROR}))
    finding = next(f for f in findings if f.code == "unknown-inspector")
    assert finding.severity is Severity.ERROR


def test_severity_override_can_silence_a_rule() -> None:
    report = analyze(UNBOUND_IT, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig(severities={"unbound-it": Severity.IGNORE}))
    assert "unbound-it" not in codes(findings)


# ---------------------------------------------------------------------------
# File and multi-path wiring
# ---------------------------------------------------------------------------


def test_lint_file_finds_no_relevance_in_an_unrecognized_suffix(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text(CLIENT)
    assert lint_file(path, LintConfig()) == ()


def test_lint_file_reports_absolute_line_numbers(tmp_path: Path) -> None:
    path = tmp_path / "broken.rel"
    # .rel is whole-file plain text relevance (Dialect.UNCERTAIN per extractor).
    path.write_text("\n\n" + BROKEN)
    findings = lint_file(path, LintConfig())
    assert findings
    finding = next(f for f in findings if f.code == "parse-error")
    # The statement starts on line 3; its own parse error is on its line 1.
    assert finding.line == 3
    assert finding.path == path


def test_lint_file_on_real_bes_example_is_clean() -> None:
    findings = lint_file(BES_EXAMPLE, LintConfig())
    assert codes(findings) <= {"unknown-inspector"}  # dumps may not cover everything


def test_lint_paths_aggregates_across_files(tmp_path: Path) -> None:
    clean = tmp_path / "clean.rel"
    clean.write_text(CLIENT)
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)
    findings = lint_paths([clean, broken], LintConfig())
    assert codes(findings) == {"parse-error", "error-token"}
    assert all(f.path == broken for f in findings)


def test_lint_paths_skips_missing_or_unreadable_paths_gracefully(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.rel"
    findings = lint_paths([missing], LintConfig())
    assert findings == ()
