#!/usr/bin/env node
// Headless-browser test for the split analyzer set (../build-playground/
// build_split.py; the contract is ../../SPLIT_ANALYZER.md): the folder's
// index.html, served over HTTP, must behave exactly like the single-file page
// -- the same shared cases, editor checks and language-server script as
// test_playground.mjs -- and must load the set the way the contract says.
//
// Over HTTP, never file://: a page cannot fetch its sibling files from file://.
// The server is a few lines of node:http below, so each scenario can bend what
// it serves:
//
//   cached       a reload revalidates every file (the page fetches with
//                cache "no-cache") and gets 304s, then still boots
//   in transit   the .gz cores sent with Content-Encoding: gzip, so the
//                browser hands the page wasm, not gzip: still boots
//   changed      the first manifest.json the page sees is from another build;
//                its files fail to verify, the page re-reads the manifest, sees
//                it changed, and boots from the new set alone
//   core count   the first manifest lists a core this folder does not have
//                (404); the page re-reads the manifest and boots from the new one
//   corrupt      a byte of glue.mjs flipped (sha256), a core truncated (size),
//                an inflated core that is not the manifest's (raw_sha256),
//                manifest.json missing, an unknown format, a "../" path, a
//                version the component does not report: the page says so and
//                does not boot
//   insecure     served from a hostname that is not a secure context, so there
//                is no crypto.subtle: the page verifies with its JS SHA-256,
//                boots, and still refuses a flipped byte
//
// Usage: node test_split_analyzer.mjs <path-to-playground/analyzer>

import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { createServer } from "node:http";
import { join, resolve } from "node:path";
import { chromium } from "playwright";

import { CASES } from "../../common/cases.mjs";
import { checkEditor } from "../../common/editor_checks.mjs";
import { LSP_STATEMENTS, checkLspTranscript, runLspScript } from "../../common/lsp_script.mjs";

const dir = process.argv[2] && resolve(process.argv[2]);
if (!dir) {
  console.error("usage: node test_split_analyzer.mjs <path-to-playground/analyzer>");
  process.exit(2);
}

const FILES = new Map(readdirSync(dir).map((name) => [name, readFileSync(join(dir, name))]));
const manifest = JSON.parse(FILES.get("manifest.json").toString("utf8"));
const SET = ["index.html", "manifest.json", manifest.editor.path, manifest.glue.path, ...manifest.cores.map((c) => c.path)];
for (const name of SET) {
  if (!FILES.has(name)) {
    console.error(`${dir} has no ${name}`);
    process.exit(2);
  }
}

const TYPES = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript", ".mjs": "text/javascript", ".gz": "application/gzip" };
const typeOf = (name) => TYPES[name.slice(name.lastIndexOf("."))] ?? "application/octet-stream";

/**
 * Serve FILES, with `override(name, count)` able to replace a body (or return
 * null for a 404) and `gzipInTransit` marking the .gz cores Content-Encoding:
 * gzip. ETag plus Cache-Control: no-cache, so a reload revalidates. `log` gets
 * one `{ name, status, conditional }` per request.
 */
async function serve({ override, gzipInTransit = false } = {}) {
  const log = [];
  const counts = new Map();
  const server = createServer((req, res) => {
    const name = decodeURIComponent(new URL(req.url, "http://x").pathname.slice(1)) || "index.html";
    const count = (counts.get(name) ?? 0) + 1;
    counts.set(name, count);
    let body = FILES.get(name) ?? null;
    if (override) {
      const replaced = override(name, count);
      if (replaced !== undefined) body = replaced;
    }
    const conditional = "if-none-match" in req.headers;
    if (body === null) {
      log.push({ name, status: 404, conditional });
      res.writeHead(404, { "Content-Type": "text/plain" }).end("not found");
      return;
    }
    const etag = `"${createHash("sha256").update(body).digest("hex").slice(0, 16)}"`;
    const headers = { "Content-Type": typeOf(name), ETag: etag, "Cache-Control": "no-cache" };
    if (gzipInTransit && name.endsWith(".gz")) headers["Content-Encoding"] = "gzip";
    if (req.headers["if-none-match"] === etag) {
      log.push({ name, status: 304, conditional });
      res.writeHead(304, headers).end();
      return;
    }
    log.push({ name, status: 200, conditional });
    res.writeHead(200, headers).end(body);
  });
  await new Promise((ok) => server.listen(0, "127.0.0.1", ok));
  const { port } = server.address();
  return {
    origin: `http://127.0.0.1:${port}`,
    insecureOrigin: `http://${INSECURE_HOST}:${port}`,
    log,
    close: () => new Promise((ok) => server.close(ok)),
  };
}

// split.test is this machine too, but unlike 127.0.0.1 it is not a secure
// context, so the page there has no crypto.subtle.
const INSECURE_HOST = "split.test";
const browser = await chromium.launch({ args: [`--host-resolver-rules=MAP ${INSECURE_HOST} 127.0.0.1`] });
let failures = 0;
const fail = (message) => {
  console.error(`FAIL: ${message}`);
  failures++;
};
const pass = (message) => console.log(`ok: ${message}`);

/** A fresh context and page that record console errors and requests. */
async function openPage() {
  const context = await browser.newContext();
  const page = await context.newPage();
  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => consoleErrors.push(String(err)));
  const requests = [];
  page.on("request", (request) => {
    if (!/^(data|blob):/.test(request.url())) requests.push(request.url());
  });
  return { context, page, consoleErrors, requests };
}

/** Load `url` and wait until it boots, refuses the browser, or refuses the set. */
async function load(page, url, { reload = false } = {}) {
  if (reload) await page.reload();
  else await page.goto(url);
  await page.waitForFunction(
    () =>
      window.__wasmProblem ||
      window.__splitProblem ||
      document.getElementById("status")?.classList.contains("error") ||
      document.getElementById("status")?.textContent === "Done.",
    { timeout: 60_000 },
  );
  return page.evaluate(() => ({
    status: document.getElementById("status").textContent,
    isError: document.getElementById("status").classList.contains("error"),
    wasmProblem: window.__wasmProblem ?? null,
    splitProblem: window.__splitProblem ?? null,
    output: document.getElementById("output").innerText,
    runDisabled: document.getElementById("run").disabled,
    version: document.getElementById("version")?.textContent ?? null,
    arrivals: Object.values(window.__coreArrivals ?? {}),
    sha256Impl: window.__sha256Impl ?? null,
    secure: window.isSecureContext,
  }));
}

function expectBooted(label, state) {
  if (state.status === "Done." && !state.isError) {
    pass(`${label}: booted`);
    return true;
  }
  fail(`${label}: did not boot: ${state.status}\n  ${state.splitProblem ?? state.wasmProblem ?? state.output}`);
  return false;
}

// --- first load: everything the single-file page is tested for ------------

{
  const server = await serve();
  const { context, page, consoleErrors, requests } = await openPage();
  const state = await load(page, `${server.origin}/index.html`);
  if (state.wasmProblem) {
    console.error(`this browser can't run the page: ${state.wasmProblem}`);
    process.exit(1);
  }
  if (expectBooted("first load", state)) {
    if (state.arrivals.length === manifest.cores.length && state.arrivals.every((a) => a === "gzip")) pass("every core arrived gzipped and verified");
    else fail(`expected every core to arrive gzipped, got ${JSON.stringify(state.arrivals)}`);
    if (state.version === `bigfix_relevance_analyzer ${manifest.version}`) pass(`version is the manifest's (${manifest.version})`);
    else fail(`footer says ${JSON.stringify(state.version)}, manifest says ${manifest.version}`);

    for (const { text, expectBadges } of CASES) {
      const badges = await page.evaluate(async (input) => {
        window.playgroundInput.setText(input);
        await run();
        return document.querySelector("#output p")?.innerText ?? null;
      }, text);
      if (badges !== expectBadges) fail(`${JSON.stringify(text)}\n  expected: ${expectBadges}\n  got:      ${badges}`);
      else pass(`${JSON.stringify(text)} -> ${badges}`);
    }

    for (const [name, failure] of await checkEditor(page)) {
      if (failure) fail(`editor: ${name}: ${failure}`);
      else pass(`editor: ${name}`);
    }

    // Last on this page: the script ends the server with exit.
    const lspFailures = checkLspTranscript(await page.evaluate(runLspScript, LSP_STATEMENTS));
    if (lspFailures.length) fail(`language server: ${lspFailures.length} problem(s):\n  ${lspFailures.join("\n  ")}`);
    else pass("language server (hover, completion, diagnostics, quick fixes, fix-all, exit)");
  }

  // Only the set, only from where index.html came from, each file once.
  const allowed = new Set(SET.map((name) => `${server.origin}/${name}`));
  const stray = requests.filter((url) => !allowed.has(url));
  if (stray.length) fail(`requests outside the set:\n  ${stray.join("\n  ")}`);
  else pass("requested only the set's own files");
  const fetched = server.log.map((entry) => entry.name).sort();
  if (JSON.stringify(fetched) !== JSON.stringify([...SET].sort())) fail(`expected each file fetched once, got ${fetched.join(", ")}`);
  else pass(`each of the ${SET.length} files fetched once`);

  // --- second load, same browser: revalidated from the HTTP cache ----------
  server.log.length = 0;
  const again = await load(page, null, { reload: true });
  if (expectBooted("reload", again)) {
    const notRevalidated = server.log.filter((entry) => entry.status !== 304);
    if (notRevalidated.length || server.log.length !== SET.length) {
      fail(`reload should revalidate all ${SET.length} files from the cache (304), got ${JSON.stringify(server.log)}`);
    } else {
      pass(`reload revalidated all ${SET.length} files from the HTTP cache (304, no bodies)`);
    }
  }

  if (consoleErrors.length) fail(`${consoleErrors.length} console error(s):\n  ${consoleErrors.join("\n  ")}`);
  await context.close();
  await server.close();
}

/** Boot (or refuse) in a fresh browser context against a bent server. */
async function scenario(label, serveOptions, { insecure = false } = {}) {
  const server = await serve(serveOptions);
  const { context, page, consoleErrors, requests } = await openPage();
  const state = await load(page, `${insecure ? server.insecureOrigin : server.origin}/index.html`);
  await context.close();
  await server.close();
  return { state, consoleErrors, log: server.log, requests };
}

/** A manifest.json body: the real manifest with `change` applied to a copy. */
function doctored(change) {
  const copy = structuredClone(manifest);
  change(copy);
  return Buffer.from(JSON.stringify(copy, null, 2) + "\n");
}
const serveManifest = (body, onlyFirst = false) => ({
  override: (name, count) => (name === "manifest.json" && (!onlyFirst || count === 1) ? body : undefined),
});

// --- a server that already inflated the .gz cores -------------------------

{
  const { state, consoleErrors } = await scenario("in transit", { gzipInTransit: true });
  if (expectBooted("cores decompressed in transit (Content-Encoding: gzip)", state)) {
    if (state.arrivals.length === manifest.cores.length && state.arrivals.every((a) => a === "wasm")) pass("every core arrived as wasm, recognised by its magic bytes");
    else fail(`expected every core to arrive already inflated, got ${JSON.stringify(state.arrivals)}`);
  }
  if (consoleErrors.length) fail(`in transit: console error(s):\n  ${consoleErrors.join("\n  ")}`);
}

// --- the manifest changed under the page ------------------------------------

{
  // A manifest from "another build": the glue's sha256 differs. Served only
  // the first time; the page's re-read gets the real one.
  const stale = { ...manifest, glue: { ...manifest.glue, sha256: "0".repeat(64) } };
  const staleText = Buffer.from(JSON.stringify(stale, null, 2) + "\n");
  const { state, log } = await scenario("changed", {
    override: (name, count) => (name === "manifest.json" && count === 1 ? staleText : undefined),
  });
  if (expectBooted("manifest changed mid-load", state)) {
    const manifestReads = log.filter((entry) => entry.name === "manifest.json").length;
    if (manifestReads === 2) pass("re-read manifest.json once and booted from the new set");
    else fail(`expected manifest.json read twice, got ${manifestReads}`);
  }
}

// --- corrupt or missing files: the page says so instead of booting ---------

function expectRefused(label, state, pattern) {
  if (state.status === "Done." || !state.isError || !state.runDisabled) {
    fail(`${label}: expected the page to refuse the set, got status ${JSON.stringify(state.status)}`);
  } else if (!pattern.test(state.splitProblem ?? "") || !pattern.test(state.output)) {
    fail(`${label}: expected the page to say ${pattern}, got\n  problem: ${state.splitProblem}\n  output:  ${state.output}`);
  } else {
    pass(`${label}: refused -- ${state.splitProblem}`);
  }
}

{
  const flipped = Buffer.from(FILES.get(manifest.glue.path));
  flipped[flipped.length - 2] ^= 0x01;
  const { state } = await scenario("corrupt glue", {
    override: (name) => (name === manifest.glue.path ? flipped : undefined),
  });
  expectRefused("glue.mjs with one byte flipped", state, new RegExp(`${manifest.glue.path}.*sha-?256`, "is"));
}

{
  const big = manifest.cores.reduce((a, b) => (a.size >= b.size ? a : b));
  const truncated = FILES.get(big.path).subarray(0, big.size - 100);
  const { state } = await scenario("truncated core", {
    override: (name) => (name === big.path ? truncated : undefined),
  });
  expectRefused(`${big.path} truncated`, state, new RegExp(`${big.path.replace(/\./g, "\\.")}.*${big.size}`, "s"));
}

{
  const { state } = await scenario("no manifest", {
    override: (name) => (name === "manifest.json" ? null : undefined),
  });
  expectRefused("manifest.json missing (404)", state, /manifest\.json.*404/s);
}

{
  const body = doctored((m) => {
    m.cores[0].raw_sha256 = "0".repeat(64);
  });
  const { state } = await scenario("wrong raw core", { ...serveManifest(body), gzipInTransit: true });
  expectRefused(`${manifest.cores[0].path} inflated in transit but not the manifest's`, state, /raw_sha256/);
}

{
  const { state } = await scenario("unknown format", serveManifest(doctored((m) => (m.format = 2))));
  expectRefused("manifest.json with format 2", state, /format 2/);
}

{
  const { state, requests } = await scenario("parent path", serveManifest(doctored((m) => (m.editor.path = "../editor.js"))));
  expectRefused('an editor path of "../editor.js"', state, /malformed editor entry/);
  const escaped = requests.filter((url) => !new URL(url).pathname.startsWith("/") || url.includes(".."));
  if (escaped.length) fail(`the page fetched outside its folder: ${escaped.join(", ")}`);
}

{
  const { state } = await scenario("version mismatch", serveManifest(doctored((m) => (m.version = "0.0.0-not-this-build"))));
  if (state.status === "Done." || !state.isError || !state.runDisabled || !/0\.0\.0-not-this-build/.test(state.output)) {
    fail(`a manifest naming another version should stop the boot, got status ${JSON.stringify(state.status)}: ${state.output}`);
  } else {
    pass(`a manifest naming another version: refused -- ${state.output.split("\n")[0]}`);
  }
}

// --- the manifest switched to a different core count under the page --------

{
  // An older set's manifest, one core more than this folder holds: that core
  // 404s, the re-read manifest differs, and the page starts over with it.
  const body = doctored((m) => {
    m.cores.push({ ...m.cores[m.cores.length - 1], name: "analyzer.core99.wasm", path: "analyzer.core99.wasm.gz" });
  });
  const { state, log } = await scenario("core count", serveManifest(body, true));
  if (expectBooted("manifest with another core count, then the real one", state)) {
    const manifestReads = log.filter((entry) => entry.name === "manifest.json").length;
    const missing = log.filter((entry) => entry.name === "analyzer.core99.wasm.gz").map((entry) => entry.status);
    if (manifestReads === 2 && JSON.stringify(missing) === "[404]") pass("a 404 re-read manifest.json once and booted from the new set");
    else fail(`expected one 404 then a second manifest read, got ${manifestReads} reads and ${JSON.stringify(missing)}`);
  }
}

// --- no crypto.subtle: the page's own SHA-256 --------------------------------

{
  const { state, consoleErrors } = await scenario("insecure", {}, { insecure: true });
  if (state.secure !== false) fail(`${INSECURE_HOST} was expected not to be a secure context`);
  if (expectBooted("not a secure context (no crypto.subtle)", state)) {
    if (state.sha256Impl === "js") pass("verified every file with the page's JS SHA-256");
    else fail(`expected the JS SHA-256 fallback, got ${JSON.stringify(state.sha256Impl)}`);
  }
  if (consoleErrors.length) fail(`insecure: console error(s):\n  ${consoleErrors.join("\n  ")}`);
}

{
  const { state } = await scenario("insecure in transit", { gzipInTransit: true }, { insecure: true });
  if (expectBooted("no crypto.subtle, cores inflated in transit", state)) {
    if (state.arrivals.every((a) => a === "wasm") && state.sha256Impl === "js") pass("checked every inflated core's raw_sha256 in JS");
    else fail(`expected wasm arrivals checked in JS, got ${JSON.stringify(state.arrivals)} / ${state.sha256Impl}`);
  }
}

{
  const flipped = Buffer.from(FILES.get(manifest.glue.path));
  flipped[flipped.length - 2] ^= 0x01;
  const { state } = await scenario(
    "insecure corrupt glue",
    { override: (name) => (name === manifest.glue.path ? flipped : undefined) },
    { insecure: true },
  );
  expectRefused("no crypto.subtle, glue.mjs with one byte flipped", state, new RegExp(`${manifest.glue.path}.*sha-?256`, "is"));
}

await browser.close();

if (failures) {
  console.error(`${failures} check(s) failed`);
  process.exit(1);
}
console.log(`all checks passed: ${CASES.length} case(s), editor, language server, cache, in-transit gzip, changed manifest, core count, corruption, no crypto.subtle`);
