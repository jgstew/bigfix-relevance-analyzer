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
  let unreachable = false;
  try {
    const head = await env.fetch(url, { method: "HEAD", cache: "no-store" });
    if (head.ok) lastModified = head.headers.get("Last-Modified");
  } catch (err) {
    if (!cached) throw err;
    unreachable = true;
    env.log(`analyzer: ${url} unreachable (${err}); using the cached copy`);
  }
  // Unreachable: the cached copy is all there is. A server that refuses HEAD
  // or sends no Last-Modified cannot say whether it changed, so download.
  if (cached && (unreachable || (lastModified !== null && cached.lastModified === lastModified))) {
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
    // Optional: the inflated wasm, to verify a core a server decompressed.
    if (core.raw_size !== undefined && (!Number.isInteger(core.raw_size) || core.raw_size < 0)) {
      throw new Error(`manifest: core ${core.name} raw_size is not a size`);
    }
    if (core.raw_sha256 !== undefined && (typeof core.raw_sha256 !== "string" || !SHA256_HEX.test(core.raw_sha256))) {
      throw new Error(`manifest: core ${core.name} raw_sha256 must be 64 lowercase hex digits`);
    }
    if (seen.has(core.name)) throw new Error(`manifest: duplicate core ${core.name}`);
    seen.add(core.name);
  }
  return m;
}

const isGzip = (bytes) => bytes[0] === 0x1f && bytes[1] === 0x8b;
const isWasm = (bytes) => bytes[0] === 0x00 && bytes[1] === 0x61 && bytes[2] === 0x73 && bytes[3] === 0x6d;
const hex = (buffer) => Array.from(new Uint8Array(buffer), (b) => b.toString(16).padStart(2, "0")).join("");

// SHA-256 of `bytes` as lowercase hex, in plain JavaScript: crypto.subtle is
// missing in insecure contexts, such as a Web Reports server on plain http,
// and every file is still checked there.
export function sha256Hex(bytes) {
  const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ]);
  const h = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
  // The message, then 0x80, zeros, and the bit length as 64 bits: a whole
  // number of 64-byte blocks.
  const total = Math.ceil((bytes.length + 9) / 64) * 64;
  const data = new Uint8Array(total);
  data.set(bytes);
  data[bytes.length] = 0x80;
  const view = new DataView(data.buffer);
  view.setUint32(total - 8, Math.floor(bytes.length / 0x20000000));
  view.setUint32(total - 4, (bytes.length * 8) >>> 0);
  const w = new Uint32Array(64);
  const rotr = (x, n) => (x >>> n) | (x << (32 - n));
  for (let block = 0; block < total; block += 64) {
    for (let i = 0; i < 16; i++) w[i] = view.getUint32(block + i * 4);
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
      const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
      w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    let [a, b, c, d, e, f, g, hh] = h;
    for (let i = 0; i < 64; i++) {
      const t1 = (hh + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) >>> 0;
      const t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
      hh = g;
      g = f;
      f = e;
      e = (d + t1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (t1 + t2) >>> 0;
    }
    h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
  }
  return Array.from(h, (x) => x.toString(16).padStart(8, "0")).join("");
}

async function sha256Of(bytes, env) {
  return env.subtle ? hex(await env.subtle.digest("SHA-256", bytes)) : sha256Hex(bytes);
}

// Throws unless `bytes` are what the manifest entry `file` describes: the
// published bytes (size, sha256), or for a core a server decompressed in
// transit, the inflated wasm (raw_size, raw_sha256).
async function verify(file, bytes, env) {
  if (file.encoding === "gzip" && !isGzip(bytes) && isWasm(bytes)) {
    if (!file.raw_sha256) throw new Error(`${file.path}: decompressed in transit, and the manifest has no raw_sha256 to check it`);
    if (bytes.length !== file.raw_size) throw new Error(`${file.path}: raw size ${bytes.length}, manifest says ${file.raw_size}`);
    if ((await sha256Of(bytes, env)) !== file.raw_sha256) throw new Error(`${file.path}: raw_sha256 does not match the manifest`);
    return;
  }
  if (bytes.length !== file.size) throw new Error(`${file.path}: size ${bytes.length}, manifest says ${file.size}`);
  if ((await sha256Of(bytes, env)) !== file.sha256) throw new Error(`${file.path}: sha256 does not match the manifest`);
}

// Every piece of a cached set, checked against its own manifest again before
// it runs, where crypto.subtle makes that cheap: storage is shared with every
// page on the origin.
async function verifyCached(pieces, env) {
  const manifest = parseManifest(pieces.manifestText);
  const encode = (text) => new TextEncoder().encode(text);
  await verify(manifest.editor, encode(pieces.editor), env);
  await verify(manifest.glue, encode(pieces.glue), env);
  for (const core of manifest.cores) {
    if (!pieces.cores[core.name]) throw new Error(`${core.path}: missing from the cache`);
    await verify(core, pieces.cores[core.name], env);
  }
}

// The set `url` names: from the cache while the manifest text is unchanged
// and the cached files still match it, or while the manifest cannot be
// fetched; else downloaded whole and checked. If a newer manifest's set fails,
// a cached set (of the older manifest) is kept rather than nothing.
export async function fromManifest(configured, env) {
  // Absolute, so the file names in it can resolve against it.
  const url = new URL(configured, env.baseUrl).href;
  const key = `manifest:${url}`;
  let cached = await env.cacheGet(key);
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
  if (cached && cached.manifestText === text) {
    // The set was fully verified when it downloaded. Checking it again
    // guards against another page on the origin rewriting the cache; that
    // costs ~5 ms with crypto.subtle, but ~150 ms of JavaScript hashing on
    // every load without it (plain http), so there the set is trusted.
    if (!env.subtle) return { pieces: cached, how: "cached" };
    try {
      await verifyCached(cached, env);
      return { pieces: cached, how: "cached" };
    } catch (err) {
      env.log(`analyzer: the cached set from ${url} does not match its manifest (${err.message}); downloading it again`);
      cached = undefined;
    }
  }
  try {
    return await downloadSet(url, key, text, env);
  } catch (err) {
    if (!cached) throw err;
    env.log(`analyzer: the newer manifest at ${url} failed (${err.message}); keeping the cached set`);
    return { pieces: cached, how: `cached (the newer manifest failed: ${err.message})` };
  }
}

async function downloadSet(url, key, text, env) {
  const manifest = parseManifest(text);
  const started = env.now();
  const files = [manifest.editor, manifest.glue, ...manifest.cores];
  const bytes = await Promise.all(
    files.map(async (file) => {
      let res;
      try {
        res = await env.fetch(new URL(file.path, url).href, { cache: "no-cache" });
      } catch (err) {
        throw new Error(`${file.path}: ${err.message || err}`);
      }
      if (!res.ok) throw new Error(`${file.path}: HTTP ${res.status}`);
      return new Uint8Array(await res.arrayBuffer());
    }),
  );
  for (let i = 0; i < files.length; i++) await verify(files[i], bytes[i], env);
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
  const how = env.subtle ? "checked sizes and sha256" : "checked sizes and sha256 (in JavaScript: no crypto.subtle here)";
  return { pieces, how: `downloaded ${files.length} files (${mb} MB) in ${Math.round(env.now() - started)} ms, ${how}` };
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
