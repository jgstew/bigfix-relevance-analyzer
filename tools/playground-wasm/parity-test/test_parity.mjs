#!/usr/bin/env node
// Loads both built playground pages in one browser and asserts they produce
// byte-identical JSON for the same inputs: the analysis of every statement, and
// the language server's reply to every step of ../common/lsp_script.mjs.
//
// This is the reason two runtimes are kept. Each runtime's own browser-test
// proves its page renders the expected badges for five cases; neither can tell
// you that the two runtimes *agree*. They embed different CPython builds
// compiled by different toolchains, so the places they could diverge are real
// and quiet: dict ordering, float repr, `re` semantics, the text of an
// exception that ends up inside a diagnostic. None of those would fail a badge
// assertion, and all of them would change what a user is told.
//
// A string comparison, not a structural one, and deliberately so. Both pages'
// `window.analyzeJson` returns the output of `json.dumps` run inside their own
// Python -- comparing those strings catches key-order and number-formatting
// differences that `JSON.parse` on both sides would silently normalise away.
//
// The corpus is the shared regression cases plus every source statement in
// tests/corpus/*.rlvcorpus. Those files exist to pin parser behaviour and are
// already curated for edge cases, which makes them exactly the right input
// here; parsing them in JS beats generating a fixture, since a fixture could
// drift from the corpus the Python tests actually run.
//
// Usage: node test_parity.mjs <pyodide-page.html> <componentize-page.html>

import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright";

import { CASES } from "../common/cases.mjs";
import { LSP_STATEMENTS, runLspScript } from "../common/lsp_script.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const CORPUS_DIR = resolve(HERE, "..", "..", "..", "tests", "corpus");

const pages = process.argv.slice(2);
if (pages.length !== 2) {
  console.error("usage: node test_parity.mjs <pyodide-page.html> <componentize-page.html>");
  process.exit(2);
}

/**
 * Pull the source side out of every record in a .rlvcorpus file.
 *
 * Record format (see tests/test_parser_corpus.py, which is the authority):
 *
 *     ==== title of the case
 *     relevance source, which may span lines
 *     ----
 *     (expected s-expression)
 *
 * Only the source matters here -- what the tree should be is the Python
 * suite's business. Records whose expected side pins a ParseError are kept
 * on purpose: "both runtimes report the same error, at the same position, with
 * the same message" is exactly the kind of agreement worth checking.
 */
function corpusSources() {
  const sources = [];
  for (const file of readdirSync(CORPUS_DIR).filter((f) => f.endsWith(".rlvcorpus")).sort()) {
    let collecting = false;
    let lines = [];
    const flush = () => {
      const source = lines.join("\n").trim();
      if (source) sources.push(source);
      lines = [];
    };
    for (const line of readFileSync(join(CORPUS_DIR, file), "utf8").split("\n")) {
      if (line.startsWith("==== ")) {
        flush();
        collecting = true;
      } else if (line.startsWith("----")) {
        flush();
        collecting = false;
      } else if (collecting) {
        lines.push(line);
      }
    }
    flush();
  }
  return sources;
}

const corpus = [...new Set([...CASES.map((c) => c.text), ...corpusSources()])];
if (corpus.length < 50) {
  console.error(
    `parity corpus is only ${corpus.length} statement(s) -- expected hundreds from ` +
      `${CORPUS_DIR}. Did the corpus move or the record format change?`
  );
  process.exit(1);
}

// The LSP script runs over the shared cases and the statements chosen for each
// editor feature; not the whole corpus, since each statement costs dozens of
// requests.
const lspStatements = [...new Set([...CASES.map((c) => c.text), ...LSP_STATEMENTS])];

const browser = await chromium.launch();

/** Boot one built page and run the whole corpus through it in the browser. */
async function collect(htmlPath) {
  const page = await browser.newPage();
  const problems = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") problems.push(`console: ${msg.text()}`);
  });
  page.on("pageerror", (err) => problems.push(`pageerror: ${err}`));

  await page.goto(pathToFileURL(htmlPath).href);
  // Both templates set window.__bootTimings as the last thing boot() does, so
  // it is the one readiness signal that means the same thing on both pages.
  await page.waitForFunction(() => window.__bootTimings, null, { timeout: 120_000 });

  const results = await page.evaluate((inputs) => {
    const out = {};
    for (const input of inputs) {
      try {
        out[input] = window.analyzeJson(input);
      } catch (err) {
        // Recorded rather than thrown: a statement one runtime can analyze and
        // the other cannot is the most interesting possible result here, and
        // aborting would hide every case after it.
        out[input] = `__THREW__ ${err && err.message ? err.message : String(err)}`;
      }
    }
    return out;
  }, corpus);

  // The language server (#142): the same script on both pages, every reply
  // kept as the raw string each page's lspHandle returned. Run after the
  // analyses, since it ends with shutdown and exit.
  const lsp = await page.evaluate(runLspScript, lspStatements);

  const timings = await page.evaluate(() => window.__bootTimings);
  await page.close();
  return { results, lsp, timings, problems };
}

const [left, right] = await Promise.all([collect(pages[0]), collect(pages[1])]);
await browser.close();

const label = (i) => pages[i].split("/").pop();

console.log(`## playground parity\n`);
console.log(`| page | boot | corpus |`);
console.log(`| --- | --- | --- |`);
console.log(`| \`${label(0)}\` | ${left.timings.totalMs} ms | ${corpus.length} statements |`);
console.log(`| \`${label(1)}\` | ${right.timings.totalMs} ms | ${corpus.length} statements |`);
console.log("");

let failures = 0;

for (const [i, side] of [left, right].entries()) {
  if (side.problems.length) {
    console.error(`FAIL: ${side.problems.length} console/page error(s) on ${label(i)}:`);
    for (const line of side.problems.slice(0, 10)) console.error(`  ${line}`);
    failures++;
  }
}

const threw = [];
const differing = [];
for (const input of corpus) {
  const a = left.results[input];
  const b = right.results[input];
  if (String(a).startsWith("__THREW__") || String(b).startsWith("__THREW__")) {
    threw.push({ input, a, b });
  } else if (a !== b) {
    differing.push({ input, a, b });
  }
}

if (threw.length) {
  console.error(`FAIL: ${threw.length} statement(s) raised in at least one runtime:`);
  for (const { input, a, b } of threw.slice(0, 10)) {
    console.error(`  ${JSON.stringify(input)}`);
    console.error(`    ${label(0)}: ${String(a).slice(0, 200)}`);
    console.error(`    ${label(1)}: ${String(b).slice(0, 200)}`);
  }
  failures++;
}

if (differing.length) {
  console.error(`FAIL: ${differing.length} statement(s) produced different JSON:`);
  for (const { input, a, b } of differing.slice(0, 10)) {
    // Point at the first differing character: these payloads run to several
    // kilobytes, and a whole-string dump of two near-identical blobs is not
    // something anyone can read.
    let at = 0;
    while (at < a.length && at < b.length && a[at] === b[at]) at++;
    const from = Math.max(0, at - 70);
    console.error(`  ${JSON.stringify(input)} -- first differs at character ${at}`);
    console.error(`    ${label(0)}: ...${a.slice(from, at + 70)}...`);
    console.error(`    ${label(1)}: ...${b.slice(from, at + 70)}...`);
  }
  failures++;
}

// The language server's replies, step by step: same steps, same strings.
const lspDiffering = [];
const steps = Math.max(left.lsp.transcript.length, right.lsp.transcript.length);
for (let i = 0; i < steps; i++) {
  const a = left.lsp.transcript[i];
  const b = right.lsp.transcript[i];
  if (!a || !b || a.step !== b.step || a.message !== b.message || a.reply !== b.reply) {
    lspDiffering.push({ step: (a ?? b).step, a: a?.reply, b: b?.reply });
  }
}
if (left.lsp.exitCode !== right.lsp.exitCode) {
  lspDiffering.push({ step: "exitCode", a: String(left.lsp.exitCode), b: String(right.lsp.exitCode) });
}
if (lspDiffering.length) {
  console.error(`FAIL: ${lspDiffering.length} language-server step(s) replied differently:`);
  for (const { step, a = "", b = "" } of lspDiffering.slice(0, 10)) {
    let at = 0;
    while (at < a.length && at < b.length && a[at] === b[at]) at++;
    const from = Math.max(0, at - 70);
    console.error(`  ${step} -- first differs at character ${at}`);
    console.error(`    ${label(0)}: ...${a.slice(from, at + 70)}...`);
    console.error(`    ${label(1)}: ...${b.slice(from, at + 70)}...`);
  }
  failures++;
}

if (failures) {
  console.error(`\n${failures} parity check(s) failed`);
  process.exit(1);
}
console.log(
  `All ${corpus.length} statements produced byte-identical JSON in both runtimes, ` +
    `and all ${left.lsp.transcript.length} language-server steps over ` +
    `${lspStatements.length} statements byte-identical replies, with no console errors.`
);
