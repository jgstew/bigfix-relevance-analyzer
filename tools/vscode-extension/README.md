# VS Code extensions

Two ways to get the analyzer's language server
(`src/bigfix_relevance_analyzer/lsp/`) into VS Code. They sit side by side so
they can be compared. Background and measurements are in
[issue #10](https://github.com/jgstew/bigfix-relevance-analyzer/issues/10).

| | `componentize-py/`: **BigFix Relevance Developer** | `python-stdio/`: PoC 1 |
|---|---|---|
| Role | the primary extension | proof of concept, kept for comparison |
| Server runs as | the Python package's `Server`, compiled with a CPython into a WebAssembly component. `server.js` runs it in a Node process VS Code forks, over Node IPC. | a child process, `bigfix-relevance-lsp` over stdio |
| Needs on the user's machine | nothing beyond VS Code | Python with `bigfix-relevance-analyzer` installed |
| Settings | `bigfixRelevance.*` | `bigfixRelevancePython.*` |
| Status | working: the shared smoke test passes in VS Code 1.140.0 | working: the shared smoke test passes in VS Code 1.140.0 |

Both are proofs of concept: neither is packaged as a `.vsix` or published yet.

## The contract both share

Both extensions keep everything that decides behaviour in the Python package,
and differ only in how the server is started:

- **Which files:** `document-patterns.json`, one glob per suffix the extractor
  recognizes. The server picks the file type from the URI's suffix, so the two
  lists must agree. `tests/test_vscode_extension_layout.py` checks them against
  `extract._RECOGNIZED_SUFFIXES`.
- **What the server is told:** `initializationOptions.maxDocumentBytes`, the
  one option the server reads today (see `lsp/linter.py`).
- **Side by side:** each extension has its own `name` and puts every setting
  under its own `settingsPrefix` (a field of `package.json`), so both can be
  installed at once. The layout test checks that no two extensions share a
  setting. With both installed, each file gets each diagnostic twice, once
  from each.
- **One smoke test:** `common/smoke/` opens the same files in a real VS Code and
  checks the same diagnostics for either extension.
- **Supply chain:** the same rules as `tools/playground-wasm/`: exact pins, a
  lockfile, `min-release-age=7` in a per-package `.npmrc`, and a dependabot
  entry for each package.

## BigFix Relevance Developer (`componentize-py/`)

```bash
cd tools/vscode-extension/componentize-py && npm ci && cd -
uv run --group wasm python tools/vscode-extension/componentize-py/build-component/build_component.py
```

The second command builds this checkout's wheel and compiles it into
`dist/component/` (gitignored). It uses the playground's two-pass
`componentize.py`, then jco. It finishes by checking that the component boots
in Node and answers `initialize`. Rebuild after changing the Python package:
the extension runs the component, not the source.

Then open `tools/vscode-extension/componentize-py/` in VS Code and press F5
(*Run Extension*). That opens an Extension Development Host window with the
extension loaded. Open any `.bes`, `.rel` or relevance-fenced `.md` file there.

- `extension.js`: which files to send, and how to start the server.
- `server.js`: the server process. It passes each LSP message to the
  component's `handle` export and sends back what it returns.
- `build-component/`: the WIT world (`handle`, `exit-code`, `version`),
  the `app.py` that componentize-py compiles, and the build script.

- `test/server.test.mjs`: unit tests for the server process in plain Node,
  with no VS Code (`node --test test/server.test.mjs`, about a second). Set `EXTENSION_DIR`
  to test another copy, such as an unzipped `.vsix`.

### In CI

`.github/workflows/vscode-extension.yaml` builds the component, packages
`bigfix-relevance-developer.vsix` with `vsce`, runs the unit tests on the
unzipped package, and uploads it as the `bigfix-relevance-developer-vsix`
artifact. A second job runs the shared smoke test against that package in a
headless VS Code (`xvfb-run`). VS Code is downloaded at a pinned version and
checked against a pinned SHA-256.

To install a build: download the artifact, unzip it, and in VS Code run
**Extensions: Install from VSIX...** on the `.vsix`.

## PoC 1 (`python-stdio/`)

```bash
cd tools/vscode-extension/python-stdio && npm ci
```

Open the directory in VS Code and press F5. The server comes from
`bigfixRelevancePython.server.command`, which defaults to
`bigfix-relevance-lsp` on `PATH`. To run this checkout instead, set:

```json
{
  "bigfixRelevancePython.server.command": "uv",
  "bigfixRelevancePython.server.args": ["run", "--project", "/path/to/bigfix-relevance-analyzer", "bigfix-relevance-lsp"]
}
```

With a stdio transport, `vscode-languageclient` appends `--stdio` to the
server's arguments. `bigfix-relevance-lsp` accepts it for that reason. Before
it did, the server exited before `initialize`.

## The smoke test

```bash
node tools/vscode-extension/common/smoke/run.mjs tools/vscode-extension/componentize-py
node tools/vscode-extension/common/smoke/run.mjs tools/vscode-extension/python-stdio
```

Each run starts an isolated VS Code instance with the extension loaded. A
window opens briefly. Your own settings and extensions are not used. It opens
a broken `.rel` and a relevance-fenced `.md`, then checks the diagnostics,
including that a fenced statement's finding lands on its line in the document.

Either extension's `trace.server` setting set to `"verbose"` logs every LSP
message to its output channel.
