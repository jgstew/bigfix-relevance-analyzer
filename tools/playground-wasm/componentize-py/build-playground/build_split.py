#!/usr/bin/env python3
"""Build the split analyzer set: the componentize-py analyzer as separate files.

    python tools/playground-wasm/componentize-py/build-playground/build_split.py \\
        --work dist/componentize/web \\
        --editor-bundle dist/playground-editor.js \\
        --out playground/analyzer \\
        --zip playground/bigfix-relevance-analyzer-analyzer.zip

The single-file page (``build_playground.py``, beside this) embeds everything
in one ~12 MiB HTML file, which is what makes it work offline -- and what makes
it a poor thing to fetch and cut apart at run time, which is what a BigFix Web
Reports custom report embedding the analyzer had to do. This writes the same
pieces as files instead, in one flat, always-latest folder:

    manifest.json              the version, and every file's size and sha256
    editor.js                  the editor bundle, unmodified
    glue.mjs                   jco's bundle.mjs, unmodified
    analyzer.core*.wasm.gz     each core module, gzipped exactly as the page does
    index.html                 a playground page that loads the set over HTTP

``tools/playground-wasm/SPLIT_ANALYZER.md`` is the contract consumers rely on;
change it and this together.

Two invariants this script exists to hold:

* **glue and cores match.** They come from the same ``--work`` directory (one
  jco transpile), and every ``analyzer.core*.wasm`` name the glue mentions must
  be a core on disk and vice versa -- a hard failure otherwise.
* **manifest.json is written last**, after every file it names, and removed
  before any of them is touched. A reader that sees a manifest therefore sees
  a set that was completely written. All inputs are validated before the
  folder is touched at all, so a failed build leaves the previous set as it was.

``--zip`` also writes the folder as a flat, deterministic zip (fixed
timestamps, manifest last): the release asset a site publishing the set
verifies against the release's SHA256SUMS.txt and unpacks as-is.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
import zipfile
from pathlib import Path
from typing import Any

# build_playground for the shared core gzip and version-pin check; embed (which
# build_playground puts on sys.path) for the template machinery. Path imports
# for the same reason as there: CI runs this from a bare python3.
sys.path.insert(0, str(Path(__file__).parent))

import build_playground
import embed

HERE = Path(__file__).parent
DEFAULT_TEMPLATE = HERE / "split_template.html"
PACKAGE = "bigfix-relevance-analyzer"
FORMAT = 1
MANIFEST = "manifest.json"
INDEX = "index.html"
EDITOR = "editor.js"
GLUE = "glue.mjs"

# The names the glue builds core URLs from: `new URL('./analyzer.core4.wasm',
# import.meta.url)`. Matched as bare names, whatever quoting jco or esbuild
# chooses.
_CORE_NAME_RE = re.compile(r"analyzer\.core\d*\.wasm")

# Files a previous build may have left that this one did not write. Only these
# are ever removed: the folder is build output, but nothing else in it is ours.
_SET_FILE_RE = re.compile(
    r"(manifest\.json|index\.html|editor\.js|glue\.mjs|analyzer\.core\d*\.wasm\.gz)"
)

# 1980-01-01, the earliest time a zip can record: any fixed value makes the
# zip reproducible, this one is the conventional choice.
_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def package_version() -> str:
    """The version in pyproject.toml -- the one the wheel, and so the glue, was built at."""
    data = tomllib.loads(build_playground.PYPROJECT.read_text(encoding="utf-8"))
    version: str = data["project"]["version"]
    return version


def glue_core_names(glue: str) -> set[str]:
    """Every core module name the glue would fetch."""
    return set(_CORE_NAME_RE.findall(glue))


def _entry(path: str, data: bytes) -> dict[str, Any]:
    return {"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _write(path: Path, data: bytes) -> None:
    """Write one file of the set. One function so tests can watch the order."""
    path.write_bytes(data)


def _manifest_bytes(manifest: dict[str, Any]) -> bytes:
    return (json.dumps(manifest, indent=2) + "\n").encode("ascii")


def write_zip(zip_path: Path, files: dict[str, bytes]) -> None:
    """Write ``files`` (name -> bytes, in order) as a flat, reproducible zip."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w") as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, date_time=_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data, compresslevel=9)


def build(
    work_dir: Path,
    editor_bundle: Path,
    out_dir: Path,
    *,
    version: str | None = None,
    template_path: Path = DEFAULT_TEMPLATE,
    zip_path: Path | None = None,
) -> dict[str, Any]:
    """Write the set into ``out_dir`` (and ``zip_path``) and return its manifest."""
    build_playground._check_pinned_version_matches()

    glue_path = work_dir / "bundle.mjs"
    transpiled = work_dir / "transpiled"
    for required in (glue_path, transpiled):
        if not required.exists():
            raise SystemExit(f"expected {required} to exist (from --work {work_dir})")

    # Everything is read and checked before out_dir is touched.
    editor = embed.editor_js(editor_bundle).encode("ascii")
    glue = glue_path.read_bytes()
    cores, raw_total = build_playground.gzip_cores(transpiled)

    wanted = glue_core_names(glue.decode("utf-8"))
    missing = sorted(wanted - cores.keys())
    unused = sorted(cores.keys() - wanted)
    if missing or unused:
        raise SystemExit(
            f"{glue_path} and {transpiled} do not match -- they must come from one jco "
            f"transpile. Named by the glue but not on disk: {missing or 'none'}; on disk "
            f"but never named by the glue: {unused or 'none'}"
        )

    files: dict[str, bytes] = {EDITOR: editor, GLUE: glue}
    core_entries = []
    for name, packed in cores.items():
        path = f"{name}.gz"
        files[path] = packed
        entry = _entry(path, packed)
        # name, path, encoding, size, sha256: the contract's order.
        core_entries.append({"name": name, "path": path, "encoding": "gzip", **entry})
    files[INDEX] = embed.render(
        template_path,
        {
            # The editor is fetched by the page, not inlined: the shared
            # script's slot for it holds only a pointer to where it comes from.
            "%%EDITOR_JS%%": f"// {EDITOR} is fetched and run by the loader below.",
        },
    ).encode("utf-8")
    if not files[INDEX].isascii():
        raise SystemExit(f"{template_path} rendered to non-ASCII text")

    manifest = {
        "format": FORMAT,
        "package": PACKAGE,
        "version": version or package_version(),
        "editor": _entry(EDITOR, editor),
        "glue": _entry(GLUE, glue),
        "cores": core_entries,
    }
    files[MANIFEST] = _manifest_bytes(manifest)

    out_dir.mkdir(parents=True, exist_ok=True)
    # The old manifest goes first, so no reader ever pairs it with new files.
    (out_dir / MANIFEST).unlink(missing_ok=True)
    for stale in out_dir.iterdir():
        if stale.is_file() and _SET_FILE_RE.fullmatch(stale.name) and stale.name not in files:
            stale.unlink()
    for name, data in files.items():
        _write(out_dir / name, data)

    if zip_path is not None:
        write_zip(zip_path, files)

    gz_total = sum(len(data) for data in cores.values())
    print(
        f"wrote {out_dir}/ ({len(files)} files, {embed.mib(sum(map(len, files.values())))}: "
        f"{len(cores)} cores, {embed.mib(raw_total)} as {embed.mib(gz_total)} gzipped) "
        f"for {PACKAGE} {manifest['version']}" + (f", and {zip_path}" if zip_path else "")
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--work",
        required=True,
        help="directory transpile.mjs wrote (expects bundle.mjs and transpiled/)",
    )
    parser.add_argument(
        "--editor-bundle",
        required=True,
        help="the editor script ../../editor-bundle/build.mjs wrote",
    )
    parser.add_argument("--out", required=True, help="output folder (flat)")
    parser.add_argument("--zip", help="also write the folder as this flat zip")
    parser.add_argument("--version", help="version for manifest.json (default: pyproject.toml's)")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="index.html template")
    args = parser.parse_args(argv)

    work_dir = Path(args.work)
    if not work_dir.is_dir():
        raise SystemExit(f"--work {work_dir} is not a directory")

    build(
        work_dir,
        Path(args.editor_bundle),
        Path(args.out),
        version=args.version,
        template_path=Path(args.template),
        zip_path=Path(args.zip) if args.zip else None,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
