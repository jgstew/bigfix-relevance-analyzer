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
from _helpers import BROKEN, CLIENT, UNKNOWN_INSPECTOR, write

from bigfix_relevance_analyzer._lint_cli import main
from bigfix_relevance_analyzer.lint import RULES, rules


def test_clean_files_exit_zero_and_print_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clean = write(tmp_path, "clean.rel", CLIENT)

    assert main([str(clean)]) == 0
    out = capsys.readouterr().out
    assert out == ""


def test_broken_file_exits_one_and_prints_a_grep_able_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = write(tmp_path, "broken.rel", BROKEN)

    assert main([str(broken)]) == 1
    out = capsys.readouterr().out
    assert f"{broken}:1: error [parse-error]" in out


def test_warning_only_exits_zero_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "unknown.rel", UNKNOWN_INSPECTOR)

    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "warning [unknown-inspector]" in out


def test_fail_on_warning_promotes_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "unknown.rel", UNKNOWN_INSPECTOR)

    assert main(["--fail-on-warning", str(path)]) == 1


def test_max_score_flag_is_wired_through(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "client.rel", CLIENT)

    assert main([str(path)]) == 0  # no threshold configured: clean
    assert main(["--max-score=1", str(path)]) == 1
    out = capsys.readouterr().out
    assert "[complexity]" in out


def test_max_evaluation_cost_flag_is_wired_through(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "descendants.rel", 'exists descendants of folder "C:\\"')

    assert main([str(path)]) == 0
    assert main(["--max-evaluation-cost=1", str(path)]) == 1
    out = capsys.readouterr().out
    assert "[evaluation-cost]" in out


def test_ignore_flag_silences_a_rule(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "unbound.rel", "size of it")

    assert main([str(path)]) == 1
    assert main(["--ignore=unbound-it", str(path)]) == 0


def test_a_path_that_does_not_exist_fails_the_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The hook's own argument being wrong is the case this catches: without it,
    # a typo'd path lints nothing and reports success.
    missing = tmp_path / "does-not-exist.bes"

    assert main([str(missing)]) == 1
    captured = capsys.readouterr()
    assert f"{missing}:1: error [file-error]" in captured.out
    assert "1 error(s)" in captured.err


def test_the_file_error_rule_can_be_ignored(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.bes"

    assert main(["--ignore=file-error", str(missing)]) == 0
    assert capsys.readouterr().out == ""


def test_error_flag_promotes_a_default_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "unknown.rel", UNKNOWN_INSPECTOR)

    assert main(["--error=unknown-inspector", str(path)]) == 1


def test_summary_line_goes_to_stderr(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    broken = write(tmp_path, "broken.rel", BROKEN)

    main([str(broken)])
    captured = capsys.readouterr()
    assert "error(s)" in captured.err  # the summary count, not a finding
    assert "error(s)" not in captured.out


def test_quiet_suppresses_findings_but_keeps_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = write(tmp_path, "broken.rel", BROKEN)

    assert main(["--quiet", str(broken)]) == 1
    out = capsys.readouterr().out
    assert out == ""


def test_no_paths_walks_the_current_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write(tmp_path, "broken.rel", BROKEN)

    assert main([]) == 1
    out = capsys.readouterr().out
    assert "broken.rel:1: error [parse-error]" in out


def test_explicit_dot_is_not_walked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write(tmp_path, "broken.rel", BROKEN)

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
    write(tmp_path, "client.rel", CLIENT)

    assert main(["--max-score=1"]) == 1
    out = capsys.readouterr().out
    assert "[complexity]" in out


def test_multiple_paths_all_get_linted(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    clean = write(tmp_path, "clean.rel", CLIENT)
    broken = write(tmp_path, "broken.rel", BROKEN)

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
    broken = write(tmp_path, "broken.rel", BROKEN)

    assert main(["--json", str(broken)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    # An unterminated literal is two findings, not one: the parser stops, and
    # the tokenizer separately could not lex the rest.
    assert payload["counts"] == {"error": 2, "warning": 0}
    assert {finding["code"] for finding in payload["findings"]} == {"parse-error", "error-token"}
    assert payload["findings"][0]["site"]["kind"] == "plain-text"


UNCLOSED_BES = (
    "<BES><Fixlet><Relevance>true</Relevance>\n"
    "<DefaultAction><ActionScript>// one\n"
    "x { name of operating system</ActionScript></DefaultAction>\n"
    "</Fixlet></BES>\n"
)
"""An action line whose `{` never closes, on line 3: a runtime failure (#70)."""


def test_an_unclosed_action_brace_fails_the_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    unclosed = write(tmp_path, "unclosed.bes", UNCLOSED_BES)

    assert main([str(unclosed)]) == 1
    assert f"{unclosed}:3: error [unterminated-substitution]" in capsys.readouterr().out

    assert main(["--json", str(unclosed)]) == 1
    (finding,) = json.loads(capsys.readouterr().out)["findings"]
    assert finding["code"] == "unterminated-substitution"
    assert finding["line"] == 3
    assert finding["site"] is None


def test_json_and_the_line_output_report_the_same_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every finding's ``text`` is the line the default mode would have printed.

    The two modes are renderings of one result, not two code paths that happen
    to agree today.
    """
    broken = write(tmp_path, "broken.rel", BROKEN)

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
    clean = write(tmp_path, "clean.rel", CLIENT)

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
    broken = write(tmp_path, "broken.rel", BROKEN)

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
    assert "--max-score" in out, "a gated rule must say what switches it on"


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
    broken = write(tmp_path, "broken.rel", BROKEN)

    assert main(["--list-rules", str(broken)]) == 0
    out = capsys.readouterr().out
    assert str(broken) not in out


# -- --fix -------------------------------------------------------------------------

SETTING_TASK = (
    '<?xml version="1.0" encoding="UTF-8"?>\n<BES><Task>\n'
    '<Relevance>exists values of setting "x" of client</Relevance>\n'
    "</Task></BES>\n"
)


def test_without_fix_a_fixable_file_is_left_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "t.bes", SETTING_TASK)
    assert main([str(path)]) == 0
    assert path.read_text() == SETTING_TASK
    assert f"{path}:3: warning [plural-preferred]" in capsys.readouterr().out


def test_fix_rewrites_the_file_reports_it_and_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Non-zero when anything was fixed, so the fix is reviewed before it is committed."""
    path = write(tmp_path, "t.bes", SETTING_TASK)
    assert main(["--fix", str(path)]) == 1
    assert path.read_text() == SETTING_TASK.replace("setting ", "settings ")
    captured = capsys.readouterr()
    assert captured.out == f"{path}:3: fixed [plural-preferred] setting -> settings\n"
    assert "1 fix(es) applied in 1 file(s)" in captured.err

    assert main(["--fix", str(path)]) == 0
    assert capsys.readouterr().out == ""


def test_fix_reports_a_fix_it_could_not_apply(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A byte that is not UTF-8 on the fix's line: no offset next to it can be trusted."""
    data = b'exists values of setting "\xff" of client\n'
    path = tmp_path / "t.rel"
    path.write_bytes(data)
    assert main(["--fix", str(path)]) == 0
    assert path.read_bytes() == data
    out = capsys.readouterr().out
    assert f"{path}:1: not fixed [plural-preferred] undecodable bytes on line 1" in out
    assert f"{path}:1: warning [plural-preferred]" in out


@pytest.mark.parametrize(
    ("name", "text", "fixed", "reported"),
    [
        (
            "t.rel",
            'exists values of setting "x" of client\n',
            'exists values of settings "x" of client\n',
            "1: fixed [plural-preferred] setting -> settings",
        ),
        (
            "t.md",
            '# T\n\n```relevance\nexists values of setting "x" of client\n```\n',
            '# T\n\n```relevance\nexists values of settings "x" of client\n```\n',
            "4: fixed [plural-preferred] setting -> settings",
        ),
        (
            "t.ojo",
            '<p><?Relevance names of bes computers | "y" ?></p>\n',
            '<p><?Relevance unique value of names of bes computers | "y" ?></p>\n',
            (
                "1: fixed [singular-required] names of bes computers -> "
                "unique value of names of bes computers"
            ),
        ),
    ],
)
def test_fix_rewrites_every_file_type_and_reports_the_whole_edit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    name: str,
    text: str,
    fixed: str,
    reported: str,
) -> None:
    """Reported per edit as the analyzer made it, never per inserted piece."""
    path = write(tmp_path, name, text)
    assert main(["--fix", str(path)]) == 1
    assert path.read_text() == fixed
    assert capsys.readouterr().out.startswith(f"{path}:{reported}\n")
    assert main(["--fix", str(path)]) == 0


def test_fix_diff_prints_the_change_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write(tmp_path, "t.bes", SETTING_TASK)
    assert main(["--fix", "--diff", str(path)]) == 1
    assert path.read_text() == SETTING_TASK
    captured = capsys.readouterr()
    assert captured.out == (
        f"--- {path}\n"
        f"+++ {path}\n"
        "@@ -1,4 +1,4 @@\n"
        ' <?xml version="1.0" encoding="UTF-8"?>\n'
        " <BES><Task>\n"
        '-<Relevance>exists values of setting "x" of client</Relevance>\n'
        '+<Relevance>exists values of settings "x" of client</Relevance>\n'
        " </Task></BES>\n"
    )
    assert "1 fix(es) would be applied in 1 file(s)" in captured.err

    clean = write(tmp_path, "c.bes", SETTING_TASK.replace("setting ", "settings "))
    assert main(["--fix", "--diff", str(clean)]) == 0
    assert capsys.readouterr().out == ""


def test_diff_needs_fix() -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--diff", "t.bes"])
    assert raised.value.code == 2


def test_fix_honours_ignore(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "t.bes", SETTING_TASK)
    assert main(["--fix", "--ignore", "plural-preferred", str(path)]) == 0
    assert path.read_text() == SETTING_TASK
    assert capsys.readouterr().out == ""


def test_fix_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "t.bes", SETTING_TASK)
    assert main(["--fix", "--json", str(path)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["changed"] == [str(path)]
    assert [fix["line"] for fix in payload["applied"]] == [3]
    assert payload["unapplied"] == []
    assert payload["findings"] == []
    assert payload["ok"] is True
    assert payload["scope"] == "1 file(s)"


def test_fix_with_no_paths_walks_the_current_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "sub").mkdir()
    path = tmp_path / "sub" / "t.bes"
    path.write_text(SETTING_TASK)
    monkeypatch.chdir(tmp_path)
    assert main(["--fix"]) == 1
    assert path.read_text() == SETTING_TASK.replace("setting ", "settings ")
    assert "fixed [plural-preferred]" in capsys.readouterr().out


def test_relevance_text_argument_is_linted_directly(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["(version of client, name of it, version of it) of operating system"]) == 0
    assert "in 1 statement(s)" in capsys.readouterr().err


def test_broken_relevance_text_exits_one(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["names of (files"]) == 1
    assert "[parse-error]" in capsys.readouterr().out


def test_missing_path_without_whitespace_is_still_a_file_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(tmp_path / "typo.bes")]) == 1
    assert "[file-error]" in capsys.readouterr().out


def test_existing_path_with_whitespace_is_still_a_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = write(tmp_path, "my broken.rel", BROKEN)
    assert main([str(broken)]) == 1
    assert "my broken.rel:" in capsys.readouterr().out


def test_fix_refuses_relevance_text() -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--fix", "name of operating system"])
    assert raised.value.code == 2


def test_markdown_lists_findings_under_a_heading_with_the_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--markdown", "name of oprating system"]) == 0
    out = capsys.readouterr().out

    assert out.startswith("# Lint results\n")
    # The finding quotes a name in backticks, so the span needs a wider fence.
    assert "- `` line 1: warning [unknown-inspector] no dump defines `oprating system` ``" in out
    assert out.rstrip().endswith("**0 error(s), 1 warning(s) in 1 statement(s)**")


def test_markdown_says_so_when_nothing_was_found(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--markdown", "name of operating system"]) == 0
    assert "No issues found." in capsys.readouterr().out


def test_json_and_markdown_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        main(["--json", "--markdown", "name of operating system"])
