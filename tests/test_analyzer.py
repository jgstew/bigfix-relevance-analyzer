"""Tests for the aggregate analysis entry point and its command line.

The individual analyses have their own test modules; these check the wiring --
that every part is reached, that the dialect and platform selection reaches the
parts that depend on it, and that broken input degrades instead of raising.
"""

import json
import re
from pathlib import Path

import pytest

from bigfix_relevance_analyzer import RelevanceAnalysis, __version__, analyze_relevance
from bigfix_relevance_analyzer.__main__ import _cell, main
from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.binding import Binder
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.typecheck import Plurality

CLIENT = 'exists file "C:\\foo.txt" whose (size of it > 100)'
SESSION = "names of bes computers"
BES_EXAMPLE = Path("tests/examples/mixed_context/task_with_client_and_session_relevance.bes")
BROKEN = 'exists file "unterminated'


def test_version_is_importable_and_nonempty() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_alias_is_the_module_function() -> None:
    assert analyze_relevance is analyze


def test_lint_api_is_exported_from_the_package_root() -> None:
    import bigfix_relevance_analyzer as package
    from bigfix_relevance_analyzer.lint import lint_paths as module_lint_paths

    assert package.lint_paths is module_lint_paths


def test_client_statement_reaches_every_analysis() -> None:
    report = analyze(CLIENT)

    assert isinstance(report, RelevanceAnalysis)
    assert report.parsed
    assert report.valid
    assert report.parse_error is None
    assert report.sexpr is not None and report.sexpr.startswith("(exists ")
    assert report.mermaid is not None and report.mermaid.startswith("flowchart TD\n")
    assert report.tree_depth > 1
    assert report.node_kinds["Whose"] == 1

    assert report.check is not None
    assert report.check.value.types == frozenset({"boolean"})
    assert report.check.value.plurality is Plurality.SINGULAR

    assert report.platforms
    assert not report.missing_platforms
    assert {entry.phrase for entry in report.references} == {"file", "size"}
    assert not report.unknown_references
    assert report.complexity.score > 0
    assert report.levels


def test_it_binding_is_resolved_to_its_context() -> None:
    (binding,) = analyze(CLIENT).it_bindings

    assert binding.binder is Binder.WHOSE
    assert binding.context is not None
    assert not analyze(CLIENT).unbound_its


def test_unbound_it_is_reported_not_raised() -> None:
    report = analyze("size of it")

    assert report.parsed
    assert len(report.unbound_its) == 1


def test_session_statement_is_classified_and_has_no_platform_axis() -> None:
    report = analyze(SESSION)

    assert report.classified_dialect is Dialect.SESSION
    assert report.dialect is Dialect.SESSION
    assert not report.dialect_assumed
    assert report.platforms == frozenset()
    assert report.environment.universe == frozenset()


def test_dialect_is_assumed_only_when_nothing_settles_it() -> None:
    # CLIENT is deliberately not used here any more: it contains 'file', which
    # resolves client-only and so settles resolved_dialect on its own -- see
    # test_resolved_dialect_settles_what_the_text_classifier_cannot below.
    both_dialects = "size of it"
    assert analyze(both_dialects).dialect_assumed
    assert analyze(both_dialects).dialect is Dialect.CLIENT
    assert not analyze(both_dialects, Dialect.CLIENT).dialect_assumed
    assert not analyze(SESSION).dialect_assumed
    assert not analyze(CLIENT).dialect_assumed  # settled by resolved_dialect instead


def test_resolved_dialect_settles_what_the_text_classifier_cannot() -> None:
    # 'files'/'folders' are excluded from the text classifier's marker list on
    # purpose (too collision-prone in prose), but they resolve as client-only
    # inspectors, so a parsed reference to them is real, unambiguous evidence.
    report = analyze('files of folder "C:\\Windows"')

    assert report.classified_dialect is None  # the text classifier has no opinion
    assert report.resolved_dialect is Dialect.CLIENT  # but every reference does
    assert not report.dialect_assumed
    assert report.dialect is Dialect.CLIENT


def test_resolved_dialect_is_both_when_every_reference_supports_both() -> None:
    report = analyze("names of it of properties")

    assert report.resolved_dialect is Dialect.BOTH
    # BOTH does not settle which one this actually is, so it still counts as
    # an assumption -- unlike a definite CLIENT or SESSION verdict.
    assert report.dialect_assumed


def test_resolved_dialect_is_uncertain_when_references_contradict() -> None:
    # 'files' is client-only; 'current fixlet' is session-only (a Web Reports
    # marker). No single dialect supports both.
    report = analyze('files of folder "x"; current fixlet')

    assert report.resolved_dialect is Dialect.UNCERTAIN


def test_resolved_dialect_is_none_before_parsing_and_when_nothing_resolves() -> None:
    assert analyze(BROKEN).resolved_dialect is None
    assert analyze("totallymadeupinspectorname").resolved_dialect is None


def test_forced_dialect_overrides_classification() -> None:
    report = analyze(SESSION, Dialect.CLIENT)

    assert report.classified_dialect is Dialect.SESSION
    assert report.requested_dialect is Dialect.CLIENT
    assert report.dialect is Dialect.CLIENT


def test_platform_narrows_the_universe() -> None:
    report = analyze(CLIENT, platform="windows")

    assert report.environment.universe == frozenset({"windows"})
    assert report.platforms == frozenset({"windows"})


def test_unknown_name_is_reported_without_failing_the_parse() -> None:
    report = analyze('exists nonexistent inspector "x"')

    assert report.parsed
    assert "nonexistent inspector" in report.unknown_references


def test_broken_input_degrades_instead_of_raising() -> None:
    report = analyze(BROKEN)

    assert not report.parsed
    assert not report.valid
    assert report.parse_error is not None
    assert (report.parse_error.line, report.parse_error.column) == (1, 13)
    assert report.node is None
    assert report.check is None
    assert report.sexpr is None
    assert report.mermaid is None
    assert report.references == ()
    assert report.levels == ()
    assert report.it_bindings == ()

    # Everything that does not need a tree still answers.
    assert report.dialect is Dialect.CLIENT
    assert len(report.error_tokens) == 1
    assert report.complexity.error_tokens == 1


@pytest.mark.parametrize("text", [CLIENT, SESSION, BROKEN, "size of it"])
def test_to_dict_is_json_serializable(text: str) -> None:
    report = analyze(text)
    round_tripped = json.loads(json.dumps(report.to_dict()))

    assert round_tripped["text"] == text
    assert round_tripped["parse"]["ok"] is report.parsed
    assert ("types" in round_tripped) is (report.check is not None)


def test_to_dict_omits_mermaid_unless_asked() -> None:
    report = analyze(CLIENT)

    assert "mermaid" not in report.to_dict()["parse"]
    assert report.to_dict(mermaid=True)["parse"]["mermaid"] == report.mermaid


def test_cli_json_adds_the_flowchart_only_when_asked(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", CLIENT]) == 0
    assert "mermaid" not in json.loads(capsys.readouterr().out)["parse"]

    assert main(["--json", "--mermaid", CLIENT]) == 0
    assert "mermaid" in json.loads(capsys.readouterr().out)["parse"]


def test_cli_prints_markdown_with_every_section(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([CLIENT]) == 0
    out = capsys.readouterr().out

    assert out.startswith("# Relevance Analysis\n")
    assert f"```\n{CLIENT}\n```" in out
    for section in ("Summary", "Lexing", "Parse tree", "Platforms", "Complexity"):
        assert f"## {section}" in out
    assert "## Breakdown probes" in out
    # The summary table is a real Markdown table with a header separator.
    assert "| | |\n|---|---|" in out
    assert "| Name | Status | Returns | Platforms |" in out
    # The flowchart is opt-in; the S-expression above it is not.
    assert "```mermaid" not in out
    assert "(exists (whose " in out


def test_cli_adds_the_flowchart_only_when_asked(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--mermaid", CLIENT]) == 0
    with_flag = capsys.readouterr().out

    assert "```mermaid\nflowchart TD\n" in with_flag

    assert main([CLIENT]) == 0
    without_flag = capsys.readouterr().out

    assert "```mermaid" not in without_flag
    # The flag adds exactly the fenced diagram block and changes nothing else.
    stripped = re.sub(r"```mermaid\n.*?\n```\n\n", "", with_flag, flags=re.DOTALL)
    assert stripped == without_flag


def test_cli_mermaid_block_is_deterministic_across_separate_runs(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main([CLIENT])
    first = capsys.readouterr().out
    main([CLIENT])
    second = capsys.readouterr().out

    assert first == second


def test_cli_reports_a_parse_failure_and_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([BROKEN]) == 1
    out = capsys.readouterr().out

    assert ":x: line 1, col 13: unterminated string literal" in out
    assert "## Parse error" in out
    assert "> Line 1, column 13: unterminated string literal" in out
    # Lexical metrics survive, so the complexity section is still printed.
    assert "## Complexity" in out
    assert "| error_tokens | 1 |" in out
    assert "## Platforms" not in out


def test_cli_json_matches_to_dict(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "--platform", "windows", CLIENT]) == 0

    emitted = json.loads(capsys.readouterr().out)
    assert emitted == json.loads(json.dumps(analyze(CLIENT, platform="windows").to_dict()))
    assert emitted["platforms"]["universe"] == ["windows"]


def test_cli_reads_stdin_when_no_argument(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(f"  {SESSION}\n"))

    assert main([]) == 0
    assert SESSION in capsys.readouterr().out


def test_cli_rejects_empty_input() -> None:
    with pytest.raises(SystemExit):
        main(["   "])


def test_cli_treats_a_real_file_path_as_a_file_to_extract(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([str(BES_EXAMPLE)]) == 0
    out = capsys.readouterr().out

    assert "2 relevance site(s) found." in out
    assert "## Site 1:" in out and "## Site 2:" in out
    assert "names of current fixlets" in out
    assert "NOT in proxy agent context" in out
    # Each site is analysed against the dialect extraction already determined,
    # and nests one heading level deeper than a standalone report.
    assert out.count("| Dialect | `session`") == 1
    assert out.count("| Dialect | `client`") == 1
    assert "### Summary" in out


def test_cli_json_for_a_file_carries_each_sites_own_dialect(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--json", str(BES_EXAMPLE)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["file"] == str(BES_EXAMPLE)
    dialects = {site["site_dialect"] for site in payload["sites"]}
    assert dialects == {"session", "client"}
    for site in payload["sites"]:
        assert site["analysis"]["dialect"]["effective"] == site["site_dialect"]


def test_cli_reports_a_file_with_no_relevance_sites(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plain = tmp_path / "notes.txt"
    plain.write_text("just some notes, no relevance here\n")

    assert main([str(plain)]) == 0
    assert "No relevance found." in capsys.readouterr().out


def test_cli_a_nonexistent_path_is_analysed_as_relevance_text(
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = "/definitely/not/a/real/path.bes"

    # It fails to parse as relevance too -- the point is *how* it fails: as a
    # single badly-lexed statement, not as a file-extraction error.
    assert main([missing]) == 1
    out = capsys.readouterr().out
    assert missing in out
    assert "relevance site(s)" not in out
    assert ":x:" in out
    assert "## Parse error" in out


def test_cell_escapes_pipes_so_a_table_row_cannot_be_split() -> None:
    # '|' is a real relevance operator (error fallback), so a source snippet
    # placed in a table cell can legitimately contain one.
    assert _cell("it | false") == "`it \\| false`"


def test_cell_collapses_whitespace_and_truncates_long_context() -> None:
    long_text = "a" * 100
    assert _cell(f"line one\n   line two  {long_text}", max_len=20) == "`line one line two a...`"


def test_cli_renders_a_valid_table_row_when_it_binding_context_has_a_pipe(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["1 of (it | false; it | true) whose (exists it)"]) == 0
    out = capsys.readouterr().out

    bindings_section = out.split("`it` bindings")[1].split("\n## ")[0]
    binding_rows = [
        line
        for line in bindings_section.splitlines()
        if line.startswith("| ") and "Location" not in line and "---" not in line
    ]
    assert binding_rows
    for row in binding_rows:
        # Splitting on unescaped '|' must yield exactly the table's own 3
        # columns (plus the two empty edges from the leading/trailing '|').
        assert len(row.replace("\\|", "").split("|")) == 5


def test_cli_forced_dialect_overrides_every_site_in_a_file(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--dialect", "client", str(BES_EXAMPLE)]) == 0
    out = capsys.readouterr().out

    assert out.count("| Dialect | `client`") == 2


def test_cli_check_lints_files_instead_of_analysing_a_single_statement(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    clean = tmp_path / "clean.rel"
    clean.write_text(CLIENT)
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main(["--check", str(clean), str(broken)]) == 1
    out = capsys.readouterr().out
    assert f"{broken}:1: error [parse-error]" in out
    assert str(clean) not in out


def test_cli_check_accepts_multiple_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clean_a = tmp_path / "a.rel"
    clean_a.write_text(CLIENT)
    clean_b = tmp_path / "b.rel"
    clean_b.write_text(CLIENT)

    assert main(["--check", str(clean_a), str(clean_b)]) == 0


def test_cli_check_requires_at_least_one_path() -> None:
    with pytest.raises(SystemExit):
        main(["--check"])


def test_cli_check_wires_max_score_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "client.rel"
    path.write_text(CLIENT)

    assert main(["--check", "--max-score=1", str(path)]) == 1
    out = capsys.readouterr().out
    assert "[complexity]" in out
