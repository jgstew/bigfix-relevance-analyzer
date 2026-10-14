"""The layout of ``tools/wasm-common/`` (#142 H2, shared with #139).

What any jco-transpiled componentize-py component needs to run in a browser,
kept in one place so the playground's build and the VS Code web server (#139)
use the same pieces instead of copies:

* ``sockets_stub.js``, the ``wasi:sockets`` stand-in preview2-shim's browser
  build needs;
* ``browser.js``, the jco and esbuild flags that select the browser shims, and
  the check that no ``node:`` import survived bundling;
* ``pump.js``, the transport-agnostic message -> ``handle`` -> replies loop.

Their behaviour is tested in Node (``tools/wasm-common/test``); these hold the
layout: one copy of each, the playground build importing them, CI running the
Node tests, and the package following this repo's npm policy.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess

import pytest
from _helpers import REPO_ROOT

WASM_COMMON = REPO_ROOT / "tools" / "wasm-common"
PLAYGROUND = REPO_ROOT / "tools" / "playground-wasm" / "componentize-py"
TRANSPILE = PLAYGROUND / "smoke" / "transpile.mjs"
TEST_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test.yaml"
WASM_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wasm-html.yaml"
SHARED = ("sockets_stub.js", "browser.js", "pump.js")


@pytest.mark.parametrize("name", SHARED)
def test_each_shared_file_exists_once(name: str) -> None:
    assert (WASM_COMMON / name).is_file()
    copies = [
        path
        for path in (REPO_ROOT / "tools").rglob(name)
        if "node_modules" not in path.parts and path.parent != WASM_COMMON
    ]
    assert not copies, copies


def test_the_playground_build_imports_the_shared_flags_and_stub() -> None:
    text = TRANSPILE.read_text(encoding="utf-8")
    assert re.search(r'from "\.\./\.\./\.\./wasm-common/browser\.js";', text)
    for name in ("SOCKETS_STUB", "jcoBrowserArgs", "ESBUILD_BROWSER_ARGS", "nodeBuiltinsIn"):
        assert re.search(rf"\b{name}\b", text), name
    # The browser-essential flags live in browser.js only.
    assert '"--no-nodejs-compat"' not in text
    assert "wasi:sockets/*=" not in text
    assert '"--conditions=browser"' not in text


def test_the_package_is_private_has_no_dependencies_and_tests_on_node_22() -> None:
    package = json.loads((WASM_COMMON / "package.json").read_text(encoding="utf-8"))
    assert package["private"] is True
    assert package["type"] == "module"
    assert "dependencies" not in package
    assert not package.get("devDependencies")
    assert package["engines"]["npm"] == ">=11.10.0"
    # Node 22 (CI's) runs a bare directory argument as a module and fails.
    assert package["scripts"]["test"] == "node --test 'test/**/*.test.mjs'"
    lock = json.loads((WASM_COMMON / "package-lock.json").read_text(encoding="utf-8"))
    assert set(lock["packages"]) == {""}


def test_ci_runs_the_node_tests() -> None:
    text = TEST_WORKFLOW.read_text(encoding="utf-8")
    job = text[text.index("  wasm-common:") :]
    following = re.search(r"\n  [\w-]+:\n", job[1:])
    job = job[: following.start() + 1] if following else job
    assert "working-directory: tools/wasm-common" in job
    assert 'node-version: "22"' in job
    assert "npm test" in job


def test_the_pages_rebuild_when_the_shared_files_change() -> None:
    assert '"tools/wasm-common/**"' in WASM_WORKFLOW.read_text(encoding="utf-8")


def test_nothing_under_wasm_common_is_gitignored() -> None:
    git = shutil.which("git")
    if git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("needs a git checkout")
    candidates = [
        path
        for path in WASM_COMMON.rglob("*")
        if path.is_file() and "node_modules" not in path.parts
    ]
    assert candidates
    result = subprocess.run(
        [git, "check-ignore", "--", *(str(p) for p in candidates)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert not result.stdout.strip(), result.stdout
