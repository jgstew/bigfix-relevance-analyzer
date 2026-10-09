// Unit tests for server.js and the component behind it, in plain Node: no VS
// Code. Run with `node --test test/server.test.mjs` (name the file: Node 22
// does not accept a directory here).
//
// Each test forks server.js with Node IPC, exactly as vscode-languageclient
// does for this extension's `TransportKind.ipc`, and exchanges raw LSP message
// objects with it. That covers the process, the component inside it and the
// exit codes, in a couple of seconds.
//
// EXTENSION_DIR picks which copy to test. It defaults to this source tree
// (after build-component/build_component.py), and CI points it at the
// unzipped .vsix, so the tests also check what is actually packaged.

import assert from "node:assert/strict";
import { fork } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const EXTENSION = resolve(
  process.env.EXTENSION_DIR ?? join(dirname(fileURLToPath(import.meta.url)), "..")
);
const BROKEN = 'exists file "unterminated';

/** A forked server.js, with helpers to talk to it and wait for it. */
function startServer() {
  const child = fork(join(EXTENSION, "server.js"), ["--node-ipc"], {
    stdio: ["ignore", "ignore", "pipe", "ipc"],
  });
  const received = [];
  const waiters = [];
  let stderr = "";
  child.stderr.on("data", (chunk) => (stderr += chunk));
  child.on("message", (message) => {
    received.push(message);
    for (const waiter of [...waiters]) waiter();
  });
  let exitCode;
  const exited = new Promise((resolveExit) =>
    child.on("exit", (code) => {
      exitCode = code;
      for (const waiter of [...waiters]) waiter();
      resolveExit(code);
    })
  );

  /** The first received message `match` accepts, waiting up to 30 s for it. */
  function next(match) {
    return new Promise((resolveMessage, reject) => {
      const timer = setTimeout(
        () => reject(new Error(`timed out; received ${JSON.stringify(received)}; stderr: ${stderr}`)),
        30_000
      );
      const check = () => {
        const index = received.findIndex(match);
        if (index === -1 && exitCode === undefined) return;
        clearTimeout(timer);
        waiters.splice(waiters.indexOf(check), 1);
        if (index === -1) {
          // A dead server will never answer: fail now, with what it said.
          reject(new Error(`server exited with ${exitCode} before answering; stderr: ${stderr}`));
        } else {
          resolveMessage(received.splice(index, 1)[0]);
        }
      };
      waiters.push(check);
      check();
    });
  }
  const send = (message) => child.send({ jsonrpc: "2.0", ...message });
  return { child, send, next, exited, stderr: () => stderr };
}

async function initialized(server) {
  server.send({ id: 1, method: "initialize", params: { processId: null, rootUri: null, capabilities: {} } });
  const response = await server.next((m) => m.id === 1);
  server.send({ method: "initialized", params: {} });
  return response;
}

test("the packaged extension holds the server, the component and its runtime", () => {
  for (const path of [
    "extension.js",
    "gate.js",
    "server-gate.json",
    "server.js",
    "document-patterns.json",
    "dist/component/lsp.js",
    "dist/component/lsp.core.wasm",
    "node_modules/vscode-languageclient/package.json",
    "node_modules/@bytecodealliance/preview2-shim/package.json",
  ]) {
    assert.ok(existsSync(join(EXTENSION, path)), `missing ${path}`);
  }
});

test("initialize answers with the analyzer's server info", async (t) => {
  const server = startServer();
  t.after(() => server.child.kill());
  const response = await initialized(server);
  assert.equal(response.result.serverInfo.name, "bigfix-relevance-analyzer");
  assert.deepEqual(response.result.capabilities.textDocumentSync, {
    openClose: true,
    change: 1,
    save: { includeText: false },
  });
});

test("an opened document gets its diagnostics published", async (t) => {
  const server = startServer();
  t.after(() => server.child.kill());
  await initialized(server);
  const uri = "file:///workspace/broken.rel";
  server.send({
    method: "textDocument/didOpen",
    params: { textDocument: { uri, languageId: "plaintext", version: 1, text: BROKEN } },
  });
  const published = await server.next((m) => m.method === "textDocument/publishDiagnostics");
  assert.equal(published.params.uri, uri);
  const codes = published.params.diagnostics.map((d) => d.code);
  assert.ok(codes.includes("error-token"), `got ${codes}`);
  for (const diagnostic of published.params.diagnostics) {
    assert.equal(diagnostic.source, "bigfix-relevance-analyzer");
    assert.equal(diagnostic.severity, 1);
  }
});

test("hover describes the inspector under the cursor", async (t) => {
  const server = startServer();
  t.after(() => server.child.kill());
  const response = await initialized(server);
  assert.equal(response.result.capabilities.hoverProvider, true);
  const uri = "file:///workspace/hover.rel";
  const text = 'exists file "x" whose (size of it > 100)';
  server.send({
    method: "textDocument/didOpen",
    params: { textDocument: { uri, languageId: "plaintext", version: 1, text } },
  });
  await server.next((m) => m.method === "textDocument/publishDiagnostics");
  const character = text.indexOf("size");
  server.send({
    id: 2,
    method: "textDocument/hover",
    params: { textDocument: { uri }, position: { line: 0, character } },
  });
  const hover = await server.next((m) => m.id === 2);
  assert.equal(hover.result.contents.kind, "markdown");
  assert.match(hover.result.contents.value, /`size of <file>`/);
  assert.deepEqual(hover.result.range, {
    start: { line: 0, character },
    end: { line: 0, character: character + "size".length },
  });
});

test("shutdown then exit ends the process with 0", async () => {
  const server = startServer();
  await initialized(server);
  server.send({ id: 2, method: "shutdown" });
  assert.equal((await server.next((m) => m.id === 2)).result, null);
  server.send({ method: "exit" });
  assert.equal(await server.exited, 0);
});

test("exit without shutdown ends the process with 1", async () => {
  const server = startServer();
  await initialized(server);
  server.send({ method: "exit" });
  assert.equal(await server.exited, 1);
});

// The shim's default gives the component the whole host filesystem (preopen
// "/"; every drive on Windows). The server lints the text it is sent and opens
// no files, so server.js takes that away before the component loads, and says
// so on stderr from the shim's own state.
test("the component is given no filesystem access", async () => {
  const server = startServer();
  await initialized(server);
  server.send({ method: "exit" });
  await server.exited;
  assert.match(server.stderr(), /filesystem access: none/);
});

// Likewise the shim passes the host's environment through by default, which
// can hold tokens and credentials. The server reads no environment variables.
test("the component sees no environment variables", async () => {
  const server = startServer();
  await initialized(server);
  server.send({ method: "exit" });
  await server.exited;
  assert.match(server.stderr(), /environment variables: none/);
});
