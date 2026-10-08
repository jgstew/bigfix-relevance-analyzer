// "BigFix Relevance Developer": lint diagnostics for BigFix Relevance, with the
// analyzer built in. The language server is the Python package's own
// `Server` (src/bigfix_relevance_analyzer/lsp/), compiled with a CPython into a
// WebAssembly component, so nothing needs installing beyond VS Code.
//
// vscode-languageclient starts ./server.js as a separate Node process, using
// VS Code's own Node, and talks LSP to it over Node IPC. A separate process
// keeps a slow lint from freezing the editor. IPC rather than stdio means
// nothing the component writes to stdout can corrupt the protocol stream.
//
// This file only says which files to send and how to start the server. Every
// protocol decision lives in Python. ../python-stdio/ is the same extension
// with the server run from a local Python instead: PoC 1, kept for comparison.

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vscode = require("vscode");
const { LanguageClient, TransportKind } = require("vscode-languageclient/node");

const manifest = require("./package.json");
// Kept in step with the analyzer's recognized suffixes by
// tests/test_vscode_extension_layout.py.
const documentPatterns = require("./document-patterns.json");

const PREFIX = manifest.settingsPrefix;
const NAME = manifest.displayName;
const SERVER = path.join(__dirname, "server.js");
const COMPONENT = path.join(__dirname, "dist", "component", "lsp.js");

/** @type {LanguageClient | undefined} */
let client;

function createClient() {
  const config = vscode.workspace.getConfiguration(PREFIX);
  const server = { module: SERVER, transport: TransportKind.ipc };
  const serverOptions = { run: server, debug: server };
  const clientOptions = {
    // `file` only: the server picks the file type from the URI's suffix, so an
    // unsaved `untitled:` buffer has nothing for it to go on yet.
    documentSelector: documentPatterns.map((pattern) => ({ scheme: "file", pattern })),
    initializationOptions: { maxDocumentBytes: config.get("maxDocumentBytes") },
  };
  return new LanguageClient(PREFIX, NAME, serverOptions, clientOptions);
}

async function start() {
  if (!fs.existsSync(COMPONENT)) {
    // Only possible in a checkout: the component is a build output, not source.
    vscode.window.showErrorMessage(
      `${NAME}: the language server component has not been built. Run ` +
        "build-component/build_component.py (see tools/vscode-extension/README.md)."
    );
    return;
  }
  client = createClient();
  try {
    await client.start();
  } catch (error) {
    vscode.window.showErrorMessage(`${NAME}: the language server failed to start: ${error?.message ?? error}`);
  }
}

async function restart() {
  if (client) {
    await client.stop().catch(() => undefined);
    client = undefined;
  }
  await start();
}

async function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand(`${PREFIX}.restartServer`, restart),
    // The limit is sent at `initialize`, so a change takes a new server.
    vscode.workspace.onDidChangeConfiguration((event) =>
      event.affectsConfiguration(`${PREFIX}.maxDocumentBytes`) ? restart() : undefined
    )
  );
  await start();
}

function deactivate() {
  return client?.stop();
}

module.exports = { activate, deactivate };
