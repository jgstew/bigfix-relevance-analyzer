#!/usr/bin/env node
// Bundles editor.mjs -- CodeMirror and the wheel's web/ modules included --
// into one minified classic script for build_playground.py to inline.
//
//     node build.mjs --out ../../../dist/playground-editor.js
//
// A classic script (IIFE), not a module: the Pyodide page boots from a classic
// script, and an inline module would run only after the document is parsed.

import { execFileSync } from "node:child_process";
import { readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const out = args[0] === "--out" && args[1] ? resolve(args[1]) : null;
if (!out) {
  console.error("usage: node build.mjs --out <file.js>");
  process.exit(2);
}

execFileSync(
  join(HERE, "node_modules", ".bin", "esbuild"),
  [join(HERE, "editor.mjs"), "--bundle", "--format=iife", "--platform=browser", "--target=es2022", "--minify", "--charset=ascii", `--outfile=${out}`],
  { cwd: HERE, stdio: ["ignore", "inherit", "inherit"] },
);

// Inlined into an HTML <script> element: the text must not close it early.
const text = readFileSync(out, "utf8");
if (/<\/script|<!--/i.test(text)) throw new Error(`${out} contains "</script" or "<!--" and cannot be inlined`);
process.stderr.write(`  editor bundle ${(statSync(out).size / 1024).toFixed(0)} KiB\n`);
