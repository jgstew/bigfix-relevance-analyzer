// Shared test fixtures for the node --test files: a miniature single-file
// playground page, a miniature split analyzer set, a fake fetch and an
// in-memory cache. Not a test file itself, so importing it runs no tests.

import { createHash, webcrypto } from "node:crypto";
import { gzipSync } from "node:zlib";

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

// A fake fetch over `routes` (url -> {body, status, headStatus, lastModified}
// or "offline"),
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
    const status = (method === "HEAD" && route.headStatus) || route.status || 200;
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
      cacheDelete: async (key) => void store.delete(key),
      log: (text) => logs.push(text),
      now: () => 0,
    },
    calls,
    logs,
    store,
  };
}

// memoryEnv with crypto.subtle, as in a secure browser context.
export function secureEnv(routes, store) {
  const made = memoryEnv(routes, store);
  made.env.subtle = webcrypto.subtle;
  return made;
}

export const DIR = "https://example.test/files/analyzer/";
export const MANIFEST = `${DIR}manifest.json`;
export const WASM_MAGIC = [0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00];
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");

// A published split set: {routes, manifest, cores (name -> raw wasm bytes),
// editor, glue}. Files depend only on `seeds` (name -> a number mixed into
// that file: "editor", "glue" or a core name), not on `version`, so two
// versions share every file whose seed is the same, as real releases mostly do.
export function splitSet({ version = "1.38.1", coreNames = ["analyzer.core.wasm", "analyzer.core2.wasm"], seeds = {}, tweak = (m) => m } = {}) {
  const editor = `(()=>{window.playgroundEditor={mount(){}}})();${seeds.editor ? `//${seeds.editor}` : ""}`;
  const glue =
    coreNames.map((n) => `kt(new URL("./${n}",import.meta.url));`).join("") +
    "globalThis.__component={};" +
    (seeds.glue ? `//${seeds.glue}` : "");
  const routes = {};
  const cores = {};
  const entries = coreNames.map((name, i) => {
    const raw = new Uint8Array([...WASM_MAGIC, i, seeds[name] || 0]);
    cores[name] = raw;
    const gz = gzipSync(raw, { level: 9 });
    const path = `${name}.gz`;
    routes[DIR + path] = { body: gz };
    return { name, path, encoding: "gzip", size: gz.length, sha256: sha256(gz), raw_size: raw.length, raw_sha256: sha256(raw) };
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
