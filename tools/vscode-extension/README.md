# VS Code extension proofs of concept

Two ways to get the analyzer's language server
(`src/bigfix_relevance_analyzer/lsp/`) into VS Code. They sit side by side so
they can be compared. Background and measurements are in
[issue #10](https://github.com/jgstew/bigfix-relevance-analyzer/issues/10).

| | `python-stdio/` (PoC 1) | `componentize-py/` (PoC 2, planned) |
|---|---|---|
| Server runs as | a child process: `bigfix-relevance-lsp` over stdio | a WebAssembly component inside the extension's own Node host |
| Needs on the user's machine | Python with `bigfix-relevance-analyzer` installed | nothing beyond VS Code |
| Ships | ~3.5 MB of JavaScript, ~0.5 MB gzip (measured) | that, plus the component: ~22 MiB, ~8 MiB gzip (issue #10 spike) |
| Status | working: `smoke/run.mjs` passes in VS Code 1.140.0 | not started |

## The contract both share

Both extensions keep everything that decides behaviour in the Python package,
and differ only in how the server is started:

- **Which files:** `document-patterns.json`, one glob per suffix the extractor
  recognizes. The server picks the file type from the URI's suffix, so the two
  lists must agree. `tests/test_vscode_extension_layout.py` checks them against
  `extract._RECOGNIZED_SUFFIXES`.
- **How the server is started:** a stdio transport makes `vscode-languageclient`
  append `--stdio` to the server's arguments. `bigfix-relevance-lsp` accepts it
  for that reason. Before it did, the server exited before `initialize`.
- **What the server is told:** `initializationOptions.maxDocumentBytes`, the
  one option the server reads today (see `lsp/linter.py`).
- **Side by side:** each extension has its own `name` and puts every setting
  under its own `settingsPrefix` (a field of `package.json`). PoC 1 uses
  `bigfixRelevancePython.*`, so both can be installed at once. The layout test
  checks that no two extensions share a setting.
- **Supply chain:** the same rules as `tools/playground-wasm/`: exact pins, a
  lockfile, `min-release-age=7` in a per-package `.npmrc`, and a dependabot
  entry for each package.

## Trying PoC 1

```bash
cd tools/vscode-extension/python-stdio && npm ci
```

Then open `tools/vscode-extension/python-stdio/` in VS Code and press F5
(*Run Extension*). That opens an Extension Development Host window with the
extension loaded. Open any `.bes`, `.rel` or relevance-fenced `.md` file there.

The server comes from `bigfixRelevancePython.server.command`, which defaults to
`bigfix-relevance-lsp` on `PATH`. To run this checkout instead, set:

```json
{
  "bigfixRelevancePython.server.command": "uv",
  "bigfixRelevancePython.server.args": ["run", "--project", "/path/to/bigfix-relevance-analyzer", "bigfix-relevance-lsp"]
}
```

`bigfixRelevancePython.trace.server: "verbose"` logs every LSP message to the
extension's output channel.

`python-stdio/smoke/` runs the same check without a person, in an isolated VS
Code instance. See that directory's `run.mjs`.
