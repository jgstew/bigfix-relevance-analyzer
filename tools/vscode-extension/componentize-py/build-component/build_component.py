#!/usr/bin/env python3
"""Build the language-server component the "BigFix Relevance Developer" extension runs.

    cd tools/vscode-extension/componentize-py && npm ci && cd -
    uv run --group wasm python \
        tools/vscode-extension/componentize-py/build-component/build_component.py \
        [--wheel dist/bigfix_relevance_analyzer-<version>-py3-none-any.whl] \
        [--package dist/vsix/bigfix-relevance-developer.vsix]

Four steps, everything under ``../dist/`` (gitignored), after copying the
repository's LICENSE and the logo's icons beside package.json for vsce to
package (gitignored too):

1. ``uv build --wheel`` of this checkout -> ``dist/wheel/``, unless ``--wheel``
   names one. A release passes the wheel it publishes, so the extension it
   attaches holds exactly that build (see .github/workflows/tag_and_release.yaml).
2. componentize-py, through the playground's ``componentize.py`` so both share
   its two-pass build and the reasons for it -> ``dist/work/lsp.wasm``
3. ``jco transpile`` for Node -> ``dist/component/lsp.js`` plus core modules,
   which server.js imports
4. a smoke check in Node: the component boots, reports the wheel's version, and
   answers ``initialize``. That proves the build snapshot holds what the server
   imports, which no host-side test can.

With ``--package``, it then packages the extension with vsce, versioned as the
analyzer it contains: the wheel's version is the extension's version, so a
.vsix always says which analyzer build is inside. The committed package.json
keeps a placeholder version and is never rewritten. A .vsix holding a native
Node addon is refused: it is one package for every platform.

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
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTENSION = HERE.parent
REPO = EXTENSION.parent.parent.parent
DIST = EXTENSION / "dist"
COMPONENTIZE = REPO / "tools/playground-wasm/componentize-py/build-playground/componentize.py"
WORLD = "lsp"

# The icons package.json names, each copied at build time from the project logo
# in docs/images/, the only copy in the repository. The light logo only: the
# Relevance file icon is it for light and dark themes alike, and the dark logo
# files there are kept but not used.
LOGO_DIR = REPO / "docs/images"
ICONS = {
    "images/icon.png": "logo-256.png",
    "images/relevance.svg": "logo.svg",
}


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


def copy_icons(target_dir: Path = EXTENSION) -> list[Path]:
    """Copy the logo into ``target_dir`` as every icon in ``ICONS``; return the copies.

    The extension's Marketplace icon and the Relevance language's file icon.
    Copied at build time, gitignored, like the LICENSE.
    """
    copies = []
    for icon, logo in ICONS.items():
        (target_dir / icon).parent.mkdir(parents=True, exist_ok=True)
        copies.append(Path(shutil.copyfile(LOGO_DIR / logo, target_dir / icon)))
    return copies


def wheel_version(wheel: Path) -> str:
    """The version in a wheel's file name: ``<name>-<version>-<tags>.whl`` (PEP 427)."""
    return wheel.name.split("-")[1]


def build(wheel: Path | None = None) -> tuple[Path, str]:
    """Build the component and the Node glue under ``dist/``.

    From ``wheel`` when given, else from a fresh build of this checkout.
    Returns the glue's path and the version of the wheel it was built from.
    """
    copy_license()
    copy_icons()
    shutil.rmtree(DIST, ignore_errors=True)
    if wheel is None:
        wheel_dir = DIST / "wheel"
        _run(
            ["uv", "build", "--wheel", "--quiet", "-o", str(wheel_dir)], "build the wheel", cwd=REPO
        )
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
    return glue_dir / f"{WORLD}.js", wheel_version(wheel)


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


def smoke(glue: Path, expected_version: str) -> None:
    """Fail the build if the component cannot boot and answer ``initialize``,
    or reports a version other than the wheel's."""
    _run(
        ["node", "--input-type=module", "-e", SMOKE, glue.as_uri(), expected_version],
        "smoke check in Node",
    )


def package(version: str, out: Path) -> None:
    """Package the extension into ``out``, stamped with ``version``.

    ``vsce package <version>`` sets the version in the .vsix;
    ``--no-update-package-json`` and ``--no-git-tag-version`` keep it from
    rewriting package.json or running ``npm version``'s commit and tag.
    """
    out.parent.mkdir(parents=True, exist_ok=True)  # vsce does not create it
    _run(
        [
            "npx",
            "vsce",
            "package",
            version,
            "--no-git-tag-version",
            "--no-update-package-json",
            "--out",
            str(out.resolve()),
        ],
        f"vsce package {version}",
        cwd=EXTENSION,
    )
    check_portable(out)


def check_portable(vsix: Path) -> None:
    """Exit if ``vsix`` holds a native Node addon (``*.node``).

    The extension ships as one .vsix for every platform, and npm installs only
    the packaging machine's native builds, so any addon inside would work on
    that platform alone. .vscodeignore leaves out the one native dependency.
    """
    with zipfile.ZipFile(vsix) as archive:
        native = sorted(name for name in archive.namelist() if name.endswith(".node"))
    if native:
        raise SystemExit(
            f"{vsix} holds native builds, so it would not work on every platform; "
            f"leave them out in .vscodeignore: {', '.join(native)}"
        )


def resolve_wheel(pattern: str) -> Path:
    """The one wheel ``pattern`` names, or exit with why not.

    A glob is resolved here rather than by the shell, through the same helper
    componentize.py uses, so zero or several matches fail with a clear message
    instead of as stray arguments. A wheel inside ``dist/`` is refused: the
    build starts by deleting that directory, which would delete the wheel first.
    """
    wheel = Path(_componentize_module()._resolve_single(pattern, kind="wheel")).resolve()
    if wheel.is_relative_to(DIST.resolve()):
        raise SystemExit(
            f"{wheel} is inside {DIST}, which the build deletes first; copy it elsewhere"
        )
    return wheel


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--wheel",
        metavar="PATH_OR_GLOB",
        help="build from this wheel instead of building this checkout; a glob must match one",
    )
    parser.add_argument(
        "--package",
        type=Path,
        metavar="OUT_VSIX",
        help="then package the extension, versioned as the wheel, into this .vsix",
    )
    args = parser.parse_args(argv)
    wheel = None if args.wheel is None else resolve_wheel(args.wheel)
    glue, version = build(wheel)
    smoke(glue, version)
    if args.package is not None:
        package(version, args.package)
    size = sum(path.stat().st_size for path in glue.parent.glob("*.wasm"))
    print(f"wrote {glue.parent} ({size / 1048576:.1f} MiB of core modules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
