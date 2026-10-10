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
// This file says which files to send, when to start the server and how. Every
// protocol decision lives in Python.
//
// It activates at startup in every window, cheaply: the language client is
// loaded, and the server started, only once an open document passes gate.js.
// Markdown and HTML pass only with relevance in them, so a window without
// BigFix content never runs the ~170 MiB server process. ../python-stdio/ is the same extension
// with the server run from a local Python instead: PoC 1, kept for comparison.

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vscode = require("vscode");

const { needsServer } = require("./gate");
const { isBesXml } = require("./sniff");
const manifest = require("./package.json");
// Kept in step with the analyzer's recognized suffixes by
// tests/test_vscode_extension_layout.py.
const documentPatterns = require("./document-patterns.json");

const PREFIX = manifest.settingsPrefix;
// The language this extension contributes for whole-file relevance (.rel, .bsr).
// The server lints a buffer in it even with no file name: see LANGUAGE_ID in
// src/bigfix_relevance_analyzer/lsp/linter.py.
const LANGUAGE_ID = manifest.contributes.languages[0].id;
// The BES XML language, found by the suffix it takes rather than by position.
// The server reads a buffer in it as BES XML even with no `.bes` name: see
// BES_LANGUAGE_ID in lsp/linter.py. Missing, it costs BES buffers only: this
// runs as the file loads, where a throw would stop relevance checking too.
const BES_LANGUAGE_ID = manifest.contributes.languages.find((language) =>
  language.extensions?.includes(".bes")
)?.id;
const NAME = manifest.displayName;
const SERVER = path.join(__dirname, "server.js");
const COMPONENT = path.join(__dirname, "dist", "component", "lsp.js");

// Files by suffix, plus buffers by language, which is what brings an unsaved
// `untitled:` buffer to the server; it then lints it by its languageId.
// BES XML buffers are sent only as files or unsaved buffers: any other scheme
// would also lint the `git:` side of every `.bes` diff view. Relevance buffers
// are still sent whatever their scheme, which has the same cost for `.rel` and
// `.bsr` diffs; whether to scope them too, and to which schemes, is #134.
const DOCUMENT_SELECTOR = [
  ...documentPatterns.map((pattern) => ({ scheme: "file", pattern })),
  { language: LANGUAGE_ID },
  ...(BES_LANGUAGE_ID
    ? [
        { language: BES_LANGUAGE_ID, scheme: "file" },
        { language: BES_LANGUAGE_ID, scheme: "untitled" },
      ]
    : []),
];

/** @type {import("vscode-languageclient/node").LanguageClient | undefined} */
let client;
// Set once a document has passed the gate (or the restart command ran): from
// then on the server is kept running, and the gate is not consulted again.
let wanted = false;

function createClient() {
  // Here rather than at the top: loading the client is part of the cost the
  // gate defers.
  const { LanguageClient, TransportKind } = require("vscode-languageclient/node");
  const config = vscode.workspace.getConfiguration(PREFIX);
  const server = { module: SERVER, transport: TransportKind.ipc };
  const serverOptions = { run: server, debug: server };
  const clientOptions = {
    documentSelector: DOCUMENT_SELECTOR,
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

/** Start the server the first time a document the client would send passes the gate. */
function consider(document) {
  if (wanted || vscode.languages.match(DOCUMENT_SELECTOR, document) === 0) return;
  if (!needsServer(document)) return;
  wanted = true;
  restart();
}

// Languages VS Code itself gives a pasted fixlet: plaintext before anything,
// xml from the built-in XML language's `firstLine` (issue #132).
const SWITCH_FROM = new Set(["plaintext", "xml"]);
// Lines read to sniff: enough for any preamble sniff.js accepts before <BES.
const SNIFF_LINES = 200;
// Unsaved tabs already switched once, by URI, so a language picked afterwards
// sticks: VS Code never re-detects after an extension sets a language, and
// neither does this.
const decided = new Set();

/** Switch an unsaved tab holding BES XML to the BES language, at most once. */
function maybeSwitch(document) {
  if (!BES_LANGUAGE_ID || document.uri.scheme !== "untitled") return;
  const key = document.uri.toString();
  if (decided.has(key) || !SWITCH_FROM.has(document.languageId)) return;
  if (!vscode.workspace.getConfiguration(PREFIX).get("detectBesXml")) return;
  if (!isBesXml(document.getText(new vscode.Range(0, 0, SNIFF_LINES, 0)))) return;
  decided.add(key);
  // Arrives as a close and an open in the new language, which `consider` sees.
  vscode.languages.setTextDocumentLanguage(document, BES_LANGUAGE_ID).then(undefined, () => undefined);
}

/** Forget a tab once it has really closed: VS Code reuses `Untitled-N` names. */
function forget(document) {
  const key = document.uri.toString();
  if (!decided.has(key)) return;
  // A language change is a close and an open of the same URI in the same
  // tick, so only a URI still closed one tick later was really closed.
  setTimeout(() => {
    if (!vscode.workspace.textDocuments.some((open) => open.uri.toString() === key)) decided.delete(key);
  }, 0);
}

async function activate(context) {
  context.subscriptions.push(
    // Explicit, so it starts the server even where nothing has passed the gate.
    vscode.commands.registerCommand(`${PREFIX}.restartServer`, () => {
      wanted = true;
      return restart();
    }),
    // The limit is sent at `initialize`, so a change takes a new server; with
    // no server yet, the next one reads the new value anyway.
    vscode.workspace.onDidChangeConfiguration((event) =>
      wanted && event.affectsConfiguration(`${PREFIX}.maxDocumentBytes`) ? restart() : undefined
    ),
    vscode.workspace.onDidOpenTextDocument((document) => {
      maybeSwitch(document);
      consider(document);
    }),
    // Markdown or HTML can gain relevance as it is edited, and an unsaved tab
    // can gain a fixlet.
    vscode.workspace.onDidChangeTextDocument(({ document }) => {
      maybeSwitch(document);
      consider(document);
    }),
    vscode.workspace.onDidCloseTextDocument(forget)
  );
  for (const document of vscode.workspace.textDocuments) {
    maybeSwitch(document);
    consider(document);
  }
  // For tests (common/smoke/suite.js): whether the server has been started.
  return { serverRunning: () => client?.isRunning() ?? false };
}

function deactivate() {
  return client?.stop();
}

module.exports = { activate, deactivate };
