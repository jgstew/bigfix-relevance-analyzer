// documentSync: "client" (#142 C1): createClientSync, the part of
// relevance_editor.js that keeps a server's copy of the document current when
// the page talks to the server directly (the playground). Pure: driven here
// with a recording transport and node:test's mock timers, no DOM.
import assert from "node:assert/strict";
import { mock, test } from "node:test";
import { pathToFileURL } from "node:url";

import { createClientSync, relevanceEditor } from "../../../src/bigfix_relevance_analyzer/web/relevance_editor.js";

const cmPath = process.env.CM_MODULE;
assert.ok(cmPath, "set CM_MODULE to a CodeMirror 6 bundle");
const CM = await import(cmPath.startsWith("file:") ? cmPath : pathToFileURL(cmPath).href);

const URI = "untitled:statement";
const DELAY = 200;

/** A transport recording every call, in order; `initialize` answers `capabilities`. */
function recording({ initialize = { capabilities: { completionProvider: { triggerCharacters: ["."] } } } } = {}) {
  const calls = [];
  return {
    calls,
    methods: () => calls.map((c) => c.method),
    sent: (method) => calls.filter((c) => c.method === method),
    request(method, params) {
      calls.push({ kind: "request", method, params });
      if (method === "initialize") {
        return initialize instanceof Error ? Promise.reject(initialize) : Promise.resolve(initialize);
      }
      return Promise.resolve(null);
    },
    notify(method, params) {
      calls.push({ kind: "notify", method, params });
    },
    onNotification() {},
  };
}

function setup(options = {}) {
  const transport = recording(options);
  let text = options.text ?? "name of operating system";
  const sync = createClientSync(transport, { uri: URI, delay: DELAY, getText: () => text });
  return { transport, sync, setText: (next) => (text = next) };
}

test("start sends initialize, then initialized and didOpen at version 1", async () => {
  const { transport, sync } = setup();
  sync.start();
  assert.equal(await sync.ready, true);
  assert.deepEqual(transport.methods(), ["initialize", "initialized", "textDocument/didOpen"]);
  const [init] = transport.sent("initialize");
  assert.equal(init.kind, "request");
  const capabilities = init.params.capabilities;
  assert.ok(capabilities.textDocument.codeAction.codeActionLiteralSupport.codeActionKind.valueSet.includes("quickfix"));
  assert.equal(capabilities.textDocument.completion.completionItem.snippetSupport, false);
  assert.equal(capabilities.workspace.workspaceEdit.documentChanges, false);
  const [open] = transport.sent("textDocument/didOpen");
  assert.equal(open.kind, "notify");
  assert.deepEqual(open.params, {
    textDocument: { uri: URI, languageId: "bigfix-relevance", version: 1, text: "name of operating system" },
  });
  assert.deepEqual(sync.capabilities, { completionProvider: { triggerCharacters: ["."] } });
});

test("an edit before initialize answers goes into didOpen, not a didChange", async () => {
  const { transport, sync, setText } = setup();
  sync.start();
  setText("names of operating systems");
  sync.changed();
  await sync.ready;
  assert.equal(transport.sent("textDocument/didOpen")[0].params.textDocument.text, "names of operating systems");
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    mock.timers.tick(DELAY * 5);
  } finally {
    mock.timers.reset();
  }
  assert.deepEqual(transport.sent("textDocument/didChange"), []);
});

test("edits are debounced into one full-text didChange, versions increasing by one", async () => {
  const { transport, sync, setText } = setup();
  sync.start();
  await sync.ready;
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    for (const text of ["1", "12", "123"]) {
      setText(text);
      sync.changed();
      mock.timers.tick(DELAY - 1);
    }
    assert.deepEqual(transport.sent("textDocument/didChange"), []);
    mock.timers.tick(1);
    setText("1234");
    sync.changed();
    mock.timers.tick(DELAY);
  } finally {
    mock.timers.reset();
  }
  assert.deepEqual(
    transport.sent("textDocument/didChange").map((c) => c.params),
    [
      { textDocument: { uri: URI, version: 2 }, contentChanges: [{ text: "123" }] },
      { textDocument: { uri: URI, version: 3 }, contentChanges: [{ text: "1234" }] },
    ],
  );
});

test("flush sends a pending change at once, and only once", async () => {
  const { transport, sync, setText } = setup();
  sync.start();
  await sync.ready;
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    setText("nme");
    sync.changed();
    sync.flush();
    assert.equal(transport.sent("textDocument/didChange").length, 1);
    mock.timers.tick(DELAY * 2);
    sync.flush();
  } finally {
    mock.timers.reset();
  }
  assert.equal(transport.sent("textDocument/didChange").length, 1);
});

test("accepts diagnostics only for the current version with nothing unsent", async () => {
  const { sync, setText } = setup();
  assert.equal(sync.accepts({ uri: URI, version: 1, diagnostics: [] }), false, "before didOpen");
  sync.start();
  await sync.ready;
  assert.equal(sync.accepts({ uri: URI, version: 1, diagnostics: [] }), true);
  assert.equal(sync.accepts({ uri: URI, diagnostics: [] }), true, "no version: current if nothing is unsent");
  assert.equal(sync.accepts({ uri: "untitled:other", version: 1, diagnostics: [] }), false, "another document");
  setText("x");
  sync.changed();
  assert.equal(sync.accepts({ uri: URI, version: 1, diagnostics: [] }), false, "an edit is unsent");
  assert.equal(sync.accepts({ uri: URI, diagnostics: [] }), false);
  sync.flush();
  assert.equal(sync.accepts({ uri: URI, version: 1, diagnostics: [] }), false, "stale");
  assert.equal(sync.accepts({ uri: URI, version: 2, diagnostics: [] }), true);
  sync.close();
  assert.equal(sync.accepts({ uri: URI, version: 2, diagnostics: [] }), false, "after didClose");
});

test("diagnostics a server publishes while didOpen or didChange is sent are current", async () => {
  // A main-thread server answers inside notify(): the version must already be set.
  const seen = [];
  const transport = recording();
  let sync;
  transport.notify = (method, params) => {
    transport.calls.push({ kind: "notify", method, params });
    const version = params.textDocument?.version;
    if (version !== undefined) seen.push(sync.accepts({ uri: URI, version }));
  };
  let text = "nme";
  sync = createClientSync(transport, { uri: URI, delay: DELAY, getText: () => text });
  sync.start();
  await sync.ready;
  text = "nme of";
  sync.changed();
  sync.flush();
  assert.deepEqual(seen, [true, true]);
});

test("close sends didClose, cancels a pending change, and ends the sync", async () => {
  const { transport, sync, setText } = setup();
  sync.start();
  await sync.ready;
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    setText("x");
    sync.changed();
    sync.close();
    mock.timers.tick(DELAY * 2);
    sync.changed();
    sync.flush();
    mock.timers.tick(DELAY * 2);
  } finally {
    mock.timers.reset();
  }
  assert.deepEqual(transport.methods(), ["initialize", "initialized", "textDocument/didOpen", "textDocument/didClose"]);
  assert.deepEqual(transport.sent("textDocument/didClose")[0].params, { textDocument: { uri: URI } });
});

test("start after close reopens the document at a higher version, without a second initialize", async () => {
  const { transport, sync, setText } = setup();
  sync.start();
  await sync.ready;
  sync.close();
  setText("names of bes computers");
  sync.start();
  assert.equal(await sync.ready, true);
  assert.deepEqual(transport.methods(), [
    "initialize",
    "initialized",
    "textDocument/didOpen",
    "textDocument/didClose",
    "textDocument/didOpen",
  ]);
  const reopened = transport.sent("textDocument/didOpen")[1].params.textDocument;
  assert.deepEqual([reopened.version, reopened.text], [2, "names of bes computers"]);
  assert.equal(sync.accepts({ uri: URI, version: 2 }), true);
  assert.equal(sync.accepts({ uri: URI, version: 1 }), false);
});

test("close then start before initialize answers opens once, when it does", async () => {
  const { transport, sync } = setup();
  sync.start();
  sync.close();
  sync.start();
  assert.equal(await sync.ready, true);
  assert.deepEqual(transport.methods(), ["initialize", "initialized", "textDocument/didOpen"]);
});

test("a notify that throws (a trapped server) closes the sync instead of rejecting", async () => {
  const transport = recording();
  let throwOn = "textDocument/didOpen";
  transport.notify = (method) => {
    transport.calls.push({ kind: "notify", method });
    if (method === throwOn) throw new Error("trap");
  };
  const sync = createClientSync(transport, { uri: URI, delay: DELAY, getText: () => "x" });
  sync.start();
  assert.equal(await sync.ready, false);
  assert.equal(sync.accepts({ uri: URI, version: 1 }), false);

  const second = recording();
  second.notify = transport.notify;
  throwOn = "textDocument/didChange";
  const other = createClientSync(second, { uri: URI, delay: DELAY, getText: () => "y" });
  other.start();
  await other.ready;
  other.changed();
  assert.doesNotThrow(() => other.flush());
  assert.equal(other.accepts({ uri: URI, version: 2 }), false);
  assert.doesNotThrow(() => other.close());
});

test("close before initialize answers: initialized follows it, but no didOpen", async () => {
  const { transport, sync } = setup();
  sync.start();
  sync.close();
  assert.equal(await sync.ready, false);
  assert.deepEqual(transport.methods(), ["initialize", "initialized"]);
});

test("a failed initialize leaves the sync closed: ready is false, nothing else is sent", async () => {
  const { transport, sync } = setup({ initialize: new Error("no server") });
  sync.start();
  assert.equal(await sync.ready, false);
  sync.changed();
  sync.flush();
  assert.deepEqual(transport.methods(), ["initialize"]);
  assert.equal(sync.accepts({ uri: URI, version: 1 }), false);
});

test("start twice is one initialize", async () => {
  const { transport, sync } = setup();
  sync.start();
  sync.start();
  await sync.ready;
  assert.equal(transport.sent("initialize").length, 1);
});

// --- the option on relevanceEditor -------------------------------------------------

test("client mode needs transport.notify", () => {
  const transport = { request: async () => null, onNotification() {} };
  assert.throws(() => relevanceEditor(CM, transport, { documentSync: "client" }), /notify/);
});

test("documentSync takes only host or client", () => {
  const transport = { request: async () => null, notify() {}, onNotification() {} };
  assert.throws(() => relevanceEditor(CM, transport, { documentSync: "server" }), /documentSync/);
  assert.ok(relevanceEditor(CM, transport, { documentSync: "host" }));
  assert.ok(relevanceEditor(CM, transport, { documentSync: "client" }));
});

test("host mode, the default, never notifies", () => {
  let notified = 0;
  const transport = { request: async () => null, notify: () => notified++, onNotification() {} };
  const state = CM.EditorState.create({ doc: "x", extensions: relevanceEditor(CM, transport) });
  state.update({ changes: { from: 1, insert: "y" } });
  assert.equal(notified, 0);
});
