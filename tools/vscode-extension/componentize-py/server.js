// The language server process: VS Code's Node, the WebAssembly component, and
// this pump between them.
//
// vscode-languageclient forks this file and speaks LSP to it over Node IPC
// (extension.js picks that transport). Each message goes to the component's
// `handle` export as JSON, and each message in the array it returns goes back.
// All protocol logic is inside the component -- the Python package's `Server`
// -- so this file knows no LSP beyond "a message has an id".

"use strict";

const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { IPCMessageReader, IPCMessageWriter } = require("vscode-jsonrpc/node");

// Built by build-component/build_component.py, not committed.
const COMPONENT = path.join(__dirname, "dist", "component", "lsp.js");
const INTERNAL_ERROR = -32603;

async function main() {
  const component = await import(pathToFileURL(COMPONENT).href);
  const reader = new IPCMessageReader(process);
  const writer = new IPCMessageWriter(process);
  console.error(`bigfix-relevance-analyzer ${component.version()} (WebAssembly component)`);

  // `handle` is synchronous, so messages are answered strictly in the order
  // they arrive, which is what the Python server assumes.
  reader.listen((message) => {
    let replies;
    try {
      replies = JSON.parse(component.handle(JSON.stringify(message)));
    } catch (error) {
      // The component traps rather than raises on a fault, and a trapped
      // instance cannot be trusted afterwards; let the client restart us.
      console.error(error);
      if (message.id === undefined) process.exit(1);
      // IPC writes are asynchronous: exit once the reply is sent, or it is lost.
      writer
        .write({ jsonrpc: "2.0", id: message.id, error: { code: INTERNAL_ERROR, message: String(error) } })
        .finally(() => process.exit(1));
      return;
    }
    for (const reply of replies) writer.write(reply);
    const code = component.exitCode();
    if (code !== undefined && code !== null) process.exit(code);
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
