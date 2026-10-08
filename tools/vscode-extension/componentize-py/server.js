// The language server process: VS Code's Node, the WebAssembly component, and
// this pump between them.
//
// vscode-languageclient forks this file and speaks LSP to it over Node IPC
// (extension.js picks that transport). Each message goes to the component's
// `handle` export as JSON, and each message in the array it returns goes back.
// All protocol logic is inside the component -- the Python package's `Server`
// -- so this file knows no LSP beyond "a message has an id".

"use strict";

const { createRequire } = require("node:module");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { IPCMessageReader, IPCMessageWriter } = require("vscode-jsonrpc/node");

// Built by build-component/build_component.py, not committed.
const COMPONENT = path.join(__dirname, "dist", "component", "lsp.js");
const INTERNAL_ERROR = -32603;

/**
 * Take away what preview2-shim would otherwise hand the component.
 *
 * By default the shim preopens the host's root (every drive on Windows), so
 * the component could read and write any file this process can, and passes
 * through this process's environment variables, which can hold tokens and
 * credentials. The server lints the text it is sent: it opens no files and
 * reads no variables, so it gets neither. Network sockets are left as the
 * shim provides them; nothing uses them yet.
 *
 * Each shim module is resolved from the glue's own location, so this changes
 * the very module instances the glue imports; it must run before the glue
 * loads. Returns those modules, to report what the component can reach.
 */
async function sandbox() {
  const shim = (name) =>
    import(pathToFileURL(createRequire(COMPONENT).resolve(`@bytecodealliance/preview2-shim/${name}`)).href);
  const [filesystem, cli] = await Promise.all([shim("filesystem"), shim("cli")]);
  filesystem._clearPreopens();
  cli._setEnv({});
  return { filesystem, cli };
}

async function main() {
  const { filesystem, cli } = await sandbox();
  const component = await import(pathToFileURL(COMPONENT).href);
  const reader = new IPCMessageReader(process);
  const writer = new IPCMessageWriter(process);
  const directories = filesystem.preopens.getDirectories().map(([, guestPath]) => guestPath);
  const variables = cli.environment.getEnvironment().map(([name]) => name);
  const listed = (names) => (names.length ? names.join(", ") : "none");
  console.error(
    `bigfix-relevance-analyzer ${component.version()} (WebAssembly component; ` +
      `filesystem access: ${listed(directories)}; environment variables: ${listed(variables)})`
  );

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
