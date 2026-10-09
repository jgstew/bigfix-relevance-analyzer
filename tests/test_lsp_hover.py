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

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import _extract_data
from bigfix_relevance_analyzer.lint import LintConfig, _analyze_cached
from bigfix_relevance_analyzer.lsp import linter as linter_module
from bigfix_relevance_analyzer.lsp.hover import DOCS_URL, MAX_QUOTED, MAX_ROWS, describe
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
    ("text", "needle", "expected", "words"),
    [
        (FILES, "of", "`of`", "of"),
        (FILES, "whose", "`whose`", "whose"),
        ('exists file "x" | false', "|", "`|`", "|"),
        ('("1" as integer) > 0', "as", "`as integer`", "as integer"),
        ('if exists file "x" then 1 else 2', "then", "`if`", "then"),
        ('number of files of folder "x"', "number", "`number of`", "number of"),
        ('not exists file "x"', "exists", "`not exists`", "not exists"),
        ('item 0 of ("a", "b")', "item", "`item 0 of`", "item 0 of"),
    ],
)
def test_a_keyword_shows_its_construct(text: str, needle: str, expected: str, words: str) -> None:
    """A construct spelled in several words highlights all of them, wherever
    in them the cursor is; one spelled in separate places (`if`) just the word."""
    markdown, highlighted = shown("a.rel", text, needle)
    assert highlighted == words
    assert expected in markdown


@pytest.mark.parametrize(
    ("text", "needle", "expected", "shift"),
    [
        ('("a") AND ("b")', "AND", "**`AND`**", 0),
        ('"a" IS NOT EQUAL TO "b"', "IS NOT EQUAL TO", "**`IS NOT EQUAL TO`**", 7),
        ('NOT ("a" = "b")', "NOT", "**`NOT`**", 0),
        ('NOT EXISTS file "x"', "NOT EXISTS", "**`NOT EXISTS`**", 5),
        ('exist file "x"', "exist", "**`exist`**", 0),
        ('"1" AS INTEGER', "AS INTEGER", "**`AS INTEGER`**", 3),
        ('NUMBER OF files of folder "x"', "NUMBER OF", "**`NUMBER OF`**", 0),
        ('"a" is /* why */ not "b"', "is /* why */ not", "**`is not`**", 0),
    ],
)
def test_an_operator_is_shown_and_highlighted_as_the_author_wrote_it(
    text: str, needle: str, expected: str, shift: int
) -> None:
    """The author's casing and spelling, every word of it, comments left out
    of the name but inside the highlight."""
    markdown, highlighted = shown("a.rel", text, needle, shift=shift)
    assert highlighted == needle
    assert expected in markdown


def test_not_exists_reads_no_value() -> None:
    markdown, _ = shown("a.rel", 'not exists file "x"', "exists")
    assert "has no value" in markdown


@pytest.mark.parametrize(
    ("text", "needle", "highlight"),
    [
        ("exists (1)", "1", "1"),
        ('(it) of file "x"', "it", "it"),
        ('( it /* c */ ) of file "x"', "it", "it"),
        ('exists ((name)) of file "x"', "name", "name"),
        ('exists ("x")', '"x"', '"x"'),
        ('exists file ("x")', "file", 'file ("x")'),
    ],
)
def test_a_grouped_leaf_highlights_itself_not_its_parentheses(
    text: str, needle: str, highlight: str
) -> None:
    """The parser folds grouping parentheses into a leaf's span; the hover
    leaves them out, as it gives none on a parenthesis. An index's own
    parentheses are part of the name and stay."""
    _, highlighted = shown("a.rel", text, needle)
    assert highlighted == highlight


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
    ("a.rel", 'exists file "x"', "exists"),
    ("a.rel", 'number of files of folder "x"', "number"),
    ("a.rel", 'if exists file "x" then 1 else 2', "then"),
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


def test_links_point_at_main() -> None:
    """Not a release tag: an unreleased build (or one whose version falls back
    to ``0.0.0``) would link to a tag that does not exist, a 404. On ``main``
    the worst a later heading rename can do is land on the top of the right
    page, and the anchor test above keeps a rename from going unnoticed."""
    assert (
        DOCS_URL == "https://github.com/jgstew/bigfix-relevance-analyzer/blob/main/docs/reference/"
    )


# ---------------------------------------------------------------------------
# Extraction is shared between diagnostics and hover
# ---------------------------------------------------------------------------


@pytest.fixture
def extractions(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """The URIs' paths each extraction ran for, in order."""
    calls: list[str] = []
    real = _extract_data

    def counted(path: Any, data: bytes) -> Any:
        calls.append(str(path))
        return real(path, data)

    monkeypatch.setattr(linter_module, "_extract_data", counted)
    return calls


def test_hovers_reuse_the_extraction_diagnostics_made(extractions: list[str]) -> None:
    linter = DocumentLinter()
    uri = "file:///workspace/a.rel"
    linter.diagnostics(uri, FILES)
    for character in (8, 14, 21, 29, 42):
        linter.hover(uri, FILES, (0, character))
    assert len(extractions) == 1


def test_a_changed_text_is_extracted_again(extractions: list[str]) -> None:
    linter = DocumentLinter()
    uri = "file:///workspace/a.rel"
    linter.diagnostics(uri, FILES)
    changed = FILES.replace('"x"', '"y"')
    found = linter.hover(uri, changed, (0, changed.index('"y"')))
    assert found is not None
    assert '"y"' in found["contents"]["value"]
    assert len(extractions) == 2


def test_the_same_text_under_another_language_is_extracted_as_that(
    extractions: list[str],
) -> None:
    """The extractor follows the file type, so the type is part of the key."""
    linter = DocumentLinter()
    uri = "untitled:Untitled-1"
    assert linter.hover(uri, FILES, (0, 8), "bigfix-relevance") is not None
    assert linter.hover(uri, FILES, (0, 8), "plaintext") is None
    assert linter.hover(uri, FILES, (0, 8), "bigfix-relevance") is not None


def test_the_extraction_cache_is_bounded(extractions: list[str]) -> None:
    linter = DocumentLinter()
    uris = [f"file:///workspace/{n}.rel" for n in range(linter_module.EXTRACTION_CACHE_SIZE + 1)]
    for uri in uris:
        linter.diagnostics(uri, FILES)
    linter.hover(uris[-1], FILES, (0, 8))
    assert len(extractions) == len(uris)
    linter.hover(uris[0], FILES, (0, 8))
    assert len(extractions) == len(uris) + 1


# ---------------------------------------------------------------------------
# Second review of #114
# ---------------------------------------------------------------------------


def test_a_name_filtered_out_by_platform_says_so_not_dialect() -> None:
    """``wmi`` is client relevance, Windows only: under macOS it is hidden by
    the platform, and blaming the dialect would be false."""
    linter = DocumentLinter(config=LintConfig(suggest=True, platform="macos"))
    found = linter.hover("file:///workspace/a.rel", "exists wmi", (0, 8))
    assert found is not None
    markdown = found["contents"]["value"]
    assert "not in client relevance" not in markdown
    assert "macos" in markdown


def test_a_name_from_the_other_dialect_names_the_dialect() -> None:
    """The control: a session inspector in a BES ``<Relevance>``, which is client."""
    markdown, _ = shown("a.bes", BES.format(body="exists bes computers"), "bes computers")
    assert "not in client relevance" in markdown


@pytest.mark.parametrize("dialect", [Dialect.UNCERTAIN, Dialect.BOTH])
def test_an_unresolved_dialect_is_never_named_as_one(dialect: Dialect) -> None:
    text = "name of operating system"
    found = describe(_analyze_cached(text, dialect, None), text.index("operating"))
    assert found is not None
    assert f"{dialect.value} relevance" not in found.markdown


@pytest.mark.parametrize("text", ["x of it", "exists x of it"])
def test_an_it_on_the_right_of_of_is_not_said_to_have_no_of(text: str) -> None:
    """Only the left side of an ``of`` binds ``it``; on the right, as the
    object, nothing outside it does -- but there is an ``of`` right there."""
    markdown, _ = shown("a.rel", text, "it")
    assert "no `of`" not in markdown
    assert "right" in markdown


def test_an_it_with_no_construct_around_it_still_says_so() -> None:
    markdown, _ = shown("a.rel", "exists it", "it")
    assert "nothing binds it" in markdown


def test_one_visible_unnarrowed_definition_is_not_one_of_one() -> None:
    doc = '<script>Relevance("name of operating system")</script>'
    markdown, _ = shown("a.html", doc, "operating")
    assert "one of 1" not in markdown
    assert markdown.startswith("**`operating system`** - inspector\n")


@pytest.mark.parametrize(
    ("text", "needle", "expected"),
    [
        ("NAME OF OPERATING SYSTEM", "OF", "**`OF`**"),
        ('EXISTS FILE "x" WHOSE (TRUE)', "WHOSE", "**`WHOSE`**"),
        ("IF TRUE THEN 1 ELSE 2", "THEN", "**`IF` ... `THEN` ... `ELSE`**"),
        ('"a" | "b"', "|", "**`|`**"),
        ('EXISTS FILE "x"', "FILE", "**`FILE`**"),
        ("NAME OF Operating   System", "System", "**`Operating System`**"),
        ('EXISTS FILE "x" WHOSE (SIZE OF IT > 0)', "IT", "**`IT`**"),
    ],
)
def test_every_title_uses_the_authors_spelling(text: str, needle: str, expected: str) -> None:
    """Not just operators: keywords, names and ``it`` too, so two hovers in one
    document never disagree on whose spelling they show. A name's words are
    joined by one space; signatures in the rows stay as the table writes them."""
    markdown, _ = shown("a.rel", text, needle)
    assert markdown.startswith(expected)


def test_closing_a_document_forgets_its_extraction(extractions: list[str]) -> None:
    linter = DocumentLinter()
    uri = "file:///workspace/a.rel"
    linter.diagnostics(uri, FILES)
    linter.forget(uri)
    linter.hover(uri, FILES, (0, 8))
    assert len(extractions) == 2
    linter.forget("file:///workspace/never-seen.rel")  # no error


ABSORB = "universal_relevance.md#errors-are-values-and-some-constructs-absorb-them"
GUARD = "client_relevance.md#only-if-guards-a-platform-specific-inspector"


@pytest.mark.parametrize(
    ("text", "needle", "page"),
    [
        ('exists file "x"', "exists", ABSORB),
        ('not exists file "x"', "not", ABSORB),
        ('number of files of folder "x"', "number", ABSORB),
        ('if exists file "x" then 1 else 2', "if", GUARD),
    ],
)
def test_exists_number_of_and_if_link_to_what_they_do_with_errors(
    text: str, needle: str, page: str
) -> None:
    """Every construct's hover links to the reference; for these three the
    section is what they do with an error, which is their surprising part."""
    markdown, _ = shown("a.rel", text, needle)
    assert f"]({DOCS_URL}{page})" in markdown


def test_the_extraction_cache_is_bounded_by_bytes(
    extractions: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A large BES document's extraction holds several MiB (8.7 MiB measured
    for 995 KiB), so the cache keeps documents up to a byte budget, not a count."""
    monkeypatch.setattr(linter_module, "EXTRACTION_CACHE_BYTES", 2 * len(FILES))
    linter = DocumentLinter()
    uris = [f"file:///workspace/{n}.rel" for n in range(3)]
    for uri in uris:
        linter.diagnostics(uri, FILES)
    linter.hover(uris[2], FILES, (0, 8))
    linter.hover(uris[1], FILES, (0, 8))
    assert len(extractions) == 3
    linter.hover(uris[0], FILES, (0, 8))
    assert len(extractions) == 4


def test_a_document_over_the_byte_budget_is_still_kept_while_it_is_the_latest(
    extractions: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one being edited and hovered is the reason the cache exists."""
    monkeypatch.setattr(linter_module, "EXTRACTION_CACHE_BYTES", 1)
    linter = DocumentLinter()
    uri = "file:///workspace/a.rel"
    linter.diagnostics(uri, FILES)
    linter.hover(uri, FILES, (0, 8))
    assert len(extractions) == 1
