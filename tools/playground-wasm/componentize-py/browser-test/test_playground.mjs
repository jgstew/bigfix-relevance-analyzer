#!/usr/bin/env node
// Headless-browser regression test for the built componentize-py playground
// page.
//
// A real browser is the only place this page can be tested end to end: the
// sibling smoke stage exercises the component through jco's Node output, but
// the page depends on things that exist only in a browser -- preview2-shim's
// *browser* build (whose stale wasi:sockets shape is why
// ../build-playground/sockets_stub.js exists), DecompressionStream inflating
// the embedded cores, and a window.fetch intercept serving core-module URLs
// that were never fetchable in the first place.
//
// The cases come from ../../common/cases.mjs, shared with the Pyodide page's
// test so the two pages are held to the same expectations. That sharing is the
// point: identical expectations are what make a divergence between the two
// runtimes show up as a test failure rather than as two separately-passing
// suites.
//
// Usage: node test_playground.mjs <path-to-built-playground.html>

import { pathToFileURL } from "node:url";
import { chromium } from "playwright";

import { CASES } from "../../common/cases.mjs";

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error("usage: node test_playground.mjs <path-to-built-playground.html>");
  process.exit(2);
}

const browser = await chromium.launch();
const page = await browser.newPage();

const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});
page.on("pageerror", (err) => consoleErrors.push(String(err)));

await page.goto(pathToFileURL(htmlPath).href);
await page.waitForFunction(() => document.getElementById("status")?.textContent === "Done.", {
  timeout: 60_000,
});

const wasmProblem = await page.evaluate(() => window.__wasmProblem);
if (wasmProblem) {
  console.error(`smoke check failed: WebAssembly unsupported in this browser: ${wasmProblem}`);
  process.exit(1);
}

let failures = 0;
for (const { text, expectBadges } of CASES) {
  const badges = await page.evaluate(async (input) => {
    document.getElementById("input").value = input;
    await run();
    return document.querySelector("#output p")?.innerText ?? null;
  }, text);

  if (badges !== expectBadges) {
    console.error(`FAIL: ${JSON.stringify(text)}\n  expected: ${expectBadges}\n  got:      ${badges}`);
    failures++;
  } else {
    console.log(`ok: ${JSON.stringify(text)} -> ${badges}`);
  }
}

if (consoleErrors.length) {
  console.error(`FAIL: ${consoleErrors.length} console error(s) during the run:`);
  for (const line of consoleErrors) console.error(`  ${line}`);
  failures++;
}

await browser.close();

if (failures) {
  console.error(`${failures} check(s) failed`);
  process.exit(1);
}
console.log(`all ${CASES.length} case(s) passed, no console errors`);
