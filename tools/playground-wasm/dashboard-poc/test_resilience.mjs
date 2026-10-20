#!/usr/bin/env node
// Unit tests for loader.mjs's resilience: the safety net for an analyzer set
// that downloads and verifies but does not start (loadAndStart), the manual
// reset behind "Reload the analyzer" (forgetAnalyzer), and reusing unchanged
// files from the cached set when a new manifest arrives.
//
//   node --test tools/playground-wasm/dashboard-poc/
//
// `start` is a fake here; the browser's (analyzer_loader.html) is covered by
// test_reports.mjs.

import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { describe, test } from "node:test";

import { DIR, MANIFEST, memoryEnv, playgroundPage, secureEnv, splitSet } from "./fixtures.mjs";
import { forgetAnalyzer, loadAndStart, loadPieces } from "./loader.mjs";

const PAGE = "https://example.test/playground.html";
const MONDAY = "Mon, 19 Oct 2026 00:00:00 GMT";
const TUESDAY = "Tue, 20 Oct 2026 00:00:00 GMT";
const SET_KEY = `manifest:${MANIFEST}`;
const RECORD_KEY = `nostart:${SET_KEY}`;
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");

const fileGets = (calls) => calls.filter((c) => c.startsWith("GET ") && !c.endsWith("manifest.json"));

// A fake start(): fails while `broken` says so, and counts its calls.
function starter(broken = () => false) {
  const runs = [];
  const start = async (pieces) => {
    runs.push(pieces.version || pieces.lastModified);
    if (broken(pieces, runs.length)) throw new Error("the glue threw: boom");
    return { started: pieces.version || pieces.lastModified };
  };
  return { start, runs };
}

// The cache after a first good load of `set`.
async function cachedAfter(set, make = secureEnv) {
  const store = new Map();
  await loadPieces([MANIFEST], make(set.routes, store).env);
  return store;
}

describe("loadAndStart: a set that verifies but does not start", () => {
  test("a set that starts is returned with what start() gave back", async () => {
    const { env, calls } = secureEnv(splitSet().routes);
    const { start, runs } = starter();
    const got = await loadAndStart([MANIFEST], env, start);
    assert.deepEqual(got.started, { started: "1.38.1" });
    assert.match(got.how, /^downloaded 4 files/);
    assert.deepEqual(runs, ["1.38.1"]);
    assert.equal(fileGets(calls).length, 4);
  });

  test("a cached set that fails to start is dropped, downloaded once more and started", async () => {
    const set = splitSet();
    const store = await cachedAfter(set);
    const { env, calls, logs } = secureEnv(set.routes, store);
    const { start, runs } = starter((pieces, n) => n === 1);
    const got = await loadAndStart([MANIFEST], env, start);
    assert.deepEqual(runs, ["1.38.1", "1.38.1"]);
    assert.match(got.how, /^downloaded 4 files/);
    assert.equal(fileGets(calls).length, 4, "one fresh copy, every file");
    assert.ok(!store.has(RECORD_KEY), "it started, so nothing is recorded");
    assert.ok(store.has(SET_KEY), "the fresh copy is cached");
    assert.ok(logs.some((l) => /did not start .*boom.*downloading it again/.test(l)), logs.join("\n"));
  });

  test("a freshly downloaded set that fails to start is recorded, not retried", async () => {
    const set = splitSet();
    const { env, calls, store } = secureEnv(set.routes);
    const { start, runs } = starter(() => true);
    await assert.rejects(loadAndStart([MANIFEST], env, start), (err) => {
      assert.equal(err.doesNotStart, true);
      assert.match(err.message, /does not start in this browser.*boom/);
      assert.match(err.message, /Reload the analyzer/);
      return true;
    });
    assert.equal(runs.length, 1);
    assert.equal(fileGets(calls).length, 4);
    const record = store.get(RECORD_KEY);
    assert.equal(record.id, sha256(set.routes[MANIFEST].body));
    assert.match(record.error, /boom/);
    assert.match(record.time, /^\d{4}-\d\d-\d\dT/);
  });

  test("a cached set that fails, then its fresh copy fails too: recorded after one retry", async () => {
    const set = splitSet();
    const store = await cachedAfter(set);
    const { env, calls } = secureEnv(set.routes, store);
    const { start, runs } = starter(() => true);
    await assert.rejects(loadAndStart([MANIFEST], env, start), /does not start/);
    assert.equal(runs.length, 2);
    assert.equal(fileGets(calls).length, 4);
    assert.ok(store.has(RECORD_KEY));
  });

  test("later loads with the same manifest neither download nor start", async () => {
    const set = splitSet();
    const store = new Map();
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(set.routes, store).env, starter(() => true).start));
    for (const make of [secureEnv, memoryEnv]) {
      const { env, calls } = make(set.routes, store);
      const { start, runs } = starter();
      await assert.rejects(loadAndStart([MANIFEST], env, start), (err) => err.doesNotStart && /boom/.test(err.message));
      assert.deepEqual(calls, [`GET ${MANIFEST}`]);
      assert.equal(runs.length, 0);
    }
  });

  test("the record stops the load: later URLs are not tried either", async () => {
    const set = splitSet();
    const store = new Map();
    const routes = { ...set.routes, [PAGE]: { body: playgroundPage(), lastModified: MONDAY } };
    await assert.rejects(loadAndStart([MANIFEST, PAGE], secureEnv(routes, store).env, starter(() => true).start));
    const { env, calls } = secureEnv(routes, store);
    await assert.rejects(loadAndStart([MANIFEST, PAGE], env, starter().start), /does not start/);
    assert.deepEqual(calls, [`GET ${MANIFEST}`]);
  });

  test("an unreachable manifest with a cached set recorded as not starting: nothing runs", async () => {
    const set = splitSet();
    const store = new Map();
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(set.routes, store).env, starter(() => true).start));
    const { env } = secureEnv({ [MANIFEST]: "offline" }, store);
    const { start, runs } = starter();
    await assert.rejects(loadAndStart([MANIFEST], env, start), /does not start/);
    assert.equal(runs.length, 0);
  });

  test("a new manifest is tried once again", async () => {
    const store = new Map();
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(splitSet().routes, store).env, starter(() => true).start));
    const newer = splitSet({ version: "1.39.0", seeds: { glue: 2 } });
    const { env } = secureEnv(newer.routes, store);
    const got = await loadAndStart([MANIFEST], env, starter().start);
    assert.deepEqual(got.started, { started: "1.39.0" });
  });

  test("a new manifest that does not start either replaces the record, again with no retry loop", async () => {
    const store = new Map();
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(splitSet().routes, store).env, starter(() => true).start));
    const newer = splitSet({ version: "1.39.0", seeds: { glue: 2 } });
    const first = secureEnv(newer.routes, store);
    await assert.rejects(loadAndStart([MANIFEST], first.env, starter(() => true).start), /does not start/);
    assert.equal(store.get(RECORD_KEY).id, sha256(newer.routes[MANIFEST].body));
    const again = secureEnv(newer.routes, store);
    await assert.rejects(loadAndStart([MANIFEST], again.env, starter().start), /does not start/);
    assert.deepEqual(again.calls, [`GET ${MANIFEST}`]);
  });

  test("network errors never count as not starting", async () => {
    const set = splitSet();
    set.routes[`${DIR}glue.mjs`] = "offline";
    const { env, store } = secureEnv(set.routes);
    const { start, runs } = starter();
    await assert.rejects(loadAndStart([MANIFEST], env, start), (err) => !err.doesNotStart && /glue\.mjs: .*Failed to fetch/.test(err.message));
    assert.equal(runs.length, 0);
    assert.ok(![...store.keys()].some((k) => k.startsWith("nostart:")));
  });

  test("checksum mismatches never count as not starting", async () => {
    const set = splitSet({ tweak: (m) => ({ ...m, editor: { ...m.editor, sha256: "0".repeat(64) } }) });
    const { env, store } = secureEnv(set.routes);
    const { start, runs } = starter();
    await assert.rejects(loadAndStart([MANIFEST], env, start), (err) => !err.doesNotStart && /sha256/.test(err.message));
    assert.equal(runs.length, 0);
    assert.ok(![...store.keys()].some((k) => k.startsWith("nostart:")));
  });

  test("a cached set is retried once per manifest: failing again on a later load records it", async () => {
    // Review of #187, finding 2: an intermittent start failure must not
    // download the whole set again on every load where it happens.
    const set = splitSet();
    const store = await cachedAfter(set);
    const first = secureEnv(set.routes, store);
    await loadAndStart([MANIFEST], first.env, starter((pieces, n) => n === 1).start);
    assert.equal(fileGets(first.calls).length, 4, "the one retry");
    const later = secureEnv(set.routes, store);
    const { start, runs } = starter(() => true);
    await assert.rejects(loadAndStart([MANIFEST], later.env, start), (err) => err.doesNotStart && /boom/.test(err.message));
    assert.equal(runs.length, 1);
    assert.deepEqual(fileGets(later.calls), [], "no second retry for the same manifest");
    assert.ok(store.has(RECORD_KEY));
    // A new release gets its own retry.
    const newer = splitSet({ version: "1.39.0", seeds: { glue: 2 } });
    await loadAndStart([MANIFEST], secureEnv(newer.routes, store).env, starter().start);
    const third = secureEnv(newer.routes, store);
    await loadAndStart([MANIFEST], third.env, starter((pieces, n) => n === 1).start);
    assert.equal(fileGets(third.calls).length, 4);
  });

  test("a recorded older set with a newer manifest that fails to download says both", async () => {
    // Review of #187, finding 4: the newer set's own failure is the news.
    const store = new Map();
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(splitSet().routes, store).env, starter(() => true).start));
    const newer = splitSet({ version: "1.39.0", seeds: { glue: 2 } });
    newer.routes[`${DIR}glue.mjs`] = { body: "gone", status: 503 };
    const { env } = secureEnv(newer.routes, store);
    const { start, runs } = starter();
    await assert.rejects(loadAndStart([MANIFEST], env, start), (err) => {
      assert.equal(err.doesNotStart, true);
      assert.match(err.message, /does not start in this browser.*boom/);
      assert.match(err.message, /the newer manifest failed: glue\.mjs: HTTP 503/);
      return true;
    });
    assert.equal(runs.length, 0);
  });

  test("records are per source: one that does not start leaves another alone", async () => {
    const set = splitSet();
    const store = new Map();
    const routes = { ...set.routes, [PAGE]: { body: playgroundPage(), lastModified: MONDAY } };
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(routes, store).env, starter(() => true).start));
    const got = await loadAndStart([PAGE], secureEnv(routes, store).env, starter().start);
    assert.deepEqual(got.started, { started: MONDAY });
  });

  test("the single-file page: recorded by its Last-Modified, retried when that changes", async () => {
    const store = new Map();
    const monday = { [PAGE]: { body: playgroundPage(), lastModified: MONDAY } };
    await assert.rejects(loadAndStart([PAGE], secureEnv(monday, store).env, starter(() => true).start), /does not start/);
    assert.equal(store.get(`nostart:page:${PAGE}`).id, MONDAY);
    const again = secureEnv(monday, store);
    const { start, runs } = starter();
    await assert.rejects(loadAndStart([PAGE], again.env, start), /does not start/);
    assert.deepEqual(again.calls, [`HEAD ${PAGE}`]);
    assert.equal(runs.length, 0);
    const tuesday = { [PAGE]: { body: playgroundPage(), lastModified: TUESDAY } };
    const got = await loadAndStart([PAGE], secureEnv(tuesday, store).env, starter().start);
    assert.deepEqual(got.started, { started: TUESDAY });
  });

  test("the single-file page with no Last-Modified on HEAD: a recorded page is not downloaded again", async () => {
    // Review of #187, finding 3: HEAD cannot say whether it changed, so the
    // GET asks with If-Modified-Since the recorded Last-Modified; 304 means
    // the same page, still recorded.
    const store = new Map();
    const routes = { [PAGE]: { body: playgroundPage(), lastModified: MONDAY, headLastModified: false } };
    await assert.rejects(loadAndStart([PAGE], secureEnv(routes, store).env, starter(() => true).start), /does not start/);
    assert.equal(store.get(`nostart:page:${PAGE}`).id, MONDAY);
    const again = secureEnv(routes, store);
    const sent = [];
    const fetch = again.env.fetch;
    again.env.fetch = async (url, init = {}) => {
      const res = await fetch(url, init);
      sent.push(`${init.method || "GET"} ${new Headers(init.headers).get("If-Modified-Since") || "-"} ${res.status}`);
      return res;
    };
    const { start, runs } = starter();
    await assert.rejects(loadAndStart([PAGE], again.env, start), (err) => err.doesNotStart && /boom/.test(err.message));
    assert.deepEqual(sent, ["HEAD - 200", `GET ${MONDAY} 304`]);
    assert.equal(runs.length, 0);
    // A changed page answers 200 and is tried.
    const tuesday = { [PAGE]: { body: playgroundPage(), lastModified: TUESDAY, headLastModified: false } };
    const got = await loadAndStart([PAGE], secureEnv(tuesday, store).env, starter().start);
    assert.deepEqual(got.started, { started: TUESDAY });
  });
});

describe("forgetAnalyzer (the Reload the analyzer button)", () => {
  test("clears the cached sets and records of the configured sources, then a load starts afresh", async () => {
    const set = splitSet();
    const store = new Map();
    const routes = { ...set.routes, [PAGE]: { body: playgroundPage(), lastModified: MONDAY } };
    await assert.rejects(loadAndStart([MANIFEST], secureEnv(routes, store).env, starter(() => true).start));
    await loadAndStart([PAGE], secureEnv(routes, store).env, starter().start);
    store.set("unrelated", 1);
    const { env, logs } = secureEnv(routes, store);
    const removed = await forgetAnalyzer([MANIFEST, PAGE], env);
    assert.deepEqual(removed.sort(), [SET_KEY, RECORD_KEY, `page:${PAGE}`].sort());
    assert.deepEqual([...store.keys()], ["unrelated"]);
    assert.ok(logs.some((l) => /forgot/.test(l)), logs.join("\n"));
    const again = secureEnv(routes, store);
    const got = await loadAndStart([MANIFEST, PAGE], again.env, starter().start);
    assert.deepEqual(got.started, { started: "1.38.1" });
    assert.equal(fileGets(again.calls).length, 4);
  });

  test("a relative manifest URL is forgotten by its absolute key", async () => {
    const set = splitSet();
    const store = await cachedAfter(set);
    const { env } = secureEnv(set.routes, store);
    env.baseUrl = "https://example.test/files/report.html";
    assert.deepEqual(await forgetAnalyzer(["analyzer/manifest.json"], env), [SET_KEY]);
  });
});

describe("a new manifest reuses the cached files that did not change", () => {
  const CHANGED = { "analyzer.core.wasm": 1 };

  test("only changed files are fetched, the rest are reused byte for byte", async () => {
    const store = await cachedAfter(splitSet());
    const newer = splitSet({ version: "1.39.0", seeds: CHANGED });
    const { env, calls } = secureEnv(newer.routes, store);
    const got = await loadAndStart([MANIFEST], env, starter().start);
    assert.deepEqual(fileGets(calls), [`GET ${DIR}analyzer.core.wasm.gz`]);
    assert.match(got.how, /^downloaded 1 file \(0\.0 MB\), reused 3 in \d+ ms/);
    assert.equal(got.pieces.version, "1.39.0");
    assert.equal(got.pieces.editor, newer.editor);
    assert.equal(got.pieces.glue, newer.glue);
    const gz2 = new Uint8Array(newer.routes[`${DIR}analyzer.core2.wasm.gz`].body);
    assert.deepEqual(got.pieces.cores["analyzer.core2.wasm"], gz2);
    // The new set is cached whole, under the new manifest.
    const cached = store.get(SET_KEY);
    assert.equal(cached.manifestText, newer.routes[MANIFEST].body);
    assert.deepEqual(Object.keys(cached.cores).sort(), ["analyzer.core.wasm", "analyzer.core2.wasm"]);
  });

  test("a changed glue or editor is fetched", async () => {
    const store = await cachedAfter(splitSet());
    const newer = splitSet({ version: "1.39.0", seeds: { glue: 3, editor: 3 } });
    const { env, calls } = secureEnv(newer.routes, store);
    const got = await loadAndStart([MANIFEST], env, starter().start);
    assert.deepEqual(fileGets(calls).sort(), [`GET ${DIR}editor.js`, `GET ${DIR}glue.mjs`]);
    assert.equal(got.pieces.glue, newer.glue);
  });

  test("a core cached as plain wasm (inflated in transit) is matched by raw_sha256", async () => {
    for (const make of [secureEnv, memoryEnv]) {
      const older = splitSet();
      older.routes[`${DIR}analyzer.core2.wasm.gz`] = { body: older.cores["analyzer.core2.wasm"] };
      const store = await cachedAfter(older, make);
      const newer = splitSet({ version: "1.39.0", seeds: CHANGED });
      const { env, calls } = make(newer.routes, store);
      const got = await loadAndStart([MANIFEST], env, starter().start);
      assert.deepEqual(fileGets(calls), [`GET ${DIR}analyzer.core.wasm.gz`]);
      assert.deepEqual(got.pieces.cores["analyzer.core2.wasm"], older.cores["analyzer.core2.wasm"]);
    }
  });

  test("with crypto.subtle a tampered cached file is caught and fetched instead", async () => {
    const store = await cachedAfter(splitSet());
    store.get(SET_KEY).glue = "globalThis.__component={evil:1};";
    const newer = splitSet({ version: "1.39.0", seeds: CHANGED });
    const { env, calls, logs } = secureEnv(newer.routes, store);
    const got = await loadAndStart([MANIFEST], env, starter().start);
    assert.deepEqual(fileGets(calls).sort(), [`GET ${DIR}analyzer.core.wasm.gz`, `GET ${DIR}glue.mjs`]);
    assert.equal(got.pieces.glue, newer.glue);
    assert.ok(logs.some((l) => /glue\.mjs.*cached copy.*does not match/.test(l)), logs.join("\n"));
  });

  test("without crypto.subtle a file is reused only when its manifest entry is unchanged", async () => {
    const store = await cachedAfter(splitSet(), memoryEnv);
    const newer = splitSet({ version: "1.39.0", seeds: CHANGED });
    const { env, calls } = memoryEnv(newer.routes, store);
    const got = await loadAndStart([MANIFEST], env, starter().start);
    assert.deepEqual(fileGets(calls), [`GET ${DIR}analyzer.core.wasm.gz`]);
    assert.match(got.how, /reused 3 .*in JavaScript/);
  });

  test("a failing download keeps the whole older set, never a mix", async () => {
    const older = splitSet();
    const store = await cachedAfter(older);
    const newer = splitSet({ version: "1.39.0", seeds: CHANGED });
    newer.routes[`${DIR}analyzer.core.wasm.gz`] = { body: "gone", status: 503 };
    const { env } = secureEnv(newer.routes, store);
    const got = await loadAndStart([MANIFEST], env, starter().start);
    assert.match(got.how, /^cached \(the newer manifest failed: analyzer\.core\.wasm\.gz: HTTP 503\)/);
    assert.equal(got.pieces.version, "1.38.1");
    assert.equal(got.pieces.manifestText, older.routes[MANIFEST].body);
  });

  test("a set built partly from the cache that fails to start is retried with every file downloaded", async () => {
    const store = await cachedAfter(splitSet());
    const newer = splitSet({ version: "1.39.0", seeds: CHANGED });
    const { env, calls } = secureEnv(newer.routes, store);
    const { start, runs } = starter((pieces, n) => n === 1);
    const got = await loadAndStart([MANIFEST], env, start);
    assert.equal(runs.length, 2);
    assert.match(got.how, /^downloaded 4 files/);
    assert.equal(fileGets(calls).length, 1 + 4);
    assert.ok(!store.has(RECORD_KEY));
  });
});
