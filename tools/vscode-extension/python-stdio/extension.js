// PoC 1 for issue #10: lint diagnostics in VS Code from `bigfix-relevance-lsp`,
// started as a child process over stdio from a Python on this machine.
//
// Deliberately thin. Every protocol decision lives in the Python server
// (src/bigfix_relevance_analyzer/lsp/), and vscode-languageclient speaks LSP to
// it, so this file only says which files to send and how to start the server.
// PoC 2 (../componentize-py/, planned) keeps all of that and changes only how
// the server is started.
//
// Plain CommonJS JavaScript rather than TypeScript, so there is no build step:
// VS Code loads this file as is.

"use strict";

const vscode = require("vscode");
const { LanguageClient, TransportKind } = require("vscode-languageclient/node");

const manifest = require("./package.json");
// Kept in step with the analyzer's recognized suffixes by
// tests/test_vscode_extension_layout.py.
const documentPatterns = require("./document-patterns.json");

// Every setting lives under this prefix, so PoC 1 and PoC 2 can be installed
// side by side. It is also the client id, which is how vscode-languageclient
// finds `<prefix>.trace.server`.
const PREFIX = manifest.settingsPrefix;
const NAME = "BigFix Relevance (Python stdio)";

/** @type {LanguageClient | undefined} */
let client;

function createClient() {
  const config = vscode.workspace.getConfiguration(PREFIX);
  const serverOptions = {
    command: config.get("server.command"),
    args: config.get("server.args"),
    transport: TransportKind.stdio,
  };
  const clientOptions = {
    // `file` only: the server picks the file type from the URI's suffix, so an
    // unsaved `untitled:` buffer has nothing for it to go on yet.
    documentSelector: documentPatterns.map((pattern) => ({ scheme: "file", pattern })),
    initializationOptions: { maxDocumentBytes: config.get("maxDocumentBytes") },
  };
  return new LanguageClient(PREFIX, NAME, serverOptions, clientOptions);
}

async function start() {
  client = createClient();
  try {
    await client.start();
  } catch (error) {
    const command = vscode.workspace.getConfiguration(PREFIX).get("server.command");
    const choice = await vscode.window.showErrorMessage(
      `${NAME}: could not start \`${command}\` (${error?.message ?? error}). ` +
        `Install bigfix-relevance-analyzer, or point ${PREFIX}.server.command at it.`,
      "Open Settings"
    );
    if (choice === "Open Settings") {
      await vscode.commands.executeCommand("workbench.action.openSettings", PREFIX);
    }
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
    // A changed command, argument or limit only takes effect in a new server.
    vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration(`${PREFIX}.server`) ||
          event.affectsConfiguration(`${PREFIX}.maxDocumentBytes`)) {
        return restart();
      }
      return undefined;
    })
  );
  await start();
}

function deactivate() {
  return client?.stop();
}

module.exports = { activate, deactivate };
