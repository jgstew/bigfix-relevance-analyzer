"""Tests for semantic tokens: :func:`~bigfix_relevance_analyzer.highlight.highlight`
served as ``textDocument/semanticTokens/full``.

Through :meth:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter.semantic_tokens`,
the protocol-free seam, and end to end through
:class:`~bigfix_relevance_analyzer.lsp.server.Server`, whose relative encoding
is decoded back here. Every token is read back from the buffer, so a test
says what text the editor colours rather than which numbers it was given.
"""

from __future__ import annotations

from itertools import pairwise
from typing import Any

import pytest
from _corpus import corpus_files
from _helpers import lsp_text
from test_lsp import initialize, notification, request, started, uri

from bigfix_relevance_analyzer.highlight import HighlightKind, highlight
from bigfix_relevance_analyzer.lsp.linter import DocumentLinter, SemanticToken
from bigfix_relevance_analyzer.lsp.positions import utf16_length
from bigfix_relevance_analyzer.lsp.server import SEMANTIC_TOKEN_TYPES, Server

K = HighlightKind
GRIN = chr(0x1F600)
"""Two UTF-16 code units: the case where characters and LSP columns part."""


def tokens(name: str, text: str, language_id: str | None = None) -> list[SemanticToken]:
    return DocumentLinter().semantic_tokens(f"file:///workspace/{name}", text, language_id)


def coloured(name: str, text: str, language_id: str | None = None) -> list[tuple[str, str]]:
    """Every token as ``(the buffer text it covers, its kind)``."""
    return [
        (
            lsp_text(
                text, (token.line, token.character), (token.line, token.character + token.length)
            ),
            token.kind,
        )
        for token in tokens(name, text, language_id)
    ]


def open_document(server: Server, name: str, text: str, language_id: str = "plaintext") -> None:
    document = {"uri": uri(name), "languageId": language_id, "version": 1, "text": text}
    server.handle(notification("textDocument/didOpen", {"textDocument": document}))


def full(server: Server, name: str) -> Any:
    (response,) = server.handle(
        request("textDocument/semanticTokens/full", {"textDocument": {"uri": uri(name)}}, id_=9)
    )
    assert response["id"] == 9
    return response


def decode(data: list[int]) -> list[tuple[int, int, int, str]]:
    """LSP's relative quintuples back to absolute ``(line, character, length, type)``."""
    assert len(data) % 5 == 0
    decoded = []
    line = character = 0
    for at in range(0, len(data), 5):
        delta_line, delta_start, length, kind, modifiers = data[at : at + 5]
        assert modifiers == 0
        if delta_line:
            line += delta_line
            character = delta_start
        else:
            character += delta_start
        decoded.append((line, character, length, SEMANTIC_TOKEN_TYPES[kind]))
    return decoded


# ---------------------------------------------------------------------------
# The legend
# ---------------------------------------------------------------------------


def test_the_legend_is_lsp_standard_types_for_every_kind_but_punctuation_and_error() -> None:
    standard = {"keyword", "operator", "property", "type", "string", "number", "comment"}
    assert set(SEMANTIC_TOKEN_TYPES) == standard
    assert len(SEMANTIC_TOKEN_TYPES) == len(standard)
    assert {kind.value for kind in K} - standard == {"punctuation", "error"}


def test_initialize_advertises_full_semantic_tokens_with_the_legend() -> None:
    response = initialize(Server())
    assert response["result"]["capabilities"]["semanticTokensProvider"] == {
        "legend": {"tokenTypes": list(SEMANTIC_TOKEN_TYPES), "tokenModifiers": []},
        "full": True,
    }


# ---------------------------------------------------------------------------
# The seam: DocumentLinter.semantic_tokens
# ---------------------------------------------------------------------------

STATEMENT = 'names of bes computers whose (name of it starts with "Win")'


def test_a_relevance_document_is_coloured_as_highlight_colours_it() -> None:
    """Punctuation and errors are left to the grammar and the diagnostics."""
    expected = [
        (STATEMENT[span.start : span.end], span.kind)
        for span in highlight(STATEMENT)
        if span.kind not in (K.PUNCTUATION, K.ERROR)
    ]
    assert coloured("a.rel", STATEMENT) == expected
    assert ("starts", K.OPERATOR) in expected
    assert ("names", K.PROPERTY) in expected


def test_starts_is_a_name_in_starts_of_ranges() -> None:
    assert coloured("a.rel", "starts of ranges")[0] == ("starts", K.PROPERTY)


def test_columns_after_a_non_bmp_character_count_utf16_code_units() -> None:
    text = f'"{GRIN}" = name of it'
    found = tokens("a.rel", text)
    assert found[0] == SemanticToken(0, 0, 4, K.STRING)  # quote, two units, quote
    # `name` is character 6 of the string, but column 7 for the editor.
    assert found[2] == SemanticToken(0, 7, 4, K.PROPERTY)
    assert [kind for _, kind in coloured("a.rel", text)] == [
        K.STRING,
        K.OPERATOR,
        K.PROPERTY,
        K.KEYWORD,
        K.KEYWORD,
    ]


def test_a_token_spanning_lines_is_split_into_one_per_line() -> None:
    text = '/* first\nsecond */ name of it = "a\r\nb"'
    assert coloured("a.rel", text) == [
        ("/* first", K.COMMENT),
        ("second */", K.COMMENT),
        ("name", K.PROPERTY),
        ("of", K.KEYWORD),
        ("it", K.KEYWORD),
        ("=", K.OPERATOR),
        ('"a', K.STRING),
        ('b"', K.STRING),
    ]


def test_a_bes_site_is_coloured_where_it_is_written_cdata_and_all() -> None:
    text = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<BES>\n<Task>\n'
        '\t<Relevance>name of it contains "a"</Relevance>\n'
        "\t<Title>name of it</Title>\n"
        '\t<Relevance><![CDATA[it < "b"]]></Relevance>\n'
        "</Task>\n</BES>\n"
    )
    assert coloured("a.bes", text) == [
        ("name", K.PROPERTY),
        ("of", K.KEYWORD),
        ("it", K.KEYWORD),
        ("contains", K.OPERATOR),
        ('"a"', K.STRING),
        ("it", K.KEYWORD),
        ("<", K.OPERATOR),
        ('"b"', K.STRING),
    ]
    assert [token.line for token in tokens("a.bes", text)] == [3] * 5 + [5] * 3


def test_a_bes_token_over_an_entity_is_left_uncoloured() -> None:
    """The source map holds no one byte range for text an entity is part of,
    so the token cannot be placed for certain: uncoloured, never misplaced.
    A token that is a whole entity maps, and its neighbours are unaffected."""
    text = '<BES><Task>\n<Relevance>it = "a&amp;b" or it &lt; name</Relevance></Task></BES>'
    assert coloured("a.bes", text) == [
        ("it", K.KEYWORD),
        ("=", K.OPERATOR),
        ("or", K.OPERATOR),
        ("it", K.KEYWORD),
        ("&lt;", K.OPERATOR),
        ("name", K.PROPERTY),
    ]


def test_a_markdown_fence_is_coloured_and_its_prose_is_not() -> None:
    text = "name of it\n\n```relevance\nversion of it\n```\n"
    assert coloured("a.md", text) == [
        ("version", K.PROPERTY),
        ("of", K.KEYWORD),
        ("it", K.KEYWORD),
    ]


def test_the_language_id_picks_the_extractor_for_an_unsaved_buffer() -> None:
    assert tokens("Untitled-1", "name of it") == []
    assert coloured("Untitled-1", "name of it", "bigfix-relevance")[0] == ("name", K.PROPERTY)


def test_nothing_is_coloured_past_the_size_guard() -> None:
    linter = DocumentLinter(max_document_bytes=10)
    assert linter.semantic_tokens("file:///workspace/a.rel", "name of operating system") == []


@pytest.mark.parametrize("path", corpus_files(), ids=lambda path: path.name)
def test_every_example_document_is_sorted_disjoint_and_within_its_lines(path: Any) -> None:
    text = path.read_bytes().decode("utf-8", errors="replace")
    found = tokens(path.name, text)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for token in found:
        assert token.length > 0
        assert token.character + token.length <= utf16_length(lines[token.line])
    for earlier, later in pairwise(found):
        assert (earlier.line, earlier.character + earlier.length) <= (later.line, later.character)


# ---------------------------------------------------------------------------
# The request, end to end
# ---------------------------------------------------------------------------


def test_semantic_tokens_full_round_trips_to_the_seams_tokens() -> None:
    text = f'"{GRIN}" = name\n/* a\nb */ of it'
    server = started()
    open_document(server, "a.rel", text)
    response = full(server, "a.rel")
    assert set(response["result"]) == {"data"}
    assert decode(response["result"]["data"]) == [
        (token.line, token.character, token.length, token.kind.value)
        for token in tokens("a.rel", text)
    ]


def test_a_document_that_is_not_open_has_no_tokens() -> None:
    assert full(started(), "a.rel")["result"] == {"data": []}


def test_semantic_tokens_without_a_uri_are_invalid_params() -> None:
    (response,) = started().handle(request("textDocument/semanticTokens/full", {}, id_=3))
    assert response["error"]["code"] == -32602
