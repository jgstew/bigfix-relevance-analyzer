# Relevance Debugger: BigFix console dashboard and Web Report (proof of concept)

This proof of concept brings what
[bigfix-relevance-debugger](https://github.com/jgstew/bigfix-relevance-debugger)
does into BigFix itself: analyze a relevance statement and evaluate it, with no
Python, SSH or REST configuration. Both builds come from one template and one
script, and each fits what its host can actually do.

| | Console dashboard (`.ojo`) | Web Report |
|---|---|---|
| Analysis (lint, dialect, types; editor with hover and completion) | no | **yes** |
| Session relevance | **yes** | **yes**, always |
| Client relevance on this computer (`qna`) | **yes** | no |
| Client relevance with FastQuery | **yes** | no |
| File size | ~45 KB | ~65 KB (the analyzer is fetched separately and cached) |

The split follows from how each host renders pages, measured in a real
deployment (see [What we measured](#what-we-measured)):

- **The console renders dashboards in its IE11 engine**, even with
  `<meta http-equiv="X-UA-Compatible" content="IE=edge">`. IE11 has no
  WebAssembly, so the analyzer cannot run there. It does have ActiveX, so the
  dashboard can run the local client's `qna`, and the console's REST API gives
  it FastQuery.
- **Web Reports runs in the user's own browser**, so the analyzer (CPython
  compiled to WebAssembly, the same build as the
  [playground](https://www.jgstew.com/files/bigfix-relevance-analyzer-playground.html))
  runs there. Web Reports can only evaluate session relevance, so it always
  does, even when the analyzer says the statement is client relevance. It
  shows that warning first, but the dialect call can be wrong and a session
  error comes back at once.
- **Web Reports regenerates a custom report on every load**, so the report
  cannot be cached. With the analyzer embedded (12 MiB), the server took 19.4 s
  before sending the first byte, against 0.6 s of download. So the report
  carries only the core, and fetches the analyzer after it is usable, keeping
  it in the browser: from the split analyzer at
  `https://www.jgstew.com/files/analyzer/` ([SPLIT_ANALYZER.md](../SPLIT_ANALYZER.md)), or,
  until that is published, from the single-file playground page.

## Using it

### Console dashboard

1. Build (see [Building](#building)) or take `relevance-debugger-console.ojo`.
2. Add it to a custom site as a site file (do **not** tick "Send to clients"),
   then open it from the Dashboards menu. For a quick try without a site, the
   console's Debug menu has "Load Wizard".
3. Type relevance, pick **Run as** (Auto guesses from keywords; the console
   has no analyzer), and click **Evaluate** or press Ctrl+Enter.

Client relevance runs on:

- **This computer (qna):** the BigFix client on the machine running the
  console. Its path comes from the registry, falling back to the default
  install folders. The first run may show an ActiveX safety prompt, and a
  command window may flash briefly.
- **FastQuery:** 5 random computers that reported in the last hour by default
  (`ids of bes computers whose (last report time of it > now - 1 * hour)`),
  or the computer IDs you type. Answers appear as they arrive. It waits until
  every target has answered or for 90 seconds (the timeout box), checking
  often at first and then less often: 2 s apart, each gap 1.5x the last, up
  to 15 s, with the last check at the deadline. Computers that never answer
  are listed as "no answer"; partial results are normal. Cancel stops it, and
  so does clicking Evaluate again: a new query abandons the one in progress.

### Web Report

1. Build or take the Web Report, as either file:
   - `relevance-debugger-webreport.beswrpt`: put it in a BigFix site's server
     files (for example a repository site's `ServerFiles/`), and Web Reports
     picks it up from the site on its own, named "Relevance Debugger".
   - `relevance-debugger-webreport.html`: the same report as a bare fragment.
2. With the `.html`, create a custom report in Web Reports instead and paste
   the file's contents as its HTML.
3. **Evaluate** works as soon as the page shows, in a plain text box. The
   analyzer follows: the first time, the browser downloads it (~12 MB); after
   that it comes from the browser's own storage, and each load only checks
   whether it changed. Then the editor replaces the text box, underlines
   problems as you type, and the analysis panel and dialect note catch up half
   a second after you stop typing. Evaluate runs the statement as session
   relevance.

Where the analyzer comes from is a list of URLs, tried in order
(`--analyzer-url`, repeatable; see [Building](#building)). The default:

1. `https://www.jgstew.com/files/analyzer/manifest.json`: the split analyzer
   ([SPLIT_ANALYZER.md](../SPLIT_ANALYZER.md)). Each load fetches only this small file; the
   rest downloads again only when it changes.
2. `https://www.jgstew.com/files/bigfix-relevance-analyzer-playground.html`:
   the single-file playground page, which stays in place (no longer updated)
   while reports move to the manifest. Each load sends a HEAD request and
   downloads again only when its `Last-Modified` changes.

A URL ending in `.json` is taken as a manifest, anything else as a
single-file page; relative URLs resolve against the report. A copy of either
on an internal web server works for sites without internet access. If none
loads, the analysis panel says why, and session relevance still works.

When a new analyzer version is published, only the files that changed
download; the rest come from the browser's copy (between 1.38.1 and 1.39.0,
12 of the 14 cores were identical).

If a downloaded and checked analyzer does not start in this browser, the
report tries once more with a fresh copy. If that fails too, it remembers that
this version does not start here, says so in the analysis panel, and does not
download or try it again until a new version is published. **Reload the
analyzer**, under Log and diagnostics, forgets the browser's copy and that
note, then loads the analyzer again without reloading the page: use it once
whatever stopped the analyzer is fixed.

### Log and diagnostics

Both builds keep a log and a diagnostics panel folded away under **Log and
diagnostics** at the bottom. IE11 has no `<details>`: the core supplies the
folding there, and the styles set `display: block` on it, since IE11 lays out
unknown elements inline. Diagnostics record the browser engine, which BigFix
functions exist, load timings (server wait, download, when Evaluate and the
analyzer became ready), where the analyzer came from, and the shape of each
host reply, keyed by query. **Copy** puts it on the clipboard, for bug
reports. The Web Report also has **Reload the analyzer** there (see above).

## How it works

```
template.html -+- core.js              ES5 only; UI and every evaluation path, both targets
               +- analyzer_loader.html Web Report only: <script type="module"> that
               |  |                    caches (IndexedDB) and starts the analyzer
               |  +- loader.mjs        where the analyzer comes from: manifest or page
               +- build_poc.py         fills the template once per target
```

- **`core.js` is ES5 only** so it parses in IE11, where one `let` or arrow
  function would stop the whole script. `RDBG_BUILD.target` (`console` or
  `webreport`, set by the builder) picks the UI and the evaluation path;
  elements marked `data-only="console"` or `data-only="webreport"` are removed
  from the other target at load.
- **The analyzer loader** starts after the page's load event and gets three
  pieces: the editor bundle, the component glue jco generated, and the gzipped
  core wasm modules that glue loads. `loader.mjs` holds the logic, with
  `fetch`, the cache and `crypto.subtle` passed in so Node tests can drive it.
  - From a **manifest** ([SPLIT_ANALYZER.md](../SPLIT_ANALYZER.md)): it fetches
    `manifest.json` (`cache: "no-cache"`) and, unless its text is identical
    to the cached one, every file it names. It checks each file's size and
    sha256 (or, for a core a server decompressed in transit, `raw_size` and
    `raw_sha256`), and that the cores are exactly the ones the glue loads. A mismatch rejects
    the whole set, so files from two versions never mix. Every file's sha256
    is checked before it is used or cached; without `crypto.subtle` (plain
    http) a JavaScript SHA-256 does it, ~150 ms for the 9 MB set on an Apple
    M1 Pro against ~5 ms with `crypto.subtle`. So a cached set is checked
    again on each load only where `crypto.subtle` exists.
  - **A new manifest reuses unchanged files.** A file whose entry in the
    cached set's (older) manifest has the same sha256 as in the new one is
    taken from the cache instead of downloaded (for a core cached as plain
    wasm, `raw_sha256` must match too). With `crypto.subtle` the reused bytes
    are hashed again against the new manifest, and a mismatch is downloaded;
    without it they are trusted, as they were checked against that same hash
    when they downloaded (the same trust as a cached reopen there). The new
    set is then checked and cached whole as before, so versions never mix.
    The diagnostics say how many files downloaded and how many were reused.
  - From the **single-file page**: it cuts the three pieces out, each found by
    text that appears exactly once there (after `Publishes
    window.playgroundEditor.`, at `const CORES_GZIP = `, and between the end
    of `async function boot()` and `// window.__wasmProblem was already
    handled`), failing loudly if that layout changes.
- **The pieces are cached in IndexedDB**, keyed by source (`manifest:<url>`,
  `page:<url>`), and used as is when the source is unreachable. GitHub Pages sends
  `access-control-allow-origin: *`, which makes the cross-site fetches
  possible.
- **Starting the analyzer** works like the playground's boot (see
  `../componentize-py/build-playground/template.html`): the editor bundle runs
  as a function, the glue as a module from a `blob:` URL, with its
  `import.meta.url` (which it uses only to name the cores) replaced by a
  placeholder base that a `fetch` intercept answers from the cached cores,
  inflated by `DecompressionStream` (or served as is, if a server already
  decompressed them in transit). Then `analyze()` feeds the analysis panel
  and `handle()` is the editor's language server. It calls
  `rdbg.onAnalyzer(...)` when ready, or `rdbg.onAnalyzerFailed(reason)`. IE
  skips module scripts entirely.
- **A set that checks out but does not start** (the editor bundle or glue
  throws, or `$init` rejects) goes through `loadAndStart()`'s safety net in
  `loader.mjs`; `analyzer_loader.html` only supplies `start(pieces)`.
  - A cached set gets one more chance, once per set and browser: it is
    dropped from the cache and downloaded afresh, then started again. Which
    set had that retry is kept under `retried:<cache key>`, so a set that
    fails now and then is recorded the next time it fails from the cache,
    not downloaded again on every such load.
  - A set that does not start after that, or that was freshly downloaded in
    the first place, is recorded in IndexedDB under `nostart:<cache key>`,
    with the sha256 of its manifest's text (the single-file page: its
    `Last-Modified`), the error and the time. A later load that finds the same
    manifest stops there, before downloading or starting anything, and shows
    the recorded error (and, if a newer manifest failed to download, that
    too). A changed manifest (a new release) is tried again.
  - The single-file page, if HEAD sends no `Last-Modified`: the GET carries
    `If-Modified-Since` with the recorded one, and a 304 counts as the same
    page. Cross-origin, that header needs a CORS preflight; if the server
    refuses it, the page downloads and is refused after the download.
  - So a browser where the analyzer cannot run costs at most one extra
    download of each release's set, never a loop. A set built partly from
    reused files counts as cached here, so for it the worst case is that
    partial download plus one full one. Network and checksum failures are
    handled before this (other sources, the cached set) and never recorded.
  - **Reload the analyzer** (`forgetAnalyzer()`) deletes the cached sets,
    records and retry notes of the configured sources, then runs the load and
    start again; `core.js` puts the editor's text back in the plain text box
    meanwhile. It is disabled while a load runs, and the loader runs one load
    at a time (a click that gets through is ignored). A Reload that never
    ends gives up after 5 minutes, as the first load does.
- **Session relevance** goes through the page's `Relevance(query, {success,
  failure})` (async), falling back to `EvaluateRelevance(query)` (sync). Both
  hosts return native values (a boolean, a `Date` for a time), so the query is
  sent as `concatenation "<~rdbg~>" of ((it as string) of (QUERY))` and split
  back into answers. If a type has no string cast, the query is sent as
  written instead: its answers are the host's values, and its error, if any,
  is the query's own.
- **qna** gets the query through a temp file on stdin, never on a command line
  (`cmd /c ""qna.exe" -t -showtypes < in > out 2>&1"`), so cmd metacharacters
  in relevance are harmless and large output cannot stall the pipe. The page
  polls the process with `setTimeout` rather than busy-waiting, then parses
  the `A:`/`E:`/`T:`/`I:` lines.
- **FastQuery** uses the console's `API.Post("clientquery", xml, cb)` with the
  query XML-escaped and `<ComputerID>` targets, then polls
  `API.Get("clientqueryresults/{id}?output=json", cb)` with the backoff above.
  Results are cumulative and there is no "done" flag, so it waits for every
  target or the timeout.
- **Each run has its own cancel token.** Its callbacks check it, so an
  abandoned run's late replies are dropped instead of landing in the next
  run's results.

## Building

The builder needs only Python 3.11 or later and this folder; the analyzer is fetched at
run time.

```bash
python3 tools/playground-wasm/dashboard-poc/build_poc.py --fake-hosts
```

`--analyzer-url URL` (repeatable) sets where the Web Report gets the
analyzer, tried in order; the default is the published manifest, then the
single-file playground page.
Outputs, in `playground/dashboard-poc/` (gitignored):

| File | What it is |
|---|---|
| `relevance-debugger-console.ojo` | The console dashboard. |
| `relevance-debugger-webreport.beswrpt` | The Web Report as `<BESWebReport>` XML (Name `Relevance Debugger`, Type `CustomReport`, Source `JGStew`, the report in `<Data>`), for a site's server files. |
| `relevance-debugger-webreport.html` | The same Web Report as a fragment to paste into a custom report. |
| `relevance-debugger-<target>-page.html` | Each target as a whole page, for a plain browser. |
| `relevance-debugger-<target>-fake.html` | With `--fake-hosts`: the same, running against `fake_host.js`, a pretend console or Web Reports. Its Web Report takes the analyzer from `analyzer/manifest.json` next to it (a split set `test_reports.mjs` makes), then the local playground build, `playground/bigfix-relevance-analyzer-component-playground.html` (`--fake-analyzer-url`). |

The builder fails if a placeholder is left over, if the page has characters
XML cannot carry, if it contains `<?relevance` (Web Reports would evaluate
it), if a script contains `</script` before its end, or if the `.ojo` or
`.beswrpt` does not parse back to the same HTML.

### Tests

From `tools/playground-wasm/dashboard-poc/`, after `npm ci`:

| Command | What it checks |
|---|---|
| `npm run test:es5` | `core.js` parses as ES5, so nothing in it can stop the script in IE11. |
| `npm run test:unit` | `test_loader.mjs`, `test_manifest.mjs` and `test_resilience.mjs` (`node --test`, no browser): extraction from the single-file page, the manifest contract, both caches, checksums, fallbacks, the does-not-start safety net and its records, `forgetAnalyzer()`, and reusing unchanged files. |
| `npm run test:browser` | `test_reports.mjs` (Playwright): the built `-fake.html` pages in Chromium. Needs `build_poc.py --fake-hosts` and the local component playground build first. |

The browser tests serve the repository root over HTTP and make a split set
from the local playground (`split_fixture.mjs`), standing in for the real one
until it is published. With `SPLIT_ANALYZER_DIR` set to a real build of the
set (the analyzer build's `playground/analyzer/`), they copy and use that
instead. They cover: Evaluate before the analyzer arrives, a
first load then a cached reload that fetches only the manifest, falling back
to the single-file page, an unreachable analyzer, folded diagnostics,
FastQuery's backoff and live rows, and a new Evaluate abandoning a running
FastQuery. For the safety net they publish a variant set through the test
server's overrides (a glue that throws until the test sets a flag) and check
the one retry, the unavailable message, that reopening downloads nothing, and
that Reload the analyzer recovers once the flag is set; also that Reload with
the analyzer running keeps the text, and that a new manifest with only a new
glue fetches only the manifest and the glue. The fakes mimic the measured behavior: native values from
`Relevance()`, one string from the wrapper, errors for client inspectors in
Web Reports, and a FastQuery where one target fails and one never answers.
`window.__fake` records what the page sent.

CI runs all three in `.github/workflows/wasm-html.yaml`'s `dashboard-poc`
job, against the component playground that workflow builds.

## What we measured

From a real BigFix console and Web Reports, October 2026:

| | Console dashboard | Web Reports |
|---|---|---|
| Engine | IE11 (`Trident/7.0`, `documentMode` 11) despite `IE=edge` | the user's browser (Chrome 155) |
| WebAssembly / DecompressionStream | no / no | yes / yes |
| ActiveX | yes (`WScript.Shell`, `Scripting.FileSystemObject`) | no |
| `Relevance()` / `EvaluateRelevance()` | both | both |
| `API.Post` / `API.Get` | yes | no |
| `Relevance()` success value | native (`false`, `Date`, ...) | native; empty string for no answers |
| `Relevance()` failure value | | a string |
| qna output on stdin | `Q: A: <answer>`, `T: <n>`, `I: <type>` | |
| `location` | `about://` | the Web Reports server |
| ~12 MiB page | imported and loaded | saved and loaded, but 19.4 s server time before the first byte (0.6 s download, 0.13 s analyzer start); not cached between loads |
| Small report, analyzer fetched | | 0.06 s server time, Evaluate usable at 0.36 s; first load fetched the published playground (11.7 MB) in 0.55 s, analyzer ready at 2.1 s |
| Small report, reopened | | 0.07 s server time, Evaluate usable at 0.35 s; analyzer from the IndexedDB cache (HEAD request only), ready at 0.83 s |

## Limits and next steps

- **Console dialect is a keyword guess.** The console has no analyzer, so
  Auto runs both dialects when the keywords don't settle it. The Run as picker
  overrides it.
- **"Valid in either dialect" is common.** The analyzer resolves statements
  like `name of operating system` and `now` as valid in both dialects. The
  debugger breaks that tie by type-checking each dialect (`dialect_fit` in its
  `upstream/relevance_analyzer.py`), which the component does not expose yet.
  Moving `dialect_fit` into the analyzer and adding a WIT export would let the
  Web Report tell the user more precisely.
- **qna needs a BigFix client on the console machine**, and the relevance is
  flattened to one line (qna reads one query per line). The temp file is
  written as ANSI, so relevance with characters outside the console
  machine's code page fails with a message saying so. Cancel and the timeout
  end qna's whole process tree (`taskkill /T`), not just `cmd.exe`.
- **The Web Report needs internet access** from the browser for the first
  load of each analyzer version, and runs code fetched from jgstew.com inside
  the user's Web Reports session. The fallback to the single-file page also
  depends on that page's layout; once every report uses the manifest, the old
  page can become a redirect and the fallback can go.
- **Not yet carried over from the debugger:** the answer tally (answers by
  how many computers gave them), the per-level breakdown, Fix all, and export.
- **A "does not start" record outlives a fix in the browser** (an extension,
  a policy, memory) until the next release or Reload the analyzer: that is
  the price of never looping. For the single-file page served without any
  `Last-Modified`, only Reload the analyzer clears it.
- **Not released yet:** the two outputs are built and tested in CI but not
  attached to releases next to the playground.
- **Not tested on a real console here:** the qna path (ActiveX) runs only in
  the console's IE11 engine, so its process handling and file cleanup are
  checked by reading, and by the measurements above, not by CI.
