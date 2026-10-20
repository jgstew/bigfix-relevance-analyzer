#!/usr/bin/env node
// Headless-browser tests for the built dashboard pages, against fake_host.js
// (a pretend console or Web Reports). Build them first:
//
//   python3 tools/playground-wasm/dashboard-poc/build_poc.py --fake-hosts
//   node tools/playground-wasm/dashboard-poc/test_reports.mjs
//
// The fake Web Report takes the analyzer from a split set (MANIFEST.md) that
// split_fixture.mjs makes from the local playground build, or, with
// SPLIT_ANALYZER_DIR set, a copy of a real one (the analyzer build's
// playground/analyzer/); it falls back to that single-file page itself. Everything is served over HTTP from the
// repository root (split files and fetch() do not work from file://).

import assert from "node:assert/strict";
import { cpSync, createReadStream, existsSync, rmSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, normalize, sep } from "node:path";
import { after, before, describe, test } from "node:test";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

import { writeSplitSet } from "./split_fixture.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = normalize(join(HERE, "../../.."));
const OUT = "playground/dashboard-poc";
const PLAYGROUND = "playground/bigfix-relevance-analyzer-component-playground.html";
const MANIFEST = `${OUT}/analyzer/manifest.json`;

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
  const splitDir = join(ROOT, OUT, "analyzer");
  rmSync(splitDir, { recursive: true, force: true });
  if (process.env.SPLIT_ANALYZER_DIR) cpSync(process.env.SPLIT_ANALYZER_DIR, splitDir, { recursive: true });
  else writeSplitSet(join(ROOT, PLAYGROUND), splitDir);
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
    overrides = new Map([[`/${MANIFEST}`, (req, res, serveIt) => setTimeout(serveIt, 2000)]]);
    const context = await browser.newContext();
    const { page, errors, requests } = await open(context, "relevance-debugger-webreport-fake.html");
    await page.click("#evaluate");
    await page.waitForFunction(() => /1 answer/.test(document.getElementById("wrResult").textContent));
    assert.equal(await page.locator(".cm-editor").count(), 0, "the analyzer should not have started yet");
    assert.match(await fact(page, "analyzer"), /loading/);
    overrides = new Map();

    await analyzerSettled(page);
    assert.match(await fact(page, "analyzer"), /loaded \(bigfix_relevance_analyzer [\d.]+, downloaded/);
    assert.match(await fact(page, "analyzer source"), /analyzer\/manifest\.json \(analyzer [\w.-]+, downloaded \d+ files/, await page.locator("#log").inputValue());
    await page.locator(".cm-editor").waitFor();
    assert.ok(requests.includes(`GET /${OUT}/analyzer/glue.mjs`));
    assert.ok(!requests.some((r) => r.endsWith(PLAYGROUND)), "the single-file page should not be needed");

    // The analysis follows the text, without Evaluate.
    await page.locator(".cm-content").click();
    await page.keyboard.press("ControlOrMeta+a");
    await page.keyboard.type('exists running application "x"');
    await page.waitForFunction(() => /dialect: client/.test(document.getElementById("analysis").textContent), null, { timeout: 5000 });
    assert.match(await page.locator("#dialectNote").textContent(), /looks like client relevance/);
    assert.deepEqual(errors, []);

    // Reopened: from the cache, fetching only the manifest.
    const again = await open(context, "relevance-debugger-webreport-fake.html");
    await analyzerSettled(again.page);
    assert.match(await fact(again.page, "analyzer source"), /\(analyzer [\w.-]+, cached\)/);
    const analyzerRequests = again.requests.filter((r) => r.includes("/analyzer/") || r.endsWith(PLAYGROUND));
    assert.deepEqual(analyzerRequests, [`GET /${MANIFEST}`]);
    await again.page.locator(".cm-editor").waitFor();
    await context.close();
  });

  test("no manifest: falls back to the single-file playground page", async () => {
    overrides = new Map([[`/${MANIFEST}`, (req, res) => res.writeHead(404).end("gone")]]);
    try {
      const context = await browser.newContext();
      const { page } = await open(context, "relevance-debugger-webreport-fake.html");
      await analyzerSettled(page);
      assert.match(await fact(page, "analyzer source"), /component-playground\.html \(downloaded/);
      await page.locator(".cm-editor").waitFor();
      assert.match(await page.locator("#log").inputValue(), /manifest\.json failed: HTTP 404/);
      await context.close();
    } finally {
      overrides = new Map();
    }
  });

  test("an unreachable analyzer leaves session relevance working", async () => {
    const gone = (req, res) => res.writeHead(404).end("gone");
    overrides = new Map([[`/${MANIFEST}`, gone], [`/${PLAYGROUND}`, gone]]);
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

  test("no answers on the no-string-cast path is no answers, not one blank one", async () => {
    // Keep the analyzer away, so the plain text box stays the input.
    const gone = (req, res) => res.writeHead(404).end("gone");
    overrides = new Map([[`/${MANIFEST}`, gone], [`/${PLAYGROUND}`, gone]]);
    try {
      const context = await browser.newContext();
      const { page } = await open(context, "relevance-debugger-webreport-fake.html");
      await page.fill("#rel", "bes computers whose (false)");
      await page.click("#evaluate");
      await page.locator("#wrResult .summary").waitFor();
      assert.match(await page.locator("#wrResult .summary").textContent(), /^0 answers/);
      assert.match(await page.locator("#wrResult .summary").textContent(), /no string cast/);
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
  test("internals: qna output, typed IDs and the FastQuery request", async () => {
    const context = await browser.newContext();
    const { page } = await open(context, "relevance-debugger-console-fake.html");
    const got = await page.evaluate(() => {
      const t = window.rdbg.internals;
      return {
        qna: t.parseQna("Q: A: first line\r\nsecond line\r\nQ: T: 12\r\nQ: I: singular string\r\nQ: "),
        ids: t.parseIds("101, 101 102;101"),
        badIds: t.parseIds("101, x"),
        xml: t.clientQueryXml('exists file "a&b" whose (size of it < 3)', ["7"]),
      };
    });
    assert.deepEqual(got.qna.answers, ["first line\nsecond line"]);
    assert.deepEqual(got.qna.times, ["12"]);
    assert.deepEqual(got.ids, ["101", "102"]);
    assert.equal(got.badIds, null);
    assert.match(got.xml, /<QueryText>exists file "a&amp;b" whose \(size of it &lt; 3\)<\/QueryText>/);
    await context.close();
  });

  test("a FastQuery reply that never comes ends at the timeout", async () => {
    const context = await browser.newContext();
    const { page } = await open(context, "relevance-debugger-console-fake.html");
    await page.evaluate(() => {
      window.API.Get = () => {}; // never calls back
    });
    await page.fill("#timeoutSec", "5");
    await page.click("#evaluate");
    await page.waitForFunction(() => document.getElementById("status").textContent === "Done.", null, { timeout: 15_000 });
    assert.match(await page.locator("#results").textContent(), /no reply/);
    await context.close();
  });

  test("Cancel stops a running FastQuery", async () => {
    const context = await browser.newContext();
    const { page } = await open(context, "relevance-debugger-console-fake.html");
    await page.click("#evaluate");
    await page.waitForFunction(() => window.__fake.gets.length >= 1);
    await page.click("#cancel");
    assert.equal(await page.locator("#status").textContent(), "Cancelled.");
    const gets = await page.evaluate(() => window.__fake.gets.length);
    await page.waitForTimeout(5000);
    assert.equal(await page.evaluate(() => window.__fake.gets.length), gets);
    await context.close();
  });

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
