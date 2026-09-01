#!/usr/bin/env node
// Headless-browser regression test for the built Pyodide playground page.
//
// This is deliberately NOT run through the sibling smoke stage's Node+Pyodide
// setup: a real browser and Node's Pyodide package take different internal code
// paths (browser_getBinaryResponse vs. node_getBinaryResponse in pyodide.mjs),
// so bugs specific to the browser path -- e.g. fetch() being called with a URL
// object rather than a string or Request -- only surface here.
//
// The cases come from ../../common/cases.mjs, shared with the componentize-py
// page's test so the two pages are held to the same expectations.
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
