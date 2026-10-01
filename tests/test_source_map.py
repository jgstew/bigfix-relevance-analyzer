"""Tests for :class:`~bigfix_relevance_analyzer.extract.SourceMap`.

A site's text is decoded -- entities resolved, CDATA merged, CRLF folded to LF
-- and stripped, so it cannot be searched for in the file it came from. The
map is what lets a fix be written back: it says which bytes of the file each
character of :attr:`RelevanceSite.text` came from.

The property every test here holds is the same one: decoding the bytes the map
points at reproduces the site's text exactly.
"""

from __future__ import annotations

import html

import pytest

from bigfix_relevance_analyzer.extract import (
    HtmlContext,
    RelevanceSite,
    SourceMap,
    extract_relevance_from_actionscript,
    extract_relevance_from_bes_xml,
    extract_relevance_from_html_text,
    extract_relevance_from_markdown,
)

HEAD = b'<?xml version="1.0" encoding="UTF-8"?>\n<BES><Task>'
TAIL = b"</Task></BES>\n"


def bes(inner: bytes) -> bytes:
    return HEAD + inner + TAIL


def decoded(data: bytes, source_map: SourceMap) -> str:
    """The text ``source_map`` says the site was decoded from.

    Independent of the implementation on purpose: plain spans are UTF-8, an
    atomic span is a line ending or an XML reference.
    """
    out: list[str] = []
    for span in source_map.spans:
        raw = data[span.raw_start : span.raw_end]
        if not span.atomic:
            out.append(raw.decode("utf-8"))
        elif raw in (b"\r\n", b"\r"):
            out.append("\n")
        else:
            assert raw.startswith(b"&") and raw.endswith(b";"), raw
            out.append(html.unescape(raw.decode("ascii")))
    return "".join(out)


def assert_round_trips(data: bytes, site: RelevanceSite) -> None:
    source_map = site.source_map
    assert source_map is not None, site
    position = 0
    for span in source_map.spans:
        assert span.start == position
        assert span.end > span.start
        position = span.end
    assert position == len(site.text)
    assert decoded(data, source_map) == site.text


def only_site(data: bytes) -> RelevanceSite:
    (site,) = extract_relevance_from_bes_xml(data)
    return site


CASES = {
    "plain": b'<Relevance>exists values of setting "x" of client</Relevance>',
    "surrounding whitespace": b'<Relevance>\n   exists file "a"  \n </Relevance>',
    "lt entity": b'<Relevance>exists file "a" and 1 &lt; 2</Relevance>',
    "quot entity": b"<Relevance>exists setting &quot;x&quot; of client</Relevance>",
    "character references": b"<Relevance>exists file &#34;a&#x22;</Relevance>",
    "cdata": b'<Relevance><![CDATA[exists file "a" and 1 < 2]]></Relevance>',
    "cdata split mid-statement": (
        b'<Relevance>exists values of setting "x" of cl<![CDATA[ient]]></Relevance>'
    ),
    "crlf": b'<Relevance>exists file "a"\r\n or exists file "b"\r\n</Relevance>',
    "lone cr": b'<Relevance>exists file "a"\r or exists file "b"</Relevance>',
    "multi-byte utf-8": (
        '<Relevance>exists file "x\u00e9y \U0001f600" of folder "\u00fc"</Relevance>'
    ).encode(),
    "multi-line start tag": (
        b'<SuccessCriteria\n  Option="CustomRelevance"\n>true</SuccessCriteria>'
    ),
}


@pytest.mark.parametrize("inner", CASES.values(), ids=CASES.keys())
def test_each_site_maps_back_to_the_bytes_it_was_decoded_from(inner: bytes) -> None:
    data = bes(inner)
    assert_round_trips(data, only_site(data))


def test_actionscript_substitutions_map_back() -> None:
    data = bes(
        b'<Action ID="a"><ActionScript MIMEType="application/x-Fixlet-Windows-Shell">'
        b'parameter "v"="{exists values of setting &quot;x&quot; of client}"\r\n'
        b'if {exists file "a"} \r\n'
        b'  wait {  name of   operating system } {{literal}} {"&lt;"}\n'
        b"endif</ActionScript></Action>"
    )
    sites = extract_relevance_from_bes_xml(data)
    assert [site.text for site in sites] == [
        'exists values of setting "x" of client',
        'exists file "a"',
        "name of   operating system",
        '"<"',
    ]
    for site in sites:
        assert_round_trips(data, site)


def test_description_html_sites_map_back() -> None:
    data = bes(
        b"<Description>&lt;p&gt;Version: &lt;?relevance  version of client ?&gt;&lt;/p&gt;"
        b"<![CDATA[<script>Relevance(' names of bes computers ');</script>]]>"
        b"</Description>"
    )
    sites = extract_relevance_from_bes_xml(data)
    assert [site.text for site in sites] == ["version of client", "names of bes computers"]
    for site in sites:
        assert_round_trips(data, site)


def test_two_identical_statements_get_their_own_maps() -> None:
    data = bes(b'<Relevance>exists file "a"</Relevance>\n<Relevance>exists file "a"</Relevance>')
    first, second = extract_relevance_from_bes_xml(data)
    assert first.source_map is not None and second.source_map is not None
    assert first.source_map.spans[0].raw_start < second.source_map.spans[0].raw_start
    assert_round_trips(data, first)
    assert_round_trips(data, second)


def test_the_map_is_left_out_of_equality_and_serialization() -> None:
    """Sites from expat and from lxml, or from bytes and from a string, still
    compare equal -- and outputs that predate the map do not change."""
    data = bes(b'<Relevance>exists file "a"</Relevance>')
    site = only_site(data)
    shifted = only_site(bes(b'<Relevance>   exists file "a"</Relevance>'))
    assert site.source_map != shifted.source_map
    assert site == shifted and hash(site) == hash(shifted)
    assert "source_map" not in site.to_dict()


def test_raw_range_refuses_to_split_an_atomic_piece() -> None:
    data = bes(b"<Relevance>1 &lt; 2</Relevance>")
    site = only_site(data)
    assert site.source_map is not None
    lt = site.text.index("<")
    start, end = site.source_map.raw_range(lt, lt + 1) or (0, 0)
    assert data[start:end] == b"&lt;"
    assert site.source_map.raw_range(0, 1) is not None
    two = site.text.index("2")
    assert site.source_map.raw_range(0, two + 1) is not None


def test_raw_range_refuses_a_range_across_markup() -> None:
    """`cl` and `ient` are adjacent in the text but not in the file."""
    data = bes(b"<Relevance>name of cl<![CDATA[ient]]></Relevance>")
    site = only_site(data)
    assert site.source_map is not None
    client = site.text.index("client")
    assert site.source_map.raw_range(client, client + 2) is not None
    assert site.source_map.raw_range(client + 2, client + 6) is not None
    assert site.source_map.raw_range(client, client + 6) is None


def test_a_document_in_another_encoding_has_no_map() -> None:
    """Byte offsets are only trusted where the bytes are the UTF-8 text."""
    data = (
        '<?xml version="1.0" encoding="UTF-16"?><BES><Task>'
        '<Relevance>exists file "a"</Relevance></Task></BES>'
    ).encode("utf-16")
    site = only_site(data)
    assert site.text == 'exists file "a"'
    assert site.source_map is None


def test_latin_1_maps_only_the_elements_it_can() -> None:
    data = (
        '<?xml version="1.0" encoding="ISO-8859-1"?><BES><Task>'
        '<Relevance>exists file "x\u00e9y"</Relevance>'
        '<Relevance>exists file "a"</Relevance></Task></BES>'
    ).encode("latin-1")
    accented, plain = extract_relevance_from_bes_xml(data)
    assert accented.source_map is None
    assert_round_trips(data, plain)


def test_sites_from_text_have_no_map() -> None:
    """Only BES XML read as bytes knows where its text sat in a file, for now.

    A ``str`` document is encoded before parsing, so offsets into it would
    describe bytes the caller never had.
    """
    for site in (
        *extract_relevance_from_bes_xml("<BES><Task><Relevance>true</Relevance></Task></BES>"),
        *extract_relevance_from_actionscript("wait {name of operating system}"),
        *extract_relevance_from_html_text("<?relevance true ?>", context=HtmlContext.CONSOLE),
        *extract_relevance_from_markdown("```relevance\ntrue\n```\n"),
    ):
        assert site.source_map is None
