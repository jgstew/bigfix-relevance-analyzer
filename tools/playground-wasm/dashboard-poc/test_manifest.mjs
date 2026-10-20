#!/usr/bin/env node
// Unit tests for loading the split analyzer (files/analyzer/manifest.json and
// the files it names; the contract is MANIFEST.md) in loader.mjs.
//
//   node --test tools/playground-wasm/dashboard-poc/

import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import { describe, test } from "node:test";
import { gzipSync } from "node:zlib";

import { loadPieces, parseManifest } from "./loader.mjs";
import { memoryEnv, playgroundPage } from "./test_loader.mjs";

const DIR = "https://example.test/files/analyzer/";
const MANIFEST = `${DIR}manifest.json`;
const PAGE = "https://example.test/playground.html";

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const WASM_MAGIC = [0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00];

// A published split set: {routes, manifest, cores (name -> raw wasm bytes)}.
function splitSet({ version = "1.38.1", coreNames = ["analyzer.core.wasm", "analyzer.core2.wasm"], tweak = (m) => m } = {}) {
  const editor = "(()=>{window.playgroundEditor={mount(){}}})();";
  const glue = coreNames.map((n) => `kt(new URL("./${n}",import.meta.url));`).join("") + "globalThis.__component={};";
  const routes = {};
  const cores = {};
  const entries = coreNames.map((name, i) => {
    const raw = new Uint8Array([...WASM_MAGIC, i, version.length]);
    cores[name] = raw;
    const gz = gzipSync(raw, { level: 9 });
    const path = `${name}.gz`;
    routes[DIR + path] = { body: gz };
    return { name, path, encoding: "gzip", size: gz.length, sha256: sha256(gz) };
  });
  routes[`${DIR}editor.js`] = { body: editor };
  routes[`${DIR}glue.mjs`] = { body: glue };
  const manifest = tweak({
    format: 1,
    package: "bigfix-relevance-analyzer",
    version,
    editor: { path: "editor.js", size: Buffer.byteLength(editor), sha256: sha256(editor) },
    glue: { path: "glue.mjs", size: Buffer.byteLength(glue), sha256: sha256(glue) },
    cores: entries,
  });
  routes[MANIFEST] = { body: JSON.stringify(manifest, null, 2) };
  return { routes, manifest, cores, editor, glue };
}

// memoryEnv with crypto.subtle, as in a secure browser context.
function env(routes, store) {
  const made = memoryEnv(routes, store);
  made.env.subtle = webcrypto.subtle;
  return made;
}

const fileGets = (calls) => calls.filter((c) => c.startsWith("GET ") && !c.endsWith("manifest.json"));

describe("parseManifest", () => {
  const good = () => structuredClone(splitSet().manifest);
  test("accepts a format 1 manifest", () => {
    assert.equal(parseManifest(JSON.stringify(good())).version, "1.38.1");
  });
  for (const [what, tweak, error] of [
    ["another format", (m) => ({ ...m, format: 2 }), /format/],
    ["a path with a slash", (m) => ({ ...m, glue: { ...m.glue, path: "../glue.mjs" } }), /path/],
    ["a core encoding other than gzip", (m) => ({ ...m, cores: [{ ...m.cores[0], encoding: "br" }, m.cores[1]] }), /encoding/],
    ["a missing size", (m) => ({ ...m, editor: { path: "editor.js", sha256: m.editor.sha256 } }), /size/],
    ["a malformed sha256", (m) => ({ ...m, editor: { ...m.editor, sha256: "abc" } }), /sha256/],
    ["no cores", (m) => ({ ...m, cores: [] }), /cores/],
    ["a duplicate core name", (m) => ({ ...m, cores: [m.cores[0], m.cores[0]] }), /duplicate/],
    ["a core name not like analyzer.core*.wasm", (m) => ({ ...m, cores: [{ ...m.cores[0], name: "x.wasm" }] }), /name/],
  ]) {
    test(`refuses ${what}`, () => assert.throws(() => parseManifest(JSON.stringify(tweak(good()))), error));
  }
  test("refuses text that is not JSON", () => assert.throws(() => parseManifest("<html>"), /JSON/));
});

describe("loadPieces (split analyzer manifest)", () => {
  test("first load fetches the manifest and every file, uncached by the browser", async () => {
    const set = splitSet();
    const { env: e, calls, store } = env(set.routes);
    const inits = [];
    const fetch = e.fetch;
    e.fetch = (url, init = {}) => (inits.push([url, init.cache]), fetch(url, init));
    const got = await loadPieces([MANIFEST], e);
    assert.deepEqual(calls.sort(), [`GET ${MANIFEST}`, `GET ${DIR}analyzer.core.wasm.gz`, `GET ${DIR}analyzer.core2.wasm.gz`, `GET ${DIR}editor.js`, `GET ${DIR}glue.mjs`].sort());
    assert.ok(inits.every(([, cache]) => cache === "no-cache"), JSON.stringify(inits));
    assert.equal(got.pieces.editor, set.editor);
    assert.equal(got.pieces.glue, set.glue);
    assert.deepEqual(Object.keys(got.pieces.cores).sort(), ["analyzer.core.wasm", "analyzer.core2.wasm"]);
    assert.ok(got.pieces.cores["analyzer.core.wasm"] instanceof Uint8Array);
    assert.match(got.how, /^downloaded 4 files/); // the files the manifest names
    assert.match(got.source, /manifest\.json \(analyzer 1\.38\.1, downloaded/);
    assert.equal(store.size, 1);
  });

  test("same manifest text: cached, only the manifest is fetched", async () => {
    const set = splitSet();
    const store = new Map();
    await loadPieces([MANIFEST], env(set.routes, store).env);
    const second = env(set.routes, store);
    const got = await loadPieces([MANIFEST], second.env);
    assert.equal(got.how, "cached");
    assert.deepEqual(second.calls, [`GET ${MANIFEST}`]);
    assert.ok(got.pieces.cores["analyzer.core.wasm"] instanceof Uint8Array);
  });

  test("a new manifest replaces the whole set", async () => {
    const store = new Map();
    await loadPieces([MANIFEST], env(splitSet({ version: "1.38.1" }).routes, store).env);
    const second = env(splitSet({ version: "1.39.0" }).routes, store);
    const got = await loadPieces([MANIFEST], second.env);
    assert.match(got.how, /^downloaded/);
    assert.equal(fileGets(second.calls).length, 4);
    assert.equal(got.pieces.version, "1.39.0");
  });

  test("a file whose size is off is refused, cached as nothing, and the next URL is tried", async () => {
    const set = splitSet();
    set.routes[`${DIR}glue.mjs`] = { body: set.glue + "// newer" };
    const routes = { ...set.routes, [PAGE]: { body: playgroundPage(), lastModified: "Mon, 19 Oct 2026 00:00:00 GMT" } };
    const { env: e, logs, store } = env(routes);
    const got = await loadPieces([MANIFEST, PAGE], e);
    assert.match(got.source, /^https:\/\/example\.test\/playground\.html/);
    assert.ok(logs.some((l) => /glue\.mjs.*size/.test(l)), logs.join("\n"));
    assert.ok(![...store.keys()].some((k) => k.includes("manifest.json")));
  });

  test("a sha256 mismatch is refused where crypto.subtle exists", async () => {
    const set = splitSet({ tweak: (m) => ({ ...m, editor: { ...m.editor, sha256: "0".repeat(64) } }) });
    await assert.rejects(loadPieces([MANIFEST], env(set.routes).env), /editor\.js.*sha256/);
  });

  test("without crypto.subtle (plain http) only sizes are checked", async () => {
    const set = splitSet({ tweak: (m) => ({ ...m, editor: { ...m.editor, sha256: "0".repeat(64) } }) });
    const plain = memoryEnv(set.routes); // no subtle
    const got = await loadPieces([MANIFEST], plain.env);
    assert.match(got.how, /sizes only/);
  });

  test("a core the server already decompressed is accepted as wasm", async () => {
    const set = splitSet();
    set.routes[`${DIR}analyzer.core.wasm.gz`] = { body: set.cores["analyzer.core.wasm"] };
    const got = await loadPieces([MANIFEST], env(set.routes).env);
    assert.deepEqual([...got.pieces.cores["analyzer.core.wasm"].slice(0, 4)], WASM_MAGIC.slice(0, 4));
  });

  test("cores that do not match the glue are refused", async () => {
    const set = splitSet();
    set.routes[`${DIR}glue.mjs`] = { body: 'kt(new URL("./analyzer.core.wasm",import.meta.url));globalThis.__component={};' };
    set.manifest.glue.size = Buffer.byteLength(set.routes[`${DIR}glue.mjs`].body);
    set.manifest.glue.sha256 = sha256(set.routes[`${DIR}glue.mjs`].body);
    set.routes[MANIFEST] = { body: JSON.stringify(set.manifest) };
    await assert.rejects(loadPieces([MANIFEST], env(set.routes).env), /analyzer\.core2\.wasm/);
  });

  test("a relative manifest URL resolves against the page, and its files against it", async () => {
    const set = splitSet();
    const { env: e, calls } = env(set.routes);
    e.baseUrl = "https://example.test/files/report.html";
    const got = await loadPieces(["analyzer/manifest.json"], e);
    assert.match(got.how, /^downloaded/);
    assert.ok(calls.includes(`GET ${DIR}glue.mjs`), calls.join("\n"));
    assert.match(got.source, /^analyzer\/manifest\.json /);
  });

  test("manifest unreachable with a cached set: uses it", async () => {
    const set = splitSet();
    const store = new Map();
    await loadPieces([MANIFEST], env(set.routes, store).env);
    const offline = env({ [MANIFEST]: "offline" }, store);
    const got = await loadPieces([MANIFEST], offline.env);
    assert.equal(got.how, "cached");
    assert.ok(offline.logs.some((l) => /unreachable/.test(l)));
  });

  test("manifest unreachable and nothing cached: fails", async () => {
    await assert.rejects(loadPieces([MANIFEST], env({ [MANIFEST]: "offline" }).env), /Failed to fetch/);
  });

  test("the single-file page still works, with its cores as bytes now", async () => {
    const page = playgroundPage({ cores: { "analyzer.core.wasm": Buffer.from(gzipSync(new Uint8Array(WASM_MAGIC))).toString("base64") } });
    const { env: e } = env({ [PAGE]: { body: page, lastModified: "Mon, 19 Oct 2026 00:00:00 GMT" } });
    const got = await loadPieces([PAGE], e);
    assert.ok(got.pieces.cores["analyzer.core.wasm"] instanceof Uint8Array);
    assert.deepEqual([...got.pieces.cores["analyzer.core.wasm"].slice(0, 2)], [0x1f, 0x8b]);
  });
});
