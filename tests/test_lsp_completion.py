"""Tests for completion through the editor's seam (#127).

Through :meth:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter.completions`,
the protocol-free entry point: a URI, the buffer's text and an LSP position in;
plain completions out. :mod:`test_lsp` covers ``textDocument/completion`` end
to end. Every replace range is read back from the buffer, so a test says what
text the editor replaces rather than which numbers it was given.
"""

from __future__ import annotations

import pytest
from _helpers import BES_BROKEN, lsp_lines, lsp_text

from bigfix_relevance_analyzer import lint
from bigfix_relevance_analyzer.lint import LintConfig, TextSpan
from bigfix_relevance_analyzer.lsp.linter import DocumentCompletion, DocumentLinter
from bigfix_relevance_analyzer.lsp.positions import utf16_length

CURSOR = "@"
"""Where the cursor is in a test document. Not a character relevance writes."""

BES = (
    '<?xml version="1.0" encoding="UTF-8"?>\n<BES>\n<Task>\n'
    "\t<Title>t</Title>\n\t<Relevance>{body}</Relevance>\n</Task>\n</BES>\n"
)


def complete(
    name: str, marked: str, linter: DocumentLinter | None = None, **options: object
) -> tuple[str, list[DocumentCompletion]]:
    """``(the buffer, its completions)`` at the cursor marker in ``marked``."""
    assert marked.count(CURSOR) == 1
    text = marked.replace(CURSOR, "")
    lines, _ = lsp_lines(marked[: marked.index(CURSOR)])
    position = (len(lines) - 1, utf16_length(lines[-1]))
    found = (linter or DocumentLinter()).completions(
        f"file:///workspace/{name}",
        text,
        position,
        **options,  # type: ignore[arg-type]
    )
    return text, found


def labels(found: list[DocumentCompletion]) -> list[str]:
    return [item.label for item in found]


def replaced(text: str, item: DocumentCompletion) -> str:
    assert item.range is not None
    return lsp_text(text, *item.range)


@pytest.mark.parametrize(
    ("name", "marked"),
    [
        ("a.rel", "exists files of @"),
        ("a.rel", "\n  exists files of\n  @\n"),
        ("a.bes", BES.format(body="x &lt; 3 and exists files of @")),
        ("a.md", "# T\n\n```relevance\nexists files of @\n```\n"),
        (
            "a.bes",
            BES.replace(
                "<Relevance>{body}</Relevance>", "<Relevance>exists files of @</Relevance>"
            ),
        ),
    ],
)
def test_after_files_of_folders_come_first(name: str, marked: str) -> None:
    text, found = complete(name, marked)
    assert found, marked
    first = found[0]
    assert first.label == "folders"
    assert first.insert_text == "folders"
    assert not first.is_snippet
    assert first.sort_text == "0000"
    assert first.detail.endswith(": folder")
    # Nothing typed yet: the edit inserts at the cursor.
    assert first.range is not None
    assert first.range[0] == first.range[1]
    assert replaced(text, first) == ""


def test_the_sort_text_follows_the_rank() -> None:
    _, found = complete("a.rel", "exists files of @")
    assert [item.sort_text for item in found] == [f"{n:04d}" for n in range(len(found))]


def test_a_partial_word_is_replaced() -> None:
    text, found = complete("a.rel", "exists files of fold@")
    assert found[0].label == "folders"
    assert replaced(text, found[0]) == "fold"
    assert all("registry" not in label for label in labels(found))


def test_a_partial_word_in_bes_after_an_entity() -> None:
    text, found = complete("a.bes", BES.format(body="x &lt; 3 and exists files of fold@"))
    assert found[0].label == "folders"
    assert replaced(text, found[0]) == "fold"


def test_an_astral_character_before_the_cursor_counts_two_units() -> None:
    marked = '"\U0001f600" & exists files of fold@'
    text, found = complete("a.rel", marked)
    assert found
    # The marker is gone and the emoji is two units: the cursor is at len(marked).
    assert found[0].range == ((0, len(marked) - len("fold")), (0, len(marked)))
    assert replaced(text, found[0]) == "fold"


def test_snippets_only_when_the_client_takes_them() -> None:
    _, found = complete("a.rel", "exists files of @", snippets=True)
    assert (found[0].insert_text, found[0].is_snippet) == ('folders "$1"', True)
    _, plain = complete("a.rel", "exists files of @")
    assert (plain[0].insert_text, plain[0].is_snippet) == ("folders", False)


def test_a_multi_word_partial_is_replaced_to_the_cursor() -> None:
    text, found = complete("a.rel", "names of bes c@")
    assert "bes computers" in labels(found)
    assert replaced(text, found[0]) == "bes c"
    text, found = complete("a.rel", "names of bes @")
    assert "bes computers" in labels(found)
    # The space is past the site's stripped text, and still replaced.
    assert replaced(text, found[0]) == "bes "


def test_inside_whose_and_at_the_start() -> None:
    _, found = complete("a.rel", "exists files whose (@")
    assert found[0].label == "name"
    _, found = complete("a.rel", "va@")
    assert found[0].label == "values"


@pytest.mark.parametrize(
    "marked",
    [
        'exists files of "fold@',
        "exists files of /* fold@",
        'exists files of "a" @',
        "exists files as @",
    ],
)
def test_nothing_where_nothing_fits(marked: str) -> None:
    assert complete("a.rel", marked)[1] == []


def test_nothing_outside_every_site() -> None:
    assert complete("a.ojo", "<p><?Relevance exists files of ?> @</p>")[1] == []
    assert complete("a.md", "# T @\n\n```relevance\nexists x\n```\n")[1] == []


def test_nothing_for_a_type_no_extractor_reads() -> None:
    assert complete("a.txt", "exists files of @")[1] == []


def test_an_untitled_relevance_buffer_uses_its_language() -> None:
    linter = DocumentLinter()
    found = linter.completions(
        "untitled:Untitled-1", "exists files of ", (0, 16), "bigfix-relevance"
    )
    assert found and found[0].label == "folders"


def test_an_untitled_bes_buffer_uses_its_language() -> None:
    """Issue #120: the same completions as a saved .bes with the same text."""
    linter = DocumentLinter()
    position = (4, len("\t<Relevance>exists "))
    found = linter.completions("untitled:Untitled-1", BES_BROKEN, position, "bigfix-bes")
    assert found
    assert found == linter.completions("file:///w/task.bes", BES_BROKEN, position)


def test_nothing_past_the_size_guard() -> None:
    linter = DocumentLinter(max_document_bytes=10)
    assert complete("a.rel", "exists files of @", linter)[1] == []


def test_the_containers_dialect_filters() -> None:
    # A session processing instruction offers no client-only producer...
    _, session = complete("a.ojo", "<p><?Relevance names of @ ?></p>")
    assert session
    assert not {"drive", "drives"} & set(labels(session))
    # ...and a fixlet's client relevance no session-only one.
    _, client = complete("a.bes", BES.format(body="names of @"))
    assert client
    assert not {"bes computer", "bes computers"} & set(labels(client))
    # A plain file is either until its content says, so both are offered.
    assert "drive" in labels(complete("a.rel", "names of dr@")[1])
    assert "bes computers" in labels(complete("a.rel", "names of bes c@")[1])


def test_the_configured_platform_filters() -> None:
    assert "apple extras folders" in labels(complete("a.rel", "exists files of apple@")[1])
    windows = DocumentLinter(config=LintConfig(platform="windows"))
    assert complete("a.rel", "exists files of apple@", windows)[1] == []


def test_completion_never_analyzes_or_lints(monkeypatch: pytest.MonkeyPatch) -> None:
    """Completion reads tokens and tables; it never pays for, or warms, lint's
    analysis -- the cache diagnostics and quick fixes share."""

    def refuse(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("completion analyzed a statement")

    monkeypatch.setattr(lint, "_analyze_cached", refuse)
    monkeypatch.setattr(lint, "_judge_site", refuse)
    linter = DocumentLinter()
    _, found = complete("a.rel", "exists files of @", linter)
    assert found
    assert linter.cache_stats() == (0, 0, 0)


def test_the_extraction_is_shared_with_hover() -> None:
    linter = DocumentLinter()
    uri = "file:///workspace/a.rel"
    linter.completions(uri, "exists files of ", (0, 16))
    kept = linter._extractions[uri]
    linter.completions(uri, "exists files of ", (0, 16))
    assert linter._extractions[uri] is kept


def test_an_unplaceable_multi_word_partial_offers_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a range the client replaces only its own word: `bes c` would
    become `bes bes computers`. Nothing is better than that (finding 8)."""
    from bigfix_relevance_analyzer.lsp.positions import DocumentIndex

    real = DocumentIndex.site_range

    def unplaceable(self: DocumentIndex, site: object, span: TextSpan) -> object:
        # Placing the cursor maps single characters; only the partial is wider.
        return None if span.end - span.start > 1 else real(self, site, span)  # type: ignore[arg-type]

    monkeypatch.setattr(DocumentIndex, "site_range", unplaceable)
    assert complete("a.rel", "names of bes c@")[1] == []
    # A one-word partial is still offered, for the client's own word range.
    _, found = complete("a.rel", "exists files of fold@")
    assert found and found[0].range is None
