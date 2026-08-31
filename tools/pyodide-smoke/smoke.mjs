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
//
// The example itself is deliberately not a bare property lookup: it needs an
// *unambiguous* dialect marker to be worth showing. `operating system` alone
// would classify as null -- dialect.py:172-174 excludes it on purpose because
// it is valid in both client and session relevance (`operating system of
// <bes computer>` is a session inspector too). `running application` has no
// such overlap, so pairing it with a second clause gives the analyzer a
// boolean expression, a comparison, an `of`-chain, and a real dialect to
// classify, all in one statement.
const resultJson = await pyodide.runPythonAsync(`
    import json

    from bigfix_relevance_analyzer import __version__, analyze_relevance_to_dict

    payload = analyze_relevance_to_dict(
        'exists running application "winlogon.exe" AND '
        'version of operating system >= "10.0"'
    )
    json.dumps({"version": __version__, "payload": payload})
`);

const { version, payload } = JSON.parse(resultJson);

function fail(message) {
  console.error(`smoke check failed: ${message}`);
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}

if (!payload || typeof payload !== "object") fail("analyze_relevance_to_dict returned no payload");
if (payload.dialect?.classified !== "client") {
  fail(`expected dialect.classified === "client", got ${JSON.stringify(payload.dialect)}`);
}
if (payload.parse?.ok !== true) fail(`expected parse.ok === true, got ${JSON.stringify(payload.parse)}`);
if (payload.types?.ok !== true) fail(`expected types.ok === true, got ${JSON.stringify(payload.types)}`);

console.log(`bigfix_relevance_analyzer ${version} imported and ran under Pyodide in Node\n`);
console.log(`input:  ${payload.text}\n`);

console.log("dialect:");
console.log(`  classified: ${payload.dialect.classified}  (effective: ${payload.dialect.effective}, assumed: ${payload.dialect.assumed})`);

console.log("\nlexing:");
console.log(`  ${payload.lexing.tokens} tokens (${payload.lexing.code_tokens} code) -- ${JSON.stringify(payload.lexing.by_kind)}`);

console.log("\nparse:");
console.log(`  ok, ${payload.parse.node_count} nodes, tree depth ${payload.parse.tree_depth}`);
console.log(`  s-expression: ${payload.parse.sexpr}`);

console.log("\ncomplexity:");
console.log(`  score: ${payload.complexity.score}  evaluation cost: ${payload.complexity.evaluation_cost}`);

console.log("\ntypes:");
console.log(`  result type(s): ${payload.types.types.join(", ")} (${payload.types.plurality})`);

console.log("\nplatforms viable:");
console.log(`  ${payload.platforms.viable.join(", ")}`);

console.log("\nreferences:");
for (const ref of payload.references) {
  console.log(`  ${ref.phrase} -- known: ${ref.known}, return type(s): ${ref.return_types.join(", ")}`);
}
