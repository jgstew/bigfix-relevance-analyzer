"""Build checks for tools/playground-wasm/dashboard-poc/build_poc.py."""

from __future__ import annotations

import importlib.util
import json
import re
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
