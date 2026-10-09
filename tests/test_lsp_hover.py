"""Tests for hover: what the cursor is on, said in a few lines of Markdown.

Through :meth:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter.hover`,
the protocol-free seam, the way any adapter calls it: a URI, the buffer's text
and an LSP position in; an LSP ``Hover`` as plain data, or ``None``, out.
:mod:`test_lsp` covers the ``textDocument/hover`` request end to end.

Every hover's range is read back from the buffer, so a test says what text the
editor highlights rather than which numbers it was given.
"""

from __future__ import annotations

import re
from typing import Any

import pytest
from _helpers import REPO_ROOT, lsp_text

from bigfix_relevance_analyzer.lsp.hover import DOCS_URL, MAX_QUOTED, MAX_ROWS
from bigfix_relevance_analyzer.lsp.linter import DocumentLinter

FILES = 'exists files whose (name of it = "x") of folder "/tmp"'

BES = (
    '<?xml version="1.0" encoding="UTF-8"?>\n<BES>\n<Task>\n'
    "\t<Title>t</Title>\n\t<Relevance>{body}</Relevance>\n</Task>\n</BES>\n"
)


def hover_at(
    name: str, text: str, needle: str, occurrence: int = 0, shift: int = 0
) -> dict[str, Any] | None:
    """The hover at the first character of ``needle`` (its ``occurrence``-th
    use) in the buffer, ``shift`` characters on. ASCII buffers only: the
    character is the code point index."""
    offset = -1
    for _ in range(occurrence + 1):
        offset = text.index(needle, offset + 1)
    offset += shift
    line = text.count("\n", 0, offset)
    character = offset - (text.rfind("\n", 0, offset) + 1)
    return DocumentLinter().hover(f"file:///workspace/{name}", text, (line, character))


def shown(name: str, text: str, needle: str, **where: int) -> tuple[str, str]:
    """``(markdown, highlighted text)`` of the hover on ``needle``."""
    found = hover_at(name, text, needle, **where)
    assert found is not None, f"no hover on {needle!r}"
    assert found["contents"]["kind"] == "markdown"
    start, end = found["range"]["start"], found["range"]["end"]
    highlighted = lsp_text(
        text, (start["line"], start["character"]), (end["line"], end["character"])
    )
    return found["contents"]["value"], highlighted


# ---------------------------------------------------------------------------
# What is under the cursor
# ---------------------------------------------------------------------------


def test_an_inspector_shows_its_resolved_signature_type_plurality_and_platforms() -> None:
    markdown, highlighted = shown("a.rel", FILES, "files")
    assert highlighted == "files"
    assert "`files of <folder>`" in markdown
    assert "`file`" in markdown
    assert "plural" in markdown
    for platform in ("debian", "macos", "rhel", "ubuntu", "windows"):
        assert platform in markdown


def test_any_character_of_an_inspector_name_shows_it() -> None:
    first, _ = shown("a.rel", FILES, "files")
    last, _ = shown("a.rel", FILES, "files", shift=4)
    assert first == last


def test_an_overloaded_inspector_shows_only_the_rows_it_resolved_to() -> None:
    markdown, highlighted = shown("a.rel", FILES, "folder")
    assert highlighted == 'folder "/tmp"'
    assert "`folder <string>`" in markdown
    assert "`folder of <" not in markdown
    assert "singular" in markdown


def test_plurality_is_the_names_as_written_not_the_rows_usual_form() -> None:
    """``keys`` is written plural even where its rows are usually singular
    (``key <string> of <registry>``): the expression's plurality is what the
    spelling says, as :func:`~bigfix_relevance_analyzer.inspectors.written_form_of` has it."""
    plural, _ = shown("a.rel", "exists keys of it", "keys")
    assert ", plural" in plural
    assert ", singular" not in plural
    singular, _ = shown("a.rel", 'exists keys of key "x" of registry', "key ")
    assert ", singular" in singular
    assert ", plural" not in singular


def test_a_name_with_many_definitions_lists_a_few_and_counts_the_rest() -> None:
    markdown, _ = shown("a.rel", "exists keys of it", "keys")
    assert markdown.count("\n- `") == MAX_ROWS
    assert re.search(r"\n- \.\.\. and \d+ more", markdown)


def test_a_session_inspector_names_its_session_contexts() -> None:
    markdown, _ = shown("a.bsr", "names of bes computers", "bes computers")
    assert "session" in markdown
    assert "`bes computers`" in markdown


def test_an_unknown_name_says_so() -> None:
    markdown, highlighted = shown("a.rel", "exists totally bogus thing", "bogus")
    assert highlighted == "totally bogus thing"
    assert "not defined" in markdown


def test_a_string_literal() -> None:
    markdown, highlighted = shown("a.rel", FILES, '"x"')
    assert highlighted == '"x"'
    assert "string" in markdown


def test_a_number_literal() -> None:
    markdown, highlighted = shown("a.rel", "exists file whose (size of it > 100)", "100")
    assert highlighted == "100"
    assert "integer" in markdown


def test_a_string_holding_backticks_stays_one_code_span() -> None:
    markdown, _ = shown("a.rel", 'exists file "a`b``c"', '"a')
    assert '``` "a`b``c" ```' in markdown


def test_a_long_literal_is_elided_to_the_limit() -> None:
    literal = '"' + "x" * 200 + '"'
    markdown, highlighted = shown("a.rel", f"exists file {literal}", '"x')
    assert highlighted == literal
    quoted = markdown.split("`")[1]
    assert len(quoted) == MAX_QUOTED
    assert quoted.endswith("...")


def test_it_shows_what_binds_it() -> None:
    markdown, highlighted = shown("a.rel", FILES, "it")
    assert highlighted == "it"
    assert "`whose`" in markdown
    assert "`files`" in markdown


def test_it_under_of_shows_its_object() -> None:
    markdown, _ = shown("a.rel", 'exists (name of it) of file "x"', "it")
    assert "`of`" in markdown
    assert '`file "x"`' in markdown


def test_an_unbound_it_says_nothing_binds_it() -> None:
    markdown, _ = shown("a.rel", "exists it", "it")
    assert "nothing" in markdown.lower()


def test_an_operator_highlights_just_the_operator() -> None:
    markdown, highlighted = shown("a.rel", FILES, "=")
    assert highlighted == "="
    assert "operator" in markdown


def test_a_word_operator_highlights_the_whole_word() -> None:
    markdown, highlighted = shown("a.rel", 'exists file "a" and exists file "b"', "and", shift=1)
    assert highlighted == "and"
    assert "`and`" in markdown


@pytest.mark.parametrize(
    ("text", "needle", "expected"),
    [
        (FILES, "of", "`of`"),
        (FILES, "whose", "`whose`"),
        ('exists file "x" | false', "|", "`|`"),
        ('("1" as integer) > 0', "as", "`as integer`"),
        ('if exists file "x" then 1 else 2', "then", "`if`"),
        ('number of files of folder "x"', "number", "`number of`"),
        ('not exists file "x"', "exists", "`not exists`"),
        ('item 0 of ("a", "b")', "item", "`item 0 of`"),
    ],
)
def test_a_keyword_shows_its_construct(text: str, needle: str, expected: str) -> None:
    markdown, highlighted = shown("a.rel", text, needle)
    assert highlighted == needle
    assert expected in markdown


@pytest.mark.parametrize(
    ("text", "needle"),
    [
        (FILES, " whose"),  # whitespace between tokens
        ('exists /* note */ file "x"', "note"),  # a comment
        ('exists the file "x"', "the"),  # an article, which the engine skips
        (FILES, "("),  # a parenthesis
    ],
)
def test_trivia_and_grouping_have_no_hover(text: str, needle: str) -> None:
    assert hover_at("a.rel", text, needle) is None


def test_a_statement_that_does_not_parse_has_no_hover() -> None:
    assert hover_at("a.rel", 'exists file "unterminated', "file") is None
    assert hover_at("a.rel", "exists file whose (", "file") is None


# ---------------------------------------------------------------------------
# Where the statement is
# ---------------------------------------------------------------------------


def test_hover_inside_a_markdown_fence() -> None:
    doc = f"# T\n\n```relevance\n{FILES}\n```\n"
    markdown, highlighted = shown("a.md", doc, "files")
    assert highlighted == "files"
    assert "`files of <folder>`" in markdown
    assert hover_at("a.md", doc, "# T") is None


def test_hover_inside_a_bes_relevance_with_an_entity() -> None:
    doc = BES.format(body='exists file "x" whose (size of it &gt; 3)')
    markdown, highlighted = shown("a.bes", doc, "&gt;", shift=2)
    assert highlighted == "&gt;"
    assert "`>`" in markdown
    markdown, highlighted = shown("a.bes", doc, "size")
    assert highlighted == "size"
    assert "`size of <file>`" in markdown


def test_hover_in_bes_markup_is_none() -> None:
    doc = BES.format(body='exists file "x"')
    assert hover_at("a.bes", doc, "Relevance") is None
    assert hover_at("a.bes", doc, "Title") is None


def test_hover_in_a_crlf_document_with_an_astral_character() -> None:
    doc = '# T\r\n```relevance\r\nexists file "\U0001f600"\r\n  whose (size of it > 3)\r\n```\r\n'
    linter = DocumentLinter()
    found = linter.hover("file:///workspace/a.md", doc, (3, 9))
    assert found is not None
    assert found["range"] == {
        "start": {"line": 3, "character": 9},
        "end": {"line": 3, "character": 13},
    }
    # On the astral character's second UTF-16 unit: it is in the string.
    found = linter.hover("file:///workspace/a.md", doc, (2, 14))
    assert found is not None
    assert "string" in found["contents"]["value"]


def test_an_untitled_relevance_buffer_has_hover() -> None:
    linter = DocumentLinter()
    assert linter.hover("untitled:Untitled-1", FILES, (0, 8), "bigfix-relevance") is not None
    assert linter.hover("untitled:Untitled-1", FILES, (0, 8), "plaintext") is None


def test_an_unrecognized_file_type_has_no_hover() -> None:
    assert DocumentLinter().hover("file:///workspace/a.txt", FILES, (0, 8)) is None


def test_an_oversized_document_has_no_hover() -> None:
    linter = DocumentLinter(max_document_bytes=10)
    assert linter.hover("file:///workspace/a.rel", FILES, (0, 8)) is None


@pytest.mark.parametrize("position", [(0, -1), (-1, 0), (0, 999), (99, 0)])
def test_a_position_outside_the_buffer_has_no_hover(position: tuple[int, int]) -> None:
    assert DocumentLinter().hover("file:///workspace/a.rel", FILES, position) is None


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------


def _anchors(path: str) -> set[str]:
    """GitHub's heading anchors in a Markdown file."""
    text = (REPO_ROOT / "docs/reference" / path).read_text(encoding="utf-8")
    slugs = set()
    for heading in re.findall(r"^#+ (.+)$", text, flags=re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        slugs.add(slug)
    return slugs


LINKED = [
    ("a.rel", FILES, needle) for needle in ("files", "of", "whose", "it", '"x"', "=", "folder")
] + [
    ("a.rel", 'exists file "x" | false', "|"),
    ("a.rel", '("1" as integer) > 0', "as"),
    ("a.rel", '("a", "b")', ","),
    ("a.bsr", "names of bes computers", "bes computers"),
]


@pytest.mark.parametrize(("name", "text", "needle"), LINKED)
def test_every_docs_link_names_a_heading_that_exists(name: str, text: str, needle: str) -> None:
    markdown, _ = shown(name, text, needle)
    links = re.findall(r"\]\(([^)]+)\)", markdown)
    for link in links:
        assert link.startswith(DOCS_URL), link
        page, _, anchor = link.removeprefix(DOCS_URL).partition("#")
        assert (REPO_ROOT / "docs/reference" / page).is_file(), link
        if anchor:
            assert anchor in _anchors(page), link


def test_the_keywords_link_to_the_syntax_reference() -> None:
    for needle in ("of", "whose", "it"):
        markdown, _ = shown("a.rel", FILES, needle)
        assert f"{DOCS_URL}syntax.md#" in markdown, needle
