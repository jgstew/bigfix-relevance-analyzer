#!/usr/bin/env node
// Headless-browser tests for the built dashboard pages, against fake_host.js
// (a pretend console or Web Reports). Build them first:
//
//   python3 tools/playground-wasm/dashboard-poc/build_poc.py --fake-hosts
//   node tools/playground-wasm/dashboard-poc/test_reports.mjs
//
// The Web Report's analyzer comes from the local playground build,
// playground/bigfix-relevance-analyzer-component-playground.html, served with
// the pages over HTTP from the repository root (split files and fetch() do
// not work from file://).

import assert from "node:assert/strict";
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, normalize, sep } from "node:path";
import { after, before, describe, test } from "node:test";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = normalize(join(HERE, "../../.."));
const OUT = "playground/dashboard-poc";
const PLAYGROUND = "playground/bigfix-relevance-analyzer-component-playground.html";

for (const needed of [`${OUT}/relevance-debugger-webreport-fake.html`, `${OUT}/relevance-debugger-console-fake.html`, PLAYGROUND]) {
  if (!existsSync(join(ROOT, needed))) {
    console.error(`missing ${needed}: build the playground and run build_poc.py --fake-hosts first`);
    process.exit(2);
  }
}

const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".gz": "application/gzip", ".wasm": "application/wasm" };

// A static file server for the repository root, with Last-Modified (the
// loader's cache check) and a per-test override hook.
let overrides = new Map();
const server = createServer((req, res) => {
  const path = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const override = overrides.get(path);
  if (override) return override(req, res, () => serve(req, res, path));
  serve(req, res, path);
});

function serve(req, res, path) {
  const file = normalize(join(ROOT, path));
  if (!file.startsWith(ROOT + sep) || !existsSync(file) || !statSync(file).isFile()) {
    res.writeHead(404).end("not found");
    return;
  }
  res.writeHead(200, {
    "Content-Type": TYPES[extname(file)] || "application/octet-stream",
    "Last-Modified": statSync(file).mtime.toUTCString(),
  });
  if (req.method === "HEAD") return res.end();
  createReadStream(file).pipe(res);
}

let browser;
let base;
before(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  base = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch();
});
after(async () => {
  await browser?.close();
  server.close();
});

// A page with its console errors and requests recorded.
async function open(context, file) {
  const page = await context.newPage();
  const errors = [];
  const requests = [];
  page.on("pageerror", (err) => errors.push(String(err)));
  page.on("console", (msg) => msg.type() === "error" && errors.push(msg.text()));
  page.on("request", (r) => requests.push(`${r.method()} ${new URL(r.url()).pathname}`));
  await page.goto(`${base}/${OUT}/${file}`);
  return { page, errors, requests };
}

const fact = (page, name) =>
  page.evaluate((n) => (document.getElementById("diagText").value.split("\n").find((l) => l.startsWith(`${n}:`)) || ""), name);

const analyzerSettled = (page) =>
  page.waitForFunction(() => /^analyzer: (loaded|unavailable)/m.test(document.getElementById("diagText").value), null, { timeout: 60_000 });

describe("Web Report", () => {
  test("Evaluate works before the analyzer, which then downloads and caches", async () => {
    // Hold the analyzer's download, as a slow link would.
    overrides = new Map([[`/${PLAYGROUND}`, (req, res, serveIt) => setTimeout(serveIt, req.method === "GET" ? 2000 : 0)]]);
    const context = await browser.newContext();
    const { page, errors, requests } = await open(context, "relevance-debugger-webreport-fake.html");
    await page.click("#evaluate");
    await page.waitForFunction(() => /1 answer/.test(document.getElementById("wrResult").textContent));
    assert.equal(await page.locator(".cm-editor").count(), 0, "the analyzer should not have started yet");
    assert.match(await fact(page, "analyzer"), /loading/);
    overrides = new Map();

    await analyzerSettled(page);
    assert.match(await fact(page, "analyzer"), /loaded \(bigfix_relevance_analyzer [\d.]+, downloaded/);
    assert.match(await fact(page, "analyzer source"), /component-playground\.html \(downloaded/);
    await page.locator(".cm-editor").waitFor();
    assert.ok(requests.includes(`GET /${PLAYGROUND}`));

    // The analysis follows the text, without Evaluate.
    await page.locator(".cm-content").click();
    await page.keyboard.press("ControlOrMeta+a");
    await page.keyboard.type('exists running application "x"');
    await page.waitForFunction(() => /dialect: client/.test(document.getElementById("analysis").textContent), null, { timeout: 5000 });
    assert.match(await page.locator("#dialectNote").textContent(), /looks like client relevance/);
    assert.deepEqual(errors, []);

    // Reopened: from the cache, with only the HEAD check.
    const again = await open(context, "relevance-debugger-webreport-fake.html");
    await analyzerSettled(again.page);
    assert.match(await fact(again.page, "analyzer source"), /\(cached,/);
    assert.ok(!again.requests.includes(`GET /${PLAYGROUND}`), again.requests.join("\n"));
    assert.ok(again.requests.includes(`HEAD /${PLAYGROUND}`));
    await context.close();
  });

  test("an unreachable analyzer leaves session relevance working", async () => {
    overrides = new Map([[`/${PLAYGROUND}`, (req, res) => res.writeHead(404).end("gone")]]);
    try {
      const context = await browser.newContext();
      const { page } = await open(context, "relevance-debugger-webreport-fake.html");
      await analyzerSettled(page);
      assert.match(await page.locator("#analysis").textContent(), /unavailable: could not load it: .*HTTP 404/);
      assert.ok(await page.locator("#rel").isVisible());
      await page.click("#evaluate");
      await page.waitForFunction(() => /1 answer/.test(document.getElementById("wrResult").textContent));
      await context.close();
    } finally {
      overrides = new Map();
    }
  });

  test("log and diagnostics start folded away", async () => {
    const context = await browser.newContext();
    const { page } = await open(context, "relevance-debugger-webreport-fake.html");
    assert.equal(await page.locator("details").getAttribute("open"), null);
    assert.equal(await page.locator("#diagText").isVisible(), false);
    await context.close();
  });
});

describe("console dashboard", () => {
  test("FastQuery backs off, draws rows as they arrive and ends at the timeout", async () => {
    const context = await browser.newContext();
    const { page, errors } = await open(context, "relevance-debugger-console-fake.html");
    await page.evaluate(() => {
      window.__polls = [];
      const get = window.API.Get;
      window.API.Get = (p, cb) => {
        window.__polls.push(performance.now());
        return get(p, cb);
      };
    });
    await page.fill("#timeoutSec", "8");
    await page.click("#evaluate");
    await page.waitForFunction(() => /waiting\.\.\./.test(document.getElementById("results").textContent));
    await page.waitForFunction(() => document.getElementById("status").textContent === "Done.", null, { timeout: 20_000 });
    const polls = await page.evaluate(() => window.__polls.map((t) => t - window.__polls[0]));
    // 0, then 2 s, 3 s, 4.5 s gaps... cut short by the 8 s deadline.
    assert.ok(polls.length >= 4 && polls.length <= 5, `polls at ${polls.map((t) => (t / 1000).toFixed(1)).join(", ")}`);
    assert.ok(polls[1] > 1800 && polls[1] < 2600, `second poll at ${polls[1]}`);
    assert.ok(polls[2] - polls[1] > 2700, `third gap ${polls[2] - polls[1]}`);
    const rows = await page.locator("#results tbody tr").allTextContents();
    assert.equal(rows.length, 5);
    assert.ok(rows.some((r) => /no answer/.test(r)));
    assert.ok(rows.some((r) => /Windows Server 2022/.test(r)));
    assert.deepEqual(errors, []);
    await context.close();
  });

  test("a new Evaluate abandons the running FastQuery", async () => {
    const context = await browser.newContext();
    const { page } = await open(context, "relevance-debugger-console-fake.html");
    await page.click("#evaluate");
    await page.waitForFunction(() => window.__fake.gets.length >= 2);
    const gets = await page.evaluate(() => window.__fake.gets.length);
    await page.selectOption("#dialect", "session");
    await page.fill("#rel", "number of bes computers");
    await page.click("#evaluate");
    await page.waitForFunction(() => document.getElementById("status").textContent === "Done.");
    await page.waitForTimeout(6000);
    assert.equal(await page.evaluate(() => window.__fake.gets.length), gets, "the abandoned run kept polling");
    const rows = await page.locator("#results tbody tr").allTextContents();
    assert.equal(rows.length, 1);
    assert.match(rows[0], /^session/);
    assert.match(await page.locator("#log").inputValue(), /previous run abandoned for a new query/);
    await context.close();
  });
});
