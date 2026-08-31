#!/usr/bin/env node
// Recompiles this project's wheel's .py files to .pyc bytecode using the
// exact same Pyodide/CPython build the playground later embeds, and writes
// a new zip with the .py sources REPLACED by their compiled .pyc rather than
// carrying both -- a "sourceless" distribution (a bare module.pyc sitting
// where module.py would be, no __pycache__ directory, no version tag in the
// filename; still a fully standard, importlib-supported layout, just an
// unusual one). Roughly halves this package's contribution to the embedded
// payload (confirmed: ~1.16 MiB of .py source vs. ~1.22 MiB of .pyc for the
// same modules -- keeping both, as an earlier version of this script did,
// nearly doubled it instead of trading one for the other).
//
// The real trade-off, worth being honest about: if something here ever
// raises an unexpected exception, the browser console traceback will show
// bare "<module>.pyc" filenames with no inline source snippet -- just a
// filename and line number, cross-referenceable against this repo's public
// source on GitHub, but not shown inline the way a normal Python traceback
// is. Given analyze_relevance_to_dict()'s documented contract is to never
// raise for bad *relevance* input, this should only ever matter for a real
// bug, not routine use.
//
// No version-mismatch risk in shipping compiled-only, either: this .pyc is
// produced by, and only ever consumed by, this exact Pyodide build.
//
// Doing this HERE, in Node with Pyodide, rather than with the CI runner's
// own host Python, is deliberate: the .pyc magic number turns out to be
// tied to the CPython *language* version, not the platform/build -- Pyodide
// 314.0.6's CPython 3.14.2 and a plain macOS CPython 3.14.6 both report the
// identical magic number (b'+\x0e\r\n' at the time of writing). But this
// project's pyodide.yaml workflow pins actions/setup-python to "3.13",
// already a minor version behind what Pyodide currently ships (3.14) --
// relying on the *host's* Python version staying in lockstep with whatever
// Pyodide happens to bundle is exactly the drift this avoids by
// construction: compiling with Pyodide itself is correct on any host,
// forever, regardless of what Python version either side is nominally on.
//
// A real compile failure -- this project's source not compiling under the
// CPython version Pyodide currently ships -- fails this script, and so this
// CI job, instead of surfacing as a confusing runtime failure for someone
// using the playground.
//
// Usage: node precompile_wheel.mjs --wheel dist/*.whl --out dist/compiled.zip

import { readFileSync, writeFileSync } from "node:fs";
import { basename } from "node:path";
import { loadPyodide } from "pyodide";

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 2) {
    args[argv[i].replace(/^--/, "")] = argv[i + 1];
  }
  return args;
}

const { wheel: wheelPath, out: outPath } = parseArgs(process.argv.slice(2));
if (!wheelPath || !outPath) {
  console.error("usage: node precompile_wheel.mjs --wheel <path> --out <path>");
  process.exit(2);
}

const wheelBytes = readFileSync(wheelPath);
const wheelName = basename(wheelPath);

const pyodide = await loadPyodide();
pyodide.FS.writeFile(`/tmp/${wheelName}`, wheelBytes);

const resultBase64 = pyodide.runPython(`
import base64
import io
import os
import py_compile
import zipfile

with zipfile.ZipFile("/tmp/${wheelName}") as archive:
    archive.extractall("/tmp/site-packages")

# Compile each .py to a *sibling* module.pyc (not module.cpython-XY.pyc in
# __pycache__/) and delete the source -- the "sourceless" layout, which
# importlib's default FileFinder recognizes on its own; nothing project-side
# needs to change to load it. doraise=True is what turns a real syntax error
# into an exception here rather than a silently-skipped file.
converted = 0
for root, _dirs, files in os.walk("/tmp/site-packages"):
    for name in list(files):
        if not name.endswith(".py"):
            continue
        src = os.path.join(root, name)
        pyc = os.path.splitext(src)[0] + ".pyc"
        py_compile.compile(src, cfile=pyc, doraise=True)
        os.remove(src)
        converted += 1
if not converted:
    raise SystemExit("no .py files found to compile -- wheel layout may have changed")

buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as out_zip:
    for root, _dirs, files in os.walk("/tmp/site-packages"):
        for name in files:
            full_path = os.path.join(root, name)
            out_zip.write(full_path, os.path.relpath(full_path, "/tmp/site-packages"))

base64.b64encode(buffer.getvalue()).decode("ascii")
`);

const outBytes = Buffer.from(resultBase64, "base64");
writeFileSync(outPath, outBytes);
console.log(`wrote ${outPath} (${(outBytes.length / 1024).toFixed(0)} KiB) with .pyc precompiled by Pyodide's own CPython`);
