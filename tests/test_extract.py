"""Unit tests for the relevance extractor.

Fixtures here are inline and minimal; `test_examples.py` covers the real
content corpus under `tests/examples/`.
"""

import logging
import sys

import pytest

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import (
    HtmlContext,
    RelevanceSite,
    extract_relevance_from_actionscript,
    extract_relevance_from_bes_xml,
    extract_relevance_from_file,
    extract_relevance_from_html_text,
    extract_relevance_from_markdown,
    looks_like_clientui,
)


def texts(sites: list[RelevanceSite]) -> list[str]:
    return [site.text for site in sites]


def kinds_lines(sites: list[RelevanceSite]) -> list[tuple[str, int]]:
    return [(site.kind, site.line) for site in sites]


# --------------------------------------------------------------------------
# ActionScript `{...}` substitution scanner
# --------------------------------------------------------------------------


def test_actionscript_simple_substitution() -> None:
    sites = extract_relevance_from_actionscript('appendfile {parameter "RootServerURL"}')
    assert len(sites) == 1
    assert sites[0].kind == "actionscript-substitution"
    assert sites[0].text == 'parameter "RootServerURL"'
    assert sites[0].line == 1
    assert sites[0].dialect is Dialect.CLIENT


def test_actionscript_no_substitution() -> None:
    assert extract_relevance_from_actionscript("waithidden cmd.exe /c dir") == []


def test_actionscript_escaped_braces_are_literal() -> None:
    """`{{` and `}}` are literal braces in ActionScript, not a substitution."""
    assert extract_relevance_from_actionscript("appendfile {{ not relevance }}") == []


def test_actionscript_escaped_brace_before_real_substitution() -> None:
    sites = extract_relevance_from_actionscript("appendfile {{literal}} and {name of it}")
    assert texts(sites) == ["name of it"]


def test_actionscript_brace_in_relevance_string_literal_does_not_terminate() -> None:
    """A `}` inside a relevance string literal must not close the substitution."""
    sites = extract_relevance_from_actionscript('appendfile { (parameter "a}b") }')
    assert texts(sites) == ['(parameter "a}b")']


def test_actionscript_two_substitutions_on_one_line() -> None:
    sites = extract_relevance_from_actionscript(
        'run cp "{pathname of client}" "{if windows of operating system then "\\" else "/"}"'
    )
    assert len(sites) == 2
    assert texts(sites) == [
        "pathname of client",
        'if windows of operating system then "\\" else "/"',
    ]
    assert [site.line for site in sites] == [1, 1]


def test_actionscript_line_numbers_are_one_based_within_the_body() -> None:
    body = "\n".join(
        [
            "action uses wow64 redirection false",
            'parameter "n"="{number of folders of client}"',
            "// nothing here",
            "exit {number of files of client}",
        ]
    )
    sites = extract_relevance_from_actionscript(body)
    assert [site.line for site in sites] == [2, 4]


def test_actionscript_multiline_substitution_reports_opening_line() -> None:
    body = "exit {\n  number of\n  folders of client\n}\nappendfile {name of it}"
    sites = extract_relevance_from_actionscript(body)
    assert [site.line for site in sites] == [1, 5]
    assert sites[0].text == "number of\n  folders of client"


def test_actionscript_createfile_heredoc_content_is_excluded() -> None:
    body = "\n".join(
        [
            "createfile until END_OF_FILE",
            "{ not a substitution, this is heredoc content }",
            "END_OF_FILE",
            "appendfile {name of it}",
        ]
    )
    sites = extract_relevance_from_actionscript(body)
    assert texts(sites) == ["name of it"]
    assert sites[0].line == 4


def test_actionscript_appendfile_heredoc_content_is_excluded() -> None:
    body = "appendfile until _END_\n{nope}\n_END_\nexit {name of it}"
    assert texts(extract_relevance_from_actionscript(body)) == ["name of it"]


def test_actionscript_heredoc_terminator_must_match_exactly() -> None:
    """A different token does not end the heredoc, so its braces stay excluded."""
    body = "createfile until END_OF_FILE\n{nope}\nSOMETHING_ELSE\n{still nope}"
    assert extract_relevance_from_actionscript(body) == []


def test_actionscript_unterminated_substitution_warns_and_yields_nothing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        sites = extract_relevance_from_actionscript("exit {number of folders of client")
    assert sites == []
    assert any(record.levelno == logging.WARNING for record in caplog.records)


# --------------------------------------------------------------------------
# HTML / text scanner: <?Relevance ?> processing instructions
# --------------------------------------------------------------------------


@pytest.mark.parametrize("opener", ["<?relevance", "<?Relevance", "<?RELEVANCE"])
def test_pi_scanner_is_case_insensitive(opener: str) -> None:
    sites = extract_relevance_from_html_text(
        f"<p>{opener} number of bes computers ?></p>", context=HtmlContext.CONSOLE
    )
    assert len(sites) == 1
    assert sites[0].kind == "relevance-pi"
    assert sites[0].text == "number of bes computers"


def test_pi_scanner_multiline_body_and_line_numbers() -> None:
    text = "line one\n<?Relevance number of\n  bes computers ?>\n<?Relevance now ?>"
    sites = extract_relevance_from_html_text(text, context=HtmlContext.CONSOLE)
    assert kinds_lines(sites) == [("relevance-pi", 2), ("relevance-pi", 4)]
    assert sites[0].text == "number of\n  bes computers"


def test_pi_scanner_ignores_other_processing_instructions() -> None:
    text = '<?xml version="1.0"?>\n<?php echo "hi"; ?>'
    assert extract_relevance_from_html_text(text, context=HtmlContext.CONSOLE) == []


def test_pi_scanner_unterminated_warns_and_yields_nothing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        sites = extract_relevance_from_html_text(
            "<?Relevance number of bes computers", context=HtmlContext.CONSOLE
        )
    assert sites == []
    assert any(record.levelno == logging.WARNING for record in caplog.records)


# --------------------------------------------------------------------------
# HTML / text scanner: JavaScript Relevance() / EvaluateRelevance() calls
# --------------------------------------------------------------------------


def test_js_call_single_quoted() -> None:
    sites = extract_relevance_from_html_text(
        "x = Relevance('name of current console user');", context=HtmlContext.CONSOLE
    )
    assert len(sites) == 1
    assert sites[0].kind == "javascript-call"
    assert sites[0].text == "name of current console user"
    assert sites[0].dialect is Dialect.SESSION


def test_js_call_double_quoted_evaluate_relevance() -> None:
    sites = extract_relevance_from_html_text(
        'x = EvaluateRelevance("number of bes computers");', context=HtmlContext.CONSOLE
    )
    assert texts(sites) == ["number of bes computers"]


def test_js_call_escaped_quotes_inside_the_literal() -> None:
    sites = extract_relevance_from_html_text(
        """x = EvaluateRelevance('tables "id=\\'t\\'" of html it');""",
        context=HtmlContext.CONSOLE,
    )
    assert texts(sites) == ["""tables "id=\\'t\\'" of html it"""]


def test_js_call_several_on_one_line() -> None:
    sites = extract_relevance_from_html_text(
        "a = Relevance('id of current fixlet') + Relevance('name of current console user');",
        context=HtmlContext.CONSOLE,
    )
    assert texts(sites) == ["id of current fixlet", "name of current console user"]
    assert [site.line for site in sites] == [1, 1]


@pytest.mark.parametrize(
    "snippet",
    [
        "results = EvaluateRelevance(relevance);",
        "results = Relevance(relevance, callbackObj);",
        "$('#d').html(EvaluateRelevance('trs of ' + SessionRelevanceQuery));",
        "results = EvaluateRelevance();",
    ],
)
def test_js_call_non_literal_argument_is_skipped(snippet: str) -> None:
    """Only a single complete string literal is a usable relevance statement."""
    assert extract_relevance_from_html_text(snippet, context=HtmlContext.CONSOLE) == []


def test_js_call_name_must_not_be_part_of_a_longer_identifier() -> None:
    text = "bigfix.relevance.errorWrapper('nope'); myRelevance('nope');"
    assert extract_relevance_from_html_text(text, context=HtmlContext.CONSOLE) == []


# --------------------------------------------------------------------------
# ClientUI vs console: dialect comes from file context, not statement content
# --------------------------------------------------------------------------

CLIENTUI_PI = "<?Relevance number of relevant fixlets of sites ?>"
CONSOLE_JS = "x = EvaluateRelevance('number of bes computers');"


def test_clientui_html_pi_is_client_relevance() -> None:
    sites = extract_relevance_from_html_text(CLIENTUI_PI, context=HtmlContext.CLIENTUI)
    assert [site.dialect for site in sites] == [Dialect.CLIENT]


def test_console_html_pi_is_session_relevance() -> None:
    sites = extract_relevance_from_html_text(CLIENTUI_PI, context=HtmlContext.CONSOLE)
    assert [site.dialect for site in sites] == [Dialect.SESSION]


def test_js_call_is_session_relevance_even_in_clientui_context() -> None:
    """A ClientUI cannot evaluate relevance from JS, so such a call is not one."""
    sites = extract_relevance_from_html_text(CONSOLE_JS, context=HtmlContext.CLIENTUI)
    assert [site.dialect for site in sites] == [Dialect.SESSION]


def test_clientui_html_with_both_mechanisms_degrades_pi_to_uncertain() -> None:
    """Contradictory context signals must not silently assert client relevance."""
    sites = extract_relevance_from_html_text(
        f"{CLIENTUI_PI}\n{CONSOLE_JS}", context=HtmlContext.CLIENTUI
    )
    assert [(site.kind, site.dialect) for site in sites] == [
        ("relevance-pi", Dialect.UNCERTAIN),
        ("javascript-call", Dialect.SESSION),
    ]


def test_console_html_with_both_mechanisms_stays_session() -> None:
    sites = extract_relevance_from_html_text(
        f"{CLIENTUI_PI}\n{CONSOLE_JS}", context=HtmlContext.CONSOLE
    )
    assert [site.dialect for site in sites] == [Dialect.SESSION, Dialect.SESSION]


def test_unknown_html_pi_alone_gets_no_context_dialect() -> None:
    """Neither renderer is established, so a static substitution proves nothing."""
    sites = extract_relevance_from_html_text("now", context=HtmlContext.UNKNOWN)
    assert sites == []
    sites = extract_relevance_from_html_text(CLIENTUI_PI, context=HtmlContext.UNKNOWN)
    assert sites[0].context_dialect is Dialect.UNCERTAIN


def test_unknown_html_with_a_js_call_is_session() -> None:
    """A JS relevance call is proof the renderer is not a ClientUI, marker or not."""
    sites = extract_relevance_from_html_text(
        f"{CLIENTUI_PI}\n{CONSOLE_JS}", context=HtmlContext.UNKNOWN
    )
    assert [(site.kind, site.context_dialect) for site in sites] == [
        ("relevance-pi", Dialect.SESSION),
        ("javascript-call", Dialect.SESSION),
    ]


@pytest.mark.parametrize(
    "marker",
    [
        '<meta version="1.0.0" product="CustomDashboardClientUI"/>',
        '<a href="cid:load?page=_dashboard.html">refresh</a>',
        '<a href="takeoffer:123">take</a>',
    ],
)
def test_looks_like_clientui_detects_corroborating_markers(marker: str) -> None:
    assert looks_like_clientui(f"<html><body>{marker}</body></html>") is True


def test_looks_like_clientui_is_false_without_markers() -> None:
    assert looks_like_clientui("<html><body><?Relevance now ?></body></html>") is False


# --------------------------------------------------------------------------
# BES XML extraction
# --------------------------------------------------------------------------

FIXLET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<BES>
\t<Fixlet>
\t\t<Title>Example</Title>
\t\t<Relevance>windows of operating system</Relevance>
\t\t<Relevance><![CDATA[exists files "a.txt"]]></Relevance>
\t\t<DefaultAction ID="Action1">
\t\t\t<ActionScript MIMEType="application/x-Fixlet-Windows-Shell"><![CDATA[
appendfile {name of operating system}
]]></ActionScript>
\t\t\t<SuccessCriteria Option="CustomRelevance">exists file "b.txt"</SuccessCriteria>
\t\t</DefaultAction>
\t</Fixlet>
</BES>
"""


def test_bes_xml_extracts_relevance_elements() -> None:
    sites = [s for s in extract_relevance_from_bes_xml(FIXLET_XML) if s.kind == "relevance"]
    assert kinds_lines(sites) == [("relevance", 5), ("relevance", 6)]
    assert texts(sites) == ["windows of operating system", 'exists files "a.txt"']
    assert all(site.dialect is Dialect.CLIENT for site in sites)


def test_bes_xml_extracts_custom_success_criteria() -> None:
    sites = [s for s in extract_relevance_from_bes_xml(FIXLET_XML) if s.kind == "success-criteria"]
    assert kinds_lines(sites) == [("success-criteria", 11)]
    assert texts(sites) == ['exists file "b.txt"']


@pytest.mark.parametrize("option", ["RunToCompletion", "OriginalRelevance"])
def test_bes_xml_skips_non_custom_success_criteria(option: str) -> None:
    xml = f'<BES><Fixlet><SuccessCriteria Option="{option}"></SuccessCriteria></Fixlet></BES>'
    assert extract_relevance_from_bes_xml(xml) == []


def test_bes_xml_extracts_actionscript_substitutions_with_absolute_lines() -> None:
    all_sites = extract_relevance_from_bes_xml(FIXLET_XML)
    sites = [s for s in all_sites if s.kind == "actionscript-substitution"]
    assert kinds_lines(sites) == [("actionscript-substitution", 9)]
    assert texts(sites) == ["name of operating system"]


def test_bes_xml_extracts_analysis_property() -> None:
    xml = (
        "<BES>\n<Analysis>\n"
        '<Property Name="p" ID="1">name of operating system</Property>\n'
        "</Analysis>\n</BES>"
    )
    sites = extract_relevance_from_bes_xml(xml)
    assert kinds_lines(sites) == [("analysis-property", 3)]
    assert texts(sites) == ["name of operating system"]
    assert sites[0].dialect is Dialect.CLIENT


def test_bes_xml_property_outside_analysis_is_not_a_relevance_site() -> None:
    """`<Property>` is only an analysis property inside an Analysis."""
    xml = "<BES>\n<Fixlet>\n<MIMEField><Property>x</Property></MIMEField>\n</Fixlet>\n</BES>"
    assert extract_relevance_from_bes_xml(xml) == []


@pytest.mark.parametrize(
    "attrs",
    ['MIMEType="application/x-Fixlet-Windows-Shell"', ""],
)
def test_bes_xml_actionscript_mimetype_accepted(attrs: str) -> None:
    xml = f"<BES><Fixlet><ActionScript {attrs}>exit {{name of it}}</ActionScript></Fixlet></BES>"
    assert texts(extract_relevance_from_bes_xml(xml)) == ["name of it"]


def test_bes_xml_actionscript_other_mimetype_is_skipped() -> None:
    xml = (
        '<BES><Fixlet><ActionScript MIMEType="application/x-sh">'
        "exit {name of it}</ActionScript></Fixlet></BES>"
    )
    assert extract_relevance_from_bes_xml(xml) == []


def test_bes_xml_description_yields_session_relevance() -> None:
    xml = (
        "<BES>\n<Task>\n"
        "<Description><![CDATA[<P><?relevance names of current fixlets?></P>\n"
        "<script>document.write(Relevance('name of current console user'));</script>]]>"
        "</Description>\n"
        "<Relevance>windows of operating system</Relevance>\n"
        "</Task>\n</BES>"
    )
    sites = extract_relevance_from_bes_xml(xml)
    assert [(s.kind, s.line, s.dialect) for s in sites] == [
        ("relevance-pi", 3, Dialect.SESSION),
        ("javascript-call", 4, Dialect.SESSION),
        ("relevance", 5, Dialect.CLIENT),
    ]


def test_bes_xml_context_label_names_the_element_path() -> None:
    sites = extract_relevance_from_bes_xml(FIXLET_XML)
    assert all(site.context for site in sites)
    relevance = next(site for site in sites if site.kind == "relevance")
    assert relevance.context == "BES/Fixlet/Relevance"


def test_bes_xml_accepts_bytes() -> None:
    sites = extract_relevance_from_bes_xml(FIXLET_XML.encode())
    assert texts(sites)[0] == "windows of operating system"


def test_bes_xml_unparsable_returns_empty_and_warns(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        sites = extract_relevance_from_bes_xml("<BES><Fixlet><Relevance>oops</BES>")
    assert sites == []
    assert any(record.levelno == logging.WARNING for record in caplog.records)


def test_bes_xml_entities_and_cdata_arrive_decoded() -> None:
    xml = "<BES><Fixlet><Relevance>a &amp; b &lt; c</Relevance></Fixlet></BES>"
    assert texts(extract_relevance_from_bes_xml(xml)) == ["a & b < c"]


# --------------------------------------------------------------------------
# lxml adapter: must agree with expat on every line number
# --------------------------------------------------------------------------

MULTILINE_START_TAG_XML = """<?xml version="1.0" encoding="UTF-8"?>
<BES>
\t<Fixlet>
\t\t<Relevance>windows of operating system</Relevance>
\t\t<DefaultAction
\t\t\tID="Action1">
\t\t\t<ActionScript
\t\t\t\tMIMEType="application/x-Fixlet-Windows-Shell"><![CDATA[
appendfile {name of operating system}
exit {number of files of client}
]]></ActionScript>
\t\t</DefaultAction>
\t</Fixlet>
</BES>
"""


def test_lxml_adapter_line_numbers_match_expat() -> None:
    """Guards the off-by-one that would shift every reported line in a file."""
    lxml_etree = pytest.importorskip("lxml.etree")
    from bigfix_relevance_analyzer.extract import extract_relevance_from_lxml_tree

    data = MULTILINE_START_TAG_XML.encode()
    tree = lxml_etree.fromstring(data).getroottree()

    from_expat = extract_relevance_from_bes_xml(data)
    from_lxml = extract_relevance_from_lxml_tree(tree)

    assert from_expat == from_lxml
    assert kinds_lines(from_expat) == [
        ("relevance", 4),
        ("actionscript-substitution", 9),
        ("actionscript-substitution", 10),
    ]


def test_package_imports_without_lxml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "lxml", None)
    monkeypatch.setitem(sys.modules, "lxml.etree", None)
    for name in [n for n in list(sys.modules) if n.startswith("bigfix_relevance_analyzer")]:
        monkeypatch.delitem(sys.modules, name)

    import bigfix_relevance_analyzer

    assert bigfix_relevance_analyzer.extract_relevance_from_bes_xml(FIXLET_XML)


# --------------------------------------------------------------------------
# Markdown, plain text, extension dispatch
# --------------------------------------------------------------------------


def test_markdown_extracts_fenced_code_blocks() -> None:
    text = "# Title\n\nSome prose.\n\n```\nwindows of operating system\n```\n\nMore prose.\n"
    sites = extract_relevance_from_markdown(text)
    assert kinds_lines(sites) == [("markdown-codeblock", 6)]
    assert texts(sites) == ["windows of operating system"]
    # A fence carries no context signal, so the content classifier settles it.
    assert sites[0].context_dialect is Dialect.UNCERTAIN
    assert sites[0].dialect is Dialect.CLIENT


def test_markdown_ignores_inline_code_spans() -> None:
    assert extract_relevance_from_markdown("Use `now` for the time.\n") == []


def test_markdown_extracts_multiple_blocks_with_language_tags() -> None:
    text = "```relevance\nnow\n```\n\ntext\n\n```\nnumber of files of client\n```\n"
    sites = extract_relevance_from_markdown(text)
    assert kinds_lines(sites) == [("markdown-codeblock", 2), ("markdown-codeblock", 8)]


def test_file_dispatch_bes(tmp_path: object) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "example.bes"
    path.write_text(FIXLET_XML, encoding="utf-8")
    assert texts(extract_relevance_from_file(path))[0] == "windows of operating system"


def test_file_dispatch_bes_xml_suffix_chain(tmp_path: object) -> None:
    """`.bes.xml` holds BES XML, so the full suffix chain has to be considered."""
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "example.bes.xml"
    path.write_text(FIXLET_XML, encoding="utf-8")
    assert texts(extract_relevance_from_file(path))[0] == "windows of operating system"


@pytest.mark.parametrize(
    ("suffix", "context_dialect"),
    [
        (".bsr", Dialect.SESSION),
        # `.rel` says nothing about dialect; here the content does.
        (".rel", Dialect.UNCERTAIN),
    ],
)
def test_file_dispatch_plain_text(tmp_path: object, suffix: str, context_dialect: Dialect) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / f"example{suffix}"
    path.write_text("number of bes computers\n", encoding="utf-8")
    sites = extract_relevance_from_file(path)
    assert kinds_lines(sites) == [("plain-text", 1)]
    assert texts(sites) == ["number of bes computers"]
    assert sites[0].context_dialect is context_dialect
    assert sites[0].dialect is Dialect.SESSION
    assert not sites[0].dialect_conflict


def test_file_dispatch_plain_text_blank_file_yields_nothing(tmp_path: object) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "empty.rel"
    path.write_text("\n  \n", encoding="utf-8")
    assert extract_relevance_from_file(path) == []


@pytest.mark.parametrize(
    ("suffix", "expected"),
    [
        (".ojo", Dialect.SESSION),
        (".besrpt", Dialect.SESSION),
        (".beswrpt", Dialect.SESSION),
        (".webreport", Dialect.SESSION),
    ],
)
def test_file_dispatch_console_like(tmp_path: object, suffix: str, expected: Dialect) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / f"example{suffix}"
    path.write_text(CLIENTUI_PI, encoding="utf-8")
    sites = extract_relevance_from_file(path)
    assert [site.dialect for site in sites] == [expected]


@pytest.mark.parametrize("suffix", [".html", ".htm"])
def test_file_dispatch_html_with_clientui_marker_is_client(tmp_path: object, suffix: str) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / f"example{suffix}"
    path.write_text(f'<meta product="CustomDashboardClientUI"/>\n{CLIENTUI_PI}', encoding="utf-8")
    sites = extract_relevance_from_file(path)
    assert [site.dialect for site in sites] == [Dialect.CLIENT]


def test_file_dispatch_html_without_marker_has_no_context_dialect(tmp_path: object) -> None:
    """The extension alone does not say who renders a bare `.html` file."""
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "example.html"
    path.write_text(CLIENTUI_PI, encoding="utf-8")
    sites = extract_relevance_from_file(path)
    assert sites[0].context_dialect is Dialect.UNCERTAIN
    # `CLIENTUI_PI`'s text is the ClientUI trap (`relevant fixlets of sites`),
    # so content has no opinion either and this stays unresolved.
    assert sites[0].dialect is Dialect.UNCERTAIN


def test_file_dispatch_html_without_marker_falls_to_content(tmp_path: object) -> None:
    """Without a marker, a static substitution's dialect is the content's to type."""
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "example.html"
    path.write_text("<?Relevance windows of operating system ?>", encoding="utf-8")
    sites = extract_relevance_from_file(path)
    assert [site.dialect for site in sites] == [Dialect.CLIENT]


def test_file_dispatch_html_without_marker_but_with_js_call_is_session(
    tmp_path: object,
) -> None:
    """A JS relevance call proves the document is not a ClientUI, marker or not."""
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "example.html"
    path.write_text(CONSOLE_JS, encoding="utf-8")
    sites = extract_relevance_from_file(path)
    assert [site.dialect for site in sites] == [Dialect.SESSION]


def test_file_dispatch_unknown_extension_yields_nothing(
    tmp_path: object, caplog: pytest.LogCaptureFixture
) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    path = tmp_path / "notes.txt"
    path.write_text("windows of operating system", encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger="bigfix_relevance_analyzer"):
        assert extract_relevance_from_file(path) == []


# --------------------------------------------------------------------------
# Dialect provenance: what context said, what content said, and disagreement
# --------------------------------------------------------------------------

# `tests/test_dialect.py` covers the classifier itself; these cover how the
# extractor records and reconciles its two sources of evidence.

CONFLICTING_FIXLET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<BES><Fixlet><Title>Wrong dialect</Title>
<Relevance>number of bes computers &gt; 0</Relevance>
</Fixlet></BES>
"""


def test_definite_context_records_a_matching_content_opinion() -> None:
    sites = extract_relevance_from_bes_xml(FIXLET_XML)
    relevance = next(site for site in sites if site.kind == "relevance")
    assert relevance.context_dialect is Dialect.CLIENT
    assert relevance.content_dialect is Dialect.CLIENT
    assert relevance.dialect is Dialect.CLIENT
    assert not relevance.dialect_conflict


def test_content_with_no_opinion_leaves_definite_context_alone() -> None:
    sites = extract_relevance_from_actionscript("appendfile {name of it}")
    assert sites[0].context_dialect is Dialect.CLIENT
    assert sites[0].content_dialect is None
    assert sites[0].dialect is Dialect.CLIENT
    assert not sites[0].dialect_conflict


def test_session_relevance_in_a_fixlet_is_reported_as_a_conflict() -> None:
    """Context still wins the verdict, but the disagreement is on the record."""
    sites = extract_relevance_from_bes_xml(CONFLICTING_FIXLET_XML)
    relevance = next(site for site in sites if site.kind == "relevance")
    assert relevance.context_dialect is Dialect.CLIENT
    assert relevance.content_dialect is Dialect.SESSION
    assert relevance.dialect is Dialect.CLIENT
    assert relevance.dialect_conflict


def test_a_conflict_is_logged_as_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        extract_relevance_from_bes_xml(CONFLICTING_FIXLET_XML)
    assert "dialect conflict" in caplog.text
    assert "BES/Fixlet/Relevance" in caplog.text


def test_a_conflict_warning_reports_the_files_own_line_numbers() -> None:
    """ActionScript sites are offset into the file before anything is reported."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<BES><Task>\n<ActionScript '
        'MIMEType="application/x-fixlet-windows-shell">\nwaithidden cmd /c echo '
        "{number of bes computers}\n</ActionScript>\n</Task></BES>\n"
    )
    sites = extract_relevance_from_bes_xml(xml)
    assert kinds_lines(sites) == [("actionscript-substitution", 4)]
    assert sites[0].dialect_conflict


def test_uncertain_context_filled_in_by_content_is_not_a_conflict() -> None:
    sites = extract_relevance_from_markdown("```\nnumber of bes computers\n```\n")
    assert sites[0].context_dialect is Dialect.UNCERTAIN
    assert sites[0].content_dialect is Dialect.SESSION
    assert sites[0].dialect is Dialect.SESSION
    assert not sites[0].dialect_conflict


def test_uncertain_context_and_no_content_opinion_stays_uncertain() -> None:
    sites = extract_relevance_from_markdown("```\nnames of types\n```\n")
    assert sites[0].context_dialect is Dialect.UNCERTAIN
    assert sites[0].content_dialect is None
    assert sites[0].dialect is Dialect.UNCERTAIN
    assert not sites[0].dialect_conflict


def test_classifier_opinion_fills_in_an_uncertain_site(monkeypatch: pytest.MonkeyPatch) -> None:
    from bigfix_relevance_analyzer import extract as extract_module

    monkeypatch.setattr(extract_module, "classify_relevance_dialect", lambda _text: Dialect.SESSION)
    sites = extract_relevance_from_markdown("```\nnumber of bes computers\n```\n")
    assert [site.dialect for site in sites] == [Dialect.SESSION]


def test_classifier_opinion_never_overrides_definite_file_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from bigfix_relevance_analyzer import extract as extract_module

    monkeypatch.setattr(extract_module, "classify_relevance_dialect", lambda _text: Dialect.SESSION)
    sites = extract_relevance_from_bes_xml(FIXLET_XML)
    relevance = next(site for site in sites if site.kind == "relevance")
    assert relevance.dialect is Dialect.CLIENT


# --------------------------------------------------------------------------
# Library behavior: importable inside a stdio MCP server
# --------------------------------------------------------------------------


def test_extraction_writes_nothing_to_stdout_or_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    extract_relevance_from_bes_xml("<BES><Fixlet><Relevance>oops</BES>")
    extract_relevance_from_actionscript("exit {unterminated")
    extract_relevance_from_html_text("<?Relevance oops", context=HtmlContext.CONSOLE)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_package_logger_has_only_a_null_handler() -> None:
    import bigfix_relevance_analyzer  # noqa: F401

    logger = logging.getLogger("bigfix_relevance_analyzer")
    assert logger.handlers
    assert all(isinstance(handler, logging.NullHandler) for handler in logger.handlers)


def test_importing_the_package_does_not_configure_the_root_logger() -> None:
    import bigfix_relevance_analyzer  # noqa: F401

    root = logging.getLogger()
    assert not any(
        getattr(handler, "_bigfix_relevance_analyzer", False) for handler in root.handlers
    )
    assert logging.getLogger("bigfix_relevance_analyzer").propagate is True


# --------------------------------------------------------------------------
# Empty and degenerate content
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "element",
    [
        "<Relevance></Relevance>",
        "<Relevance>   </Relevance>",
        '<SuccessCriteria Option="CustomRelevance"></SuccessCriteria>',
    ],
)
def test_bes_xml_empty_bodies_are_not_sites(element: str) -> None:
    """An empty <Relevance/> is common in real content and is not a statement."""
    assert extract_relevance_from_bes_xml(f"<BES><Fixlet>{element}</Fixlet></BES>") == []


def test_bes_xml_empty_analysis_property_is_not_a_site() -> None:
    xml = '<BES><Analysis><Property Name="p" ID="1"></Property></Analysis></BES>'
    assert extract_relevance_from_bes_xml(xml) == []


def test_bes_xml_root_element_of_interest_is_still_walked() -> None:
    """A fragment whose root is itself a <Relevance> must not be skipped."""
    assert texts(extract_relevance_from_bes_xml("<Relevance>now</Relevance>")) == ["now"]


def test_bes_xml_comments_and_processing_instructions_are_ignored() -> None:
    xml = (
        "<BES>\n<!-- a comment -->\n<?some-pi data?>\n<Fixlet>\n"
        "<Relevance>now</Relevance>\n</Fixlet>\n</BES>"
    )
    assert kinds_lines(extract_relevance_from_bes_xml(xml)) == [("relevance", 5)]


def test_actionscript_empty_substitution_is_not_a_site() -> None:
    assert extract_relevance_from_actionscript("exit { }") == []


def test_actionscript_escaped_brace_inside_a_substitution_does_not_terminate() -> None:
    """`}}` is an escaped literal brace, so it does not close the substitution."""
    sites = extract_relevance_from_actionscript("exit {a }} b}")
    assert texts(sites) == ["a }} b"]


def test_pi_scanner_empty_body_is_not_a_site() -> None:
    assert extract_relevance_from_html_text("<?Relevance ?>", context=HtmlContext.CONSOLE) == []


def test_js_call_literal_broken_by_a_newline_is_skipped() -> None:
    """An unescaped newline ends a JS string literal, so this is not one."""
    text = "x = Relevance('number of\nbes computers');"
    assert extract_relevance_from_html_text(text, context=HtmlContext.CONSOLE) == []


def test_markdown_unterminated_fence_warns(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        sites = extract_relevance_from_markdown("text\n\n```\nnow\n")
    assert sites == []
    assert any(record.levelno == logging.WARNING for record in caplog.records)


def test_lxml_element_without_a_source_line_warns(caplog: pytest.LogCaptureFixture) -> None:
    """A tree built in memory has no line numbers to report."""
    lxml_etree = pytest.importorskip("lxml.etree")
    from bigfix_relevance_analyzer.extract import extract_relevance_from_lxml_tree

    root = lxml_etree.Element("BES")
    relevance = lxml_etree.SubElement(root, "Relevance")
    relevance.text = "windows of operating system"

    with caplog.at_level(logging.WARNING, logger="bigfix_relevance_analyzer"):
        sites = extract_relevance_from_lxml_tree(root)

    assert texts(sites) == ["windows of operating system"]
    assert sites[0].line == 0
    assert any(record.levelno == logging.WARNING for record in caplog.records)
