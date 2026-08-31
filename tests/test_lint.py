"""Tests for the lint rule layer that a pre-commit hook consumes.

These pin the judgement layer (:mod:`bigfix_relevance_analyzer.lint`), not any
particular CLI wrapper: a rule is right when it fires on the statement it is
meant to catch and stays silent on everything else, independent of how a
caller renders or exits on the result.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
from pathlib import Path

import pytest

from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_EVALUATION_COST,
    DEFAULT_MAX_SCORE,
    DEFAULT_SEVERITIES,
    RULES,
    Finding,
    LintConfig,
    Severity,
    lint_analysis,
    lint_directory,
    lint_file,
    lint_paths,
    rules,
)

CLIENT = 'exists file "C:\\foo.txt" whose (size of it > 100)'
BROKEN = 'exists file "unterminated'
UNBOUND_IT = "size of it"  # `it` with nothing to bind to
UNKNOWN_INSPECTOR = "totally bogus made up inspector"
BES_EXAMPLE = Path("tests/examples/mixed_context/task_with_client_and_session_relevance.bes")
# A real type mismatch, not merely an unbound `it` (which the type checker
# also reports, under `used-without-context` -- deliberately excluded from
# `type-error`, see the `lint` module docstring).
TYPE_MISMATCH = '1 + "a"'
# Non-zero evaluation cost, so the `evaluation-cost` ceiling has something to
# exceed: hashing a file is the `COST_EXTREME` tier on the client.
COSTLY = 'sha1 of file "/tmp/x" = "abc"'
# A property written singular over a plural object: legal, and a runtime risk
# rather than a type error. The corpus writes exactly this, with `| 0`.
NON_UNIQUE_RISK = "free space of drives of system folders"
# A `whose` on a singular spelling that cannot collapse -- the index makes it
# unique -- so only the style rule has anything to say about it.
PLURAL_PREFERRED = 'pathname of file "x.bes" whose (size of it > 1) of folder "c:\\"'
# Two version-comparison defects, both read off a live engine. The engine
# answers each cleanly and the answer is wrong, which is why they are warnings
# on well-typed relevance rather than type errors.
VERSION_TRUNCATING = 'version of operating system > version "14"'
VERSION_LIKE_STRING = '"2.10.1" > "2.3.3"'


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


def test_type_mismatch_is_reported_as_error() -> None:
    report = analyze(TYPE_MISMATCH, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert "type-error" in codes(findings)
    finding = next(f for f in findings if f.code == "type-error")
    assert finding.severity is Severity.ERROR
    assert "not defined" in finding.message


def test_unbound_it_does_not_also_report_as_a_type_error() -> None:
    # The type checker independently detects the same unbound `it` under its
    # own `used-without-context` diagnostic -- it must not double up with the
    # `unbound-it` rule above as a second `type-error` finding.
    report = analyze(UNBOUND_IT, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert codes(findings) == {"unbound-it"}


def test_unknown_inspector_is_reported_as_warning() -> None:
    report = analyze(UNKNOWN_INSPECTOR, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert "unknown-inspector" in codes(findings)
    unknown = next(f for f in findings if f.code == "unknown-inspector")
    assert unknown.severity is Severity.WARNING


def test_a_world_name_known_only_with_a_direct_object_is_a_warning_not_an_error() -> None:
    """The MDM Devices false positive, end to end. `devices` and `management
    statuses` are proxy agent inspectors no dump covers; `devices` also
    collides with the captured grub `device of <grub file location>`, so it
    used to fall through the unknown-name net into a hard `type-error`. Both
    now land on `unknown-inspector`, each by its own route."""
    report = analyze(
        "(in proxy agent context) AND exists management statuses of devices", Dialect.CLIENT
    )
    findings = lint_analysis(report, LintConfig())
    assert codes(findings) == {"unknown-inspector"}
    assert all(f.severity is Severity.WARNING for f in findings)
    messages = sorted(f.message for f in findings)
    assert messages == [
        "no dump defines `management statuses`",
        "no dump defines the property 'devices' without a direct object",
    ]


def test_statement_level_findings_land_on_the_statement_first_line() -> None:
    """`unknown-inspector` (and the two ceilings) carry no span, so they land
    on relative line 1, which `emit` offsets by `base_line`. Passing
    `base_line` itself there double-counted the offset for extracted sites --
    a finding at line 15 of an 11-line .bes file."""
    report = analyze(UNKNOWN_INSPECTOR, Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig(), base_line=8)
    assert [(f.code, f.line) for f in findings] == [("unknown-inspector", 8)]


def test_a_singular_form_over_a_plural_object_is_a_warning_not_an_error() -> None:
    """`value of results` is a singular expression, so the static singularity
    rule does not apply -- but the object may still be non-unique, which the
    engine answers at runtime. That is a warning, and configurable."""
    report = analyze('value of results from (bes property "X") of bes computers', Dialect.SESSION)
    findings = lint_analysis(report, LintConfig())
    assert "type-error" not in codes(findings)
    risk = next(f for f in findings if f.code == "non-unique-risk")
    assert risk.severity is Severity.WARNING
    # Not the engine's error text: nothing has errored, and quoting it would
    # read as if something had.
    assert "Singular expression refers to" not in risk.message
    assert risk.message.endswith("a singular context errors at evaluation if it is")


def test_the_non_unique_risk_rule_can_be_silenced() -> None:
    report = analyze('value of results from (bes property "X") of bes computers', Dialect.SESSION)
    config = LintConfig(severities={"non-unique-risk": Severity.IGNORE})
    assert "non-unique-risk" not in codes(lint_analysis(report, config))


def test_a_singular_form_of_a_multivalued_property_is_the_same_warning() -> None:
    """The property-side sibling lands on the same rule: `file of folder ...`
    risks the same `Singular expression refers to non-unique object.` as a
    singular form over a plural object, so it is one configurable code, not a
    second vocabulary entry downstream tools would have to map."""
    report = analyze('file of folder "c:\\"', Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig())
    assert "type-error" not in codes(findings)
    risk = next(f for f in findings if f.code == "non-unique-risk")
    assert risk.severity is Severity.WARNING
    assert "the plural 'files' is preferred" in risk.message

    config = LintConfig(severities={"non-unique-risk": Severity.IGNORE})
    assert codes(lint_analysis(report, config)) == set()


def test_the_webreport_example_has_no_errors() -> None:
    """A `&` over `value of results ...` is correct relevance: the operand is
    singular. Only the runtime non-uniqueness risk remains."""
    findings = lint_file(
        Path(
            "tests/examples/session_relevance/webreports/webreport_session_relevance_basic.besrpt"
        ),
        LintConfig(),
    )
    assert [f for f in findings if f.severity is Severity.ERROR] == []


def test_complexity_is_silent_under_the_default_ceiling() -> None:
    # A nested, filtered statement that scores meaningfully above zero, but
    # nowhere near the default ceiling (`DEFAULT_MAX_SCORE`).
    report = analyze(
        'exists files whose (name of it starts with "bes" AND size of it > 0) '
        'of folders whose (name of it as lowercase as string != "") of folder "/tmp"'
    )
    assert 0 < report.complexity.score < DEFAULT_MAX_SCORE
    findings = lint_analysis(report, LintConfig())
    assert "complexity" not in codes(findings)


def test_complexity_fires_by_default_once_it_is_genuinely_extreme() -> None:
    # `complexity` is on by default: a statement scoring above the built-in
    # ceiling fires with no configuration at all.
    report = analyze(CLIENT)
    findings = lint_analysis(report, LintConfig(max_score=report.complexity.score - 1))
    assert "complexity" in codes(findings)
    finding = next(f for f in findings if f.code == "complexity")
    assert finding.severity is Severity.ERROR
    assert "score" in finding.message


def test_complexity_fires_with_the_bare_default_config_when_truly_extreme() -> None:
    # No threshold configured at all -- `LintConfig()` alone -- for a
    # statement genuinely past the built-in ceiling.
    report = analyze("(" * 40 + "1" + ")" * 40)
    assert report.complexity.score > DEFAULT_MAX_SCORE
    findings = lint_analysis(report, LintConfig())
    assert "complexity" in codes(findings)


def test_complexity_is_silent_when_score_is_under_configured_max() -> None:
    report = analyze(CLIENT)
    findings = lint_analysis(report, LintConfig(max_score=report.complexity.score + 1))
    assert "complexity" not in codes(findings)


def test_complexity_can_be_disabled_entirely_via_the_library_api() -> None:
    report = analyze(CLIENT)
    findings = lint_analysis(report, LintConfig(max_score=None))
    assert "complexity" not in codes(findings)


def test_evaluation_cost_is_silent_under_the_default_ceiling() -> None:
    report = analyze('exists descendants of folder "C:\\"', Dialect.CLIENT)
    assert 0 < report.complexity.evaluation_cost < DEFAULT_MAX_EVALUATION_COST
    findings = lint_analysis(report, LintConfig())
    assert "evaluation-cost" not in codes(findings)


def test_evaluation_cost_fires_by_default_once_it_is_genuinely_extreme() -> None:
    report = analyze('exists descendants of folder "C:\\"', Dialect.CLIENT)
    findings = lint_analysis(
        report, LintConfig(max_evaluation_cost=report.complexity.evaluation_cost - 1)
    )
    assert "evaluation-cost" in codes(findings)
    finding = next(f for f in findings if f.code == "evaluation-cost")
    assert finding.severity is Severity.ERROR


def test_evaluation_cost_fires_with_the_bare_default_config_when_truly_extreme() -> None:
    stmt = (
        'sha1 of file "/a" ; sha1 of file "/b" ; sha1 of file "/c" ; '
        'sha1 of file "/d" ; sha1 of file "/e"'
    )
    report = analyze(stmt, Dialect.CLIENT)
    assert report.complexity.evaluation_cost > DEFAULT_MAX_EVALUATION_COST
    findings = lint_analysis(report, LintConfig())
    assert "evaluation-cost" in codes(findings)


def test_evaluation_cost_can_be_disabled_entirely_via_the_library_api() -> None:
    report = analyze('exists descendants of folder "C:\\"', Dialect.CLIENT)
    findings = lint_analysis(report, LintConfig(max_evaluation_cost=None))
    assert "evaluation-cost" not in codes(findings)


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


def test_a_path_that_does_not_exist_is_reported_as_an_error(tmp_path: Path) -> None:
    """A missing path is a finding, not a silent pass.

    Nothing else distinguishes a typo'd path from a clean file: both produce no
    sites. A hook whose argument was misspelled would otherwise report success
    over content it never read.
    """
    missing = tmp_path / "does-not-exist.rel"
    findings = lint_paths([missing], LintConfig())
    assert len(findings) == 1
    finding = findings[0]
    assert finding.code == "file-error"
    assert finding.severity is Severity.ERROR
    assert finding.path == missing
    assert finding.line == 1
    assert finding.site is None


def test_a_missing_path_is_reported_whatever_its_suffix(tmp_path: Path) -> None:
    # A suffix the extractor does not recognize never reaches the filesystem at
    # all, so the "does it exist" question has to be asked before extraction --
    # otherwise a typo'd `notes.txt` is indistinguishable from a real one.
    missing = tmp_path / "does-not-exist.txt"
    assert codes(lint_file(missing, LintConfig())) == {"file-error"}


def test_an_unreadable_file_is_reported_as_an_error(tmp_path: Path) -> None:
    path = tmp_path / "unreadable.rel"
    path.write_text(CLIENT)
    path.chmod(0o000)
    try:
        if os.access(path, os.R_OK):  # root ignores the mode; nothing to test
            pytest.skip("running as a user that can read a mode-000 file")
        assert codes(lint_file(path, LintConfig())) == {"file-error"}
    finally:
        path.chmod(0o600)


def test_the_file_error_rule_can_be_silenced(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.rel"
    config = LintConfig(severities={"file-error": Severity.IGNORE})
    assert lint_paths([missing], config) == ()


def test_lint_paths_never_expands_a_directory_argument(tmp_path: Path) -> None:
    # An explicit path, even a directory with lintable content inside it, is
    # taken literally -- only lint_directory() recurses. This is deliberate,
    # confirmed behavior, not a gap: see the module docstring.
    (tmp_path / "broken.rel").write_text(BROKEN)
    assert lint_paths([tmp_path], LintConfig()) == ()
    assert lint_file(tmp_path, LintConfig()) == ()


# ---------------------------------------------------------------------------
# lint_directory: the one entry point that walks
# ---------------------------------------------------------------------------


def test_lint_directory_finds_sites_in_nested_files_of_different_types(
    tmp_path: Path,
) -> None:
    (tmp_path / "top.rel").write_text(CLIENT)
    nested = tmp_path / "sub" / "deeper"
    nested.mkdir(parents=True)
    (nested / "broken.rel").write_text(BROKEN)

    findings = lint_directory(tmp_path, LintConfig())
    assert codes(findings) == {"parse-error", "error-token"}
    assert all(f.path == nested / "broken.rel" for f in findings)


def test_lint_directory_prunes_default_excluded_directories(tmp_path: Path) -> None:
    for name in (".git", "__pycache__", "venv", ".mypy_cache"):
        excluded = tmp_path / name
        excluded.mkdir()
        (excluded / "broken.rel").write_text(BROKEN)
    (tmp_path / "clean.rel").write_text(CLIENT)

    findings = lint_directory(tmp_path, LintConfig())
    assert findings == ()


def test_lint_directory_scans_a_tree_exactly_max_depth_levels_deep(tmp_path: Path) -> None:
    deep = tmp_path
    for _ in range(DEFAULT_MAX_DEPTH):
        deep = deep / "d"
        deep.mkdir()
    (deep / "broken.rel").write_text(BROKEN)

    findings = lint_directory(tmp_path, LintConfig())
    assert "parse-error" in codes(findings)
    assert "max-depth-exceeded" not in codes(findings)


def test_lint_directory_reports_and_stops_one_level_past_max_depth(tmp_path: Path) -> None:
    deep = tmp_path
    for _ in range(DEFAULT_MAX_DEPTH + 1):
        deep = deep / "d"
        deep.mkdir()
    (deep / "broken.rel").write_text(BROKEN)

    findings = lint_directory(tmp_path, LintConfig())
    assert codes(findings) == {"max-depth-exceeded"}
    exceeded = findings[0]
    assert exceeded.severity is Severity.ERROR
    # The too-deep file itself must not have been visited.
    assert exceeded.path != deep / "broken.rel"


def test_lint_directory_max_depth_override_reaches_deeper_content(tmp_path: Path) -> None:
    deep = tmp_path
    for _ in range(DEFAULT_MAX_DEPTH + 1):
        deep = deep / "d"
        deep.mkdir()
    (deep / "broken.rel").write_text(BROKEN)

    findings = lint_directory(tmp_path, LintConfig(), max_depth=DEFAULT_MAX_DEPTH + 2)
    assert "max-depth-exceeded" not in codes(findings)
    assert "parse-error" in codes(findings)


# ---------------------------------------------------------------------------
# The rule catalog
# ---------------------------------------------------------------------------
# `RULES` exists so that every consumer -- a hook, a CI log, an MCP server,
# an editor hover -- explains a finding with the same words, instead of each
# inventing its own. These tests are what keep it honest: a catalog nothing
# holds to the code it describes is documentation, and drifts like it.


def test_the_catalog_and_the_default_severities_cannot_disagree() -> None:
    """``DEFAULT_SEVERITIES`` is derived from ``RULES``, so it cannot drift.

    Kept as an assertion rather than trusted from the implementation, because
    the derivation is one line that a future edit could quietly replace with a
    second hand-maintained literal -- which is exactly the state this replaced.
    """
    assert set(DEFAULT_SEVERITIES) == set(RULES)
    for code, rule in RULES.items():
        assert DEFAULT_SEVERITIES[code] is rule.default_severity


def _every_emitted_code() -> set[str]:
    """Drive every rule and collect the codes that actually come out.

    Deliberately exercises the rules through :func:`lint_analysis` and
    :func:`lint_directory` rather than reading a list, so a rule that stopped
    firing counts as missing.
    """
    emitted: set[str] = set()
    thresholds = LintConfig(max_score=0.0, max_evaluation_cost=0.0)
    for text in (
        BROKEN,
        UNBOUND_IT,
        UNKNOWN_INSPECTOR,
        CLIENT,
        COSTLY,
        TYPE_MISMATCH,
        NON_UNIQUE_RISK,
        PLURAL_PREFERRED,
        VERSION_TRUNCATING,
        VERSION_LIKE_STRING,
    ):
        for config in (LintConfig(), thresholds):
            emitted.update(finding.code for finding in lint_analysis(analyze(text), config))
    return emitted


def test_every_rule_in_the_catalog_is_a_rule_that_fires(tmp_path: Path) -> None:
    """The catalog names exactly the codes the linter can emit -- no more, no less.

    Both directions matter and they catch opposite mistakes: an extra catalog
    entry is a rule that was removed without the docs following, and a missing
    one is a new rule whose explanation nobody wrote. Either way a consumer
    joining a finding to :data:`RULES` gets a ``KeyError`` or a stale answer.
    """
    emitted = _every_emitted_code()

    # `max-depth-exceeded` only comes from the directory walk, so it needs its
    # own trigger: a tree deeper than the limit it is reporting on.
    deep = tmp_path
    for level in range(3):
        deep = deep / f"level{level}"
    deep.mkdir(parents=True)
    (deep / "x.rel").write_text(CLIENT)
    emitted.update(finding.code for finding in lint_directory(tmp_path, LintConfig(), max_depth=1))

    # `file-error` is about the path rather than its content, so no statement
    # can trigger it -- it needs a path that is not there.
    emitted.update(
        finding.code for finding in lint_file(tmp_path / "does-not-exist.rel", LintConfig())
    )

    assert emitted == set(RULES)


def test_a_gated_rule_ships_on_by_default_with_a_ceiling() -> None:
    """``gated`` marks the two rules controlled by a numeric ceiling.

    Named ``gated`` rather than ``configurable`` on purpose: *every* rule's
    severity is configurable via :attr:`LintConfig.severities`, so
    ``configurable`` would read as true of all eight. What distinguishes
    these two is a ceiling with its own default (:data:`DEFAULT_MAX_SCORE`,
    :data:`DEFAULT_MAX_EVALUATION_COST`), tunable independently of severity --
    they still report by default, just only past that ceiling.
    """
    gated = {code for code, rule in RULES.items() if rule.gated}
    assert gated == {"complexity", "evaluation-cost"}

    # An ordinary statement, nowhere near either default ceiling: silent.
    silent = {finding.code for finding in lint_analysis(analyze(CLIENT), LintConfig())}
    assert not silent & gated

    # `COSTLY` rather than `CLIENT`: both ceilings are `>` comparisons, so a
    # statement whose evaluation cost is genuinely 0.0 cannot exceed 0.0 and
    # the second rule would look broken when it is only unexercised. Lowering
    # both ceilings to 0.0 here demonstrates they are tunable, not that they
    # are off by default -- see the dedicated "bare default config" tests for
    # that.
    loud = {
        finding.code
        for finding in lint_analysis(
            analyze(COSTLY), LintConfig(max_score=0.0, max_evaluation_cost=0.0)
        )
    }
    assert loud >= gated


def test_a_gated_rule_names_the_config_field_that_switches_it_on() -> None:
    """``threshold`` is a real :class:`LintConfig` field, and only gated rules have one.

    A consumer showing "set ``max_score`` to enable this" must be naming a
    field that exists, so the name is checked against the dataclass rather
    than trusted as a string.
    """
    fields = {field.name for field in dataclasses.fields(LintConfig)}
    for code, rule in RULES.items():
        if rule.gated:
            assert rule.threshold in fields, code
        else:
            assert rule.threshold is None, code


def test_every_rule_explains_itself_in_a_usable_shape() -> None:
    """``summary`` fits one line of a rule list; ``rationale`` is prose.

    The length and punctuation rules are not fussiness: ``summary`` goes in a
    table cell and an editor hover, so a paragraph there wraps badly and a
    trailing period reads wrong mid-row. ``rationale`` is the opposite -- full
    sentences, because it answers "why does this default this way".
    """
    for code, rule in RULES.items():
        assert rule.code == code, "a rule's key and its code must agree"
        assert rule.summary and "\n" not in rule.summary, code
        assert len(rule.summary) <= 100, code
        assert not rule.summary.endswith("."), code
        assert rule.rationale.endswith("."), code
        assert len(rule.rationale) > len(rule.summary), code


def test_the_catalog_serializes_to_plain_json() -> None:
    """A server serves this catalog once and joins findings to it by code."""
    payload = [rule.to_dict() for rule in rules()]
    assert payload == json.loads(json.dumps(payload))
    assert [entry["code"] for entry in payload] == [rule.code for rule in rules()]


def test_the_catalog_is_ordered_errors_first() -> None:
    """``rules()`` is a stable order a consumer can render without sorting.

    Errors before warnings, because a rule list is read to find out what will
    block a commit; alphabetical within a severity so the order never depends
    on dict insertion.
    """
    listed = rules()
    assert len(listed) == len(RULES)
    errors = [rule.code for rule in listed if rule.default_severity is Severity.ERROR]
    warnings = [rule.code for rule in listed if rule.default_severity is Severity.WARNING]
    assert [rule.code for rule in listed] == errors + warnings
    assert errors == sorted(errors)
    assert warnings == sorted(warnings)


def test_a_finding_does_not_repeat_the_catalog() -> None:
    """A finding carries its ``code``, not the rule's prose.

    The prose is identical on every finding of a kind, so inlining it would
    multiply a large repo's payload for no added information -- the join on
    ``code`` is what :data:`RULES` is for.
    """
    finding = lint_analysis(analyze(BROKEN), LintConfig())[0]
    payload = finding.to_dict()
    assert payload["code"] in RULES
    assert "summary" not in payload
    assert "rationale" not in payload


README = Path(__file__).parent.parent / "README.md"
#: The README's generated rule table: `| \`code\` | severity | ... |` rows only,
#: so prose and fenced example output cannot be mistaken for entries.
_README_RULE_ROW = re.compile(r"^\|\s*`([a-z-]+)`\s*\|\s*(error|warning)\s*\|", re.MULTILINE)


def test_the_readme_rule_table_matches_the_catalog() -> None:
    """Every rule is in the README's table, with the severity it actually has.

    The README is where an adopting repo decides which rules to ratchet on, so a
    table that has drifted from the code is worse than no table: it is a
    confident wrong answer. This happened once already with the dump README,
    which is why :mod:`test_inspector_data` checks the same way.
    """
    documented = dict(_README_RULE_ROW.findall(README.read_text(encoding="utf-8")))

    assert documented, "the README's rule table is missing or its shape changed"
    assert set(documented) == set(RULES), (
        "README rule table and lint.RULES disagree: "
        f"only in README {sorted(set(documented) - set(RULES))}, "
        f"only in code {sorted(set(RULES) - set(documented))}"
    )
    for code, severity in documented.items():
        assert severity == RULES[code].default_severity.value, code


def test_the_readme_rule_table_says_which_rules_are_gated() -> None:
    """A gated rule's row names its threshold; an always-on rule's says so.

    Which rules are off by default is the single most consequential thing on
    that table for someone adopting the hook -- get it wrong and they configure
    a ceiling that was already failing, or trust one that was never on.
    """
    text = README.read_text(encoding="utf-8")
    for row in text.splitlines():
        match = _README_RULE_ROW.match(row)
        if match is None:
            continue
        rule = RULES[match.group(1)]
        if rule.gated:
            assert rule.threshold is not None
            assert f"`{rule.threshold}`" in row, rule.code
            default = getattr(LintConfig(), rule.threshold)
            # Defaults are floats (e.g. 550.0) but the README writes them as
            # plain ints (550) -- format the same way so the two can't drift
            # apart on trailing ".0" while the assertion still catches a real
            # value change.
            rendered = (
                int(default) if isinstance(default, float) and default.is_integer() else default
            )
            assert f"default {rendered}" in row, rule.code
        else:
            assert "always on" in row, rule.code


# ---------------------------------------------------------------------------
# `unknown-inspector` suggestions
# ---------------------------------------------------------------------------
# The rule's own rationale calls it "a lead rather than a fault". A lead is much
# more useful with candidates attached -- but fuzzy matching costs milliseconds
# per unknown name, and unknown names are common in a repo running newer
# inspectors than the dumps, which is the rule's whole reason for existing. So
# it is opt-in: off, nothing changes and nothing is paid for.

# A deliberately garbled name whose correction is a real inspector. Reuses the
# misspelling `tests/test_inspectors.py` already relies on, because `_typos.toml`
# and `.codespellrc` allowlist it -- a fresh typo written here gets silently
# "corrected" by the spell-check hooks, which quietly guts the test.
TYPO = "exists oprating system"


def test_suggestions_are_off_by_default() -> None:
    """A default lint run pays nothing for fuzzy matching, and says nothing new.

    This is the load-bearing test for the whole feature: a pre-commit hook over
    a few thousand sites must not silently acquire seconds of latency for a
    warning that blocks nothing.
    """
    findings = lint_analysis(analyze(TYPO), LintConfig())
    unknown = [f for f in findings if f.code == "unknown-inspector"]
    assert unknown, "the typo should still be reported"
    assert unknown[0].suggestions == ()
    assert "did you mean" not in unknown[0].message


def test_suggestions_are_reported_when_asked_for() -> None:
    """With ``suggest=True`` the warning names what the author probably meant."""
    findings = lint_analysis(analyze(TYPO), LintConfig(suggest=True))
    unknown = next(f for f in findings if f.code == "unknown-inspector")

    assert "operating system" in unknown.suggestions
    assert "did you mean" in unknown.message
    assert "`operating system`" in unknown.message


def test_suggestions_are_structured_as_well_as_rendered() -> None:
    """A server gets a list; a human gets the sentence. Both, deliberately.

    The duplication matches the precedent of ``Finding.to_dict()["text"]``
    repeating the rendered line: an MCP server should not have to parse prose
    back out of a message to act on it.
    """
    finding = next(
        f
        for f in lint_analysis(analyze(TYPO), LintConfig(suggest=True))
        if f.code == "unknown-inspector"
    )
    payload = finding.to_dict()
    assert payload["suggestions"] == list(finding.suggestions)
    assert payload == json.loads(json.dumps(payload))
    for name in payload["suggestions"]:
        assert f"`{name}`" in payload["message"]


def test_suggestions_are_absent_from_every_other_rule() -> None:
    """``suggestions`` is empty, never null, on the six codes that cannot have any.

    An empty list keeps the key's type honest for every finding, which is what
    ``_serialize``'s never-omit rule is for; ``None`` would make a consumer
    special-case six of seven codes.
    """
    findings = lint_analysis(
        analyze(BROKEN), LintConfig(suggest=True, max_score=0.0, max_evaluation_cost=0.0)
    )
    for finding in findings:
        if finding.code != "unknown-inspector":
            assert finding.suggestions == ()
            assert finding.to_dict()["suggestions"] == []


def test_a_dialect_narrows_what_is_suggested() -> None:
    """A suggestion must be writable where the author is writing.

    Proposing a session inspector inside a fixlet's ``<Relevance>`` would be a
    lead into a different failure, so the configured dialect is passed through
    to the suggester rather than dropped.
    """
    # `wnidows` is the other allowlisted garble; its correction `windows` is a
    # client inspector, so a session-scoped search must not offer it.
    client = lint_analysis(
        analyze("exists wnidows", Dialect.CLIENT),
        LintConfig(suggest=True, dialect=Dialect.CLIENT),
    )
    assert "windows" in next(f for f in client if f.code == "unknown-inspector").suggestions

    session = lint_analysis(
        analyze("exists wnidows", Dialect.SESSION),
        LintConfig(suggest=True, dialect=Dialect.SESSION),
    )
    assert "windows" not in next(f for f in session if f.code == "unknown-inspector").suggestions


def test_a_name_with_no_plausible_correction_gets_no_suggestions() -> None:
    """Nonsense stays nonsense here too -- an empty tuple, and no dangling prose."""
    findings = lint_analysis(analyze("exists xyzzy"), LintConfig(suggest=True))
    unknown = next(f for f in findings if f.code == "unknown-inspector")
    assert unknown.suggestions == ()
    assert "did you mean" not in unknown.message


# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------


def test_the_version_rules_warn_rather_than_error() -> None:
    """Both fire on relevance that parses and type-checks, so neither may fail it.

    The engine accepts `version of operating system > version "14"` and answers
    `False` on a 14.6.1 host. Nothing is malformed; the author asked the wrong
    question. That makes these warnings by default -- an adopting repo can
    ratchet them to errors, which is the point of the severity being
    configurable, but shipping them as errors would break every build that has
    one of these in a file nobody is touching.
    """
    for text, code in (
        (VERSION_TRUNCATING, "version-truncating-compare"),
        (VERSION_LIKE_STRING, "version-like-string-compare"),
    ):
        findings = lint_analysis(analyze(text), LintConfig())
        assert codes(findings) == {code}, text
        assert RULES[code].default_severity is Severity.WARNING
        assert [finding.severity for finding in findings] == [Severity.WARNING], text
        # Not a type error: the statement is well-formed and the checker agrees.
        assert analyze(text).parsed


def test_the_version_rules_stay_off_the_safe_shapes() -> None:
    """The shapes real content actually uses, including this repo's own examples.

    `>=` against a shorter threshold is the common idiom and is *not* wrong --
    truncation only changes the answer for the operators that flip at equality
    in the direction of the dropped tail. Three of this package's own example
    files use this shape, so a rule that flagged it would have been noise on its
    first contact with real content.
    """
    for text in (
        'version of operating system >= "5.1"',
        'version of client >= "9.0" as version',
        'version of client < "8.0"',
        'pad of version of operating system > pad of version "14"',
        '"2.10.1" > "2.3.3" as version',
    ):
        assert codes(lint_analysis(analyze(text), LintConfig())) == set(), text
