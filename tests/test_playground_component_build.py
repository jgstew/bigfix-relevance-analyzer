"""The componentize-py single-file playground build, pinned from fake inputs.

``build_playground.py`` is CI-only and its real inputs are a multi-minute
componentize-py + jco build, so nothing else in ``pytest`` runs it. These tests
feed it a tiny stand-in ``--work`` directory (two fake cores and a fake glue
bundle) and pin exactly what the page is: ``template.html`` rendered with the
shared partials, the glue and the editor inlined as text, and every core as
base64 of gzip level 9 with mtime 0. Splitting the analyzer into separate files
(``build_split.py``, see ``tools/playground-wasm/SPLIT_ANALYZER.md``) shares the
core-gzip step with this script; these tests are what say the single-file page
did not change because of it.
"""

from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path
from types import ModuleType

import pytest
from _helpers import REPO_ROOT, load_tool

BUILD_DIR = REPO_ROOT / "tools" / "playground-wasm" / "componentize-py" / "build-playground"

# Not real wasm: the build never parses the cores, it only gzips them. The
# magic number is there so the bytes at least look like what they stand for.
FAKE_CORES = {
    "analyzer.core.wasm": b"\x00asm\x01\x00\x00\x00" + bytes(range(256)) * 40,
    "analyzer.core2.wasm": b"\x00asm\x01\x00\x00\x00second core",
}
FAKE_GLUE = (
    "const a = new URL('./analyzer.core.wasm', import.meta.url);\n"
    "const b = new URL('./analyzer.core2.wasm', import.meta.url);\n"
    "globalThis.__component = { a, b };\n"
)
FAKE_EDITOR = "window.playgroundEditor = { mount() {} };\n"


@pytest.fixture(scope="module")
def build_playground() -> ModuleType:
    return load_tool(BUILD_DIR / "build_playground.py", "_component_build_playground")


def make_inputs(root: Path) -> tuple[Path, Path]:
    """Write a stand-in for transpile.mjs's ``--work`` dir and the editor bundle."""
    work = root / "web"
    (work / "transpiled").mkdir(parents=True)
    for name, data in FAKE_CORES.items():
        (work / "transpiled" / name).write_bytes(data)
    # Not a core, and must not be picked up as one.
    (work / "transpiled" / "analyzer.d.ts").write_text("export {};\n", encoding="utf-8")
    (work / "bundle.mjs").write_text(FAKE_GLUE, encoding="utf-8")
    editor = root / "playground-editor.js"
    editor.write_text(FAKE_EDITOR, encoding="utf-8")
    return work, editor


def test_the_page_is_the_template_with_gzipped_cores_glue_and_editor(
    build_playground: ModuleType, tmp_path: Path
) -> None:
    work, editor = make_inputs(tmp_path)
    out = tmp_path / "page.html"
    build_playground.build(work, editor, build_playground.DEFAULT_TEMPLATE, out)

    embed = build_playground.embed
    cores = {
        name: base64.b64encode(gzip.compress(FAKE_CORES[name], compresslevel=9, mtime=0)).decode()
        for name in sorted(FAKE_CORES)
    }
    expected = embed.render(
        build_playground.DEFAULT_TEMPLATE,
        {
            "%%CORES_GZIP_JSON%%": json.dumps(cores),
            "%%BUNDLE_JS%%": FAKE_GLUE,
            "%%EDITOR_JS%%": FAKE_EDITOR,
        },
    )
    assert out.read_text(encoding="utf-8") == expected


def test_a_rebuild_of_unchanged_input_is_byte_identical(
    build_playground: ModuleType, tmp_path: Path
) -> None:
    work, editor = make_inputs(tmp_path)
    first, second = tmp_path / "first.html", tmp_path / "second.html"
    build_playground.build(work, editor, build_playground.DEFAULT_TEMPLATE, first)
    build_playground.build(work, editor, build_playground.DEFAULT_TEMPLATE, second)
    assert first.read_bytes() == second.read_bytes()


def test_no_cores_is_a_hard_failure(build_playground: ModuleType, tmp_path: Path) -> None:
    work, editor = make_inputs(tmp_path)
    for core in (work / "transpiled").glob("*.wasm"):
        core.unlink()
    with pytest.raises(SystemExit, match=r"no analyzer\.core\*\.wasm"):
        build_playground.build(work, editor, build_playground.DEFAULT_TEMPLATE, tmp_path / "x.html")
