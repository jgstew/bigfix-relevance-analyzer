"""Tests for the ``bigfix-relevance-lint`` console script.

Rendering and exit-code behaviour only -- the judgement itself is pinned in
:mod:`test_lint`. Invoked the same way :mod:`test_analyzer` invokes
:func:`~bigfix_relevance_analyzer.__main__.main`: call ``main`` directly and
read ``capsys``, no subprocess.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bigfix_relevance_analyzer._lint_cli import main
from bigfix_relevance_analyzer.lint import RULES, rules

CLIENT = 'exists file "C:\\foo.txt" whose (size of it > 100)'
BROKEN = 'exists file "unterminated'


def test_clean_files_exit_zero_and_print_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clean = tmp_path / "clean.rel"
    clean.write_text(CLIENT)

    assert main([str(clean)]) == 0
    out = capsys.readouterr().out
    assert out == ""


def test_broken_file_exits_one_and_prints_a_grep_able_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main([str(broken)]) == 1
    out = capsys.readouterr().out
    assert f"{broken}:1: error [parse-error]" in out


def test_warning_only_exits_zero_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "unknown.rel"
    path.write_text("totally bogus made up inspector")

    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "warning [unknown-inspector]" in out


def test_fail_on_warning_promotes_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "unknown.rel"
    path.write_text("totally bogus made up inspector")

    assert main(["--fail-on-warning", str(path)]) == 1


def test_max_score_flag_is_wired_through(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "client.rel"
    path.write_text(CLIENT)

    assert main([str(path)]) == 0  # no threshold configured: clean
    assert main(["--max-score=1", str(path)]) == 1
    out = capsys.readouterr().out
    assert "[complexity]" in out


def test_max_evaluation_cost_flag_is_wired_through(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "descendants.rel"
    path.write_text('exists descendants of folder "C:\\"')

    assert main([str(path)]) == 0
    assert main(["--max-evaluation-cost=1", str(path)]) == 1
    out = capsys.readouterr().out
    assert "[evaluation-cost]" in out


def test_ignore_flag_silences_a_rule(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "unbound.rel"
    path.write_text("size of it")

    assert main([str(path)]) == 1
    assert main(["--ignore=unbound-it", str(path)]) == 0


def test_error_flag_promotes_a_default_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "unknown.rel"
    path.write_text("totally bogus made up inspector")

    assert main(["--error=unknown-inspector", str(path)]) == 1


def test_summary_line_goes_to_stderr(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    main([str(broken)])
    captured = capsys.readouterr()
    assert "error(s)" in captured.err  # the summary count, not a finding
    assert "error(s)" not in captured.out


def test_quiet_suppresses_findings_but_keeps_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main(["--quiet", str(broken)]) == 1
    out = capsys.readouterr().out
    assert out == ""


def test_no_paths_walks_the_current_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "broken.rel").write_text(BROKEN)

    assert main([]) == 1
    out = capsys.readouterr().out
    assert "broken.rel:1: error [parse-error]" in out


def test_explicit_dot_is_not_walked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "broken.rel").write_text(BROKEN)

    # An explicit "." is a literal path argument, not a walk root: extract_relevance_from_file(".")
    # matches no recognized suffix, so this finds nothing -- same as any other explicit path.
    assert main(["."]) == 0
    out = capsys.readouterr().out
    assert out == ""


def test_max_depth_is_wired_through_on_the_walk_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    deep = tmp_path
    for _ in range(7):
        deep = deep / "d"
        deep.mkdir()
    (deep / "broken.rel").write_text(BROKEN)

    assert main([]) == 1
    out = capsys.readouterr().out
    assert "max-depth-exceeded" in out
    assert "parse-error" not in out

    assert main(["--max-depth=8"]) == 1
    out = capsys.readouterr().out
    assert "parse-error" in out
    assert "max-depth-exceeded" not in out


def test_another_flag_with_no_paths_still_walks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "client.rel").write_text(CLIENT)

    assert main(["--max-score=1"]) == 1
    out = capsys.readouterr().out
    assert "[complexity]" in out


def test_multiple_paths_all_get_linted(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    clean = tmp_path / "clean.rel"
    clean.write_text(CLIENT)
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main([str(clean), str(broken)]) == 1
    out = capsys.readouterr().out
    assert str(clean) not in out
    assert str(broken) in out


def test_json_emits_one_object_with_findings_counts_and_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--json`` replaces the line-per-finding output with one parseable object.

    This is the mode CI and an MCP server read, so the whole point is that it
    parses -- a stray print alongside it would break the parse, not just look
    untidy.
    """
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main(["--json", str(broken)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    # An unterminated literal is two findings, not one: the parser stops, and
    # the tokenizer separately could not lex the rest.
    assert payload["counts"] == {"error": 2, "warning": 0}
    assert {finding["code"] for finding in payload["findings"]} == {"parse-error", "error-token"}
    assert payload["findings"][0]["site"]["kind"] == "plain-text"


def test_json_and_the_line_output_report_the_same_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every finding's ``text`` is the line the default mode would have printed.

    The two modes are renderings of one result, not two code paths that happen
    to agree today.
    """
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    main([str(broken)])
    lines = [line for line in capsys.readouterr().out.splitlines() if line]
    main(["--json", str(broken)])
    payload = json.loads(capsys.readouterr().out)

    assert [finding["text"] for finding in payload["findings"]] == lines


def test_json_stays_clean_when_nothing_was_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A clean run is an empty findings list, not empty output.

    The default mode prints nothing at all, which a JSON consumer cannot tell
    from a crash; ``--json`` always emits the envelope.
    """
    clean = tmp_path / "clean.rel"
    clean.write_text(CLIENT)

    assert main(["--json", str(clean)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "findings": [],
        "counts": {"error": 0, "warning": 0},
        "ok": True,
        "scope": "1 file(s)",
    }


def test_quiet_beats_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``--quiet`` means print nothing, including no JSON. Exit code still set."""
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main(["--json", "--quiet", str(broken)]) == 1
    assert capsys.readouterr().out == ""


def test_list_rules_prints_every_rule_and_exits_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--list-rules`` is how a hook's codes get looked up with the hook's own tool.

    Exits zero and lints nothing: it is a question about the tool, not a run.
    """
    assert main(["--list-rules"]) == 0
    out = capsys.readouterr().out
    for code in RULES:
        assert code in out
    assert "needs --max-score" in out, "a gated rule must say what switches it on"


def test_list_rules_json_is_the_catalog_verbatim(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With ``--json`` the same listing is machine-readable, for a server to serve."""
    assert main(["--list-rules", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == [rule.to_dict() for rule in rules()]


def test_list_rules_ignores_paths_rather_than_linting_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A broken file alongside ``--list-rules`` does not turn it into a lint run.

    Otherwise asking what the rules are could exit non-zero, which a script
    checking the tool's capabilities would read as a failure.
    """
    broken = tmp_path / "broken.rel"
    broken.write_text(BROKEN)

    assert main(["--list-rules", str(broken)]) == 0
    out = capsys.readouterr().out
    assert str(broken) not in out
