// Where the Web Report's analyzer comes from, and its cache: the parts of the
// loader that run without a page, so test_loader.mjs can drive them in Node
// with a fake fetch and cache. build_poc.py inlines this file into
// analyzer_loader.html's module script, which supplies the real ones:
//
//   env = { fetch, cacheGet(key), cachePut(key, value), log(text), now(),
//           subtle,    (crypto.subtle; missing in insecure contexts)
//           baseUrl }  (what relative URLs resolve against: the page)
//
// Two kinds of source, by URL: a split analyzer's manifest.json (the
// contract is MANIFEST.md), or the single-file playground page.
//
// Either way the result is the same set of pieces: { editor (script text),
// glue (module text), cores: { name: Uint8Array } } where each core's bytes
// are gzipped, or already plain wasm if a server decompressed them in transit.
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
export async function fromPage(url, env) {
  const key = `page:${url}`;
  const cached = await env.cacheGet(key);
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
  const found = extract(html);
  const cores = {};
  for (const [name, b64] of Object.entries(found.cores)) cores[name] = bytesFromBase64(b64);
  const pieces = { ...found, cores, lastModified: res.headers.get("Last-Modified") || lastModified };
  const mb = (html.length / 1048576).toFixed(1);
  try {
    await env.cachePut(key, pieces);
  } catch (err) {
    env.log(`analyzer: could not cache it (${err}); it will download again next time`);
  }
  return { pieces, how: `downloaded ${mb} MB in ${Math.round(env.now() - started)} ms` };
}

// The first of `urls` that works; `source` names it for the diagnostics. A URL
// ending in .json is a split analyzer's manifest, anything else the
// single-file playground page.
export async function loadPieces(urls, env) {
  const problems = [];
  for (const url of urls) {
    try {
      if (isManifestUrl(url)) {
        const got = await fromManifest(url, env);
        return { ...got, source: `${url} (analyzer ${got.pieces.version}, ${got.how})` };
      }
      const got = await fromPage(url, env);
      return { ...got, source: `${url} (${got.how}, Last-Modified ${got.pieces.lastModified || "unknown"})` };
    } catch (err) {
      problems.push(`${url}: ${err.message || err}`);
      env.log(`analyzer: ${url} failed: ${err.message || err}`);
    }
  }
  throw new Error(problems.join("; ") || "no analyzer URL configured");
}

// ---- the split analyzer: manifest.json and its files ------------------------

export const isManifestUrl = (url) => /\.json([?#]|$)/.test(url);

const BARE_NAME = /^[A-Za-z0-9_-][A-Za-z0-9._-]*$/;
const SHA256_HEX = /^[0-9a-f]{64}$/;
const CORE_NAME = /^analyzer\.core\d*\.wasm$/;
const GLUE_CORES = /"\.\/(analyzer\.core\d*\.wasm)"/g;

// The manifest, checked against MANIFEST.md (format 1); throws on anything
// else.
export function parseManifest(text) {
  let m;
  try {
    m = JSON.parse(text);
  } catch (err) {
    throw new Error(`manifest: not JSON (${err.message})`);
  }
  if (!m || m.format !== 1) throw new Error(`manifest: format ${m && m.format} is not 1`);
  if (typeof m.version !== "string" || !m.version) throw new Error("manifest: no version");
  const checkFile = (f, what) => {
    if (!f || typeof f.path !== "string" || !BARE_NAME.test(f.path)) {
      throw new Error(`manifest: ${what} path must be a bare file name`);
    }
    if (!Number.isInteger(f.size) || f.size < 0) throw new Error(`manifest: ${what} size is missing`);
    if (typeof f.sha256 !== "string" || !SHA256_HEX.test(f.sha256)) {
      throw new Error(`manifest: ${what} sha256 must be 64 lowercase hex digits`);
    }
  };
  checkFile(m.editor, "editor");
  checkFile(m.glue, "glue");
  if (!Array.isArray(m.cores) || !m.cores.length) throw new Error("manifest: no cores");
  const seen = new Set();
  for (const core of m.cores) {
    checkFile(core, `core ${core && core.name}`);
    if (typeof core.name !== "string" || !CORE_NAME.test(core.name)) {
      throw new Error(`manifest: core name ${core.name} is not like analyzer.core*.wasm`);
    }
    if (core.encoding !== "gzip") throw new Error(`manifest: core ${core.name} encoding ${core.encoding} is not gzip`);
    if (seen.has(core.name)) throw new Error(`manifest: duplicate core ${core.name}`);
    seen.add(core.name);
  }
  return m;
}

const isGzip = (bytes) => bytes[0] === 0x1f && bytes[1] === 0x8b;
const isWasm = (bytes) => bytes[0] === 0x00 && bytes[1] === 0x61 && bytes[2] === 0x73 && bytes[3] === 0x6d;
const hex = (buffer) => Array.from(new Uint8Array(buffer), (b) => b.toString(16).padStart(2, "0")).join("");

// The set `url` names, from the cache while the manifest text is unchanged
// (or the manifest cannot be fetched), else downloaded whole and checked.
export async function fromManifest(configured, env) {
  // Absolute, so the file names in it can resolve against it.
  const url = new URL(configured, env.baseUrl).href;
  const key = `manifest:${url}`;
  const cached = await env.cacheGet(key);
  let text;
  try {
    const res = await env.fetch(url, { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    text = await res.text();
  } catch (err) {
    if (!cached) throw err;
    env.log(`analyzer: ${url} unreachable (${err.message || err}); using the cached set`);
    return { pieces: cached, how: "cached" };
  }
  if (cached && cached.manifestText === text) return { pieces: cached, how: "cached" };

  const manifest = parseManifest(text);
  const started = env.now();
  const files = [manifest.editor, manifest.glue, ...manifest.cores];
  const bytes = await Promise.all(
    files.map(async (file) => {
      const res = await env.fetch(new URL(file.path, url).href, { cache: "no-cache" });
      if (!res.ok) throw new Error(`${file.path}: HTTP ${res.status}`);
      return new Uint8Array(await res.arrayBuffer());
    }),
  );
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    // A core a server decompressed in transit is no longer the published
    // bytes, so there is nothing to compare; it is still the right wasm.
    if (file.encoding === "gzip" && !isGzip(bytes[i]) && isWasm(bytes[i])) continue;
    if (bytes[i].length !== file.size) throw new Error(`${file.path}: size ${bytes[i].length}, manifest says ${file.size}`);
    if (env.subtle && hex(await env.subtle.digest("SHA-256", bytes[i])) !== file.sha256) {
      throw new Error(`${file.path}: sha256 does not match the manifest`);
    }
  }
  const decode = (b) => new TextDecoder().decode(b);
  const editor = decode(bytes[0]);
  const glue = decode(bytes[1]);
  const cores = {};
  manifest.cores.forEach((core, i) => (cores[core.name] = bytes[i + 2]));
  const loaded = new Set(Array.from(glue.matchAll(GLUE_CORES), (m) => m[1]));
  for (const name of Object.keys(cores)) {
    if (!loaded.has(name)) throw new Error(`manifest core ${name} is not loaded by glue.mjs`);
  }
  for (const name of loaded) {
    if (!(name in cores)) throw new Error(`glue.mjs loads ${name}, which the manifest does not list`);
  }

  const pieces = { editor, glue, cores, version: manifest.version, manifestText: text };
  try {
    await env.cachePut(key, pieces);
  } catch (err) {
    env.log(`analyzer: could not cache it (${err}); it will download again next time`);
  }
  const mb = (bytes.reduce((n, b) => n + b.length, 0) / 1048576).toFixed(1);
  const checked = env.subtle ? "checked sizes and sha256" : "checked sizes only (no crypto.subtle here)";
  return { pieces, how: `downloaded ${files.length} files (${mb} MB) in ${Math.round(env.now() - started)} ms, ${checked}` };
}

export function bytesFromBase64(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
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
