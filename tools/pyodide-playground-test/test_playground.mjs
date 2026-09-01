#!/usr/bin/env node
// Headless-browser regression test for the built playground page. This is
// deliberately NOT run via tools/pyodide-smoke's Node+Pyodide setup: a real
// browser and Node's Pyodide package take different internal code paths
// (browser_getBinaryResponse vs. node_getBinaryResponse in pyodide.mjs), so
// bugs specific to the browser path -- e.g. fetch() being called with a URL
// object rather than a string or Request -- only surface here.
//
// Usage: node test_playground.mjs <path-to-built-playground.html>

import { pathToFileURL } from "node:url";
import { chromium } from "playwright";

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error("usage: node test_playground.mjs <path-to-built-playground.html>");
  process.exit(2);
}

// Each case is a relevance string plus the badge text run() should produce.
// Chosen to cover every failure mode a real bug has actually hit in this
// page: the happy path, an unresolved identifier, a parse error, and an
// it-binding (see template.html's renderPayload for what these read).
//
// The dialect badge reads `dialect.resolved` -- the inspector tables' own
// post-parse verdict -- rather than `dialect.classified`, which runs on raw
// text and is deliberately blind to common English words like `file`. The
// last two cases are the ones that distinguish them: a statement the text
// classifier has no opinion about is still definitely client relevance if
// every name in it resolves that way, and a statement it *does* have an
// opinion about is still valid as neither dialect when the names contradict.
const CASES = [
  {
    text: 'exists running application "winlogon.exe" AND version of operating system >= "10.0"',
    expectBadges: "dialect: client parse: ok types: ok",
  },
  { text: "asdfdffds", expectBadges: "dialect: undetermined parse: ok types: ok" },
  {
    text: "exists ((( unclosed nonsense here",
    expectBadges: "dialect: undetermined parse: error types: n/a",
  },
  {
    text: 'exists file "x.txt" of folders "/" whose (size of it > 100)',
    expectBadges: "dialect: client parse: ok types: error",
  },
  {
    // `files`/`folders` are client-only, `bes computers` is session-only, so
    // no engine evaluates this. The text classifier calls it session on the
    // strength of the `bes ` prefix alone.
    text: '(exists files of folders "/") AND (exists bes computers)',
    expectBadges: "dialect: uncertain (client and session) parse: ok types: ok",
  },
];

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
