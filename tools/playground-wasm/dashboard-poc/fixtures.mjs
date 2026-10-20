// Shared test fixtures for test_loader.mjs and test_manifest.mjs: a
// miniature single-file playground page, a fake fetch and an in-memory cache.
// Not a test file itself, so importing it runs no tests.

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
      log: (text) => logs.push(text),
      now: () => 0,
    },
    calls,
    logs,
    store,
  };
}
