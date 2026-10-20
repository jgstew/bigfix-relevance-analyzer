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
| File size | ~45 KB | ~55 KB (the analyzer is fetched separately and cached) |

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
  carries only the core, and fetches the analyzer from the published
  playground page after it is usable, keeping it in the browser.

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

1. Build or take `relevance-debugger-webreport.html`.
2. In Web Reports, create a custom report and paste the file's contents as its
   HTML.
3. **Evaluate** works as soon as the page shows, in a plain text box. The
   analyzer follows: the first time, the browser downloads the playground page
   (~12 MB) from
   `https://www.jgstew.com/files/bigfix-relevance-analyzer-playground.html`;
   after that it comes from the browser's own storage. Then the editor
   replaces the text box, underlines problems as you type, and the analysis
   panel and dialect note catch up half a second after you stop typing.
   Evaluate runs the statement as session relevance.

Where the analyzer comes from is a list of URLs, tried in order
(`--analyzer-url`, repeatable; see [Building](#building)). Any page with the
playground's layout works, for example a copy on an internal web server for
sites without internet access. If none loads, the analysis panel says why, and
session relevance still works.

### Log and diagnostics

Both builds keep a log and a diagnostics panel folded away under **Log and
diagnostics** at the bottom. IE11 has no `<details>`: the core supplies the
folding there, and the styles set `display: block` on it, since IE11 lays out
unknown elements inline. Diagnostics record the browser engine, which BigFix
functions exist, load timings (server wait, download, when Evaluate and the
analyzer became ready), where the analyzer came from, and the shape of each
host reply, keyed by query. **Copy** puts it on the clipboard, for bug
reports.

## How it works

```
template.html -+- core.js              ES5 only; UI and every evaluation path, both targets
               +- analyzer_loader.html Web Report only: <script type="module"> that
               |                       fetches, caches and starts the analyzer
               +- build_poc.py         fills the template once per target
```

- **`core.js` is ES5 only** so it parses in IE11, where one `let` or arrow
  function would stop the whole script. `RDBG_BUILD.target` (`console` or
  `webreport`, set by the builder) picks the UI and the evaluation path;
  elements marked `data-only="console"` or `data-only="webreport"` are removed
  from the other target at load.
- **The analyzer loader** starts after the page's load event. It fetches the
  playground page and cuts out three pieces, each found by text that appears
  exactly once there: the editor bundle (after `Publishes
  window.playgroundEditor.`), the gzipped core wasm modules (`const CORES_GZIP
  = `), and the component glue jco generated for those cores (between the end
  of `async function boot()` and `// window.__wasmProblem was already
  handled`). Taking all three from one page keeps the glue and cores matched.
  It checks each piece and fails loudly if the playground's layout changes.
- **The pieces are cached in IndexedDB**, keyed by URL. Each load sends a HEAD
  request and downloads again only when `Last-Modified` changed (a header
  browsers expose cross-site); offline, the cached copy is used as is. GitHub
  Pages sends `access-control-allow-origin: *`, which makes the cross-site
  fetch possible.
- **Starting the analyzer** works like the playground's boot (see
  `../componentize-py/build-playground/template.html`): the editor bundle runs
  as a function, the glue as a module from a `blob:` URL, with its
  `import.meta.url` (which it uses only to name the cores) replaced by a
  placeholder base that a `fetch` intercept answers from the cached cores,
  inflated by `DecompressionStream`. Then `analyze()` feeds the analysis panel
  and `handle()` is the editor's language server. It calls
  `rdbg.onAnalyzer(...)` when ready, or `rdbg.onAnalyzerFailed(reason)`. IE
  skips module scripts entirely.
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

The builder needs only Python and this folder; the analyzer is fetched at
run time.

```bash
python3 tools/playground-wasm/dashboard-poc/build_poc.py --fake-hosts
```

`--analyzer-url URL` (repeatable) sets where the Web Report gets the
analyzer, tried in order; the default is the published playground page.
Outputs, in `playground/dashboard-poc/` (gitignored):

| File | What it is |
|---|---|
| `relevance-debugger-console.ojo` | The console dashboard. |
| `relevance-debugger-webreport.html` | The Web Report fragment to paste. |
| `relevance-debugger-<target>-page.html` | Each target as a whole page, for a plain browser. |
| `relevance-debugger-<target>-fake.html` | With `--fake-hosts`: the same, running against `fake_host.js`, a pretend console or Web Reports. Its Web Report takes the analyzer from the local playground build, `playground/bigfix-relevance-analyzer-component-playground.html` (`--fake-analyzer-url`). |

The builder fails if a placeholder is left over, if the page has characters
XML cannot carry, if it contains `<?relevance` (Web Reports would evaluate
it), if a script contains `</script` before its end, or if the `.ojo` does
not parse back to the same HTML.

### Checking a change

```bash
npx --yes acorn@8.14.0 --ecma5 --silent tools/playground-wasm/dashboard-poc/core.js
```

This catches anything in `core.js` that IE11 cannot parse. Then open the
`-fake.html` pages from a local web server (for example
`python3 -m http.server` at the repository root) and try both targets. The
fakes mimic the measured behavior: native values from `Relevance()`, one
string from the wrapper, errors for client inspectors in Web Reports, and a
FastQuery where one target fails and one never answers. `window.__fake`
records what the page sent.

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
  written as ANSI, so non-ASCII text in relevance may not survive.
- **The Web Report depends on the playground page's layout** and, for the
  first load of each analyzer version, on internet access from the browser.
  It runs code fetched from that URL inside the user's Web Reports session.
  Explicit start/end markers in the playground template, or a dedicated
  analyzer file published next to it, would make the extraction sturdier.
- **Not yet carried over from the debugger:** the answer tally (answers by
  how many computers gave them), the per-level breakdown, Fix all, and export.
- **Not in CI yet:** the ES5 parse check, Playwright runs against the fake
  hosts, and attaching the two outputs to releases next to the playground.
