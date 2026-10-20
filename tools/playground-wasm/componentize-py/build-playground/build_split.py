#!/usr/bin/env python3
"""Build the split analyzer set: the componentize-py analyzer as separate files.

    python tools/playground-wasm/componentize-py/build-playground/build_split.py \\
        --work dist/componentize/web \\
        --editor-bundle dist/playground-editor.js \\
        --out playground/analyzer \\
        --zip playground/bigfix-relevance-analyzer-web.zip

The single-file page (``build_playground.py``, beside this) embeds everything
in one ~12 MiB HTML file, which is what makes it work offline -- and what makes
it a poor thing to fetch and cut apart at run time, which is what a BigFix Web
Reports custom report embedding the analyzer had to do. This writes the same
pieces as files instead, in one flat, always-latest folder:

    manifest.json              the version, and every file's size and sha256
                               (and each core's inflated raw_size/raw_sha256)
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
* **the version is the transpiled wheel's.** It is read from the
  ``.dist-info`` componentize.py staged beside ``--work`` (``<work>/../deps``),
  which is exactly what the component's ``version()`` reads at run time -- not
  from ``pyproject.toml``, which a stale ``dist/`` can disagree with.
* **the glue uses ``import.meta`` only as ``import.meta.url``.** Consumers that
  run it from a blob: URL substitute that literal text, so the build fails if
  it is missing or if any other ``import.meta`` use appears.
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
import gzip
import hashlib
import json
import re
import sys
import zipfile
from email.parser import HeaderParser
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

# Any `import.meta` that is not exactly `import.meta.url` (`.resolve(`, a bare
# `import.meta`, a future property): the contract promises consumers there is
# none, see the module docstring.
_OTHER_IMPORT_META_RE = re.compile(r"import\.meta(?!\.url\b)")

# Files a previous build may have left that this one did not write. Only these
# are ever removed: the folder is build output, but nothing else in it is ours.
_SET_FILE_RE = re.compile(
    r"(manifest\.json|index\.html|editor\.js|glue\.mjs|analyzer\.core\d*\.wasm\.gz)"
)

# 1980-01-01, the earliest time a zip can record: any fixed value makes the
# zip reproducible, this one is the conventional choice.
_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def staged_version(deps: Path) -> str:
    """The version of the wheel componentize.py staged into ``deps``.

    Read from its ``.dist-info/METADATA``, the same file ``importlib.metadata``
    reads inside the component, so this is what ``version()`` will report.
    """
    found = sorted(deps.glob("bigfix_relevance_analyzer-*.dist-info"))
    if len(found) != 1:
        raise SystemExit(
            f"expected exactly one bigfix_relevance_analyzer-*.dist-info in {deps} (staged by "
            f"componentize.py), found {[p.name for p in found] or 'none'}"
        )
    metadata = HeaderParser().parsestr((found[0] / "METADATA").read_text(encoding="utf-8"))
    version = metadata["Version"]
    if not version:
        raise SystemExit(f"{found[0] / 'METADATA'} has no Version")
    return str(version)


def check_import_meta(glue: str, glue_path: Path) -> None:
    """The glue must reference ``import.meta.url`` and no other ``import.meta``."""
    if "import.meta.url" not in glue:
        raise SystemExit(f"{glue_path} never uses import.meta.url -- not jco's glue?")
    other = _OTHER_IMPORT_META_RE.search(glue)
    if other:
        context = glue[max(0, other.start() - 40) : other.end() + 40]
        raise SystemExit(
            f"{glue_path} uses import.meta other than as import.meta.url, which consumers "
            f"that substitute import.meta.url cannot handle: ...{context!r}..."
        )


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
            # Unix, a regular file, 0644: the same bytes whichever OS builds it
            # (ZipInfo would otherwise record the building OS).
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)


def build(
    work_dir: Path,
    editor_bundle: Path,
    out_dir: Path,
    *,
    deps_dir: Path | None = None,
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
    glue_text = glue.decode("utf-8")
    check_import_meta(glue_text, glue_path)
    cores, raw_total = build_playground.gzip_cores(transpiled)
    version = staged_version(deps_dir if deps_dir is not None else work_dir.parent / "deps")

    wanted = glue_core_names(glue_text)
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
        raw = gzip.decompress(packed)
        # name, path, encoding, size, sha256, raw_size, raw_sha256: the
        # contract's order. raw_* are what a consumer checks when a server
        # inflated the .gz in transit and the published bytes never arrived.
        core_entries.append(
            {
                "name": name,
                "path": path,
                "encoding": "gzip",
                "size": len(packed),
                "sha256": hashlib.sha256(packed).hexdigest(),
                "raw_size": len(raw),
                "raw_sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
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
        "version": version,
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
    parser.add_argument(
        "--deps",
        help="componentize.py's staged deps/, for the wheel version (default: <work>/../deps)",
    )
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="index.html template")
    args = parser.parse_args(argv)

    work_dir = Path(args.work)
    if not work_dir.is_dir():
        raise SystemExit(f"--work {work_dir} is not a directory")

    build(
        work_dir,
        Path(args.editor_bundle),
        Path(args.out),
        deps_dir=Path(args.deps) if args.deps else None,
        template_path=Path(args.template),
        zip_path=Path(args.zip) if args.zip else None,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
