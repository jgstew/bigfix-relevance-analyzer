# The split analyzer: `files/analyzer/` and its manifest (format 1)

The browser analyzer (the componentize-py component plus its CodeMirror
editor) published as separate files in one flat folder, so pages can cache
it instead of downloading the whole ~12 MB single-file playground each time.
Two consumers read it: the playground page in the same folder, and the
relevance debugger Web Report (`analyzer_loader.html`).

Published at `https://www.jgstew.com/files/analyzer/`, always the latest
release; there are no version folders. The version lives only in the
manifest, which is what keeps the files matched.

This is a draft contract between the producer (the analyzer's release build)
and its consumers. Change it only together with both.

## Files

| File | What it is |
|---|---|
| `manifest.json` | Names the version and every other file, with sizes and checksums. |
| `editor.js` | The editor bundle (`../editor-bundle/build.mjs` output): a classic script, an IIFE that sets `window.playgroundEditor`. |
| `glue.mjs` | The component glue: jco's transpiled, bundled ES module (`bundle.mjs`), unmodified. It sets `globalThis.__component`; awaiting `__component.$init` instantiates the cores. |
| `analyzer.core*.wasm.gz` | Each core wasm module jco produced, gzipped (`gzip -9`, `mtime` 0). |
| `index.html` | The playground page that loads the above (optional for other consumers). |

All paths are bare file names relative to `manifest.json`: no `/`, no `..`.

## `manifest.json`

```json
{
  "format": 1,
  "package": "bigfix-relevance-analyzer",
  "version": "1.38.1",
  "editor": { "path": "editor.js", "size": 431003, "sha256": "<64 hex>" },
  "glue": { "path": "glue.mjs", "size": 777165, "sha256": "<64 hex>" },
  "cores": [
    {
      "name": "analyzer.core.wasm",
      "path": "analyzer.core.wasm.gz",
      "encoding": "gzip",
      "size": 1234567,
      "sha256": "<64 hex>",
      "raw_size": 4567890,
      "raw_sha256": "<64 hex>"
    }
  ]
}
```

- `format` is `1`. A consumer refuses any other value.
- `size` and `sha256` describe the file's bytes exactly as published (for a
  core, the gzipped bytes).
- `cores[].name` is the name the glue asks for: it builds each core's URL as
  `new URL("./<name>", import.meta.url)`. Every `analyzer.core*.wasm` name the
  glue mentions has exactly one entry, and no entry is unused.
- `cores[].encoding` is `"gzip"`, the only value in format 1.
- `cores[].raw_size` and `cores[].raw_sha256` describe the inflated wasm, so a
  core a server decompressed in transit can still be verified. Added within
  format 1; consumers check them when they are present and need them.

## Rules for consumers

- The glue asks for `<name>`, which is not a published file. Serve it from the
  matching `.gz` through a `fetch` intercept, inflated with
  `DecompressionStream("gzip")`, as `application/wasm`.
- Fetch `manifest.json` with `cache: "no-cache"` on every load. Treat the
  cached set as current only if the manifest text is identical; otherwise
  fetch every file again (also `cache: "no-cache"`) and replace the set
  together. Never mix files from two manifests.
- Verify every file by `sha256` before using or caching it, also where
  `crypto.subtle` is missing (insecure contexts, such as a Web Reports server
  on plain `http://`): use a JavaScript SHA-256 there (`loader.mjs` has one).
  On any mismatch, use none of the set.
- A server may decompress a `.gz` file in transit (`Content-Encoding: gzip`).
  Tell by the bytes: gzip starts `1f 8b`, wasm starts `00 61 73 6d`. Check a
  core that arrived inflated against `raw_size` and `raw_sha256`; without
  them it cannot be verified, so refuse it.
- Re-verify a cached set against its manifest before running it: browser
  storage is shared with every page on the origin.
- If a newer manifest's set fails to download or verify, keep using the
  cached set rather than nothing.

The canonical contract is `../SPLIT_ANALYZER.md`, from the producer's pull
request (jgstew/bigfix-relevance-analyzer#177); this copy records what the
Web Report's loader implements, and goes once that is merged.

## Rules for the producer

- Build all files from one build: the glue and cores must come from the same
  jco transpile.
- Write `manifest.json` last, so a mirror copied file by file never names
  files it does not have yet.
- Serve with `Access-Control-Allow-Origin: *` (GitHub Pages does), so other
  sites, such as Web Reports, can fetch the files.
