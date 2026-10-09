"""Tests for writing fixes back into files (:mod:`bigfix_relevance_analyzer.fixfile`).

The acceptance tests here are the behaviour the pre-commit-bigfix hook relies
on: a fix rewrites only the words it changes, every other byte of the file is
kept as written, and a second run has nothing left to do.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest
from _fix_cases import BOM, CASES, FixCase
from _helpers import REPO_ROOT, SETTING

from bigfix_relevance_analyzer import fixfile
from bigfix_relevance_analyzer.autofix import _SAFE_TEXT, AutofixResult, TextEdit
from bigfix_relevance_analyzer.extract import (
    RelevanceSite,
    _ExtractionProblem,
    extract_relevance_from_bes_xml,
)
from bigfix_relevance_analyzer.fixfile import (
    ByteEdit,
    Unmapped,
    fix_file,
    fix_paths,
    fix_paths_to_dict,
    plan_fix,
    site_fixes,
    source_edits,
    write_fix,
)
from bigfix_relevance_analyzer.lint import Finding, LintConfig, Severity, lint_file

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


def fixed_once(
    tmp_path: Path, data: bytes, config: LintConfig | None = None, name: str = "t.bes"
) -> bytes:
    """Fix ``data`` as a file, check a second run changes nothing, return the bytes."""
    path = write(tmp_path, data, name)
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


def test_an_unclosed_action_brace_is_still_reported_after_a_fix(tmp_path: Path) -> None:
    """A problem from extraction is not a site, so it neither blocks the fix nor
    gets lost in the re-lint: `--fix` must not print a cleaner result than lint."""
    data = task(
        f"<Relevance>{SETTING}</Relevance>",
        '<DefaultAction ID="Action1">',
        "<ActionScript>x { name of operating system</ActionScript>",
        "</DefaultAction>",
    )
    path = write(tmp_path, data)
    result = fix_file(path, LintConfig())
    assert result.changed
    assert path.read_bytes() == data.replace(b"setting ", b"settings ")
    unclosed = [f for f in result.findings if f.code == "unterminated-substitution"]
    assert [(f.line, f.severity) for f in unclosed] == [(7, Severity.ERROR)]


def test_an_unclosed_action_brace_is_reported_when_there_is_nothing_to_fix(
    tmp_path: Path,
) -> None:
    data = task(
        '<DefaultAction ID="Action1">',
        "<ActionScript>x {   </ActionScript>",
        "</DefaultAction>",
    )
    result = fix_file(write(tmp_path, data), LintConfig())
    assert not result.changed
    assert [f.line for f in result.findings if f.code == "unterminated-substitution"] == [6]


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
    (finding,) = (f for f in findings if f.autofix is not None)
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

    def tampered(
        file_path: Path, contents: bytes
    ) -> tuple[list[RelevanceSite], list[_ExtractionProblem]]:
        sites, problems = real(file_path, contents)
        if contents == data:
            return sites, problems
        return [
            RelevanceSite(**{**{f: getattr(s, f) for f in s.__dataclass_fields__}, "text": "x"})
            for s in sites
        ], problems

    monkeypatch.setattr(fixfile, "_extract", tampered)
    result = fix_file(path, LintConfig())
    assert path.read_bytes() == data
    assert not result.changed
    assert result.applied == ()
    (unapplied,) = result.unapplied
    assert unapplied.reason == "re-extract mismatch"
    assert any(finding.code == "plural-preferred" for finding in result.findings)


# -- refusals ----------------------------------------------------------------------


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


def test_source_edits_map_each_edit_to_the_bytes_it_changes() -> None:
    """Minimal since #115: `client` -> `clients` inserts `s`, rather than
    rewriting the name whole."""
    data = task("<Relevance>1 &lt; 2 and name of client</Relevance>")
    site = _site(data)
    start = site.text.index("client")
    edits = source_edits(site, _result(site.text, TextEdit(start, start + 6, "clients", "c")))
    assert isinstance(edits, tuple)
    (edit,) = edits
    assert isinstance(edit, ByteEdit)
    assert edit.start == edit.end == data.index(b"client<") + len(b"client")
    assert edit.replacement == b"s"


def test_source_edits_replace_an_entity_whole_but_never_with_markup() -> None:
    data = task("<Relevance>1 &lt; 2</Relevance>")
    site = _site(data)
    lt = site.text.index("<")
    result = source_edits(site, _result(site.text, TextEdit(lt, lt + 1, "x", "c")))
    assert isinstance(result, tuple)
    (edit,) = result
    assert data[edit.start : edit.end] == b"&lt;"
    assert edit.replacement == b"x"
    for unsafe in ("&", ">", '"', "'", "\r", "=", "]]>"):
        result = source_edits(site, _result(site.text, TextEdit(lt, lt + 1, unsafe, "c")))
        assert isinstance(result, Unmapped), unsafe
        assert "escap" in result.reason
        assert repr(unsafe)[1:-1] in result.reason


def test_source_edits_refuse_a_replacement_across_markup() -> None:
    site = _site(task("<Relevance>name of cl<![CDATA[ient]]></Relevance>"))
    start = site.text.index("client")
    result = source_edits(site, _result(site.text, TextEdit(start, start + 6, "zzzzzz", "c")))
    assert isinstance(result, Unmapped)
    assert "split by an entity or markup" in result.reason


def test_source_edits_insert_after_a_name_split_by_markup() -> None:
    data = task("<Relevance>name of cl<![CDATA[ient]]></Relevance>")
    site = _site(data)
    start = site.text.index("client")
    result = source_edits(site, _result(site.text, TextEdit(start, start + 6, "clients", "c")))
    assert isinstance(result, tuple)
    (edit,) = result
    assert edit.start == edit.end
    assert fixfile._splice(data, result) == data.replace(b"ient]]>", b"ients]]>")


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


# -- minimal edits, for every file type (#115) -------------------------------------
#
# The hazard tests check the bytes written, so a later "simplification" back to
# whole replacements -- which un-escapes what the author escaped -- fails them.


def _plan_of(path: Path, config: LintConfig | None = None) -> fixfile.FixPlan:
    return fixfile.plan_fix(path, config or LintConfig())


def _assert_only_new_text_inserted(plan: fixfile.FixPlan) -> None:
    """Every byte the plan writes is new, safe text; nothing else moves."""
    assert plan.edits, "nothing planned"
    assert fixfile._splice(plan.original, plan.edits) == plan.fixed
    for edit in plan.edits:
        assert _SAFE_TEXT.fullmatch(edit.replacement.decode("ascii")), edit


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_every_hazard_is_fixed_with_only_new_text_inserted(tmp_path: Path, case: FixCase) -> None:
    """Entities, CDATA, escaped quotes, line endings and the BOM stay as written;
    the bytes are the input with only the pieces inserted; a second run changes
    nothing."""
    plan = _plan_of(write(tmp_path, case.data, case.name))
    assert [fix.reason for fix in plan.unapplied] == []
    assert len(plan.applied) == case.sites
    _assert_only_new_text_inserted(plan)
    assert plan.fixed == case.fixed
    (tmp_path / "again").mkdir()
    assert fixed_once(tmp_path / "again", case.data, name=case.name) == case.fixed


def test_a_bes_wrap_over_lt_keeps_the_file_well_formed(tmp_path: Path) -> None:
    """The corruption case if a wrap were ever written whole: `<` un-escaped."""
    (case,) = (case for case in CASES if case.id == "bes-wrap-over-lt")
    path = write(tmp_path, case.data)
    result = fix_file(path, LintConfig())
    assert result.changed
    assert b"&lt; 5" in path.read_bytes()
    assert "xml-parse-error" not in [finding.code for finding in lint_file(path, LintConfig())]
    (site,) = extract_relevance_from_bes_xml(path.read_bytes())
    assert site.text.startswith("unique value of pathnames of files whose (size of it < 5)")


def test_a_bes_merged_wrap_and_respelling_is_exactly_two_insertions(tmp_path: Path) -> None:
    (case,) = (case for case in CASES if case.id == "bes-merged-wrap-and-respelling")
    plan = _plan_of(write(tmp_path, case.data))
    assert [(edit.end - edit.start, edit.replacement) for edit in plan.edits] == [
        (0, b"unique value of "),
        (0, b"s"),
    ]


def test_an_astral_character_before_the_fix_is_four_bytes(tmp_path: Path) -> None:
    (case,) = (case for case in CASES if case.id == "rel-astral-before-the-fix-crlf")
    plan = _plan_of(write(tmp_path, case.data, case.name))
    (edit,) = plan.edits
    assert edit.start == case.data.index(b"setting ") + len(b"setting")


def test_undecodable_bytes_refuse_only_the_site_on_their_line(tmp_path: Path) -> None:
    data = (
        b'```relevance\nexists values of setting "\xff" of client\n```\n\n'
        b"```relevance\n/* \xfe */ true\n"
        b'and exists values of setting "y" of client\n```\n'
    )
    path = write(tmp_path, data, "t.md")
    result = fix_file(path, LintConfig())
    assert result.changed
    (applied,) = result.applied
    assert applied.line == 6
    (unapplied,) = result.unapplied
    assert unapplied.line == 2
    assert unapplied.reason == "undecodable bytes on line 2"
    assert path.read_bytes() == data.replace(b'setting "y"', b'settings "y"')


def test_undecodable_bytes_on_another_line_do_not_stop_the_fix(tmp_path: Path) -> None:
    data = b"/* \xff */ true and\n" + SETTING.encode() + b"\n"
    assert fixed_once(tmp_path, data, name="t.rel") == data.replace(b"setting ", b"settings ")


def test_a_bom_file_planned_from_a_buffer_without_the_bom(tmp_path: Path) -> None:
    """VS Code strips the BOM from its buffer and keeps it on disk (#107). The
    editor plans against the buffer's bytes, so the edits are offsets into those
    bytes, not the file's -- and the file is never read or written."""
    (case,) = (case for case in CASES if case.id == "rel-bom-line-1")
    path = write(tmp_path, case.data, case.name)
    buffer = case.data.removeprefix(BOM)
    plan = fixfile._plan(path, buffer, LintConfig())
    assert plan.original == buffer
    assert plan.fixed == case.fixed.removeprefix(BOM)
    (edit,) = plan.edits
    assert edit.start == buffer.index(b"setting ") + len(b"setting")
    assert path.read_bytes() == case.data


def test_source_edits_on_a_text_site_need_the_files_bytes(tmp_path: Path) -> None:
    path = write(tmp_path, f"{SETTING}\n".encode(), "t.rel")
    (finding,) = (f for f in lint_file(path, LintConfig()) if f.autofix is not None)
    assert finding.site is not None and finding.autofix is not None
    result = source_edits(finding.site, finding.autofix)
    assert isinstance(result, Unmapped)
    assert "pass the file's bytes" in result.reason
    mapped = source_edits(finding.site, finding.autofix, path.read_bytes())
    assert mapped == (ByteEdit(24, 24, b"s"),)


def test_source_edits_refuse_unsafe_text_in_a_text_file(tmp_path: Path) -> None:
    data = f"{SETTING}\n".encode()
    path = write(tmp_path, data, "t.rel")
    (site,) = (f.site for f in lint_file(path, LintConfig()) if f.autofix is not None)
    assert site is not None
    start = site.text.index('"x"')
    result = source_edits(site, _result(site.text, TextEdit(start, start, '"', "c")), data)
    assert isinstance(result, Unmapped)
    assert result.reason == "text '\"' would need escaping"


def test_source_edits_refuse_a_column_that_reads_back_wrong(tmp_path: Path) -> None:
    """A site whose column points at other text is never written: wrong bytes
    are worse than no fix."""
    data = f"  {SETTING}\n".encode()
    path = write(tmp_path, data, "t.rel")
    (finding,) = (f for f in lint_file(path, LintConfig()) if f.autofix is not None)
    assert finding.site is not None and finding.site.column == 3
    assert finding.autofix is not None
    moved = dataclasses.replace(finding.site, column=2)
    result = source_edits(moved, finding.autofix, data)
    assert isinstance(result, Unmapped)
    assert result.reason == "'setting' does not read back at line 1"


# -- plan, then write (#115 A2) ----------------------------------------------------


def test_plan_fix_never_writes(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    stamp = path.stat().st_mtime_ns
    plan = plan_fix(path, LintConfig())
    assert path.read_bytes() == data and path.stat().st_mtime_ns == stamp
    assert plan.path == path and plan.original == data and plan.changed
    assert plan.fixed == data.replace(b"setting ", b"settings ")
    assert not any(f.code == "plural-preferred" for f in plan.findings)
    assert any(f.code == "plural-preferred" for f in plan.original_findings)
    fix_file(path, LintConfig())
    assert path.read_bytes() == plan.fixed


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_fix_file_is_write_fix_of_plan_fix(tmp_path: Path, case: FixCase) -> None:
    path = write(tmp_path, case.data, case.name)
    by_fix_file = fix_file(path, LintConfig())
    path.write_bytes(case.data)
    by_plan = write_fix(plan_fix(path, LintConfig()))
    assert by_plan == by_fix_file
    assert path.read_bytes() == case.fixed


def test_an_unchanged_plan_writes_nothing(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTINGS}</Relevance>")
    path = write(tmp_path, data)
    plan = plan_fix(path, LintConfig())
    assert not plan.changed and plan.fixed == plan.original == data and plan.edits == ()
    assert plan.findings == plan.original_findings
    path.unlink()  # write_fix must not even look
    result = write_fix(plan)
    assert not result.changed and result.applied == ()


def test_plan_fix_reports_a_missing_file(tmp_path: Path) -> None:
    plan = plan_fix(tmp_path / "nope.rel", LintConfig())
    assert not plan.changed
    assert [finding.code for finding in plan.findings] == ["file-error"]


def test_plan_reads_the_bytes_it_is_given_not_the_disk(tmp_path: Path) -> None:
    """The editor plans its open buffer, which may differ from the saved file."""
    path = write(tmp_path, b"true\n", "t.rel")
    buffer = b"true and\n" + SETTING.encode() + b"\n"
    plan = fixfile._plan(path, buffer, LintConfig())
    assert plan.original == buffer
    assert plan.fixed == buffer.replace(b"setting ", b"settings ")
    assert path.read_bytes() == b"true\n"


def test_plan_only_the_anchored_site(tmp_path: Path) -> None:
    """One editor quick fix: that site's bytes change, the other site stays
    as written and still fixable, and the whole-file checks still run."""
    (case,) = (case for case in CASES if case.id == "md-two-fences-from-line-3")
    path = write(tmp_path, case.data, case.name)
    sites, _ = fixfile._extract(path, case.data)
    first, second = sites
    plan = fixfile._plan(path, case.data, LintConfig(), only={fixfile._site_anchor(second)})
    assert [fix.line for fix in plan.applied] == [second.line]
    assert plan.unapplied == ()
    head, tail = case.data.split(b"```\n\n", 1)
    assert plan.fixed == head + b"```\n\n" + tail.replace(b"setting ", b"settings ")
    rest = fixfile._plan(path, plan.fixed, LintConfig())
    assert [fix.line for fix in rest.applied] == [first.line]
    assert rest.fixed == case.fixed


def test_plan_only_still_checks_the_whole_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (case,) = (case for case in CASES if case.id == "md-two-fences-from-line-3")
    path = write(tmp_path, case.data, case.name)
    sites, _ = fixfile._extract(path, case.data)
    real = fixfile._extract

    def lose_the_other_site(
        file_path: Path, contents: bytes
    ) -> tuple[list[RelevanceSite], list[_ExtractionProblem]]:
        found, problems = real(file_path, contents)
        return (found if contents == case.data else found[1:]), problems

    monkeypatch.setattr(fixfile, "_extract", lose_the_other_site)
    plan = fixfile._plan(path, case.data, LintConfig(), only={fixfile._site_anchor(sites[1])})
    assert not plan.changed
    assert [fix.reason for fix in plan.unapplied] == ["re-extract mismatch"]


def test_plan_uses_the_judge_it_is_given(tmp_path: Path) -> None:
    """So the language server's per-site findings cache is honoured."""
    from bigfix_relevance_analyzer.lint import _judge_site

    calls: list[str] = []

    def counting(
        file_path: Path | None, site: RelevanceSite, config: LintConfig
    ) -> tuple[Finding, ...]:
        calls.append(site.text)
        return _judge_site(file_path, site, config)

    data = f"{SETTING}\n".encode()
    plan = fixfile._plan(write(tmp_path, data, "t.rel"), data, LintConfig(), judge=counting)
    assert plan.changed
    assert calls == [SETTING, SETTINGS]  # the original, then the fixed bytes


def test_write_fix_refuses_a_file_changed_since_it_was_planned(tmp_path: Path) -> None:
    data = task(f"<Relevance>{SETTING}</Relevance>")
    path = write(tmp_path, data)
    plan = plan_fix(path, LintConfig())
    edited = data.replace(b"<Title>t</Title>", b"<Title>edited</Title>")
    path.write_bytes(edited)
    result = write_fix(plan)
    assert path.read_bytes() == edited
    assert not result.changed and result.applied == ()
    (unapplied,) = result.unapplied
    assert unapplied.reason == "file changed since it was planned"
    assert any(f.code == "plural-preferred" for f in result.findings)


def test_a_fix_that_would_add_a_finding_is_refused(tmp_path: Path) -> None:
    """`unique value of` raises the score: 12 before, 20 after. With the ceiling
    between the two, the fix would trade a warning for an error."""
    data = b'pathnames of files "x" | "y"\n'
    path = write(tmp_path, data, "t.rel")
    config = LintConfig(max_score=15)
    assert not any(f.code == "complexity" for f in lint_file(path, config))
    result = fix_file(path, config)
    assert path.read_bytes() == data
    assert not result.changed
    (unapplied,) = result.unapplied
    assert unapplied.reason == "the fix would add a complexity finding"
    assert fix_file(path, LintConfig()).changed  # the default ceiling allows it


def test_planning_a_text_file_never_reads_it_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The fixed bytes are re-extracted from memory, for every type."""
    from bigfix_relevance_analyzer import extract

    path = write(tmp_path, f"{SETTING}\n".encode(), "t.rel")

    def no_disk(file_path: Path) -> None:
        raise AssertionError(f"read {file_path} from disk while planning")

    monkeypatch.setattr(extract, "_extract_file", no_disk)
    if hasattr(fixfile, "_extract_file"):
        monkeypatch.setattr(fixfile, "_extract_file", no_disk)
    assert plan_fix(path, LintConfig()).changed


def test_every_example_fix_is_applied_and_idempotent(tmp_path: Path) -> None:
    """Real content: tests/examples holds 5 fixable sites. Every one goes in,
    with nothing but new text inserted, and a second run has nothing to do."""
    from _corpus import corpus_files

    applied = 0
    for source in corpus_files():
        target = tmp_path / source.relative_to(REPO_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        plan = plan_fix(target, LintConfig())
        assert plan.unapplied == (), [fix.reason for fix in plan.unapplied]
        if plan.changed:
            _assert_only_new_text_inserted(plan)
            applied += len(plan.applied)
            write_fix(plan)
            assert not plan_fix(target, LintConfig()).changed
    assert applied == 5


# -- site anchors: telling equal sites apart across extractions (#115, #113) --------


@pytest.mark.parametrize(
    ("name", "data"),
    [
        (
            "t.bes",
            task(
                '<DefaultAction ID="Action1">',
                '<ActionScript MIMEType="application/x-Fixlet-Windows-Shell">'
                f'parameter "v"="{{{SETTING}}}{{{SETTING}}}"</ActionScript>',
                "</DefaultAction>",
            ),
        ),
        (
            "t.ojo",
            b"<p><?Relevance names of bes computers ?> <?Relevance names of bes computers ?></p>\n",
        ),
        ("t.md", b"```relevance\ntrue\n```\n\n```relevance\ntrue\n```\n"),
    ],
    ids=["bes-twin-substitutions", "ojo-twin-pis", "md-twin-fences"],
)
def test_site_anchors_are_stable_and_tell_equal_sites_apart(name: str, data: bytes) -> None:
    sites, _ = fixfile._extract(Path(name), data)
    again, _ = fixfile._extract(Path(name), data)
    first, second = sites
    assert (first.kind, first.text) == (second.kind, second.text)
    anchors = [fixfile._site_anchor(site) for site in sites]
    assert anchors[0] != anchors[1]
    assert anchors == [fixfile._site_anchor(site) for site in again]
    hash(anchors[0])
