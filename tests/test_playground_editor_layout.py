"""The playground pages' editor (#142 C1): how it is built and wired.

``tools/playground-wasm/editor-bundle/`` bundles CodeMirror 6 with the wheel's
own ``web/`` modules (imported from ``src/``, so the pages run what the wheel
ships) into one classic script; both ``build_playground.py`` scripts inline it
at ``%%EDITOR_JS%%`` in the shared script, so each page stays a single offline
file. What the editor does is the browser tests' job
(``common/editor_checks.mjs``); these hold the layout.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from _helpers import REPO_ROOT, load_tool

PLAYGROUND = REPO_ROOT / "tools" / "playground-wasm"
BUNDLE = PLAYGROUND / "editor-bundle"
COMMON = PLAYGROUND / "common"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wasm-html.yaml"
RUNTIMES = ("componentize-py", "pyodide")


def test_the_bundle_package_pins_codemirror_and_esbuild_exactly() -> None:
    """Exactly, with the lockfile agreeing. Its esbuild may differ from the smoke
    stage's for a while: dependabot bumps each directory in its own PR."""
    package = json.loads((BUNDLE / "package.json").read_text(encoding="utf-8"))
    assert package["private"] is True
    pins = package["dependencies"]
    codemirror = {"codemirror", "@codemirror/state", "@codemirror/view", "@codemirror/language"}
    assert set(pins) == {*codemirror, "@codemirror/autocomplete", "@lezer/highlight", "esbuild"}
    assert all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in pins.values()), pins
    lock = json.loads((BUNDLE / "package-lock.json").read_text(encoding="utf-8"))
    for name, version in pins.items():
        assert lock["packages"][f"node_modules/{name}"]["version"] == version, name


def test_the_editor_runs_the_wheel_s_own_web_modules() -> None:
    text = (BUNDLE / "editor.mjs").read_text(encoding="utf-8")
    for module in ("relevance_editor.js", "relevance_language.js"):
        assert f'from "../../../src/bigfix_relevance_analyzer/web/{module}";' in text, module
    assert 'documentSync: "client"' in text
    assert "window.playgroundEditor" in text


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_each_page_build_requires_the_editor_bundle(runtime: str) -> None:
    script = PLAYGROUND / runtime / "build-playground" / "build_playground.py"
    text = script.read_text(encoding="utf-8")
    assert '"--editor-bundle",\n        required=True,' in text
    assert '"%%EDITOR_JS%%": embed.editor_js(editor_bundle)' in text
    template_path = PLAYGROUND / runtime / "build-playground" / "template.html"
    template = template_path.read_text(encoding="utf-8")
    assert "<textarea" not in template
    assert '<div id="input">' in template


def test_the_shared_script_inlines_and_mounts_the_editor() -> None:
    text = (COMMON / "shared_script.html").read_text(encoding="utf-8")
    assert "%%EDITOR_JS%%" in text
    assert "window.playgroundEditor.mount(inputEl" in text
    assert "editor.connect(window.lspHandle)" in text
    assert "inputEl.value" not in text


@pytest.mark.parametrize(
    ("content", "complaint"),
    [
        ('window.playgroundEditor={};x="</script>"', "</script"),
        ('window.playgroundEditor={};x="</SCRIPT"', "</script"),
        ('window.playgroundEditor={};x="<!--"', "<!--"),
        ('window.playgroundEditor={};x="' + chr(0xE9) + '"', "ASCII"),  # an e-acute
        ("window.somethingElse={}", "playgroundEditor"),
    ],
)
def test_the_inlined_bundle_is_checked(tmp_path: Path, content: str, complaint: str) -> None:
    embed = load_tool(COMMON / "embed.py", "_playground_embed_editor")
    bundle = tmp_path / "editor.js"
    bundle.write_text(content, encoding="utf-8")
    with pytest.raises(SystemExit, match=complaint):
        embed.editor_js(bundle)
    with pytest.raises(SystemExit, match=r"did editor-bundle/build\.mjs run"):
        embed.editor_js(tmp_path / "missing.js")
    bundle.write_text("window.playgroundEditor={}", encoding="utf-8")
    assert embed.editor_js(bundle) == "window.playgroundEditor={}"


def _job(text: str, name: str) -> str:
    job = text[text.index(f"\n  {name}:\n") :]
    following = re.search(r"\n  [\w-]+:\n", job[1:])
    return job[: following.start() + 1] if following else job


@pytest.mark.parametrize("job", RUNTIMES)
def test_ci_builds_the_bundle_before_each_page(job: str) -> None:
    text = _job(WORKFLOW.read_text(encoding="utf-8"), job)
    build = text.index("node build.mjs --out ../../../dist/playground-editor.js")
    page = text.index("--editor-bundle dist/playground-editor.js")
    assert "working-directory: tools/playground-wasm/editor-bundle" in text
    assert build < page
    assert "tools/playground-wasm/editor-bundle/package-lock.json" in text
