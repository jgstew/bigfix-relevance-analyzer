// pump.js: the transport-agnostic loop between a JSON-RPC reader/writer and a
// component's `handle` / `exitCode` exports, driven with in-memory fakes.

import assert from "node:assert/strict";
import { test } from "node:test";

import { listen } from "../pump.js";

/** A reader in vscode-jsonrpc's shape: listen(callback) -> a disposable. */
function fakeReader() {
  let callback = null;
  return {
    listen(cb) {
      callback = cb;
      return { dispose: () => (callback = null) };
    },
    send(message) {
      callback(message);
    },
    get listening() {
      return callback !== null;
    },
  };
}

/** A writer whose write() resolves on the next microtask, like IPC does. */
function fakeWriter() {
  const written = [];
  return { written, write: (message) => Promise.resolve(written.push(message)) };
}

/** A component that echoes each request as one reply, plus any `extra` replies. */
function fakeComponent({ exitAfter = null, trapOn = null, extra = [] } = {}) {
  const seen = [];
  let exitCode;
  return {
    seen,
    handle(text) {
      assert.equal(typeof text, "string");
      const message = JSON.parse(text);
      seen.push(message);
      if (message.method === trapOn) throw new Error("RuntimeError: unreachable");
      if (message.method === exitAfter) exitCode = message.params.code;
      const replies = message.id === undefined ? [] : [{ jsonrpc: "2.0", id: message.id, result: message.method }];
      return JSON.stringify([...replies, ...extra]);
    },
    exitCode: () => exitCode,
  };
}

const tick = () => new Promise((resolve) => setImmediate(resolve));

function harness(componentOptions) {
  const reader = fakeReader();
  const writer = fakeWriter();
  const component = fakeComponent(componentOptions);
  const exits = [];
  const logged = [];
  const disposable = listen(reader, writer, component, (code) => exits.push(code), {
    log: (...args) => logged.push(args),
  });
  return { reader, writer, component, exits, logged, disposable };
}

test("each message goes to handle as JSON and its replies are written in order", () => {
  const { reader, writer, component } = harness();
  reader.send({ jsonrpc: "2.0", id: 1, method: "initialize", params: {} });
  reader.send({ jsonrpc: "2.0", id: 2, method: "textDocument/hover", params: {} });
  assert.deepEqual(component.seen.map((m) => m.id), [1, 2]);
  assert.deepEqual(writer.written, [
    { jsonrpc: "2.0", id: 1, result: "initialize" },
    { jsonrpc: "2.0", id: 2, result: "textDocument/hover" },
  ]);
});

test("a notification with no reply writes nothing", () => {
  const { reader, writer, component, exits } = harness();
  reader.send({ jsonrpc: "2.0", method: "textDocument/didOpen", params: {} });
  assert.equal(component.seen.length, 1);
  assert.deepEqual(writer.written, []);
  assert.deepEqual(exits, []);
});

test("every message handle returns is written, server-initiated ones included", () => {
  const diagnostics = { jsonrpc: "2.0", method: "textDocument/publishDiagnostics", params: {} };
  const { reader, writer } = harness({ extra: [diagnostics] });
  reader.send({ jsonrpc: "2.0", method: "textDocument/didChange", params: {} });
  assert.deepEqual(writer.written, [diagnostics]);
});

test("exit stops the loop with the component's exit code", () => {
  const { reader, writer, component, exits } = harness({ exitAfter: "exit" });
  reader.send({ jsonrpc: "2.0", method: "exit", params: { code: 0 } });
  assert.deepEqual(exits, [0]);
  reader.send({ jsonrpc: "2.0", id: 9, method: "textDocument/hover", params: {} });
  assert.equal(component.seen.length, 1, "nothing is handled after exit");
  assert.deepEqual(writer.written, []);
});

test("exit code 1 (no shutdown first) is passed through", () => {
  const { reader, exits } = harness({ exitAfter: "exit" });
  reader.send({ jsonrpc: "2.0", method: "exit", params: { code: 1 } });
  assert.deepEqual(exits, [1]);
});

test("a trap on a request answers it with an internal error, then exits 1 once written", async () => {
  const { reader, writer, component, exits, logged } = harness({ trapOn: "textDocument/completion" });
  reader.send({ jsonrpc: "2.0", id: 7, method: "textDocument/completion", params: {} });
  assert.deepEqual(exits, [], "not before the error reply is written");
  await tick();
  assert.equal(writer.written.length, 1);
  const [reply] = writer.written;
  assert.equal(reply.id, 7);
  assert.equal(reply.error.code, -32603);
  assert.match(reply.error.message, /unreachable/);
  assert.deepEqual(exits, [1]);
  assert.equal(logged.length, 1);
  reader.send({ jsonrpc: "2.0", id: 8, method: "textDocument/hover", params: {} });
  assert.equal(component.seen.length, 1, "a trapped instance is never called again");
});

test("a trap on a notification exits 1 and writes nothing", () => {
  const { reader, writer, exits, logged } = harness({ trapOn: "textDocument/didChange" });
  reader.send({ jsonrpc: "2.0", method: "textDocument/didChange", params: {} });
  assert.deepEqual(exits, [1]);
  assert.deepEqual(writer.written, []);
  assert.equal(logged.length, 1);
});

test("a trap while the error reply fails to write still exits 1", async () => {
  const reader = fakeReader();
  const exits = [];
  const writer = { write: () => Promise.reject(new Error("pipe closed")) };
  listen(reader, writer, fakeComponent({ trapOn: "x" }), (code) => exits.push(code), { log: () => {} });
  reader.send({ jsonrpc: "2.0", id: 1, method: "x" });
  await tick();
  await tick();
  assert.deepEqual(exits, [1]);
});

test("a writer whose write returns nothing (a synchronous one) works too", async () => {
  const reader = fakeReader();
  const written = [];
  const exits = [];
  const writer = { write: (message) => void written.push(message) };
  listen(reader, writer, fakeComponent({ trapOn: "boom" }), (code) => exits.push(code), { log: () => {} });
  reader.send({ jsonrpc: "2.0", id: 1, method: "ok" });
  reader.send({ jsonrpc: "2.0", id: 2, method: "boom" });
  await tick();
  assert.deepEqual(written.map((m) => m.id), [1, 2]);
  assert.deepEqual(exits, [1]);
});

test("returns what the reader's listen returns, so the host can dispose it", () => {
  const { reader, disposable } = harness();
  assert.equal(reader.listening, true);
  disposable.dispose();
  assert.equal(reader.listening, false);
});

test("logs to console.error by default", () => {
  const reader = fakeReader();
  const original = console.error;
  const logged = [];
  console.error = (...args) => logged.push(args);
  try {
    listen(reader, fakeWriter(), fakeComponent({ trapOn: "x" }), () => {});
    reader.send({ jsonrpc: "2.0", method: "x" });
  } finally {
    console.error = original;
  }
  assert.equal(logged.length, 1);
});

test("a write that throws after handle succeeded exits 1, and nothing is handled after", () => {
  const reader = fakeReader();
  const exits = [];
  const logged = [];
  const component = fakeComponent();
  const writer = { write: () => { throw new Error("port closed"); } };
  listen(reader, writer, component, (code) => exits.push(code), { log: (...a) => logged.push(a) });
  assert.doesNotThrow(() => reader.send({ jsonrpc: "2.0", id: 1, method: "x" }));
  assert.deepEqual(exits, [1]);
  assert.equal(logged.length, 1);
  reader.send({ jsonrpc: "2.0", id: 2, method: "y" });
  assert.equal(component.seen.length, 1);
});

test("exitCode trapping exits 1 instead of throwing out of the reader", () => {
  const reader = fakeReader();
  const exits = [];
  const component = { handle: () => "[]", exitCode: () => { throw new Error("RuntimeError: unreachable"); } };
  listen(reader, fakeWriter(), component, (code) => exits.push(code), { log: () => {} });
  assert.doesNotThrow(() => reader.send({ jsonrpc: "2.0", method: "x" }));
  assert.deepEqual(exits, [1]);
});

test("handle returning something other than a JSON array exits 1", () => {
  const reader = fakeReader();
  const exits = [];
  const component = { handle: () => "null", exitCode: () => undefined };
  listen(reader, fakeWriter(), component, (code) => exits.push(code), { log: () => {} });
  assert.doesNotThrow(() => reader.send({ jsonrpc: "2.0", method: "x" }));
  assert.deepEqual(exits, [1]);
});

test("exit is called once even when a write delivers the next message re-entrantly", () => {
  const reader = fakeReader();
  const exits = [];
  const component = fakeComponent({ exitAfter: "exit" });
  let nested = false;
  const writer = {
    write: () => {
      if (!nested) {
        nested = true;
        reader.send({ jsonrpc: "2.0", method: "exit", params: { code: 0 } });
      }
    },
  };
  listen(reader, writer, component, (code) => exits.push(code), { log: () => {} });
  // A request whose own handling also reports exit 0 (the component is shared).
  component.handle(JSON.stringify({ jsonrpc: "2.0", method: "exit", params: { code: 0 } }));
  reader.send({ jsonrpc: "2.0", id: 1, method: "shutdown" });
  assert.deepEqual(exits, [0]);
});

test("an exit callback that throws on the trap path is logged, not an unhandled rejection", async () => {
  const reader = fakeReader();
  const logged = [];
  const unhandled = [];
  const onUnhandled = (reason) => unhandled.push(reason);
  process.on("unhandledRejection", onUnhandled);
  try {
    listen(reader, fakeWriter(), fakeComponent({ trapOn: "x" }), () => { throw new Error("exit failed"); }, {
      log: (...a) => logged.push(a),
    });
    reader.send({ jsonrpc: "2.0", id: 1, method: "x" });
    await tick();
    await tick();
  } finally {
    process.off("unhandledRejection", onUnhandled);
  }
  assert.deepEqual(unhandled, []);
  assert.equal(logged.length, 2);
});

test("a write whose promise rejects exits 1, not an unhandled rejection", async () => {
  const reader = fakeReader();
  const exits = [];
  const unhandled = [];
  const onUnhandled = (reason) => unhandled.push(reason);
  process.on("unhandledRejection", onUnhandled);
  try {
    const writer = { write: () => Promise.reject(new Error("port closed")) };
    listen(reader, writer, fakeComponent(), (code) => exits.push(code), { log: () => {} });
    reader.send({ jsonrpc: "2.0", id: 1, method: "x" });
    await tick();
    await tick();
  } finally {
    process.off("unhandledRejection", onUnhandled);
  }
  assert.deepEqual(unhandled, []);
  assert.deepEqual(exits, [1]);
});

test("a message delivered during a write is handled after the current replies are written", () => {
  const reader = fakeReader();
  const written = [];
  const component = {
    handle: (text) => {
      const { id } = JSON.parse(text);
      return JSON.stringify([`a${id}`, `b${id}`]);
    },
    exitCode: () => undefined,
  };
  const writer = {
    write: (message) => {
      written.push(message);
      if (message === "a1") reader.send({ jsonrpc: "2.0", id: 2, method: "y" });
    },
  };
  listen(reader, writer, component, () => {}, { log: () => {} });
  reader.send({ jsonrpc: "2.0", id: 1, method: "x" });
  assert.deepEqual(written, ["a1", "b1", "a2", "b2"]);
});

test("a trap on a client's response (an id, no method) writes no reply and exits 1", () => {
  const reader = fakeReader();
  const writer = fakeWriter();
  const exits = [];
  const component = { handle: () => { throw new Error("trap"); }, exitCode: () => undefined };
  listen(reader, writer, component, (code) => exits.push(code), { log: () => {} });
  reader.send({ jsonrpc: "2.0", id: 7, result: null });
  assert.deepEqual(writer.written, []);
  assert.deepEqual(exits, [1]);
});

test("odd inputs never throw out of the reader: a null message, a throwing log", () => {
  const reader = fakeReader();
  const exits = [];
  const component = { handle: () => { throw new Error("trap"); }, exitCode: () => undefined };
  listen(reader, fakeWriter(), component, (code) => exits.push(code), {
    log: () => {
      throw new Error("log failed");
    },
  });
  assert.doesNotThrow(() => reader.send(null));
  assert.deepEqual(exits, [1]);
});
