#!/usr/bin/env python3
"""Build ``template.html`` into a single, fully offline playground page.

    python tools/playground-wasm/pyodide/build-playground/build_playground.py \\
        --wheel dist/bigfix_relevance_analyzer-*.whl \\
        --pyodide-dir tools/playground-wasm/pyodide/smoke/node_modules/pyodide \\
        --out playground/index.html

Every asset Pyodide needs at runtime -- its two JS modules, the wasm binary,
the Python stdlib zip, the package lock file -- plus this project's own wheel
are embedded into the page as base64. The built file makes no network
requests at all when opened; see template.html's ``boot()`` for how each
asset is handed to Pyodide instead of being fetched.

The styling, pre-flight checks and rendering come from ../../common/ and are
shared with the componentize-py page; ``embed.render`` injects them. Only the
asset embedding below is Pyodide-specific.

``--pyodide-dir`` is a local install of the npm ``pyodide`` package (i.e.
``tools/playground-wasm/pyodide/smoke/node_modules/pyodide``
  after ``npm ci`` there) --
that package ships these exact files for its own offline/Node use, so this
script reads them from there instead of fetching them a second time.
PYODIDE_VERSION below must match the version pinned in
tools/playground-wasm/pyodide/smoke/package.json; this script checks that itself.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

# The substitution/hard-fail machinery and the shared UI partials, both shared
# with the componentize-py build script next door. sys.path rather than a
# package import: these scripts run from a bare `python3` in CI with nothing
# installed, so there is no package to import from.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

import embed

# Keep in step with the "pyodide" version pinned in
# tools/playground-wasm/pyodide/smoke/package.json -- checked against that file below so the
# two can't silently drift into embedding different Pyodide releases.
PYODIDE_VERSION = "314.0.6"

DEFAULT_TEMPLATE = Path(__file__).parent / "template.html"
PACKAGE_JSON = Path(__file__).parent.parent / "smoke" / "package.json"

# Filename -> template placeholder, for the files read from --pyodide-dir.
_PYODIDE_ASSETS = {
    "pyodide.mjs": "%%PYODIDE_MJS_BASE64%%",
    "pyodide.asm.mjs": "%%PYODIDE_ASM_MJS_BASE64%%",
    "pyodide.asm.wasm": "%%PYODIDE_WASM_BASE64%%",
    "python_stdlib.zip": "%%PYTHON_STDLIB_ZIP_BASE64%%",
    "pyodide-lock.json": "%%PYODIDE_LOCK_JSON_BASE64%%",
}


def _check_pinned_version_matches() -> None:
    """Fail loudly if this script's pin and the npm pin have drifted apart.

    Both name the same Pyodide release on purpose (see module docstring) --
    a silent mismatch would mean the browser page and the Node smoke test
    are quietly exercising two different Pyodide builds.
    """
    package_json = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    npm_version = package_json["dependencies"]["pyodide"]
    if npm_version != PYODIDE_VERSION:
        raise SystemExit(
            f"PYODIDE_VERSION ({PYODIDE_VERSION!r}) in this script does not match "
            f'the "pyodide" version in {PACKAGE_JSON} ({npm_version!r}) -- bump '
            "both together."
        )


def build(wheel_path: Path, pyodide_dir: Path, template_path: Path, out_path: Path) -> None:
    """Fill ``template_path``'s placeholders and write the result to ``out_path``."""
    _check_pinned_version_matches()

    substitutions = {"%%WHEEL_BASE64%%": embed.b64_file(wheel_path)}
    for filename, placeholder in _PYODIDE_ASSETS.items():
        asset_path = pyodide_dir / filename
        if not asset_path.is_file():
            raise SystemExit(f"expected {asset_path} to exist (from --pyodide-dir {pyodide_dir})")
        substitutions[placeholder] = embed.b64_file(asset_path)

    # embed.render injects the shared UI partials, then these substitutions, and
    # hard-fails on any placeholder left over -- including ones this script
    # never knew about.
    embed.write_page(out_path, embed.render(template_path, substitutions))


def _resolve_single(pattern: str, *, kind: str) -> Path:
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise SystemExit(f"no {kind} found matching {pattern!r}")
    if len(matches) > 1:
        raise SystemExit(
            f"expected exactly one {kind} matching {pattern!r}, found {len(matches)}: {matches}"
        )
    return Path(matches[0])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wheel", required=True, help="path or glob to the built wheel")
    parser.add_argument(
        "--pyodide-dir",
        required=True,
        help=(
            "local npm 'pyodide' package install to read the runtime assets from "
            "(e.g. tools/playground-wasm/pyodide/smoke/node_modules/pyodide)"
        ),
    )
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="template HTML path")
    parser.add_argument("--out", required=True, help="output HTML path")
    args = parser.parse_args(argv)

    wheel_path = _resolve_single(args.wheel, kind="wheel")
    pyodide_dir = Path(args.pyodide_dir)
    if not pyodide_dir.is_dir():
        raise SystemExit(f"--pyodide-dir {pyodide_dir} is not a directory")

    build(wheel_path, pyodide_dir, Path(args.template), Path(args.out))
    out_path = Path(args.out)
    print(
        f"wrote {out_path} ({embed.mib(out_path.stat().st_size)}, embedding "
        f"{wheel_path.name} + Pyodide {PYODIDE_VERSION})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
