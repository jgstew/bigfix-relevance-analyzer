#!/usr/bin/env node
// Turns the .wasm component componentize-py produced into one browser-ready
// JS bundle, plus the core wasm modules the page will embed.
//
//     node transpile.mjs --component ../../../../dist/analyzer.wasm --work ../../../../dist/componentize
//
// Browsers cannot load a WebAssembly *component* directly, so this is two
// steps:
//
//   1. `jco transpile` lowers the component to core wasm modules plus JS glue.
//   2. `esbuild` bundles that glue -- and preview2-shim, which the glue
//      imports -- into a single self-contained ES module.
//
// Only the BROWSER bundle is produced. smoke.mjs instead imports the transpiled
// glue directly and lets Node resolve preview2-shim's own Node build, via a
// node_modules symlink dropped into the work directory (see below).
//
// Bundling for Node was tried and is a trap: preview2-shim's Node build loads
// a worker-thread file by path at runtime, which esbuild cannot inline, so the
// bundled version dies with MODULE_NOT_FOUND on that file. The symlink keeps
// the real package layout intact, which is what the shim expects.
//
// The three flag choices below are the ones that took real debugging, so they
// are spelled out rather than left to be rediscovered:
//
// --no-nodejs-compat is REQUIRED, not an optimisation. Without it jco's glue
//   contains `await import('node:fs/promises')` for loading cores off disk, and
//   esbuild's browser build cannot resolve it. This is the first hard error you
//   hit trying to bundle jco output for a browser.
//
// --base64-cutoff 0 keeps every core as a separate file. The default (4096)
//   inlines the small ones as base64 inside the JS, which would then get
//   base64'd a second time on its way into the page -- 1.78x on ~20 MiB. Keep
//   them raw here and let build_playground.py encode each exactly once.
//   Side effect worth knowing: 0 yields ~14 cores where the default yields ~5.
//
// --map 'wasi:sockets/*=...' swaps preview2-shim's sockets for the local stub.
//   componentize-py's CPython links the `socket` module, so the component
//   imports wasi:sockets even though the analyzer never opens one, and
//   preview2-shim's *browser* build still ships the pre-resource flat-function
//   shape for wasi:sockets/ip-name-lookup. Without the map, instantiation dies
//   with "unexpectedly undefined local import 'ResolveAddressStream'". See
//   ../build-playground/sockets_stub.js.
//
// Not used, deliberately: --instantiation async. It would let the page pass
// core modules in directly, but the page already intercepts window.fetch for
// exactly this -- the same trick the Pyodide template uses for
// pyodide.asm.wasm -- and reusing that pattern keeps the two templates
// readable against each other.

import { execFileSync } from "node:child_process";
import {
  copyFileSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  symlinkSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const BUILD = resolve(HERE, "..", "build-playground");

// Kept in step with the pins in this directory's package.json, checked below --
// a silent mismatch would mean the page was built by a different toolchain than
// the one recorded.
const JCO_VERSION = "1.32.1";
const ESBUILD_VERSION = "0.28.2";

function parseArgs(argv) {
  const args = { component: null, work: null };
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i]?.replace(/^--/, "");
    if (!(key in args) || argv[i + 1] === undefined) {
      throw new Error(`usage: node transpile.mjs --component <file.wasm> --work <dir>`);
    }
    args[key] = argv[i + 1];
  }
  if (!args.component || !args.work) {
    throw new Error(`usage: node transpile.mjs --component <file.wasm> --work <dir>`);
  }
  return args;
}

/** Fail loudly if this script's pins and package.json's have drifted apart. */
function checkPinnedVersions() {
  const pkg = JSON.parse(readFileSync(join(HERE, "package.json"), "utf8"));
  for (const [name, expected] of [
    ["@bytecodealliance/jco", JCO_VERSION],
    ["esbuild", ESBUILD_VERSION],
  ]) {
    const pinned = pkg.dependencies[name];
    if (pinned !== expected) {
      throw new Error(
        `${name} is pinned to ${pinned} in package.json but this script expects ` +
          `${expected} -- bump both together.`
      );
    }
  }
}

function run(bin, argv, label, env) {
  process.stderr.write(`  ${label}\n`);
  execFileSync(bin, argv, {
    cwd: HERE,
    stdio: ["ignore", "inherit", "inherit"],
    env: { ...process.env, ...env },
  });
}

const { component, work } = parseArgs(process.argv.slice(2));
checkPinnedVersions();

const componentPath = resolve(component);
const workDir = resolve(work);
const transpiled = join(workDir, "transpiled");

// A stale core module from a previous run would be silently embedded by
// build_playground.py, which globs this directory.
rmSync(workDir, { recursive: true, force: true });
mkdirSync(workDir, { recursive: true });

// The stub and the bundle entry are source (in ../build-playground/); copy them
// in so the whole bundle input is one generated directory and the entry's
// `./transpiled/analyzer.js` import resolves.
copyFileSync(join(BUILD, "sockets_stub.js"), join(workDir, "sockets_stub.js"));
copyFileSync(join(BUILD, "entry.mjs"), join(workDir, "entry.mjs"));

// The work directory lives under dist/, so nothing in it can resolve
// `@bytecodealliance/preview2-shim` by name -- there is no node_modules on the
// way up to the repo root. This symlink puts one there, which is how smoke.mjs
// gets to import the transpiled glue directly and exercise the shim's real
// Node build (worker thread and all) rather than a bundled copy of it.
symlinkSync(join(HERE, "node_modules"), join(workDir, "node_modules"), "dir");

run(
  join(HERE, "node_modules", ".bin", "jco"),
  [
    "transpile",
    componentPath,
    "-o",
    transpiled,
    "--tla-compat",
    "--no-nodejs-compat",
    "--base64-cutoff",
    "0",
    // Resolved relative to the emitted glue, which lands in transpiled/.
    "--map",
    "wasi:sockets/*=../sockets_stub.js#*",
  ],
  `jco ${JCO_VERSION} transpile`
);

// The work directory is outside this npm package (it lives under dist/), so
// walking up from the entry file never reaches a node_modules holding
// preview2-shim. NODE_PATH is how the esbuild CLI takes an extra resolution
// root -- its --node-paths equivalent exists only in the JS API. Pointing it
// here beats moving generated files into the source tree.
const esbuildEnv = { NODE_PATH: join(HERE, "node_modules") };

function bundle(outfile, platformArgs, label) {
  run(
    join(HERE, "node_modules", ".bin", "esbuild"),
    [
      join(workDir, "entry.mjs"),
      "--bundle",
      "--format=esm",
      ...platformArgs,
      "--target=es2022",
      "--minify",
      `--outfile=${join(workDir, outfile)}`,
    ],
    label,
    esbuildEnv
  );
}

bundle(
  "bundle.mjs",
  [
    "--platform=browser",
    // This is what selects preview2-shim's browser entry (in-memory virtual FS)
    // over its Node one. If it stops taking effect, the unresolved-node:-import
    // check below is what catches it.
    "--conditions=browser",
  ],
  `esbuild ${ESBUILD_VERSION} bundle (browser)`
);

// A `node:` specifier surviving into the BROWSER bundle means the browser
// condition did not apply and the page would fail at load. Assert rather than
// hope -- the alternative is a 10 MiB page that throws on open. (The Node
// bundle is expected to contain them, so it is not checked.)
const browserBundle = readFileSync(join(workDir, "bundle.mjs"), "utf8");
const nodeImports = [...new Set(browserBundle.match(/node:[a-z_/]+/g) ?? [])];
if (nodeImports.length) {
  throw new Error(
    `bundle still references Node builtins (${nodeImports.join(", ")}) -- the ` +
      `browser condition did not apply. Do NOT paper over this with --external.`
  );
}

const cores = readdirSync(transpiled).filter((f) => /^analyzer\.core\d*\.wasm$/.test(f));
if (cores.length === 0) {
  throw new Error(`jco emitted no core modules into ${transpiled}`);
}
const coreBytes = cores.reduce((n, f) => n + statSync(join(transpiled, f)).size, 0);
const mib = (n) => `${(n / 1048576).toFixed(1)} MiB`;
process.stderr.write(
  `  ${cores.length} core module(s), ${mib(coreBytes)}; browser bundle ${mib(browserBundle.length)}\n`
);
