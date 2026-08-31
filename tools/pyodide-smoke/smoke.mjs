#!/usr/bin/env node
// Proves the wheel this project builds actually installs and runs under
// Pyodide (CPython compiled to WASM) in Node -- with no system Python
// involved at all, which is the constraint a VS Code extension bundling this
// package would ship under (see issue #10). This is the smallest thing that
// can go wrong on that path short of building a real language server: a
// build that produces a wheel micropip can't install, or code that reaches
// for something the WASM runtime doesn't have. It does not exercise LSP,
// completion, or any editor surface -- just import, run one analysis, and
// check the shape of what comes back.
//
// Usage: node tools/pyodide_smoke.mjs dist/bigfix_relevance_analyzer-*.whl

import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { loadPyodide } from "pyodide";

const wheelPath = process.argv[2];
if (!wheelPath) {
  console.error("usage: node tools/pyodide_smoke.mjs <path-to-wheel>");
  process.exit(2);
}

const wheelBytes = readFileSync(wheelPath);
const wheelName = basename(wheelPath);

const pyodide = await loadPyodide();
await pyodide.loadPackage("micropip");
const micropip = pyodide.pyimport("micropip");

// Hand the wheel to micropip via Pyodide's in-memory filesystem rather than
// a PyPI round trip or a throwaway local HTTP server -- `emfs:` is
// micropip's scheme for a file already sitting in the Emscripten FS.
pyodide.FS.writeFile(`/tmp/${wheelName}`, wheelBytes);
await micropip.install(`emfs:/tmp/${wheelName}`);

// dependencies = [] in pyproject.toml is what makes this whole approach
// viable in the first place; nothing extra to micropip.install here proves
// that's still true.
const resultJson = await pyodide.runPythonAsync(`
    import json

    from bigfix_relevance_analyzer import __version__, analyze_relevance_to_dict

    # Small but non-trivial: a property comparison, so there's a dialect to
    # classify and a type to check, not just a bare token.
    payload = analyze_relevance_to_dict('name of operating system = "Test"')
    json.dumps({"version": __version__, "payload": payload})
`);

const { version, payload } = JSON.parse(resultJson);

if (!payload || typeof payload !== "object" || !("dialect" in payload)) {
  console.error("smoke check failed: analyze_relevance_to_dict did not return the expected shape");
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}

console.log(`bigfix_relevance_analyzer ${version} imported and ran under Pyodide in Node`);
console.log(`classified dialect: ${payload.dialect.classified}`);
console.log(`token count: ${payload.lexing.tokens}`);
