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
be served at `https://www.jgstew.com/files/analyzer/`, with each release
replacing the whole folder and `manifest.json` saying which version is there.
The site side of that is not in place yet: see "How a release publishes it"
below.

## The files

| File | What it is |
| --- | --- |
| `manifest.json` | The version, and the size and sha256 of every file below except `index.html` (plus each core's inflated `raw_size` and `raw_sha256`). |
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
    {"name": "analyzer.core.wasm", "path": "analyzer.core.wasm.gz", "encoding": "gzip", "size": 6253802, "sha256": "<64 lowercase hex>", "raw_size": 15868983, "raw_sha256": "<64 lowercase hex>"},
    {"name": "analyzer.core10.wasm", "path": "analyzer.core10.wasm.gz", "encoding": "gzip", "size": 86146, "sha256": "<64 lowercase hex>", "raw_size": 336472, "raw_sha256": "<64 lowercase hex>"}
  ]
}
```

The values above are illustrative. The real file is written with a two-space
indent and a trailing newline.

- `format` is `1`. A consumer that does not know the format refuses the set.
  It must not guess. `raw_size` and `raw_sha256` were added within format 1,
  before any set was published, so every format 1 manifest has them.
- `package` is always `"bigfix-relevance-analyzer"`.
- `version` is the version of the wheel that was actually transpiled. It is read
  from the `.dist-info` that `componentize.py` staged, which is the same
  metadata the component's `version()` export reads, so the two always agree.
  Comparing the two is optional for a consumer. The reference page does compare them and refuses to boot if they
  disagree.
- `editor` and `glue` each have `path`, `size` and `sha256`, in that order.
- `cores` has one entry per core module, sorted by `name`. Each entry has
  `name`, `path`, `encoding`, `size`, `sha256`, `raw_size` and `raw_sha256`, in
  that order. `name` is the file name the glue asks for (`analyzer.core4.wasm`),
  `path` is the published file (`analyzer.core4.wasm.gz`), and `encoding` is
  always `"gzip"`.
- `size` and `sha256` describe the bytes as published. For the cores, that
  means the gzipped bytes. A core's `raw_size` and `raw_sha256` describe the
  inflated wasm: what a consumer receives when a server decompressed the `.gz`
  in transit.
- Every `analyzer.core*.wasm` name the glue mentions has exactly one entry, and
  no entry goes unused. The build verifies this and fails otherwise.

## Producer rules

- The glue and the cores come from the same jco transpile (one `--work`
  directory).
- The glue uses `import.meta` only as the literal text `import.meta.url`, at
  least once and in no other form (no `import.meta.resolve`, no bare
  `import.meta`). Consumers that run the glue from a blob: URL rely on
  replacing that text, so the build fails if this does not hold.
- `version` comes from the staged wheel's metadata, not from `pyproject.toml`.
  The build fails unless there is exactly one staged
  `bigfix_relevance_analyzer-*.dist-info`.
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
4. Never mix files from two manifests. If any file fails to fetch (an HTTP or
   network error) or fails its checks, re-read `manifest.json` once. If it
   changed, the folder was replaced mid-load, so start over with the new
   manifest. If it did not change, the failure is real: refuse the set and say
   which file failed and why.
5. Verify every file by size and sha256 before using it or caching it. There
   is no size-only mode. `crypto.subtle` exists only in secure contexts
   (https, localhost), so a consumer that can run anywhere else (plain http, as
   in a Web Reports deployment) must carry a JS SHA-256 to fall back on.
   `index.html` has one.
6. Check what was received against the matching fields. A file as published is
   checked against `size` and `sha256`. A server may also have decompressed a
   `.gz` in transit (sent it with `Content-Encoding: gzip`, so the browser
   hands over wasm). Tell the two apart by magic bytes: gzip starts `1f 8b`,
   wasm starts `00 61 73 6d`. Check a core that arrived as wasm against
   `raw_size` and `raw_sha256`. Refuse anything that is neither.
7. Run the glue so that its core URLs reach your fetch intercept. The glue
   builds each core's URL as `new URL("./<name>", import.meta.url)` and fetches
   it. Serve those fetches from the verified bytes through a `window.fetch`
   intercept keyed on the last path segment: inflate gzip with
   `DecompressionStream("gzip")` and answer with `Content-Type:
   application/wasm`, so `WebAssembly.compileStreaming` accepts it. Either of
   these is valid:
   - Run the glue text as an inline `<script type="module">`, so
     `import.meta.url` is the document's URL and `./<name>` resolves normally.
     `index.html` does this, as the single-file page does.
   - Run it from a blob: URL after replacing `import.meta.url` in the text
     with a placeholder base URL that the intercept answers by core name. A
     blob: URL alone cannot resolve `./<name>`, so the replacement is required
     in this case. The Web Reports loader does this.
8. After the glue runs, `globalThis.__component` holds `$init` (a promise:
   await it before calling anything), `analyze(text) -> JSON string`,
   `version()`, `handle(message) -> JSON array string` (the language server),
   and `exitCode()`.

9. A consumer that keeps its own cache may reuse a cached file instead of
   downloading it when a new manifest arrives, if the file's entry in the
   manifest it was cached under has the same `sha256` as its entry in the new
   manifest (and, for a core cached as inflated wasm, the same `raw_sha256`).
   Rehash reused bytes against the new manifest where that is cheap
   (`crypto.subtle`). Where only a JS SHA-256 is available, a consumer may
   instead trust them after checking their size, because they were checked
   against that same hash when they downloaded: this is an explicit
   exception to rule 5, for bytes from the consumer's own cache only. Rules
   4 and 6 still apply to the new set as a whole. Producers need nothing for this: an
   unchanged core keeps its bytes because it is gzipped with level 9 and
   mtime 0.

How the Web Reports loader does it: it follows rules 1 to 3 and 6 to 9, with
two differences. Rule 4: it refuses a set that fails, but does not re-read
the manifest; it keeps the older cached set if it has one, or tries its next
configured source. Rule 5: everything it downloads is checked by size and
sha256, but without `crypto.subtle` (plain http) it does not hash its own
cached bytes again: an unchanged cached set is used as is, and reused files
are checked by size only (rule 9's exception). It also has a
consumer-side safety net that the contract does not need: a set that checks
out but does not start is downloaded once more, then recorded against that
manifest's text so it is not downloaded again in that browser (see
`dashboard-poc/README.md`).

How `index.html` does it: it uses the browser's HTTP cache as its only cache
and persists nothing itself. It fetches everything with `no-cache`, so a
reload costs one 304 per file. It follows rules 1 and 3 to 8; rules 2 and 9 do not
apply, since it keeps no cache of its own. For rule 7 it uses the inline module
script. It uses `crypto.subtle` where it exists and its own JS SHA-256
elsewhere. If the set is refused, it shows the reason in place of the
playground, with Analyze left disabled. It also refuses to boot if
`component.version()` differs from the manifest's `version`.

## How a release publishes it

`wasm-html.yaml` builds the folder into `playground/analyzer/`, and also builds
the same files as one flat zip, `bigfix-relevance-analyzer-web.zip`, with
no directory inside it, fixed timestamps and `manifest.json` last. The zip is
uploaded as the artifact `bigfix-relevance-analyzer-web`. Releases up to
1.39.0 named it `bigfix-relevance-analyzer-analyzer.zip`; the site's
publishing script accepts both.
`tag_and_release.yaml` attaches the zip to the GitHub release, and the zip is
listed in the release's `SHA256SUMS.txt` like every other asset. Each line
there is `<sha256>  ./<asset>` (two spaces, then the asset name with a `./`
prefix), for example `<sha256>  ./bigfix-relevance-analyzer-web.zip`.

The site side is jgstew/jgstew.github.io#17, which is open and not merged yet.
Until it is merged, nothing publishes the set to `files/analyzer/`. A site
update workflow verifies it and unpacks it like this:

```bash
sha256sum -c --ignore-missing SHA256SUMS.txt
unzip -o bigfix-relevance-analyzer-web.zip -d files/analyzer/
```

It then removes any file in `files/analyzer/` that the zip does not contain.
It can also check each manifest entry's `size` and `sha256` against the
unpacked files before committing.
