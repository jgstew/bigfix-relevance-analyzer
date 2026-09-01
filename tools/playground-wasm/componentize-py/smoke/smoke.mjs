#!/usr/bin/env node
// Proves the component componentize.py built actually runs -- in Node, with no
// system Python involved at all, which is the constraint a VS Code extension
// bundling this package would ship under (see issue #10). The componentize-py
// counterpart of ../../pyodide/smoke/smoke.mjs, checking the same things about
// the same example so the two reports read against each other.
//
// What can go wrong on this path and only shows up here:
//
// * an import the build-time snapshot missed. componentize-py resolves imports
//   when it pre-initializes the interpreter, so a module first reached at
//   runtime throws (bytecodealliance/componentize-py#23) -- and `analyze` is
//   the first thing that runs any of the analyzer's real code paths.
// * `version()` coming back "0.0.0", which means the wheel's .dist-info did not
//   survive into the component and `importlib.metadata` found nothing. Asserted
//   below, because it is silent otherwise -- the page would just show a wrong
//   version.
//
// This runs the Node bundle (jco's glue plus preview2-shim's *Node* build), so
// it says nothing about the browser: the browser build resolves preview2-shim
// differently -- including the stale wasi:sockets shape the page has to stub
// around -- and is covered by ../browser-test/.
//
// Usage: node smoke.mjs <work-dir>   (the directory transpile.mjs wrote)

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { join, resolve } from "node:path";

const workDir = process.argv[2];
if (!workDir) {
  console.error("usage: node smoke.mjs <work-dir>");
  process.exit(2);
}

// transpile.mjs passes jco's --no-nodejs-compat, which is mandatory for the
// browser bundle (its Node fallback does `import('node:fs/promises')`, which
// esbuild's browser build cannot resolve). The consequence here is that the
// glue loads core modules with plain `fetch`, and Node's fetch rejects `file:`
// URLs outright -- "not implemented... yet...".
//
// Teaching fetch about the core modules is a handful of lines. The alternative
// is a second 30-second jco pass purely to get Node-flavoured glue, which is
// not worth it for a smoke test.
//
// Matched on basename, not full path, the same way the page's intercept does --
// see ../build-playground/template.html.
const realFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
  const name = url.split("/").pop();
  if (url.startsWith("file:") && /^analyzer\.core\d*\.wasm$/.test(name)) {
    return new Response(readFileSync(join(resolve(workDir), "transpiled", name)), {
      status: 200,
      headers: { "Content-Type": "application/wasm" },
    });
  }
  return realFetch(input, init);
};

// The transpiled glue directly, not a bundle. It imports preview2-shim by name,
// which resolves because transpile.mjs symlinks a node_modules into the work
// directory -- and that matters: preview2-shim's Node build loads a worker
// thread by path at runtime, so a bundled copy of it dies with
// MODULE_NOT_FOUND. Imported by file URL so a path outside this package works.
const gluePath = resolve(join(workDir, "transpiled", "analyzer.js"));
const component = await import(pathToFileURL(gluePath).href);

// --tla-compat means the glue does not top-level-await its own instantiation;
// awaiting $init is what drives it. Timed because it is the number the whole
// componentize-py-over-Pyodide case rests on.
const bootStart = performance.now();
await component.$init;
const bootMs = Math.round(performance.now() - bootStart);

const version = component.version();

// Same example as the Pyodide smoke test, for the same reasons: it is not a
// bare property lookup, because that would have no unambiguous dialect marker.
// `operating system` alone classifies as null on purpose (dialect.py:172-174
// excludes it -- it is valid in both client and session relevance), whereas
// `running application` has no such overlap. Pairing them gives the analyzer a
// boolean expression, a comparison, an `of`-chain and a real dialect to
// classify, all in one statement.
const payload = JSON.parse(
  component.analyze(
    'exists running application "winlogon.exe" AND version of operating system >= "10.0"'
  )
);

function fail(message) {
  console.error(`smoke check failed: ${message}`);
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}

if (!payload || typeof payload !== "object") fail("analyze returned no payload");
if (version === "0.0.0") {
  fail(
    "version() is \"0.0.0\", which means importlib.metadata found no package " +
      "metadata inside the component -- the wheel's .dist-info did not make it " +
      "in. componentize.py installs the wheel with `uv pip install --target` " +
      "rather than vendoring the package directory precisely to avoid this."
  );
}
if (payload.dialect?.classified !== "client") {
  fail(`expected dialect.classified === "client", got ${JSON.stringify(payload.dialect)}`);
}
if (payload.parse?.ok !== true) fail(`expected parse.ok === true, got ${JSON.stringify(payload.parse)}`);
if (payload.types?.ok !== true) fail(`expected types.ok === true, got ${JSON.stringify(payload.types)}`);

// Plain Markdown on stdout, nothing CI-specific -- this script has no idea
// whether it's running in a GitHub Action, a terminal, or anything else, and it
// stays that way on purpose: where this output *goes* (a log, a step summary,
// both) is a decision for whatever invokes it. See
// .github/workflows/wasm-html.yaml for how the workflow uses it.
const referenceRows = payload.references
  .map((ref) => `| \`${ref.phrase}\` | ${ref.known} | ${ref.return_types.join(", ")} |`)
  .join("\n");

const coreCount = readFileSync(resolve(join(workDir, "transpiled", "analyzer.js")), "utf8").match(
  /analyzer\.core\d*\.wasm/g
);

console.log(`\
## bigfix-relevance-analyzer as a WebAssembly component (Node)

\`bigfix_relevance_analyzer\` ${version}, compiled by componentize-py into a single Wasm component together with its own CPython, then transpiled by jco -- no system Python involved. See [issue #10](https://github.com/jgstew/bigfix-relevance-analyzer/issues/10).

Instantiated in **${bootMs} ms** from ${new Set(coreCount ?? []).size} core module(s). The interpreter is pre-initialized at build time, so there is no stdlib unpack and no import cost here -- only Wasm compilation.

**Input:** \`${payload.text}\`

| | |
| --- | --- |
| dialect | ${payload.dialect.classified} (effective: ${payload.dialect.effective}, assumed: ${payload.dialect.assumed}) |
| tokens | ${payload.lexing.tokens} (${payload.lexing.code_tokens} code) |
| parse | ok, ${payload.parse.node_count} nodes, depth ${payload.parse.tree_depth} |
| complexity score | ${payload.complexity.score} |
| evaluation cost | ${payload.complexity.evaluation_cost} |
| result type | ${payload.types.types.join(", ")} (${payload.types.plurality}) |
| viable in | ${payload.platforms.viable.join(", ")} |

**S-expression**

\`\`\`
${payload.parse.sexpr}
\`\`\`

**References**

| phrase | known | return type(s) |
| --- | --- | --- |
${referenceRows}`);
