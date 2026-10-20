#!/usr/bin/env node
// Unit tests for loader.mjs, the part of the Web Report's analyzer loader that
// runs without a page: where the analyzer comes from, and its cache.
//
//   node --test tools/playground-wasm/dashboard-poc/
//
// No dependencies: node:test, a fake fetch and an in-memory cache. The real
// browser path (IndexedDB, starting the analyzer) is covered by
// test_reports.mjs.

import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, test } from "node:test";
import { fileURLToPath } from "node:url";

import { dialectChoice, extract, loadPieces } from "./loader.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const REAL_PLAYGROUND = join(HERE, "../../../playground/bigfix-relevance-analyzer-component-playground.html");

// ---- fixtures ------------------------------------------------------------------

// A page laid out like the built single-file playground, in miniature.
export function playgroundPage({ cores = { "analyzer.core.wasm": "AAAA", "analyzer.core2.wasm": "BBBB" }, extra = "" } = {}) {
  const coreUrls = Object.keys(cores)
    .map((n) => `kt(new URL("./${n}",import.meta.url))`)
    .join(",");
  return [
    "<!doctype html><html><body>",
    "<script>",
    "// The editor: CodeMirror and the wheel's web/ modules, bundled by",
    "// ../editor-bundle/build.mjs. Publishes window.playgroundEditor.",
    "(()=>{window.playgroundEditor={mount(){}}})();",
    "</script>",
    '<script type="module">',
    `const CORES_GZIP = ${JSON.stringify(cores)};`,
    "async function boot() {",
    "  return 1;",
    "}",
    `let s=[${coreUrls}];globalThis.__component={};`,
    "// window.__wasmProblem was already handled (and window.stop() called) above.",
    "</script>",
    extra,
    "</body></html>",
  ].join("\n");
}

// A fake fetch over `routes` (url -> {body, status, lastModified} or "offline"),
// recording every call as "METHOD url".
export function fakeFetch(routes) {
  const calls = [];
  const fetch = async (url, init = {}) => {
    const method = init.method || "GET";
    calls.push(`${method} ${url}`);
    const route = routes[url];
    if (route === undefined || route === "offline") throw new TypeError("Failed to fetch");
    const headers = new Headers();
    if (route.lastModified) headers.set("Last-Modified", route.lastModified);
    const status = route.status || 200;
    return new Response(method === "HEAD" ? null : route.body, { status, headers });
  };
  return { fetch, calls };
}

export function memoryEnv(routes, store = new Map()) {
  const { fetch, calls } = fakeFetch(routes);
  const logs = [];
  return {
    env: {
      fetch,
      cacheGet: async (key) => store.get(key),
      cachePut: async (key, value) => void store.set(key, structuredClone(value)),
      log: (text) => logs.push(text),
      now: () => 0,
    },
    calls,
    logs,
    store,
  };
}

const PAGE = "https://example.test/playground.html";
const MONDAY = "Mon, 19 Oct 2026 00:00:00 GMT";
const TUESDAY = "Tue, 20 Oct 2026 00:00:00 GMT";

// ---- regression: the single-file page, as the loader worked before manifests

describe("extract (single-file playground page)", () => {
  test("cuts out the editor, the cores and the glue", () => {
    const pieces = extract(playgroundPage());
    assert.match(pieces.editor, /window\.playgroundEditor=/);
    assert.deepEqual(Object.keys(pieces.cores), ["analyzer.core.wasm", "analyzer.core2.wasm"]);
    assert.match(pieces.glue, /globalThis\.__component/);
    assert.doesNotMatch(pieces.glue, /async function boot/);
  });

  test("refuses a page without one of the anchors", () => {
    assert.throws(() => extract(playgroundPage().replace("const CORES_GZIP = ", "const X = ")), /core modules/);
  });

  test("refuses a page where an anchor appears twice", () => {
    const twice = playgroundPage({ extra: "<p>Publishes window.playgroundEditor.\n</p>" });
    assert.throws(() => extract(twice), /expected exactly one/);
  });

  test("refuses cores the glue does not load", () => {
    const page = playgroundPage().replace('kt(new URL("./analyzer.core2.wasm",import.meta.url))', "0");
    assert.throws(() => extract(page), /does not load analyzer\.core2\.wasm/);
  });

  test("works on the real local playground build", { skip: !existsSync(REAL_PLAYGROUND) && "no local playground build" }, () => {
    const pieces = extract(readFileSync(REAL_PLAYGROUND, "utf8"));
    assert.ok(Object.keys(pieces.cores).length >= 1);
    assert.ok(pieces.editor.length > 100_000);
    assert.ok(pieces.glue.length > 100_000);
  });
});

describe("loadPieces (single-file playground page)", () => {
  test("first load downloads the page and caches it", async () => {
    const { env, calls, store } = memoryEnv({ [PAGE]: { body: playgroundPage(), lastModified: MONDAY } });
    const got = await loadPieces([PAGE], env);
    assert.match(got.how, /^downloaded/);
    assert.deepEqual(calls, [`HEAD ${PAGE}`, `GET ${PAGE}`]);
    assert.equal(got.pieces.lastModified, MONDAY);
    assert.equal(store.size, 1);
    assert.match(got.source, new RegExp(`^${PAGE} \\(downloaded`));
  });

  test("unchanged Last-Modified: cached, HEAD only", async () => {
    const routes = { [PAGE]: { body: playgroundPage(), lastModified: MONDAY } };
    const store = new Map();
    await loadPieces([PAGE], memoryEnv(routes, store).env);
    const second = memoryEnv(routes, store);
    const got = await loadPieces([PAGE], second.env);
    assert.equal(got.how, "cached");
    assert.deepEqual(second.calls, [`HEAD ${PAGE}`]);
  });

  test("changed Last-Modified: downloads again", async () => {
    const store = new Map();
    await loadPieces([PAGE], memoryEnv({ [PAGE]: { body: playgroundPage(), lastModified: MONDAY } }, store).env);
    const second = memoryEnv({ [PAGE]: { body: playgroundPage(), lastModified: TUESDAY } }, store);
    const got = await loadPieces([PAGE], second.env);
    assert.match(got.how, /^downloaded/);
    assert.equal(got.pieces.lastModified, TUESDAY);
  });

  test("offline with a cached copy: uses it", async () => {
    const store = new Map();
    await loadPieces([PAGE], memoryEnv({ [PAGE]: { body: playgroundPage(), lastModified: MONDAY } }, store).env);
    const offline = memoryEnv({ [PAGE]: "offline" }, store);
    const got = await loadPieces([PAGE], offline.env);
    assert.equal(got.how, "cached");
    assert.ok(offline.logs.some((l) => /unreachable/.test(l)));
  });

  test("offline without a cached copy: fails", async () => {
    await assert.rejects(loadPieces([PAGE], memoryEnv({ [PAGE]: "offline" }).env), /Failed to fetch/);
  });

  test("an HTTP error fails that URL and tries the next", async () => {
    const other = "https://mirror.test/playground.html";
    const { env, logs } = memoryEnv({
      [PAGE]: { body: "gone", status: 404 },
      [other]: { body: playgroundPage(), lastModified: MONDAY },
    });
    const got = await loadPieces([PAGE, other], env);
    assert.match(got.source, /^https:\/\/mirror\.test/);
    assert.ok(logs.some((l) => /HTTP 404/.test(l)));
  });

  test("every URL failing names each problem", async () => {
    await assert.rejects(loadPieces([PAGE], memoryEnv({ [PAGE]: { body: "<html></html>" } }).env), /playground\.html: editor bundle/);
  });

  test("no URL at all says so", async () => {
    await assert.rejects(loadPieces([], memoryEnv({}).env), /no analyzer URL configured/);
  });
});

describe("dialectChoice", () => {
  const choice = (resolved, classified = null) => dialectChoice({ dialect: { resolved, classified } }).dialects;
  test("resolved wins", () => {
    assert.deepEqual(choice("client"), ["client"]);
    assert.deepEqual(choice("session"), ["session"]);
  });
  test("both and uncertain mean either, session first", () => {
    assert.deepEqual(choice("both"), ["session", "client"]);
    assert.deepEqual(choice("uncertain"), ["session", "client"]);
  });
  test("else the classifier, else either", () => {
    assert.deepEqual(choice(null, "client"), ["client"]);
    assert.deepEqual(choice(null, null), ["session", "client"]);
  });
});
