"""Build checks for tools/playground-wasm/dashboard-poc/build_poc.py."""

from __future__ import annotations

import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from types import ModuleType

BUILD_POC = Path(__file__).parent.parent / "tools/playground-wasm/dashboard-poc/build_poc.py"


def _build_poc() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_poc", BUILD_POC)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_json(body: str) -> str:
    match = re.search(r"window\.RDBG_BUILD = (.*);\n", body)
    assert match, "no RDBG_BUILD in the page"
    return match.group(1)


def test_analyzer_urls_cannot_break_out_of_the_build_script() -> None:
    """A URL is JSON inside a classic <script>: no "<" may reach the HTML.

    "</script" would end the element, and "<!--<script" would put the parser
    in a state where the real closing tag no longer ends it.
    """
    build_poc = _build_poc()
    hostile = "https://example.test/<!--<script></script>.json"
    _head, body = build_poc._render("webreport", "2026-01-01T00:00Z", [hostile])
    build_json = _build_json(body)
    assert "<" not in build_json
    assert json.loads(build_json)["analyzerUrls"] == [hostile]


def test_console_build_has_no_analyzer_urls() -> None:
    build_poc = _build_poc()
    _head, body = build_poc._render("console", "2026-01-01T00:00Z", ["https://example.test/m.json"])
    assert "analyzerUrls" not in json.loads(_build_json(body))


def test_build_writes_the_webreport_as_a_beswrpt(tmp_path: Path) -> None:
    """Besides the raw fragment, the Web Report comes as a .beswrpt: the
    <BESWebReport> XML a BigFix site's server files carry, which Web Reports
    picks up on its own. Its <Data> is exactly the fragment."""
    build_poc = _build_poc()
    build_poc.build(tmp_path, ["https://example.test/m.json"], False, [])
    fragment = (tmp_path / "relevance-debugger-webreport.html").read_text(encoding="utf-8")
    beswrpt = tmp_path / "relevance-debugger-webreport.beswrpt"
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    assert beswrpt.read_text(encoding="utf-8").startswith(xml_declaration)
    root = ET.parse(beswrpt).getroot()
    assert root.tag == "BESWebReport"
    assert [child.tag for child in root] == ["Name", "Description", "Type", "Source", "Data"]
    assert root.findtext("Name") == "Relevance Debugger"
    assert root.findtext("Description") == ""
    assert root.findtext("Type") == "CustomReport"
    assert root.findtext("Source") == "JGStew"
    data = root.findtext("Data")
    assert data is not None
    # The CDATA opens and closes on lines of their own.
    assert data == "\n" + fragment + "\t"


def test_beswrpt_keeps_a_cdata_terminator_in_the_report() -> None:
    """A "]]>" in the report would end the CDATA early; it is split so the
    XML still parses to the exact text."""
    build_poc = _build_poc()
    text = "<script>if (a[b[0]]>1) {}</script>\n"
    root = ET.fromstring(build_poc._beswrpt(text).encode("utf-8"))
    assert root.findtext("Data") == "\n" + text + "\t"
