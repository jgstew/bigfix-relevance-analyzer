// Where the Web Report's analyzer comes from, and its cache: the parts of the
// loader that run without a page, so test_loader.mjs can drive them in Node
// with a fake fetch and cache. build_poc.py inlines this file into
// analyzer_loader.html's module script, which supplies the real ones:
//
//   env = { fetch, cacheGet(key), cachePut(key, value), log(text), now() }
//
// It is inlined into a <script> element, so it must never spell out that
// element's closing tag, even in a string or comment (the builder checks).

// ---- the single-file playground page --------------------------------------

export function between(text, start, end, what) {
  const i = text.indexOf(start);
  if (i < 0 || text.indexOf(start, i + 1) >= 0) throw new Error(`${what}: expected exactly one "${start}"`);
  const from = i + start.length;
  const to = text.indexOf(end, from);
  if (to < 0) throw new Error(`${what}: no "${end}" after "${start}"`);
  return text.slice(from, to);
}

// The three pieces of the published single-file playground page, found by
// text that appears exactly once there (see
// ../componentize-py/build-playground/template.html and
// ../common/shared_script.html): the editor bundle, the gzipped cores
// (base64), and the component glue jco generated for exactly those cores.
export function extract(html) {
  const editor = between(html, "Publishes window.playgroundEditor.\n", "\n<\/script>", "editor bundle");
  const coresLiteral = between(html, "const CORES_GZIP = ", ";\n", "core modules");
  // The glue sits between the end of boot() and the template's closing code.
  const afterBoot = between(html, "async function boot()", "// window.__wasmProblem was already handled", "component glue");
  const glue = afterBoot.slice(afterBoot.indexOf("\n}\n") + 3);
  const cores = JSON.parse(coresLiteral);
  const names = Object.keys(cores);
  if (!editor.includes("playgroundEditor")) throw new Error("editor bundle: no playgroundEditor");
  if (!glue.includes("__component")) throw new Error("component glue: no globalThis.__component");
  if (!names.length || !names.every((n) => /^analyzer\.core\d*\.wasm$/.test(n))) {
    throw new Error(`core modules: unexpected names ${names.join(", ")}`);
  }
  for (const name of names) {
    if (!glue.includes(`"./${name}"`)) throw new Error(`component glue does not load ${name}`);
  }
  return { editor, cores, glue };
}

// ---- fetching and caching ---------------------------------------------------

// The pieces from `url`: the cached copy while the page's Last-Modified is
// unchanged (or cannot be checked), else a fresh download.
export async function fromSource(url, env) {
  const cached = await env.cacheGet(url);
  let lastModified = null;
  try {
    const head = await env.fetch(url, { method: "HEAD", cache: "no-store" });
    if (head.ok) lastModified = head.headers.get("Last-Modified");
  } catch (err) {
    if (!cached) throw err;
    env.log(`analyzer: ${url} unreachable (${err}); using the cached copy`);
  }
  if (cached && (lastModified === null || cached.lastModified === lastModified)) {
    return { pieces: cached, how: "cached" };
  }
  const started = env.now();
  const res = await env.fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const html = await res.text();
  const pieces = { ...extract(html), lastModified: res.headers.get("Last-Modified") || lastModified };
  const mb = (html.length / 1048576).toFixed(1);
  try {
    await env.cachePut(url, pieces);
  } catch (err) {
    env.log(`analyzer: could not cache it (${err}); it will download again next time`);
  }
  return { pieces, how: `downloaded ${mb} MB in ${Math.round(env.now() - started)} ms` };
}

// The first of `urls` that works; `source` names it for the diagnostics.
export async function loadPieces(urls, env) {
  const problems = [];
  for (const url of urls) {
    try {
      const got = await fromSource(url, env);
      return { ...got, source: `${url} (${got.how}, Last-Modified ${got.pieces.lastModified || "unknown"})` };
    } catch (err) {
      problems.push(`${url}: ${err.message || err}`);
      env.log(`analyzer: ${url} failed: ${err.message || err}`);
    }
  }
  throw new Error(problems.join("; ") || "no analyzer URL configured");
}

// ---- what the analysis means here ----------------------------------------

// The analyzer's payload "dialect" -> what it means here. A stand-in for the
// debugger's dialect_fit (not in the component yet): resolved wins, "both"
// and "uncertain" mean either, else the text classifier.
export function dialectChoice(payload) {
  const d = payload.dialect;
  if (d.resolved === "client" || d.resolved === "session") {
    return { dialects: [d.resolved], why: `the analyzer resolved it as ${d.resolved}` };
  }
  if (d.resolved === "both") {
    return { dialects: ["session", "client"], why: "the analyzer says it is valid in either dialect" };
  }
  if (d.resolved === "uncertain") {
    return { dialects: ["session", "client"], why: "it mixes client and session references" };
  }
  if (d.classified === "client" || d.classified === "session") {
    return { dialects: [d.classified], why: `the analyzer's text classifier says ${d.classified}` };
  }
  return { dialects: ["session", "client"], why: "the analyzer could not tell" };
}
