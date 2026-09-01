#!/usr/bin/env python3
"""Build ``template.html`` into a single, fully offline playground page.

    python tools/playground-wasm/componentize-py/build-playground/build_playground.py \\
        --work dist/componentize \\
        --out playground/bigfix-relevance-analyzer-component-playground.html

The componentize-py counterpart of
``tools/playground-wasm/pyodide/build-playground/build_playground.py``, and
deliberately the same shape: read a generated directory, base64 everything the
page needs into ``template.html``'s placeholders, hard-fail on any placeholder
left unreplaced. The built file makes no network requests at all when opened.

``--work`` is the directory ``../../componentize-py/smoke/transpile.mjs`` wrote:
a ``transpiled/`` subdirectory of core wasm modules, plus ``bundle.mjs``. This
script never runs jco or esbuild itself -- the npm toolchain lives in the smoke
stage, exactly as the Pyodide build script reads Pyodide's runtime assets out of
its smoke stage's ``node_modules``.

One thing this script does that the Pyodide one does not: **the core wasm
modules are embedded gzipped**, and the page inflates them with
``DecompressionStream``. That is not premature optimisation. The cores are
~20 MiB raw, which base64s to ~28 MiB -- a page substantially larger than the
17.7 MiB Pyodide one. Gzipped they are ~7 MiB, so the page lands near 10 MiB
and comes out *smaller* than the Pyodide page instead of half again as large.
The cost is one extra browser requirement, which ``template.html``'s pre-flight
check tests for before the multi-MiB payload downloads.

The core-module count is not pinned: jco decides it, and it moves with the
``--base64-cutoff`` the transpile step passes (0 gives ~14; the default gives
~5). Every ``analyzer.core*.wasm`` found is embedded, and finding none is a
hard failure -- asserting an exact count would just break on the next jco bump
for no safety gained.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import sys
import tomllib
from pathlib import Path

# The substitution/hard-fail machinery and the shared UI partials, both shared
# with the Pyodide build script next door. sys.path rather than a package
# import: these scripts run from a bare `python3` in CI with nothing installed,
# so there is no package to import from.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

import embed

# Keep in step with the `wasm` dependency-group pin in pyproject.toml -- checked
# against it below so the two can't silently drift into building the component
# with a different toolchain (and therefore a different embedded CPython) than
# the one recorded.
COMPONENTIZE_PY_VERSION = "0.25.0"

HERE = Path(__file__).parent
DEFAULT_TEMPLATE = HERE / "template.html"
PYPROJECT = HERE.parent.parent.parent.parent / "pyproject.toml"


def _check_pinned_version_matches() -> None:
    """Fail loudly if this script's pin and pyproject.toml's have drifted apart.

    Both name the same componentize-py release on purpose. componentize-py
    embeds its own CPython-for-WASI build, so its version decides which Python
    actually runs inside the page -- a silent mismatch would mean the page and
    the recorded toolchain are two different things.
    """
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    pins = data["dependency-groups"]["wasm"]
    expected = f"componentize-py=={COMPONENTIZE_PY_VERSION}"
    if expected not in pins:
        raise SystemExit(
            f"COMPONENTIZE_PY_VERSION ({COMPONENTIZE_PY_VERSION!r}) in this script does "
            f"not appear in {PYPROJECT}'s [dependency-groups] wasm ({pins!r}) -- bump "
            "both together."
        )


def _encode_cores(transpiled: Path) -> tuple[str, int, int]:
    """Return the cores as a JSON object of name -> base64(gzip(bytes)).

    Also returns the raw and gzipped byte totals, purely so the caller can
    report them -- the size story is the whole reason this page is viable, so
    it is worth printing rather than leaving to be measured by hand.
    """
    cores = sorted(transpiled.glob("analyzer.core*.wasm"))
    if not cores:
        raise SystemExit(f"no analyzer.core*.wasm found in {transpiled} -- did transpile.mjs run?")

    encoded: dict[str, str] = {}
    raw_total = gz_total = 0
    for core in cores:
        data = core.read_bytes()
        # mtime=0 so a rebuild of unchanged input produces an identical page;
        # gzip stamps the current time into its header otherwise.
        packed = gzip.compress(data, compresslevel=9, mtime=0)
        raw_total += len(data)
        gz_total += len(packed)
        encoded[core.name] = base64.b64encode(packed).decode("ascii")
    return json.dumps(encoded), raw_total, gz_total


def build(work_dir: Path, template_path: Path, out_path: Path) -> None:
    """Fill ``template_path``'s placeholders and write the result to ``out_path``."""
    _check_pinned_version_matches()

    bundle_path = work_dir / "bundle.mjs"
    transpiled = work_dir / "transpiled"
    for required in (bundle_path, transpiled):
        if not required.exists():
            raise SystemExit(f"expected {required} to exist (from --work {work_dir})")

    cores_json, raw_total, gz_total = _encode_cores(transpiled)

    # The bundle goes in as-is, not base64: it is inlined into a
    # <script type="module"> block rather than imported from a data: URL, so
    # there is nothing to decode. (The Pyodide template base64s its JS only
    # because it imports it as a data: URL module.) That also keeps
    # `import.meta.url` inside the bundle pointing at the document, which is
    # what makes the core-module URLs -- and therefore the page's fetch
    # intercept -- resolve.
    substitutions = {
        "%%CORES_GZIP_JSON%%": cores_json,
        "%%BUNDLE_JS%%": bundle_path.read_text(encoding="utf-8"),
    }

    # embed.render injects the shared UI partials, then these substitutions, and
    # hard-fails on any placeholder left over -- including ones this script
    # never knew about.
    size = embed.write_page(out_path, embed.render(template_path, substitutions))
    print(
        f"wrote {out_path} ({embed.mib(size)}, embedding "
        f"{embed.mib(raw_total)} of core wasm as {embed.mib(gz_total)} gzipped "
        f"+ componentize-py {COMPONENTIZE_PY_VERSION})"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--work",
        required=True,
        help="directory transpile.mjs wrote (expects bundle.mjs and transpiled/)",
    )
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="template HTML path")
    parser.add_argument("--out", required=True, help="output HTML path")
    args = parser.parse_args(argv)

    work_dir = Path(args.work)
    if not work_dir.is_dir():
        raise SystemExit(f"--work {work_dir} is not a directory")

    build(work_dir, Path(args.template), Path(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
