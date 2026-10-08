#!/usr/bin/env python3
"""Build the language-server component the "BigFix Relevance Developer" extension runs.

    cd tools/vscode-extension/componentize-py && npm ci && cd -
    uv run --group wasm python \
        tools/vscode-extension/componentize-py/build-component/build_component.py

Four steps, everything under ``../dist/`` (gitignored), after copying the
repository's LICENSE beside package.json for vsce to package (gitignored too):

1. ``uv build --wheel`` of this checkout -> ``dist/wheel/``
2. componentize-py, through the playground's ``componentize.py`` so both share
   its two-pass build and the reasons for it -> ``dist/work/lsp.wasm``
3. ``jco transpile`` for Node -> ``dist/component/lsp.js`` plus core modules,
   which server.js imports
4. a smoke check in Node: the component boots, reports a real version, and
   answers ``initialize``. That proves the build snapshot holds what the server
   imports, which no host-side test can.

``uv run --group wasm`` is what puts ``componentize-py`` (pinned in
pyproject.toml's ``wasm`` group) on ``PATH`` for step 2.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTENSION = HERE.parent
REPO = EXTENSION.parent.parent.parent
DIST = EXTENSION / "dist"
COMPONENTIZE = REPO / "tools/playground-wasm/componentize-py/build-playground/componentize.py"
WORLD = "lsp"


def _run(argv: list[str], label: str, cwd: Path | None = None) -> None:
    sys.stderr.write(f"  {label}\n")
    subprocess.run(argv, check=True, cwd=cwd)


def _componentize_module():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("_playground_componentize", COMPONENTIZE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_license(target_dir: Path = EXTENSION) -> Path:
    """Copy the repository's LICENSE into ``target_dir``; return the copy.

    vsce packages the LICENSE that sits beside package.json and warns without
    one. Copying it at build time, gitignored, keeps the root LICENSE the
    only copy in the repository.
    """
    return Path(shutil.copyfile(REPO / "LICENSE", target_dir / "LICENSE"))


def build() -> Path:
    """Build the component and the Node glue under ``dist/``; return the glue's path."""
    copy_license()
    shutil.rmtree(DIST, ignore_errors=True)
    wheel_dir = DIST / "wheel"
    _run(["uv", "build", "--wheel", "--quiet", "-o", str(wheel_dir)], "build the wheel", cwd=REPO)
    (wheel,) = wheel_dir.glob("*.whl")

    component = _componentize_module().componentize(
        wheel,
        DIST / "work",
        wit_dir=HERE / "wit",
        world=WORLD,
        app_module=HERE / "app.py",
    )

    # For Node, not the browser: no --no-nodejs-compat, so the glue reads its
    # core modules from disk itself. The playground's browser flags (and their
    # reasons) are in tools/playground-wasm/componentize-py/smoke/transpile.mjs.
    glue_dir = DIST / "component"
    jco = EXTENSION / "node_modules" / ".bin" / "jco"
    if not jco.exists():
        raise SystemExit(f"{jco} is missing; run `npm ci` in {EXTENSION} first")
    _run([str(jco), "transpile", str(component), "-o", str(glue_dir), "--quiet"], "jco transpile")
    # The glue is an ES module, but this extension's package.json is CommonJS
    # (VS Code loads extension.js with `require`). A package.json beside the
    # glue makes Node load it as ESM.
    (glue_dir / "package.json").write_text(json.dumps({"type": "module"}) + "\n")
    return glue_dir / f"{WORLD}.js"


SMOKE = """
const [glue, expected] = process.argv.slice(1);
const component = await import(glue);
const version = component.version();
if (version !== expected) throw new Error(`component reports ${version}, expected ${expected}`);
const replies = JSON.parse(component.handle(JSON.stringify(
  { jsonrpc: "2.0", id: 1, method: "initialize", params: {} })));
if (replies[0]?.result?.serverInfo?.version !== expected) {
  throw new Error(`unexpected initialize reply: ${JSON.stringify(replies)}`);
}
console.log(`component ok: bigfix-relevance-analyzer ${version}`);
"""


def smoke(glue: Path) -> None:
    """Fail the build if the component cannot boot and answer ``initialize``."""
    sys.path.insert(0, str(REPO / "src"))
    from bigfix_relevance_analyzer import __version__

    _run(
        ["node", "--input-type=module", "-e", SMOKE, glue.as_uri(), __version__],
        "smoke check in Node",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    glue = build()
    smoke(glue)
    size = sum(path.stat().st_size for path in glue.parent.glob("*.wasm"))
    print(f"wrote {glue.parent} ({size / 1048576:.1f} MiB of core modules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
