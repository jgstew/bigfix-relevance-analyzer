# The split analyzer set

This is the contract for the split analyzer set. It is the canonical copy:
consumers follow this file, and producer and consumer change together with it.
The set is the componentize-py analyzer (the same component, glue and editor
the single-file playground embeds) published as separate files in one flat
folder, so that a page can fetch the analyzer at run time and keep it in a
cache. A BigFix Web Reports custom report is the first such consumer. It was
fetching the whole single-file page and cutting the pieces out of it.

- **Producer:**
  [`componentize-py/build-playground/build_split.py`](componentize-py/build-playground/build_split.py),
  run by `.github/workflows/wasm-html.yaml`.
- **Reference consumer:** the folder's own `index.html`, built from
  [`componentize-py/build-playground/split_template.html`](componentize-py/build-playground/split_template.html).
- **Tests:** `tests/test_playground_split_analyzer.py` (producer) and
  [`componentize-py/browser-test/test_split_analyzer.mjs`](componentize-py/browser-test/test_split_analyzer.mjs)
  (`index.html` over HTTP).

The single-file page (`bigfix-relevance-analyzer-playground.html`) is
unchanged by all of this. It is still built, still a release asset and still
works offline. Its old URL stays in place.

## Where it is published

The folder is flat and always-latest, with no version folders. It is meant to
be served at `https://www.jgstew.com/files/analyzer/`. Each release replaces
the whole folder, and `manifest.json` says which version is there.

## The files

| File | What it is |
| --- | --- |
| `manifest.json` | The version, and the size and sha256 of every file below except `index.html`. |
| `editor.js` | The editor bundle (`editor-bundle/build.mjs`), unmodified. A classic script that publishes `window.playgroundEditor`. ASCII. |
| `glue.mjs` | jco's transpiled glue, esbuild-bundled (`dist/componentize/web/bundle.mjs`), unmodified. An ES module that publishes its namespace on `globalThis.__component`. |
| `analyzer.core.wasm.gz`, `analyzer.core2.wasm.gz`, ... | Each core wasm module from the same jco transpile, gzip level 9 with mtime 0 (the same bytes the single-file page embeds). jco decides how many there are. Today it is 14. |
| `index.html` | A playground page that loads the set from its own folder. It is not part of the manifest. |

Paths are bare file names, relative to `manifest.json`. They never contain `/`
or `..`.

## manifest.json

```json
{
  "format": 1,
  "package": "bigfix-relevance-analyzer",
  "version": "1.38.1",
  "editor": {"path": "editor.js", "size": 430967, "sha256": "<64 lowercase hex>"},
  "glue": {"path": "glue.mjs", "size": 785049, "sha256": "<64 lowercase hex>"},
  "cores": [
    {"name": "analyzer.core.wasm", "path": "analyzer.core.wasm.gz", "encoding": "gzip", "size": 6253802, "sha256": "<64 lowercase hex>"},
    {"name": "analyzer.core10.wasm", "path": "analyzer.core10.wasm.gz", "encoding": "gzip", "size": 86146, "sha256": "<64 lowercase hex>"}
  ]
}
```

The values above are illustrative. The real file is written with a two-space
indent and a trailing newline.

- `format` is `1`. A consumer that does not know the format refuses the set.
  It must not guess.
- `package` is always `"bigfix-relevance-analyzer"`.
- `version` is the package version (`pyproject.toml`), which is also what the
  component's `version()` export returns. The reference page refuses to boot if
  the two disagree.
- `editor` and `glue` each have `path`, `size` and `sha256`, in that order.
- `cores` has one entry per core module, sorted by `name`. Each entry has
  `name`, `path`, `encoding`, `size` and `sha256`, in that order. `name` is the
  file name the glue asks for (`analyzer.core4.wasm`), `path` is the published
  file (`analyzer.core4.wasm.gz`), and `encoding` is always `"gzip"`.
- `size` and `sha256` describe the bytes as published. For the cores, that
  means the gzipped bytes.
- Every `analyzer.core*.wasm` name the glue mentions has exactly one entry, and
  no entry goes unused. The build verifies this and fails otherwise.

## Producer rules

- The glue and the cores come from the same jco transpile (one `--work`
  directory).
- All inputs are read and validated before the folder is touched, so a failed
  build leaves the previous set as it was.
- The old `manifest.json` is removed first and the new one is written last,
  after every file it names. Files from an older set that this build did not
  write (a core jco no longer emits, say) are removed.
- Output is deterministic: unchanged input produces byte-identical files and a
  byte-identical zip.

## Consumer rules

1. Fetch `manifest.json` with `cache: "no-cache"` on every load.
2. A cached set (for example in IndexedDB) counts as current only if it was
   stored under a manifest whose text is identical to the manifest just
   fetched. Compare the text, not just `version`: a rebuild at the same
   version is a different set.
3. Fetch the files with `cache: "no-cache"`.
4. Never mix files from two manifests. If a file fails its size or sha256
   check, re-read `manifest.json` once. If it changed, the folder was replaced
   mid-load, so start over with the new manifest. If it did not change, the
   failure is real: refuse the set and say which file failed and why.
5. Check `size` and `sha256` on the published bytes only. sha256 needs
   `crypto.subtle`, which exists only in secure contexts (https, localhost).
   Elsewhere, check the size alone.
6. Accept a `.gz` that a server already decompressed in transit (sent with
   `Content-Encoding: gzip`, so the browser hands over wasm). Tell the two
   apart by magic bytes: gzip starts `1f 8b`, wasm starts `00 61 73 6d`.
   Anything else is refused. An already-inflated core cannot be checked against
   the manifest, because its published bytes never arrived.
7. Run the glue so that `import.meta.url` resolves the core names. The glue
   builds each core's URL as `new URL("./<name>", import.meta.url)` and fetches
   it. Serve those fetches from the verified bytes through a `window.fetch`
   intercept keyed on the last path segment: inflate gzip with
   `DecompressionStream("gzip")` and answer with `Content-Type:
   application/wasm`, so `WebAssembly.compileStreaming` accepts it. A blob: URL
   cannot resolve `./<name>`, so `index.html` runs the glue as an inline
   `<script type="module">`, which gives it the document's URL, as in the
   single-file page.
8. After the glue runs, `globalThis.__component` holds `$init` (a promise:
   await it before calling anything), `analyze(text) -> JSON string`,
   `version()`, `handle(message) -> JSON array string` (the language server),
   and `exitCode()`.

How `index.html` does it: it uses the browser's HTTP cache as its only cache.
It fetches everything with `no-cache`, so a reload costs one 304 per file. It
follows rules 4 to 7 as written, and if a file is refused it shows the reason
in place of the playground, with Analyze left disabled.

## How a release publishes it

`wasm-html.yaml` builds the folder into `playground/analyzer/`, and also builds
the same files as one flat zip, `bigfix-relevance-analyzer-analyzer.zip`, with
no directory inside it, fixed timestamps and `manifest.json` last. The zip is
uploaded as the artifact `bigfix-relevance-analyzer-analyzer`.
`tag_and_release.yaml` attaches the zip to the GitHub release, and the zip is
listed in the release's `SHA256SUMS.txt` like every other asset.

A site update workflow verifies it and unpacks it like this:

```bash
sha256sum -c --ignore-missing SHA256SUMS.txt
unzip -o bigfix-relevance-analyzer-analyzer.zip -d files/analyzer/
```

It then removes any file in `files/analyzer/` that the zip does not contain.
It can also check each manifest entry's `size` and `sha256` against the
unpacked files before committing.
