"""Tests for writing fixes back into files (:mod:`bigfix_relevance_analyzer.fixfile`).

The acceptance tests here are the behaviour the pre-commit-bigfix hook relies
on: a fix rewrites only the words it changes, every other byte of the file is
kept as written, and a second run has nothing left to do.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bigfix_relevance_analyzer import fixfile
from bigfix_relevance_analyzer.autofix import AutofixResult, TextEdit
from bigfix_relevance_analyzer.extract import RelevanceSite, extract_relevance_from_bes_xml
from bigfix_relevance_analyzer.fixfile import (
    ByteEdit,
    Unmapped,
    fix_file,
    fix_paths,
    fix_paths_to_dict,
    site_fixes,
    source_edits,
)
from bigfix_relevance_analyzer.lint import LintConfig, Severity, lint_file

SETTING = 'exists values of setting "x" of client'
SETTINGS = 'exists values of settings "x" of client'

HEAD = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
    "\t<Task>\n"
    "\t\t<Title>t</Title>\n"
)
TAIL = "\t</Task>\n</BES>\n"


def task(*lines: str, newline: str = "\n") -> bytes:
    return (
        (HEAD + "".join(f"\t\t{line}\n" for line in lines) + TAIL)
        .replace("\n", newline)
        .encode("utf-8")
    )


def write(tmp_path: Path, data: bytes, name: str = "t.bes") -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


def fixed_once(tmp_path: Path, data: bytes, config: LintConfig | None = None) -> bytes:
    """Fix ``data`` as a file, check a second run changes nothing, return the bytes."""
    path = write(tmp_path, data)
    result = fix_file(path, config or LintConfig())
    after = path.read_bytes()
    assert result.changed is (after != data)
    again = fix_file(path, config or LintConfig())
    assert not again.changed and not again.applied
    assert path.read_bytes() == after
    return after


# -- acceptance --------------------------------------------------------------------


def test_the_singular_spelling_is_rewritten_and_nothing_else(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    result = fix_file(path, LintConfig())
    assert path.read_bytes() == data.replace(b"setting ", b"settings ")
    assert result.changed
    (applied,) = result.applied
    assert applied.path == path
    assert applied.line == 5
    assert applied.autofix.fixed == SETTINGS
    assert applied.reason is None
    assert result.unapplied == ()
    assert not any(finding.code == "plural-preferred" for finding in result.findings)

    again = fix_file(path, LintConfig())
    assert not again.changed and again.applied == ()


def test_an_escaped_lt_stays_escaped(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING} and 1 &lt; 2</Relevance>")
    assert fixed_once(tmp_path, data) == data.replace(b"setting ", b"settings ")


def test_escaped_quotes_stay_escaped(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING.replace(chr(34), '&quot;')}</Relevance>")
    after = fixed_once(tmp_path, data)
    assert after == data.replace(b"setting ", b"settings ")
    assert b"&quot;x&quot;" in after


def test_a_cdata_body_stays_cdata(tmp_path: Path) -> None:
    data = task(f"<Relevance><![CDATA[{SETTING} and 1 < 2]]></Relevance>")
    assert fixed_once(tmp_path, data) == data.replace(b"setting ", b"settings ")


def test_a_body_split_by_cdata_mid_statement_is_fixed(tmp_path: Path) -> None:
    data = task('<Relevance>exists values of setting "x" of cl<![CDATA[ient]]></Relevance>')
    after = fixed_once(tmp_path, data)
    assert after == data.replace(b"setting ", b"settings ")


def test_an_actionscript_substitution_is_fixed(tmp_path: Path) -> None:
    data = task(
        '<DefaultAction ID="Action1">',
        '<ActionScript MIMEType="application/x-Fixlet-Windows-Shell">'
        f'parameter "v"="{{{SETTING}}}"</ActionScript>',
        "</DefaultAction>",
    )
    assert fixed_once(tmp_path, data) == data.replace(b"setting ", b"settings ")


def test_a_crlf_file_stays_crlf(tmp_path: Path) -> None:
    data = task('<Relevance>exists values of setting\n"x" of client</Relevance>', newline="\r\n")
    assert b"\r\n" in data
    after = fixed_once(tmp_path, data)
    assert after == data.replace(b"setting\r\n", b"settings\r\n")
    assert after.count(b"\r\n") == data.count(b"\r\n")
    assert b"\n" not in after.replace(b"\r\n", b"")


def test_the_same_statement_on_two_lines_is_fixed_and_reported_twice(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>", f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    result = fix_file(path, LintConfig())
    assert path.read_bytes() == data.replace(b"setting ", b"settings ")
    assert [fix.line for fix in result.applied] == [5, 6]


def test_two_identical_substitutions_on_one_line_are_both_fixed(tmp_path: Path) -> None:
    """Equal sites (same text, line, kind, context) are still two places."""
    data = task(
        '<DefaultAction ID="Action1">',
        '<ActionScript MIMEType="application/x-Fixlet-Windows-Shell">'
        f'parameter "v"="{{{SETTING}}}{{{SETTING}}}"</ActionScript>',
        "</DefaultAction>",
    )
    path = write(tmp_path, data)
    result = fix_file(path, LintConfig())
    assert path.read_bytes() == data.replace(b"setting ", b"settings ")
    assert len(result.applied) == 2


def test_an_ignored_rule_leaves_the_file_untouched(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    result = fix_file(path, LintConfig(severities={"plural-preferred": Severity.IGNORE}))
    assert path.read_bytes() == data
    assert not result.changed
    assert result.applied == () and result.unapplied == ()


def test_a_fix_with_an_ignored_rule_among_its_rules_is_not_applied(tmp_path: Path) -> None:
    """A site's fix is one result over all its edits: if any of them is under
    an ignored rule, none of it is applied."""
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    findings = lint_file(path, LintConfig())
    (finding,) = [f for f in findings if f.autofix is not None]
    assert finding.autofix is not None
    blocked = fixfile._ignored_rules(
        finding.autofix, LintConfig(severities={"plural-preferred": Severity.IGNORE})
    )
    assert blocked == ("plural-preferred",)


def test_a_re_extract_mismatch_restores_the_original_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    real = fixfile._extract

    def tampered(file_path: Path, contents: bytes) -> list[RelevanceSite]:
        sites = real(file_path, contents)
        if contents == data:
            return sites
        return [
            RelevanceSite(**{**{f: getattr(s, f) for f in s.__dataclass_fields__}, "text": "x"})
            for s in sites
        ]

    monkeypatch.setattr(fixfile, "_extract", tampered)
    result = fix_file(path, LintConfig())
    assert path.read_bytes() == data
    assert not result.changed
    assert result.applied == ()
    (unapplied,) = result.unapplied
    assert unapplied.reason == "re-extract mismatch"
    assert any(finding.code == "plural-preferred" for finding in result.findings)


# -- refusals ----------------------------------------------------------------------


def test_a_file_type_without_a_source_map_reports_the_fix_unapplied(tmp_path: Path) -> None:
    path = write(tmp_path, f"{SETTING}\n".encode(), name="t.rel")
    result = fix_file(path, LintConfig())
    assert path.read_text() == f"{SETTING}\n"
    assert not result.changed
    (unapplied,) = result.unapplied
    assert unapplied.reason is not None and "no source map" in unapplied.reason


def test_a_missing_file_is_a_file_error_not_an_exception(tmp_path: Path) -> None:
    result = fix_file(tmp_path / "nope.bes", LintConfig())
    assert [finding.code for finding in result.findings] == ["file-error"]
    assert not result.changed


def test_an_unparsable_file_is_left_alone(tmp_path: Path) -> None:
    path = write(tmp_path, b"<BES><Task><Relevance>" + SETTING.encode())
    result = fix_file(path, LintConfig())
    assert not result.changed and result.applied == ()


def test_an_unwritable_file_restores_nothing_and_reports_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)

    def refuse(_path: Path, _data: bytes) -> None:
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(fixfile, "_write", refuse)
    result = fix_file(path, LintConfig())
    assert path.read_bytes() == data
    assert not result.changed
    (unapplied,) = result.unapplied
    assert unapplied.reason is not None and "Permission denied" in unapplied.reason
    assert "file-error" in [finding.code for finding in result.findings]


# -- source_edits ------------------------------------------------------------------


def _site(data: bytes) -> RelevanceSite:
    (site,) = extract_relevance_from_bes_xml(data)
    return site


def _result(original: str, *edits: TextEdit) -> AutofixResult:
    from bigfix_relevance_analyzer.autofix import _apply

    return AutofixResult(original=original, fixed=_apply(original, edits), edits=edits)


def test_source_edits_map_each_edit_to_the_bytes_it_replaces() -> None:
    data = task("<Relevance>1 &lt; 2 and name of client</Relevance>")
    site = _site(data)
    start = site.text.index("client")
    edits = source_edits(site, _result(site.text, TextEdit(start, start + 6, "clients", "c")))
    assert isinstance(edits, tuple)
    (edit,) = edits
    assert isinstance(edit, ByteEdit)
    assert data[edit.start : edit.end] == b"client"
    assert edit.replacement == b"clients"


def test_source_edits_replace_an_entity_whole_but_never_with_markup() -> None:
    data = task("<Relevance>1 &lt; 2</Relevance>")
    site = _site(data)
    lt = site.text.index("<")
    result = source_edits(site, _result(site.text, TextEdit(lt, lt + 1, "=", "c")))
    assert isinstance(result, tuple)
    (edit,) = result
    assert data[edit.start : edit.end] == b"&lt;"
    for unsafe in ("&", "<", ">", '"', "'", "\r"):
        result = source_edits(site, _result(site.text, TextEdit(lt, lt + 1, unsafe, "c")))
        assert isinstance(result, Unmapped), unsafe
        assert "escap" in result.reason


def test_source_edits_refuse_an_edit_across_markup() -> None:
    site = _site(task("<Relevance>name of cl<![CDATA[ient]]></Relevance>"))
    start = site.text.index("client")
    result = source_edits(site, _result(site.text, TextEdit(start, start + 6, "clients", "c")))
    assert isinstance(result, Unmapped)


def test_source_edits_need_a_map() -> None:
    site = extract_relevance_from_bes_xml("<BES><Task><Relevance>true</Relevance></Task></BES>")[0]
    result = source_edits(site, _result("true", TextEdit(0, 4, "false", "c")))
    assert isinstance(result, Unmapped)
    assert "no source map" in result.reason


def test_source_edits_refuse_a_result_for_another_statement() -> None:
    site = _site(task("<Relevance>true</Relevance>"))
    result = source_edits(site, _result("false", TextEdit(0, 5, "true", "c")))
    assert isinstance(result, Unmapped)


# -- site_fixes, fix_paths and serialization ---------------------------------------


def test_site_fixes_gives_one_fix_per_site(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        task(
            '<Relevance>exists values of setting "x" of client and exists values of '
            'setting "y" of client</Relevance>'
        ),
    )
    findings = lint_file(path, LintConfig())
    assert sum(finding.autofix is not None for finding in findings) == 2
    (fix,) = site_fixes(findings)
    assert fix.autofix.applied == {"singular-spelling-mid-chain": 2}


def test_fix_paths_reports_every_file(tmp_path: Path) -> None:
    fixable = write(tmp_path, task(f"<Relevance>{SETTING}</Relevance>"), "a.bes")
    clean = write(tmp_path, task(f"<Relevance>{SETTINGS}</Relevance>"), "b.bes")
    result = fix_paths([fixable, clean, tmp_path / "missing.bes"], LintConfig())
    assert result.changed == (fixable,)
    assert [fix.path for fix in result.applied] == [fixable]
    assert [finding.code for finding in result.findings] == ["file-error"]


def test_fix_paths_to_dict_shape(tmp_path: Path) -> None:
    path = write(tmp_path, task(f"<Relevance>{SETTING}</Relevance>"))
    payload = fix_paths_to_dict([path], LintConfig())
    json.dumps(payload)
    assert payload["changed"] == [str(path)]
    assert payload["ok"] is True
    assert payload["counts"] == {"error": 0, "warning": 0}
    (applied,) = payload["applied"]
    assert applied["path"] == str(path)
    assert applied["line"] == 5
    assert applied["reason"] is None
    assert applied["autofix"]["fixed"] == SETTINGS
    assert applied["site"]["text"] == SETTING
    assert payload["unapplied"] == []
    assert payload["findings"] == []
