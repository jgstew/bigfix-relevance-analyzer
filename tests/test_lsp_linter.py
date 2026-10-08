"""Tests for :class:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter`: the seam.

Everything an editor needs from the analyzer, with no protocol in it. The
hand-rolled :class:`~bigfix_relevance_analyzer.lsp.server.Server` is one adapter
over it; a pygls server would be another. These tests call it the way any
adapter does -- a URI and the buffer's text in, LSP-shaped diagnostics out --
so they hold for whichever protocol layer sits on top.

:mod:`test_lsp` covers the same behaviour end to end through the protocol.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pytest
from _helpers import (
    BES_EXAMPLE,
    BROKEN,
    CLIENT,
    UNKNOWN_INSPECTOR,
    diagnostic_text,
    lsp_lines,
    run_fresh_python,
    write,
)

from bigfix_relevance_analyzer.lint import LintConfig, Severity, lint_file, lint_text
from bigfix_relevance_analyzer.lsp.linter import (
    DEFAULT_MAX_DOCUMENT_BYTES,
    DOCUMENT_TOO_LARGE,
    SOURCE,
    DocumentLinter,
)

URI = "file:///workspace/doc.md"
TWO_SITES = f"```relevance\n{UNKNOWN_INSPECTOR}\n```\n\n```relevance\n{BROKEN}\n```\n"


def span_range(line: int, start: int, end_line: int, end: int) -> dict[str, Any]:
    return {
        "start": {"line": line, "character": start},
        "end": {"line": end_line, "character": end},
    }


def whole_line(text: str, line: int) -> dict[str, Any]:
    return span_range(line, 0, line, len(lsp_lines(text)[0][line]))


def as_lint(found: list[dict[str, Any]]) -> list[tuple[str, str, int]]:
    return [(d["code"], d["message"], d["range"]["start"]["line"] + 1) for d in found]


def lint_expected(path: Path, config: LintConfig | None = None) -> list[tuple[str, str, int]]:
    findings = lint_file(path, config or LintConfig(suggest=True))
    return [(finding.code, finding.message, finding.line) for finding in findings]


# ---------------------------------------------------------------------------
# The seam itself
# ---------------------------------------------------------------------------


def test_the_linter_never_imports_the_protocol_layer() -> None:
    """What makes swapping the protocol layer cheap: nothing here depends on it."""
    run_fresh_python(
        """
import sys
import bigfix_relevance_analyzer.lsp.linter
assert "bigfix_relevance_analyzer.lsp.server" not in sys.modules
assert "bigfix_relevance_analyzer.lsp.stdio" not in sys.modules
print("ok")
"""
    )


def test_diagnostics_are_plain_json_in_lsp_field_names() -> None:
    """Plain dicts with LSP's own keys, so any protocol layer can pass them on
    -- or structure them into ``lsprotocol`` types, as the pygls spike did."""
    found = DocumentLinter().diagnostics("file:///w/a.rel", BROKEN)
    assert found
    assert json.loads(json.dumps(found)) == found
    for diagnostic in found:
        assert set(diagnostic) == {"range", "severity", "code", "source", "message"}
        assert set(diagnostic["range"]) == {"start", "end"}
        assert set(diagnostic["range"]["start"]) == {"line", "character"}


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def test_a_clean_document_has_no_diagnostics() -> None:
    assert DocumentLinter().diagnostics("file:///w/a.rel", CLIENT) == []


def test_an_unrecognized_file_type_has_no_diagnostics() -> None:
    assert DocumentLinter().diagnostics("file:///w/notes.txt", BROKEN) == []


def test_a_broken_statement_is_an_error_over_the_offending_text() -> None:
    """``exists file "unterminated``: the string, not the line (issue #96, item 1)."""
    found = DocumentLinter().diagnostics("file:///w/a.rel", BROKEN)
    assert {d["code"] for d in found} == {"parse-error", "error-token"}
    for diagnostic in found:
        assert diagnostic["severity"] == 1
        assert diagnostic["source"] == SOURCE
        assert diagnostic["range"] == span_range(0, 12, 0, len(BROKEN))


@pytest.mark.parametrize(
    ("name", "text"),
    [("example.bes", BES_EXAMPLE.read_text()), ("doc.md", TWO_SITES)],
)
def test_diagnostics_carry_exactly_what_lint_finds(tmp_path: Path, name: str, text: str) -> None:
    found = DocumentLinter().diagnostics(f"file:///w/{name}", text)
    assert as_lint(found) == lint_expected(write(tmp_path, name, text))


def test_the_lint_config_is_the_callers(tmp_path: Path) -> None:
    config = LintConfig(severities={"unknown-inspector": Severity.ERROR})
    found = DocumentLinter(config=config).diagnostics(URI, TWO_SITES)
    assert as_lint(found) == lint_expected(write(tmp_path, "doc.md", TWO_SITES), config)
    assert {d["severity"] for d in found} == {1}


# ---------------------------------------------------------------------------
# Per-site cache
# ---------------------------------------------------------------------------


def test_an_unchanged_site_is_served_from_the_cache() -> None:
    linter = DocumentLinter()
    linter.diagnostics(URI, TWO_SITES)
    linter.diagnostics(URI, TWO_SITES.replace(BROKEN, CLIENT))
    stats = linter.cache_stats()
    assert (stats.hits, stats.misses, stats.size) == (1, 3, 3)


def test_a_cached_site_that_moved_reports_its_new_line(tmp_path: Path) -> None:
    linter = DocumentLinter()
    linter.diagnostics(URI, TWO_SITES)
    moved = "intro\n\n\n" + TWO_SITES
    found = linter.diagnostics(URI, moved)
    assert linter.cache_stats().misses == 2
    assert as_lint(found) == lint_expected(write(tmp_path, "doc.md", moved))


def test_the_cache_is_bounded() -> None:
    linter = DocumentLinter(cache_size=2)
    for index in range(4):
        linter.diagnostics(f"file:///w/{index}.rel", f"{UNKNOWN_INSPECTOR} {index}")
    assert linter.cache_stats().size == 2


# ---------------------------------------------------------------------------
# Large-document guard and options
# ---------------------------------------------------------------------------


def test_the_default_limit_is_one_mebibyte() -> None:
    assert DocumentLinter().max_document_bytes == DEFAULT_MAX_DOCUMENT_BYTES == 1024 * 1024


def test_an_oversized_document_is_reported_not_linted() -> None:
    linter = DocumentLinter(max_document_bytes=10)
    (diagnostic,) = linter.diagnostics("file:///w/a.rel", BROKEN)
    assert linter.cache_stats().misses == 0
    assert diagnostic["code"] == DOCUMENT_TOO_LARGE
    assert diagnostic["severity"] == 3
    assert "maxDocumentBytes" in diagnostic["message"]


def test_apply_options_sets_the_limit() -> None:
    linter = DocumentLinter()
    linter.apply_options({"maxDocumentBytes": 5, "somethingElse": True})
    assert linter.max_document_bytes == 5


@pytest.mark.parametrize("options", [None, {}, {"other": 1}])
def test_apply_options_without_a_limit_changes_nothing(options: Any) -> None:
    linter = DocumentLinter(max_document_bytes=7)
    linter.apply_options(options)
    assert linter.max_document_bytes == 7


@pytest.mark.parametrize("value", ["10", -1, True, 1.5, None])
def test_apply_options_ignores_an_invalid_limit(
    value: object, caplog: pytest.LogCaptureFixture
) -> None:
    linter = DocumentLinter()
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        linter.apply_options({"maxDocumentBytes": value})
    assert linter.max_document_bytes == DEFAULT_MAX_DOCUMENT_BYTES
    assert "maxDocumentBytes" in caplog.text


def test_apply_options_ignores_options_that_are_not_an_object(
    caplog: pytest.LogCaptureFixture,
) -> None:
    linter = DocumentLinter()
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        linter.apply_options(["maxDocumentBytes", 5])
    assert linter.max_document_bytes == DEFAULT_MAX_DOCUMENT_BYTES
    assert "initialization options" in caplog.text


def test_an_oversized_document_is_never_split_into_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    """The guard exists for documents too big to process; splitting one is processing it."""
    import bigfix_relevance_analyzer.lsp.linter as linter_module

    def refuse(text: str, data: bytes) -> None:
        raise AssertionError("indexed an oversized document")

    monkeypatch.setattr(linter_module, "DocumentIndex", refuse)
    (diagnostic,) = DocumentLinter(max_document_bytes=10).diagnostics("file:///w/a.rel", BROKEN)
    assert diagnostic["code"] == DOCUMENT_TOO_LARGE
    assert DocumentLinter().diagnostics("file:///w/a.rel", CLIENT) == []


# ---------------------------------------------------------------------------
# Buffers identified by language rather than by file name
# ---------------------------------------------------------------------------


def test_an_untitled_relevance_buffer_is_linted_as_whole_file_relevance() -> None:
    from bigfix_relevance_analyzer.lsp.linter import LANGUAGE_ID

    found = DocumentLinter().diagnostics("untitled:Untitled-1", BROKEN, language_id=LANGUAGE_ID)
    assert "error-token" in {d["code"] for d in found}


def test_an_untitled_buffer_of_another_language_is_not_linted() -> None:
    assert (
        DocumentLinter().diagnostics("untitled:Untitled-1", BROKEN, language_id="plaintext") == []
    )
    assert DocumentLinter().diagnostics("untitled:Untitled-1", BROKEN) == []


def test_a_file_switched_to_the_relevance_language_is_linted(tmp_path: Path) -> None:
    from bigfix_relevance_analyzer.lsp.linter import LANGUAGE_ID

    found = DocumentLinter().diagnostics("file:///w/notes.txt", BROKEN, language_id=LANGUAGE_ID)
    assert found
    assert as_lint(found) == lint_expected(write(tmp_path, "notes.rel", BROKEN))


def test_a_recognized_suffix_wins_over_the_language() -> None:
    """A .md stays markdown: only its relevance fences are linted, not the prose."""
    from bigfix_relevance_analyzer.lsp.linter import LANGUAGE_ID

    prose = "# Notes\n\nnot relevance at all\n"
    assert DocumentLinter().diagnostics("file:///w/doc.md", prose, language_id=LANGUAGE_ID) == []


def test_untitled_linting_survives_a_second_untyped_suffix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fallback borrows an untyped suffix only to pick the extractor, and
    every untyped suffix picks the same one; a second must not break it."""
    import bigfix_relevance_analyzer.lsp.linter as linter_module
    from bigfix_relevance_analyzer.lsp.linter import LANGUAGE_ID

    monkeypatch.setattr(linter_module, "_UNTYPED_TEXT_SUFFIXES", frozenset({".rel", ".relevance"}))
    found = DocumentLinter().diagnostics("untitled:Untitled-1", BROKEN, language_id=LANGUAGE_ID)
    assert "error-token" in {d["code"] for d in found}


# ---------------------------------------------------------------------------
# Precise ranges (issue #96, item 1)
# ---------------------------------------------------------------------------

BES_TYPE_ERROR = (
    '<BES>\n<Task>\n\t<Relevance>exists file "x"\n'
    '\twhose (version of it &gt; "1" AND size of it = "big")</Relevance>\n'
    "</Task>\n</BES>\n"
)


def test_a_bes_type_error_covers_the_comparison_only() -> None:
    (diagnostic,) = DocumentLinter().diagnostics("file:///w/a.bes", BES_TYPE_ERROR)
    assert diagnostic["code"] == "type-error"
    assert diagnostic_text(BES_TYPE_ERROR, diagnostic) == 'size of it = "big"'
    assert diagnostic["range"]["start"]["line"] == 3


def test_a_bes_range_counts_an_entity_as_written() -> None:
    """``&gt;`` is one character in the statement and four in the buffer."""
    (diagnostic,) = DocumentLinter().diagnostics("file:///w/a.bes", BES_TYPE_ERROR)
    line = BES_TYPE_ERROR.splitlines()[3]
    assert diagnostic["range"]["start"]["character"] == line.index("size")


def test_unknown_inspector_gets_one_diagnostic_per_name() -> None:
    text = "exists bogus one whose (exists bogus two)"
    config = LintConfig(suggest=False)
    found = DocumentLinter(config=config).diagnostics("file:///w/a.rel", text)
    assert [d["code"] for d in found] == ["unknown-inspector", "unknown-inspector"]
    assert [diagnostic_text(text, d) for d in found] == ["bogus one", "bogus two"]
    # Each one names its own name: with no "did you mean" to attribute, the
    # message is tailored to it.
    assert [d["message"] for d in found] == [
        "no dump defines `bogus one`",
        "no dump defines `bogus two`",
    ]
    # ...while lint, and so the hook, still reports one finding.
    (finding,) = lint_text(text, config)
    assert finding.message == "no dump defines `bogus one`, `bogus two`"


def test_every_use_of_an_unknown_name_is_underlined() -> None:
    text = "exists bogus one and exists bogus one"
    found = DocumentLinter(config=LintConfig()).diagnostics("file:///w/a.rel", text)
    assert [diagnostic_text(text, d) for d in found] == ["bogus one", "bogus one"]
    assert found[0]["range"] != found[1]["range"]


def test_each_unknown_name_gets_only_its_own_leads() -> None:
    """Leads are worked out per name, so each diagnostic offers its own."""
    text = "exists oprating system and exists bogus two"
    linter = DocumentLinter()
    found = linter.diagnostics("file:///w/a.rel", text)
    assert [diagnostic_text(text, d) for d in found] == ["oprating system", "bogus two"]
    assert "did you mean `operating system`" in found[0]["message"]
    assert "`bogus two`" not in found[0]["message"]
    assert found[1]["message"] == "no dump defines `bogus two`"


def test_one_unknown_name_with_suggestions_keeps_the_findings_message() -> None:
    text = "exists oprating system"
    linter = DocumentLinter()
    (diagnostic,) = linter.diagnostics("file:///w/a.rel", text)
    (finding,) = lint_text(text, linter.config)
    assert "did you mean" in diagnostic["message"]
    assert diagnostic["message"] == finding.message
    assert diagnostic_text(text, diagnostic) == "oprating system"


def test_a_statement_level_finding_still_covers_its_line() -> None:
    text = '  exists descendants of folder "c:\\"'
    config = LintConfig(max_score=None, max_evaluation_cost=0.0)
    (diagnostic,) = DocumentLinter(config=config).diagnostics("file:///w/a.rel", text)
    assert diagnostic["code"] == "evaluation-cost"
    assert diagnostic["range"] == whole_line(text, 0)


def test_an_unmappable_span_falls_back_to_the_whole_line() -> None:
    """The statement starts a line below its processing instruction: no column."""
    text = "<p><?Relevance\n  names of bogus things ?></p>\n"
    (diagnostic,) = DocumentLinter().diagnostics("file:///w/a.ojo", text)
    assert diagnostic["code"] == "unknown-inspector"
    assert diagnostic["range"] == whole_line(text, 0)


def test_a_parse_error_at_the_end_covers_the_last_character() -> None:
    text = 'exists file "x" whose (it\n    is'
    (diagnostic,) = DocumentLinter().diagnostics("file:///w/a.rel", text)
    assert diagnostic["code"] == "parse-error"
    assert diagnostic["range"] == span_range(1, 5, 1, 6)


def test_a_multi_line_span_is_one_multi_line_range() -> None:
    text = 'exists file "x" whose (size of it\n    = "big")'
    (diagnostic,) = DocumentLinter().diagnostics("file:///w/a.rel", text)
    assert diagnostic["range"] == span_range(0, 23, 1, 11)


def test_ranges_in_a_crlf_markdown_file() -> None:
    text = '# T\r\n\r\n```relevance\r\nexists file "x"\r\n  whose (size of it = "big")\r\n```\r\n'
    (diagnostic,) = DocumentLinter().diagnostics("file:///w/a.md", text)
    assert diagnostic["range"] == span_range(4, 9, 4, 27)


def test_a_cached_site_that_moved_sideways_keeps_its_range_right() -> None:
    linter = DocumentLinter()
    linter.diagnostics("file:///w/a.ojo", "<p><?Relevance exists bogus thing ?></p>")
    text = "<div><p>moved <?Relevance exists bogus thing ?></p></div>"
    (diagnostic,) = linter.diagnostics("file:///w/a.ojo", text)
    assert linter.cache_stats().hits == 1
    assert diagnostic_text(text, diagnostic) == "bogus thing"


def test_diagnostics_stay_in_finding_order_then_span_order() -> None:
    text = 'exists bogus one whose (size of it = "big") and exists bogus two'
    found = DocumentLinter(config=LintConfig()).diagnostics("file:///w/a.rel", text)
    codes = [d["code"] for d in found]
    findings = lint_text(text, LintConfig())
    expected: list[str] = []
    for finding in findings:
        expected.extend([finding.code] * max(len(finding.spans), 1))
    assert codes == expected
