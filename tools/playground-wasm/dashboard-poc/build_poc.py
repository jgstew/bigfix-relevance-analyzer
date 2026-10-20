#!/usr/bin/env python3
"""Build the relevance debugger dashboard proof of concept.

    python3 tools/playground-wasm/dashboard-poc/build_poc.py --fake-hosts

Writes two targets from one template and one ES5 core (see README.md):

* ``relevance-debugger-console.ojo``: the console dashboard (``<BES><Wizard>``,
  as in jgstew/bigfix-content). Client relevance (local qna, FastQuery) and
  session relevance; no analyzer, since the console renders dashboards in its
  IE11 engine, which has no WebAssembly.
* ``relevance-debugger-webreport.html``: the fragment to paste into a Web
  Reports custom report. Session relevance, plus the analyzer, which it
  fetches after loading (``--analyzer-url``, repeatable, tried in order:
  by default the split analyzer's manifest at jgstew.com, then the
  single-file playground page) and caches in the browser. Web Reports
  regenerates a custom report on every load, so the report itself stays small.
* ``relevance-debugger-<target>-page.html``: each target as a whole page for a
  plain browser, and with ``--fake-hosts`` also ``-fake.html`` pages that load
  fake_host.js, a pretend console or Web Reports, and take the analyzer from
  the local playground build (``--fake-analyzer-url``), for trying it offline.

Pure standard library, like the playground build scripts.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "common"))

import embed  # noqa: E402

NAME = "relevance-debugger"
# target -> (title, sample statement, whether it loads the analyzer)
TARGETS = {
    "console": ("Relevance Debugger", "name of operating system", False),
    "webreport": ("Relevance Debugger for Web Reports", "number of bes computers", True),
}
# fake_host.js's mode for each target's -fake.html page.
FAKE_MODES = {"console": "console", "webreport": "webreports"}
# Where the Web Report gets the analyzer, tried in order: the split analyzer
# (MANIFEST.md), then the single-file playground page, which stays in place
# (no longer updated) until every report has moved to the manifest.
ANALYZER_URLS = [
    "https://www.jgstew.com/files/analyzer/manifest.json",
    "https://www.jgstew.com/files/bigfix-relevance-analyzer-playground.html",
]
# For the -fake.html pages, relative to the output directory: the split set
# test_reports.mjs writes there (split_fixture.mjs), then the local
# single-file playground build one level up.
FAKE_ANALYZER_URLS = [
    "analyzer/manifest.json",
    "../bigfix-relevance-analyzer-component-playground.html",
]
_PLACEHOLDER_RE = re.compile(r"%%[A-Z0-9_]+%%")
# XML 1.0 forbids these even inside CDATA.
_XML_BAD_CHARS = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _strip_leading_comment(text: str) -> str:
    if text.lstrip().startswith("<!--"):
        _, _, text = text.partition("-->")
    return text.lstrip("\n")


def _fill(text: str, values: dict[str, str]) -> str:
    """Replace placeholders, checking the template has exactly these."""
    found = set(_PLACEHOLDER_RE.findall(text))
    if found != set(values):
        raise SystemExit(f"placeholders {sorted(found)} != substitutions {sorted(values)}")
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    return text


def _cdata(text: str) -> str:
    """``text`` as CDATA, split wherever it contains ``]]>``."""
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def _ojo(title: str, head: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<BES>\n<Wizard>\n"
        f"<Title>{title}</Title>\n"
        '<UIHooks LaunchType="Document" RequiresAuthoring="false" Menu="Dashboards"></UIHooks>\n'
        "<DefaultPage>Page1</DefaultPage>\n"
        '<Page Name="Page1" DocType="HTML5">\n'
        f"<Title>{title}</Title>\n"
        f"<Head>{_cdata(head)}</Head>\n"
        f"<HTML>{_cdata(body)}</HTML>\n"
        "</Page>\n</Wizard>\n</BES>\n"
    )


def _page(title: str, head: str, body: str, extra_head: str = "") -> str:
    return (
        f"<!doctype html>\n<html>\n<head>\n<title>{title}</title>\n{extra_head}{head}</head>\n"
        f"<body>\n{body}</body>\n</html>\n"
    )


def _render(target: str, built: str, analyzer_urls: list[str]) -> tuple[str, str]:
    """The (head, body) of ``target``'s page, loading the analyzer from ``analyzer_urls``."""
    template = _strip_leading_comment((HERE / "template.html").read_text(encoding="utf-8"))
    core = (HERE / "core.js").read_text(encoding="utf-8")
    if "</script" in core.lower():
        raise SystemExit("core.js contains '</script' and cannot be inlined")
    _title, sample, with_analyzer = TARGETS[target]
    loader = ""
    if with_analyzer:
        loader_mjs = (HERE / "loader.mjs").read_text(encoding="utf-8")
        if "</script" in loader_mjs.lower():
            raise SystemExit("loader.mjs contains '</script' and cannot be inlined")
        loader = _fill(
            _strip_leading_comment((HERE / "analyzer_loader.html").read_text(encoding="utf-8")),
            {"%%LOADER_MJS%%": loader_mjs},
        )
        # One module script whose only closing tag is its last line: one
        # inside the code (even in a string) would end the element early.
        code = loader.strip()
        if not code.startswith('<script type="module">') or not code.endswith("</script>"):
            raise SystemExit("analyzer_loader.html must be one <script type=module> element")
        if "</script" in code[: -len("</script>")].lower():
            raise SystemExit("analyzer_loader.html has '</script' inside its script")
    build_info = {"target": target, "built": built, "analyzer": with_analyzer}
    if with_analyzer:
        build_info["analyzerUrls"] = analyzer_urls
    page = _fill(
        template,
        {
            "%%HEAD%%": "%%HEAD%%",
            "%%BODY%%": "%%BODY%%",
            "%%SAMPLE%%": sample,
            # No "<" at all, so a URL can neither close the <script> element
            # nor start "<!--<script", after which "</script>" would not.
            "%%BUILD_JSON%%": json.dumps(build_info).replace("<", "\\u003c"),
            "%%CORE_JS%%": core,
            "%%ANALYZER%%": loader,
        },
    )
    _, _, rest = page.partition("%%HEAD%%")
    head, _, body = rest.partition("%%BODY%%")
    head, body = head.strip() + "\n", body.strip() + "\n"
    if _XML_BAD_CHARS.search(head + body):
        raise SystemExit(f"{target}: contains characters XML cannot carry")
    if "<?relevance" in body.lower():
        raise SystemExit(f"{target}: contains '<?relevance', which Web Reports would evaluate")
    return head, body


def build(
    out_dir: Path, analyzer_urls: list[str], fake_hosts: bool, fake_analyzer_urls: list[str]
) -> None:
    built = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")
    for target, (title, _sample, _with_analyzer) in TARGETS.items():
        head, body = _render(target, built, analyzer_urls)
        outputs = {f"{NAME}-{target}-page.html": _page(title, head, body)}
        if target == "console":
            outputs[f"{NAME}-console.ojo"] = _ojo(title, head, body)
        else:
            outputs[f"{NAME}-webreport.html"] = head + body
        if fake_hosts:
            fake_head, fake_body = _render(target, built, fake_analyzer_urls)
            fake = (HERE / "fake_host.js").read_text(encoding="utf-8")
            extra = (
                f'<script>window.FAKE_HOST = "{FAKE_MODES[target]}";</script>\n'
                f"<script>\n{fake}</script>\n"
            )
            outputs[f"{NAME}-{target}-fake.html"] = _page(title, fake_head, fake_body, extra)
        for filename, text in outputs.items():
            size = embed.write_page(out_dir / filename, text)
            print(f"wrote {out_dir / filename} ({size // 1024} KiB)")
        if target == "console":
            # The .ojo must be well-formed XML with the page intact inside it.
            root = ET.parse(out_dir / f"{NAME}-console.ojo").getroot()
            if root.findtext("Wizard/Page/HTML") != body:
                raise SystemExit(f"{NAME}-console.ojo does not round-trip its HTML")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path("playground/dashboard-poc"))
    parser.add_argument(
        "--analyzer-url",
        action="append",
        dest="analyzer_urls",
        help=(
            "where the Web Report gets the analyzer, tried in order: a manifest.json "
            f"or a single-file playground page (default {' then '.join(ANALYZER_URLS)})"
        ),
    )
    parser.add_argument(
        "--fake-hosts",
        action="store_true",
        help="also write -fake.html pages that run against fake_host.js",
    )
    parser.add_argument(
        "--fake-analyzer-url",
        action="append",
        dest="fake_analyzer_urls",
        help=(
            "where the -fake.html Web Report gets the analyzer, tried in order "
            f"(default {' then '.join(FAKE_ANALYZER_URLS)})"
        ),
    )
    args = parser.parse_args(argv)
    build(
        args.out,
        args.analyzer_urls or ANALYZER_URLS,
        args.fake_hosts,
        args.fake_analyzer_urls or FAKE_ANALYZER_URLS,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
