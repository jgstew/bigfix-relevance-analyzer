"""Tests for quick fixes in the editor: :meth:`DocumentLinter.fixes` (#113).

Whether a fix is safe, and which bytes it writes, is decided once in
:mod:`~bigfix_relevance_analyzer.fixfile` (#115), and its tests pin the bytes.
These pin that the editor applies the same bytes at the right positions: each
test applies an action's edits to the buffer, as an editor would, and checks
the text that results. :mod:`test_lsp` covers ``textDocument/codeAction``.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pytest
from _fix_cases import BOM, CASES, FixCase

from bigfix_relevance_analyzer import fixfile
from bigfix_relevance_analyzer.extract import _extract_data
from bigfix_relevance_analyzer.lint import LintConfig, Severity
from bigfix_relevance_analyzer.lsp import linter as linter_module
from bigfix_relevance_analyzer.lsp.linter import (
    FIX_ALL_KIND,
    QUICKFIX_KIND,
    DocumentFix,
    DocumentLinter,
)

SETTING = 'exists values of setting "x" of client'
SETTINGS = 'exists values of settings "x" of client'
WHOLE = ((0, 0), (10_000, 0))
"""A request range covering any test document."""

_LINE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+\Z")


def uri(name: str) -> str:
    return f"file:///workspace/{name}"


def _offset(text: str, line: int, character: int) -> int:
    """The index in ``text`` of LSP position ``(line, character)``, UTF-16 counted."""
    lines = _LINE.findall(text) or [""]
    start = sum(len(written) for written in lines[:line])
    units = 0
    for index, char in enumerate(text[start:]):
        if units == character:
            return start + index
        units += 2 if ord(char) > 0xFFFF else 1
    assert units == character
    return len(text)


def apply(text: str, fix: DocumentFix) -> str:
    """``text`` with ``fix``'s edits applied, right to left, as an editor does."""
    edits = sorted(
        ((_offset(text, *start), _offset(text, *end), new) for (start, end), new in fix.edits),
        reverse=True,
    )
    for start, end, new in edits:
        text = text[:start] + new + text[end:]
    return text


Range = tuple[tuple[int, int], tuple[int, int]]


def fixes(
    name: str,
    text: str,
    linter: DocumentLinter | None = None,
    *,
    range: Range | None = WHOLE,
    only: list[str] | None = None,
) -> list[DocumentFix]:
    return (linter or DocumentLinter()).fixes(uri(name), text, range=range, only=only)


def quick_fixes(name: str, text: str, linter: DocumentLinter | None = None) -> list[DocumentFix]:
    """The per-statement quick fixes: kind ``quickfix``, not the fix-all entry."""
    return [
        fix for fix in fixes(name, text, linter) if fix.kind == QUICKFIX_KIND and fix.is_preferred
    ]


def decoded(case: FixCase) -> tuple[str, str]:
    """A case as an editor buffer: text, without the BOM VS Code strips."""
    return case.data.removeprefix(BOM).decode(), case.fixed.removeprefix(BOM).decode()


# -- the same bytes as --fix, at the right positions -------------------------------


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_every_hazard_gives_the_bytes_fix_file_writes(case: FixCase) -> None:
    """Every action, applied one at a time, then fix-all: both give #115's bytes.

    The BOM case is planned as VS Code holds it, without the BOM (#107)."""
    text, expected = decoded(case)
    per_site = quick_fixes(case.name, text)
    assert len(per_site) == case.sites
    result = text
    for _ in range(case.sites):
        (first, *_) = quick_fixes(case.name, result)
        result = apply(result, first)
    assert result == expected
    (fix_all,) = (fix for fix in fixes(case.name, text) if fix.kind == FIX_ALL_KIND)
    assert apply(text, fix_all) == expected


def test_a_bes_wrap_over_lt_keeps_the_entity_and_parses() -> None:
    (case,) = (case for case in CASES if case.id == "bes-wrap-over-lt")
    text, _ = decoded(case)
    (fix,) = quick_fixes(case.name, text)
    after = apply(text, fix)
    assert "&lt; 5" in after
    sites, problems = _extract_data(Path("t.bes"), after.encode())
    assert not problems
    (site,) = sites
    assert site.text.startswith("unique value of pathnames of files whose (size of it < 5)")


def test_a_name_split_by_cdata_keeps_the_cdata() -> None:
    (case,) = (case for case in CASES if case.id == "bes-name-split-by-cdata")
    text, expected = decoded(case)
    (fix,) = quick_fixes(case.name, text)
    assert apply(text, fix) == expected
    assert "<![CDATA[ing]]>s" in expected


def test_escaped_javascript_quotes_are_untouched() -> None:
    (case,) = (case for case in CASES if case.id == "html-js-call-escaped-quotes")
    text, expected = decoded(case)
    (fix,) = quick_fixes(case.name, text)
    assert apply(text, fix) == expected
    assert expected.count('\\"') == 2


def test_an_astral_character_before_the_fix_counts_two_utf16_units() -> None:
    (case,) = (case for case in CASES if case.id == "rel-astral-before-the-fix-crlf")
    text, _ = decoded(case)
    (fix,) = quick_fixes(case.name, text)
    (((line, character), end), new) = fix.edits[0]
    assert (line, new) == (0, "s")
    assert end == (line, character)
    assert character == text.index("setting ") + len("setting") + 1


def test_two_fences_get_independent_actions() -> None:
    (case,) = (case for case in CASES if case.id == "md-two-fences-from-line-3")
    text, _ = decoded(case)
    first, second = quick_fixes(case.name, text)
    assert first.edits != second.edits
    once = apply(text, first)
    assert once.count(SETTINGS) == 1
    (remaining,) = quick_fixes(case.name, once)
    assert apply(once, remaining).count(SETTINGS) == 2


def test_the_same_statement_twice_on_one_line_gets_two_actions() -> None:
    (case,) = (case for case in CASES if case.id == "ojo-two-identical-pis-on-one-line")
    text, _ = decoded(case)
    first, second = quick_fixes(case.name, text)
    assert first.edits != second.edits
    assert first.diagnostics != second.diagnostics


def test_fix_all_plans_the_whole_file_once(monkeypatch: pytest.MonkeyPatch) -> None:
    (case,) = (case for case in CASES if case.id == "md-two-fences-from-line-3")
    text, expected = decoded(case)
    calls: list[object] = []
    real = fixfile._plan

    def counting(*args: object, **kwargs: object) -> object:
        calls.append(kwargs.get("only"))
        return real(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(linter_module, "_plan", counting)
    (fix_all,) = fixes(case.name, text, only=[FIX_ALL_KIND])
    assert fix_all.kind == FIX_ALL_KIND
    assert fix_all.title == "Fix all safe issues in this file"
    assert apply(text, fix_all) == expected
    assert calls == [None]


def test_the_buffer_is_fixed_not_the_file_on_disk(tmp_path: Path) -> None:
    """Planning the open buffer: `_plan(path, data)`, never `plan_fix(path)`."""
    path = tmp_path / "t.rel"
    path.write_text("true\n")
    buffer = f"true and\n{SETTING}\n"
    (fix,) = (
        fix
        for fix in DocumentLinter().fixes(path.as_uri(), buffer, range=WHOLE)
        if fix.kind == QUICKFIX_KIND
    )
    assert apply(buffer, fix) == f"true and\n{SETTINGS}\n"
    assert path.read_text() == "true\n"


def test_a_plan_fixfile_refuses_gives_no_action_and_logs_why(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """`pathnames of files "x" | "y"` scores 12, its wrap 20: over a ceiling of 15."""
    linter = DocumentLinter(config=LintConfig(suggest=True, max_score=15))
    with caplog.at_level(logging.DEBUG, logger=linter_module.__name__):
        found = fixes("t.rel", 'pathnames of files "x" | "y"\n', linter)
    assert found == []
    assert "the fix would add a complexity finding" in caplog.text


def test_an_ignored_rule_gives_no_action() -> None:
    linter = DocumentLinter(
        config=LintConfig(suggest=True, severities={"plural-preferred": Severity.IGNORE})
    )
    assert fixes("t.rel", f"{SETTING}\n", linter) == []


def test_an_oversized_document_gives_no_actions() -> None:
    linter = DocumentLinter(max_document_bytes=10)
    assert fixes("t.rel", f"{SETTING}\n", linter) == []


def test_an_unrecognized_document_gives_no_actions() -> None:
    assert fixes("t.txt", f"{SETTING}\n") == []


def test_no_fixable_diagnostic_in_range_means_no_planning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cursor moves ask for actions constantly: the cheap path never plans."""

    def never(*args: object, **kwargs: object) -> object:
        raise AssertionError("planned with nothing fixable in range")

    monkeypatch.setattr(linter_module, "_plan", never)
    text = f"true and\n{SETTING}\n"
    assert fixes("t.rel", text, range=((0, 0), (0, 4))) == []
    assert fixes("t.rel", "true\n") == []


def test_a_cursor_on_the_diagnostic_gets_its_fix() -> None:
    text = f"true and\n{SETTING}\n"
    column = SETTING.index("setting") + 2
    fix, fix_all = fixes("t.rel", text, range=((1, column), (1, column)))
    assert fix.kind == QUICKFIX_KIND and fix.is_preferred
    assert fix_all.kind == FIX_ALL_KIND
    assert apply(text, fix) == f"true and\n{SETTINGS}\n"


# -- what an action says ---------------------------------------------------------------


def test_a_respelling_is_titled_with_both_spellings() -> None:
    (fix,) = quick_fixes("t.rel", f"{SETTING}\n")
    assert fix.title == "Change `setting` to `settings`"


def test_a_wrap_is_titled_as_one() -> None:
    (fix,) = quick_fixes("t.rel", 'pathnames of files "x" | "y"\n')
    assert fix.title == "Wrap in `unique value of`"


def test_several_edits_are_counted() -> None:
    text = 'number of names of files of folder "etc" of folder "private" of folder "/"\n'
    (fix,) = quick_fixes("t.rel", text)
    assert fix.title == "Apply 2 safe fixes to this statement"


def test_an_actions_diagnostics_are_the_published_ones() -> None:
    linter = DocumentLinter()
    text = 'exists values of setting "x" of client or exists values of setting "y" of client\n'
    published = [
        d for d in linter.diagnostics(uri("t.rel"), text) if d["code"] == "plural-preferred"
    ]
    (fix,) = quick_fixes("t.rel", text, linter)
    assert list(fix.diagnostics) == published
    assert len(published) == 2


def test_fix_all_joins_the_lightbulb_only_with_two_or_more_fixable_sites() -> None:
    one = fixes("t.rel", f"{SETTING}\n")
    assert [fix.kind for fix in one] == [QUICKFIX_KIND, FIX_ALL_KIND]
    (case,) = (case for case in CASES if case.id == "md-two-fences-from-line-3")
    text, _ = decoded(case)
    two = fixes(case.name, text)
    assert [(fix.kind, fix.is_preferred) for fix in two] == [
        (QUICKFIX_KIND, True),
        (QUICKFIX_KIND, True),
        (QUICKFIX_KIND, False),
        (FIX_ALL_KIND, False),
    ]
    assert two[2].title == two[3].title == "Fix all safe issues in this file"
    assert two[2].edits == two[3].edits


def test_only_filters_by_kind_prefix() -> None:
    text = f"{SETTING}\n"
    assert [fix.kind for fix in fixes("t.rel", text, only=["source.fixAll"])] == [FIX_ALL_KIND]
    assert [fix.kind for fix in fixes("t.rel", text, only=["source"])] == [FIX_ALL_KIND]
    assert [fix.kind for fix in fixes("t.rel", text, only=["quickfix"])] == [QUICKFIX_KIND]
    assert fixes("t.rel", text, only=["refactor"]) == []


def test_fix_all_on_save_ignores_the_range() -> None:
    """Save sends `only: ["source.fixAll"]`; the fix is for the file, wherever it is."""
    text = f"true and\n{SETTING}\n"
    (fix,) = fixes("t.rel", text, range=((0, 0), (0, 0)), only=["source.fixAll"])
    assert apply(text, fix) == f"true and\n{SETTINGS}\n"


def test_fixes_are_cached_per_document_text(monkeypatch: pytest.MonkeyPatch) -> None:
    linter = DocumentLinter()
    text = f"{SETTING}\n"
    first = fixes("t.rel", text, linter)
    calls: list[object] = []
    real = fixfile._plan

    def counting(*args: object, **kwargs: object) -> object:
        calls.append(kwargs.get("only"))
        return real(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(linter_module, "_plan", counting)
    assert fixes("t.rel", text, linter) == first
    assert calls == []
    fixes("t.rel", f"true and {SETTING}\n", linter)
    assert calls
    linter.forget(uri("t.rel"))
    calls.clear()
    fixes("t.rel", text, linter)
    assert calls


# -- golden: every action over the examples and the hazards ---------------------------

GOLDEN = Path(__file__).parent / "golden" / "lsp_code_actions.json"


def _golden_documents() -> list[tuple[str, str]]:
    """``(name, buffer)`` for every example with a fix, then every hazard case."""
    from _corpus import EXAMPLES, corpus_files

    documents = []
    for path in corpus_files():
        try:
            text = path.read_bytes().removeprefix(BOM).decode("utf-8")
        except UnicodeDecodeError:
            continue
        if fixes(path.name, text):
            documents.append((path.relative_to(EXAMPLES).as_posix(), text))
    return documents + [(f"{case.id}/{case.name}", decoded(case)[0]) for case in CASES]


def test_every_action_is_pinned_and_round_trips() -> None:
    """Title, kind, ranges and new text of every action; each applied leaves its
    statement with nothing to fix, and fix-all leaves the file with nothing."""
    import json

    from _helpers import golden_text

    pinned: dict[str, list[dict[str, object]]] = {}
    sites = 0
    for name, text in _golden_documents():
        found = fixes(name.rsplit("/", 1)[-1], text)
        pinned[name] = [
            {
                "title": fix.title,
                "kind": fix.kind,
                "preferred": fix.is_preferred,
                "edits": [[list(start), list(end), new] for (start, end), new in fix.edits],
            }
            for fix in found
        ]
        per_site = [fix for fix in found if fix.is_preferred]
        sites += len(per_site)
        for fix in per_site:
            after = apply(text, fix)
            assert len(quick_fixes(name.rsplit("/", 1)[-1], after)) == len(per_site) - 1, name
        (fix_all,) = (fix for fix in found if fix.kind == FIX_ALL_KIND)
        assert fixes(name.rsplit("/", 1)[-1], apply(text, fix_all)) == [], name
    assert sites >= 5 + sum(case.sites for case in CASES)
    actual = json.dumps(pinned, indent=1, ensure_ascii=True) + "\n"
    assert actual == golden_text(GOLDEN, actual)


# -- review of #125 -------------------------------------------------------------------

PARTLY_FIXABLE = (
    '```relevance\npathnames of files "x" | "y"\n```\n\n'  # a wrap: score 12 -> 20
    f"```relevance\n{SETTING}\n```\n"
)


def test_fix_all_reports_only_the_sites_it_applies() -> None:
    """With the wrap over the ceiling, fix-all only respells: it must not claim
    the wrap's diagnostic, and with one site left there is no second-choice
    "Fix all" beside that site's own fix."""
    linter = DocumentLinter(config=LintConfig(suggest=True, max_score=15))
    found = fixes("t.md", PARTLY_FIXABLE, linter)
    assert [(fix.kind, fix.is_preferred) for fix in found] == [
        (QUICKFIX_KIND, True),
        (FIX_ALL_KIND, False),
    ]
    quick, fix_all = found
    assert quick.title == "Change `setting` to `settings`"
    assert {d["code"] for d in fix_all.diagnostics} == {"plural-preferred"}
    assert fix_all.diagnostics == quick.diagnostics
    assert apply(PARTLY_FIXABLE, fix_all) == PARTLY_FIXABLE.replace("setting ", "settings ")


def test_no_fix_all_when_the_whole_file_plan_applies_nothing() -> None:
    linter = DocumentLinter(config=LintConfig(suggest=True, max_score=15))
    text = '```relevance\npathnames of files "x" | "y"\n```\n'
    assert fixes("t.md", text, linter) == []
    assert fixes("t.md", text, linter, only=["source.fixAll"]) == []
