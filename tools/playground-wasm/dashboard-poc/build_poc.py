#!/usr/bin/env python3
"""Build the relevance debugger dashboard proof of concept.

    python3 tools/playground-wasm/dashboard-poc/build_poc.py \\
        --work dist/componentize/web \\
        --editor-bundle dist/playground-editor.js \\
        --out playground/dashboard-poc

Reads the same inputs as the componentize-py playground build (the transpiled
component and the editor bundle) and writes two targets from one template and
one ES5 core (see README.md):

* ``relevance-debugger-console.ojo``: the console dashboard (``<BES><Wizard>``,
  as in jgstew/bigfix-content). Client relevance (local qna, FastQuery) and
  session relevance; no analyzer, since the console renders dashboards in its
  IE11 engine, which has no WebAssembly.
* ``relevance-debugger-webreport.html``: the fragment to paste into a Web
  Reports custom report. The analyzer plus session relevance; Web Reports runs
  in the user's own browser but cannot evaluate client relevance.
* ``relevance-debugger-<target>-page.html``: each target as a whole page for a
  plain browser, and with ``--fake-hosts`` also ``-fake.html`` pages that load
  fake_host.js, a pretend console or Web Reports, for trying the UI locally.

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
sys.path.insert(0, str(HERE.parent / "componentize-py" / "build-playground"))

import build_playground  # noqa: E402  (for _encode_cores)
import embed  # noqa: E402

NAME = "relevance-debugger"
# target -> (title, sample statement, whether it embeds the analyzer)
TARGETS = {
    "console": ("Relevance Debugger", "name of operating system", False),
    "webreport": ("Relevance Debugger for Web Reports", "number of bes computers", True),
}
# fake_host.js's mode for each target's -fake.html page.
FAKE_MODES = {"console": "console", "webreport": "webreports"}
_PLACEHOLDER_RE = re.compile(r"%%[A-Z0-9_]+%%")
# XML 1.0 forbids these even inside CDATA.
_XML_BAD_CHARS = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _strip_leading_comment(text: str) -> str:
    if text.lstrip().startswith("<!--"):
        _, _, text = text.partition("-->")
    return text.lstrip("\n")


def _fill(text: str, values: dict[str, str]) -> str:
    """Replace placeholders, checking the template has exactly these.

    Checked before substituting, because the embedded bundles are large and
    could themselves contain ``%%...%%`` text.
    """
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


def _xml_safe_js(js: str) -> str:
    r"""``js`` with XML-illegal control characters written as ``\xNN`` escapes.

    They can only appear inside JS string, template or regex literals (the
    editor bundle has one, in a RegExp source), where the escape means the
    same character.
    """
    return _XML_BAD_CHARS.sub(lambda m: f"\\x{ord(m.group()):02x}", js)


def _analyzer_layer(work_dir: Path, editor_bundle: Path) -> str:
    bundle = work_dir / "bundle.mjs"
    transpiled = work_dir / "transpiled"
    for required in (bundle, transpiled):
        if not required.exists():
            raise SystemExit(f"expected {required} to exist (from --work {work_dir})")
    cores_json, _raw, _gz = build_playground._encode_cores(transpiled)
    layer = _strip_leading_comment((HERE / "analyzer.html").read_text(encoding="utf-8"))
    return _fill(
        layer,
        {
            "%%EDITOR_JS%%": _xml_safe_js(embed.editor_js(editor_bundle)),
            "%%CORES_GZIP_JSON%%": cores_json,
            "%%BUNDLE_JS%%": _xml_safe_js(bundle.read_text(encoding="utf-8")),
        },
    )


def _page(title: str, head: str, body: str, extra_head: str = "") -> str:
    return (
        f"<!doctype html>\n<html>\n<head>\n<title>{title}</title>\n{extra_head}{head}</head>\n"
        f"<body>\n{body}</body>\n</html>\n"
    )


def build(work_dir: Path, editor_bundle: Path, out_dir: Path, fake_hosts: bool) -> None:
    template = _strip_leading_comment((HERE / "template.html").read_text(encoding="utf-8"))
    core = (HERE / "core.js").read_text(encoding="utf-8")
    if "</script" in core.lower():
        raise SystemExit("core.js contains '</script' and cannot be inlined")
    built = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")

    for target, (title, sample, with_analyzer) in TARGETS.items():
        analyzer = _analyzer_layer(work_dir, editor_bundle) if with_analyzer else ""
        page = _fill(
            template,
            {
                "%%HEAD%%": "%%HEAD%%",
                "%%BODY%%": "%%BODY%%",
                "%%SAMPLE%%": sample,
                "%%BUILD_JSON%%": json.dumps(
                    {"target": target, "built": built, "analyzer": with_analyzer}
                ),
                "%%CORE_JS%%": core,
                "%%ANALYZER%%": analyzer,
            },
        )
        _, _, rest = page.partition("%%HEAD%%")
        head, _, body = rest.partition("%%BODY%%")
        head, body = head.strip() + "\n", body.strip() + "\n"
        if _XML_BAD_CHARS.search(head + body):
            raise SystemExit(f"{target}: contains characters XML cannot carry")
        if "<?relevance" in body.lower():
            raise SystemExit(f"{target}: contains '<?relevance', which Web Reports would evaluate")

        outputs = {f"{NAME}-{target}-page.html": _page(title, head, body)}
        if target == "console":
            outputs[f"{NAME}-console.ojo"] = _ojo(title, head, body)
        else:
            outputs[f"{NAME}-webreport.html"] = head + body
        if fake_hosts:
            fake = (HERE / "fake_host.js").read_text(encoding="utf-8")
            extra = (
                f'<script>window.FAKE_HOST = "{FAKE_MODES[target]}";</script>\n'
                f"<script>\n{fake}</script>\n"
            )
            outputs[f"{NAME}-{target}-fake.html"] = _page(title, head, body, extra)
        for filename, text in outputs.items():
            size = embed.write_page(out_dir / filename, text)
            print(f"wrote {out_dir / filename} ({embed.mib(size)})")
        if target == "console":
            # The .ojo must be well-formed XML with the page intact inside it.
            root = ET.parse(out_dir / f"{NAME}-console.ojo").getroot()
            if root.findtext("Wizard/Page/HTML") != body:
                raise SystemExit(f"{NAME}-console.ojo does not round-trip its HTML")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work", type=Path, default=Path("dist/componentize/web"))
    parser.add_argument("--editor-bundle", type=Path, default=Path("dist/playground-editor.js"))
    parser.add_argument("--out", type=Path, default=Path("playground/dashboard-poc"))
    parser.add_argument(
        "--fake-hosts",
        action="store_true",
        help="also write -fake.html pages that run against fake_host.js",
    )
    args = parser.parse_args(argv)
    build(args.work, args.editor_bundle, args.out, args.fake_hosts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
