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
// The language this extension contributes for whole-file relevance (.rel, .bsr).
// The server lints a buffer in it even with no file name: see LANGUAGE_ID in
// src/bigfix_relevance_analyzer/lsp/linter.py.
const LANGUAGE_ID = manifest.contributes.languages[0].id;
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
    // Files by suffix, plus any buffer in the relevance language whatever its
    // scheme: that is what brings an unsaved `untitled:` buffer to the server,
    // which then lints it by its languageId.
    documentSelector: [
      ...documentPatterns.map((pattern) => ({ scheme: "file", pattern })),
      { language: LANGUAGE_ID },
    ],
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

/** @type {Promise<void>} */
let restarting = Promise.resolve();

// Serialized: two overlapping restarts (the command and a settings change, say)
// would otherwise both create a client, and the first would never be stopped.
function restart() {
  restarting = restarting.then(async () => {
    if (client) {
      await client.stop().catch(() => undefined);
      client = undefined;
    }
    await start();
  });
  return restarting;
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
