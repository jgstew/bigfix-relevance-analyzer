"""Tests for :mod:`bigfix_relevance_analyzer.lsp.positions`: spans to editor ranges.

A :class:`~bigfix_relevance_analyzer.lint.TextSpan` is an offset into a site's
text. An editor wants a line and a UTF-16 character in the buffer it holds,
which keeps its line endings, its entities and its CDATA sections. Each test
maps a span and reads the buffer back at the range it got; the mapping is right
when that is the span's text, and ``None`` -- a whole-line fallback -- is right
whenever the buffer cannot be shown to hold it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bigfix_relevance_analyzer.extract import RelevanceSite, _extract_data
from bigfix_relevance_analyzer.lint import TextSpan
from bigfix_relevance_analyzer.lsp.positions import DocumentIndex, Range


def sites_of(name: str, text: str) -> tuple[list[RelevanceSite], DocumentIndex]:
    """The sites an editor buffer holding ``text`` yields, and its index."""
    data = text.encode("utf-8", errors="surrogatepass")
    return _extract_data(Path(name), data)[0], DocumentIndex(text, data)


def span_of(site: RelevanceSite, needle: str, occurrence: int = 0) -> TextSpan:
    start = -1
    for _ in range(occurrence + 1):
        start = site.text.index(needle, start + 1)
    return TextSpan(start, start + len(needle))


def utf16_to_index(line: str, character: int) -> int:
    """The code point index of UTF-16 offset ``character`` in ``line``."""
    units = 0
    for index, char in enumerate(line):
        if units >= character:
            return index
        units += 2 if ord(char) > 0xFFFF else 1
    assert units == character, "a range ended inside a surrogate pair or past the line"
    return len(line)


def read(text: str, found: Range) -> str:
    """What the buffer holds over ``found``, with LSP's own line breaks."""
    import re

    pieces = re.split(r"(\r\n|\r|\n)", text)
    lines, breaks = pieces[0::2], pieces[1::2]
    (start_line, start_char), (end_line, end_char) = found
    start = utf16_to_index(lines[start_line], start_char)
    end = utf16_to_index(lines[end_line], end_char)
    if start_line == end_line:
        return lines[start_line][start:end]
    middle = "".join(lines[i] + breaks[i] for i in range(start_line + 1, end_line))
    return lines[start_line][start:] + breaks[start_line] + middle + lines[end_line][:end]


def mapped(name: str, text: str, needle: str, site_index: int = 0) -> tuple[Range, str]:
    sites, index = sites_of(name, text)
    site = sites[site_index]
    found = index.site_range(site, span_of(site, needle))
    assert found is not None, f"{needle!r} in {name} did not map"
    return found, read(text, found)


# ---------------------------------------------------------------------------
# Text extractors: through the site's line and column
# ---------------------------------------------------------------------------


def test_a_markdown_fence() -> None:
    found, text = mapped(
        "a.md", "# T\n\n```relevance\nexists totally bogus\n```\n", "totally bogus"
    )
    assert found == ((3, 7), (3, 20))
    assert text == "totally bogus"


def test_an_indented_markdown_fence() -> None:
    doc = "- item\n\n    ```relevance\n    exists totally bogus\n    ```\n"
    found, text = mapped("a.md", doc, "totally bogus")
    assert found == ((3, 11), (3, 24))
    assert text == "totally bogus"


def test_a_rel_file_with_leading_blank_lines_and_indentation() -> None:
    doc = '\n\n   exists file "x"\n     whose (size of it = "big")\n'
    found, text = mapped("a.rel", doc, 'size of it = "big"')
    assert found == ((3, 12), (3, 30))
    assert text == 'size of it = "big"'


def test_a_bsr_file() -> None:
    found, text = mapped("a.bsr", "  names of bes computers whose (bogus thing)", "bogus thing")
    assert found == ((0, 32), (0, 43))
    assert text == "bogus thing"


def test_an_html_processing_instruction_mid_line() -> None:
    doc = "<html>\n<p>Name: <?Relevance names of bogus things ?></p>\n</html>\n"
    found, text = mapped("a.ojo", doc, "bogus things")
    assert found == ((1, 30), (1, 42))
    assert text == "bogus things"


def test_a_javascript_call_with_an_escaped_quote() -> None:
    doc = '<script>\n  var x = Relevance("exists \\"a\\" whose (bogus thing)");\n</script>\n'
    found, text = mapped("a.ojo", doc, "bogus thing")
    assert text == "bogus thing"
    assert found[0][0] == 1


def test_a_second_site_on_the_same_line() -> None:
    doc = "<p><?Relevance bogus one ?> and <?Relevance bogus two ?></p>"
    found, text = mapped("a.ojo", doc, "bogus two", site_index=1)
    assert text == "bogus two"
    assert found == ((0, 44), (0, 53))


@pytest.mark.parametrize(("name", "break_"), [("a.md", "\r\n"), ("a.rel", "\r\n"), ("a.rel", "\r")])
def test_crlf_and_cr_line_endings_do_not_drift(name: str, break_: str) -> None:
    lines = ['exists file "x"', '  whose (size of it = "big")', '  and exists bogus thing "y"']
    if name == "a.md":
        lines = ["# T", "", "```relevance", *lines, "```", ""]
    doc = break_.join(lines)
    for needle in ('size of it = "big"', "bogus thing"):
        _, text = mapped(name, doc, needle)
        assert text == needle


def test_astral_characters_count_two_utf16_units() -> None:
    doc = 'exists file "\U0001f600\U0001f600" whose (size of it = "big")'
    found, text = mapped("a.rel", doc, 'size of it = "big"')
    start = doc.index("size")
    assert found == ((0, start + 2), (0, start + 2 + len('size of it = "big"')))
    assert text == 'size of it = "big"'


def test_a_multi_line_span() -> None:
    doc = '# T\n```relevance\nexists file "x" whose (size of it\n    = "big")\n```\n'
    found, text = mapped("a.md", doc, 'size of it\n    = "big"')
    assert found == ((2, 23), (3, 11))
    assert text == 'size of it\n    = "big"'


def test_a_site_with_no_column_falls_back() -> None:
    sites, index = sites_of("a.ojo", "<p><?Relevance\n  names of bogus things ?></p>")
    (site,) = sites
    assert index.site_range(site, span_of(site, "bogus things")) is None


def test_the_guard_falls_back_when_decoding_replaced_a_character() -> None:
    """A lone surrogate the editor holds decodes, through UTF-8, to several
    replacement characters: offsets after it no longer line up, and a range
    that would underline the wrong text must not be returned."""
    # Enough after the span that the shifted range still fits on the line:
    # only reading the buffer back can tell it is wrong.
    doc = 'exists file "\ud800" whose (size of it = "big") and exists file "y"'
    sites, index = sites_of("a.rel", doc)
    (site,) = sites
    assert "\ufffd" in site.text
    assert index.site_range(site, span_of(site, 'size of it = "big"')) is None


def test_the_guard_still_maps_before_a_replaced_character() -> None:
    doc = 'exists bogus thing "\ud800"'
    sites, index = sites_of("a.rel", doc)
    (site,) = sites
    found = index.site_range(site, span_of(site, "bogus thing"))
    assert found == ((0, 7), (0, 18))


def test_a_span_out_of_the_sites_text_falls_back() -> None:
    sites, index = sites_of("a.rel", "exists file")
    (site,) = sites
    assert index.site_range(site, TextSpan(5, 99)) is None


# ---------------------------------------------------------------------------
# An empty span (a parse error at the end of the statement)
# ---------------------------------------------------------------------------


def test_an_empty_span_at_the_end_covers_the_last_character() -> None:
    doc = 'exists file "x" whose (it\n    is\n'
    sites, index = sites_of("a.rel", doc)
    (site,) = sites
    end = len(site.text)
    assert index.site_range(site, TextSpan(end, end)) == ((1, 5), (1, 6))


def test_an_empty_span_inside_covers_the_next_character() -> None:
    sites, index = sites_of("a.rel", "exists file")
    (site,) = sites
    assert index.site_range(site, TextSpan(7, 7)) == ((0, 7), (0, 8))


# ---------------------------------------------------------------------------
# BES XML: through the source map's bytes
# ---------------------------------------------------------------------------

BES = (
    '<?xml version="1.0" encoding="UTF-8"?>\n<BES>\n<Task>\n'
    "\t<Title>t</Title>\n{body}\n</Task>\n</BES>\n"
)


def bes(body: str, break_: str = "\n") -> str:
    return BES.format(body=body).replace("\n", break_)


def test_a_relevance_element_mid_line() -> None:
    found, text = mapped(
        "a.bes", bes("\t<Relevance>exists totally bogus</Relevance>"), "totally bogus"
    )
    assert found == ((4, 19), (4, 32))
    assert text == "totally bogus"


def test_an_entity_before_the_span() -> None:
    doc = bes('\t<Relevance>size of file "x" &gt; 3 and exists totally bogus</Relevance>')
    found, text = mapped("a.bes", doc, "totally bogus")
    assert text == "totally bogus"
    assert found[0] == (4, doc.split("\n")[4].index("totally"))


def test_a_span_holding_an_entity_reads_back_as_written() -> None:
    doc = bes('\t<Relevance>exists file "x" whose (size of it &gt; "big")</Relevance>')
    _, text = mapped("a.bes", doc, 'size of it > "big"')
    assert text == 'size of it &gt; "big"'


def test_a_relevance_wholly_inside_cdata() -> None:
    doc = bes("\t<Relevance><![CDATA[exists totally bogus]]></Relevance>")
    _, text = mapped("a.bes", doc, "totally bogus")
    assert text == "totally bogus"


def test_a_span_straddling_cdata_falls_back() -> None:
    doc = bes("\t<Relevance>exists totally <![CDATA[bogus]]></Relevance>")
    sites, index = sites_of("a.bes", doc)
    (site,) = sites
    assert index.site_range(site, span_of(site, "totally bogus")) is None


@pytest.mark.parametrize("break_", ["\n", "\r\n"])
def test_a_multi_line_relevance_in_bes(break_: str) -> None:
    body = (
        '\t<Relevance>exists file "x"\n\twhose (size of it = "big")\n'
        "\tand exists bogus thing</Relevance>"
    )
    doc = bes(body, break_)
    for needle, line in (('size of it = "big"', 5), ("bogus thing", 6)):
        found, text = mapped("a.bes", doc, needle)
        assert text == needle
        assert found[0][0] == line


def test_a_relevance_body_starting_on_the_next_line_maps_where_it_is() -> None:
    """``site.line`` (and so ``Finding.line``) is the element's body line here,
    one above the statement; the source map knows better, and the editor
    underlines the statement where it is."""
    doc = bes("\t<Relevance>\n\t\texists totally bogus\n\t</Relevance>")
    sites, index = sites_of("a.bes", doc)
    (site,) = sites
    assert site.line == 5
    found = index.site_range(site, span_of(site, "totally bogus"))
    assert found == ((5, 9), (5, 22))


def test_an_astral_character_in_bes() -> None:
    doc = bes('\t<Relevance>exists file "\U0001f600" whose (bogus thing)</Relevance>')
    found, text = mapped("a.bes", doc, "bogus thing")
    assert text == "bogus thing"
    assert found[0][1] == doc.split("\n")[4].index("bogus") + 1


def test_actionscript_in_bes_maps_through_the_source_map() -> None:
    doc = bes(
        '\t<DefaultAction ID="Action1"><ActionScript MIMEType="application/x-Fixlet-Windows-Shell">'
        'wait\nparameter "x" = "{name of bogus thing}"</ActionScript></DefaultAction>'
    )
    found, text = mapped("a.bes", doc, "bogus thing")
    assert text == "bogus thing"
    assert found[0][0] == 5


def test_a_description_processing_instruction_in_bes() -> None:
    doc = bes("\t<Description>see &lt;?Relevance names of bogus things ?&gt;</Description>")
    _, text = mapped("a.bes", doc, "bogus things")
    assert text == "bogus things"


def test_a_bes_site_without_a_source_map_falls_back() -> None:
    from bigfix_relevance_analyzer.extract import extract_relevance_from_bes_xml

    doc = bes("\t<Relevance>exists totally bogus</Relevance>")
    (site,) = extract_relevance_from_bes_xml(doc)  # a str: no source map
    assert site.source_map is None
    index = DocumentIndex(doc, doc.encode("utf-8"))
    assert index.site_range(site, span_of(site, "totally bogus")) is None


# ---------------------------------------------------------------------------
# The index itself
# ---------------------------------------------------------------------------


def test_lines_split_where_lsp_splits_them() -> None:
    index = DocumentIndex("a\r\nb\rc\nd\x0ce f", b"")
    assert index.lines == ["a", "b", "c", "d\x0ce f"]


def test_line_length_counts_utf16_units() -> None:
    index = DocumentIndex("a\U0001f600b\n", b"")
    assert index.line_length(0) == 4
    assert index.line_length(1) == 0
    assert index.line_length(5) == 0
