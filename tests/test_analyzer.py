"""Tests for the aggregate analysis entry point and its command line.

The individual analyses have their own test modules; these check the wiring --
that every part is reached, that the dialect and platform selection reaches the
parts that depend on it, and that broken input degrades instead of raising.
"""

import json

import pytest

from bigfix_relevance_analyzer import RelevanceAnalysis, __version__, analyze_relevance
from bigfix_relevance_analyzer.__main__ import main
from bigfix_relevance_analyzer.analyzer import analyze
from bigfix_relevance_analyzer.binding import Binder
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.typecheck import Plurality

CLIENT = 'exists file "C:\\foo.txt" whose (size of it > 100)'
SESSION = "names of bes computers"
BROKEN = 'exists file "unterminated'


def test_version_is_importable_and_nonempty() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_alias_is_the_module_function() -> None:
    assert analyze_relevance is analyze


def test_client_statement_reaches_every_analysis() -> None:
    report = analyze(CLIENT)

    assert isinstance(report, RelevanceAnalysis)
    assert report.parsed
    assert report.valid
    assert report.parse_error is None
    assert report.sexpr is not None and report.sexpr.startswith("(exists ")
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
    assert analyze(CLIENT).dialect_assumed
    assert analyze(CLIENT).dialect is Dialect.CLIENT
    assert not analyze(CLIENT, Dialect.CLIENT).dialect_assumed
    assert not analyze(SESSION).dialect_assumed


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


def test_cli_prints_every_section(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([CLIENT]) == 0
    out = capsys.readouterr().out

    for section in ("dialect", "lexing", "parse", "types", "platforms", "complexity"):
        assert f"== {section} " in out
    assert "breakdown probes" in out


def test_cli_reports_a_parse_failure_and_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([BROKEN]) == 1
    out = capsys.readouterr().out

    assert "FAILED at line 1, column 13" in out
    # Lexical metrics survive, so the complexity section is still printed.
    assert "== complexity " in out
    assert "error_tokens: 1" in out
    assert "== types " not in out


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
