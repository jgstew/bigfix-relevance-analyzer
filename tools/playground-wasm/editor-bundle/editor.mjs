// The playground pages' editor (#142 C1): CodeMirror 6 with the wheel's own
// web/ modules -- relevanceLanguage for highlighting and relevanceEditor in
// "client" mode for diagnostics, completion, hover and quick fixes -- talking
// to the language server the page already runs (window.lspHandle, see
// ../common/shared_script.html) on the main thread.
//
// build.mjs bundles this, CodeMirror included, into one classic script both
// build_playground.py scripts inline, so each page stays a single offline
// file. It publishes one global, window.playgroundEditor.

import { basicSetup } from "codemirror";
import * as language from "@codemirror/language";
import * as state from "@codemirror/state";
import * as view from "@codemirror/view";

import { relevanceEditor } from "../../../src/bigfix_relevance_analyzer/web/relevance_editor.js";
import { relevanceLanguage } from "../../../src/bigfix_relevance_analyzer/web/relevance_language.js";

const CM = { ...state, ...view, ...language };

/**
 * A transport over a synchronous `handle(message) -> string` (a JSON array of
 * replies): requests resolve with their reply's result (or reject with its
 * error), and every server notification goes to the handlers. A throw from
 * `handle` means the server is gone: it is rethrown (the client stops syncing)
 * and every later call fails at once.
 */
export function handleTransport(handle) {
  const handlers = [];
  let id = 0;
  let dead = null;
  const exchange = (message) => {
    if (dead) throw dead;
    let replies;
    try {
      replies = JSON.parse(handle(JSON.stringify({ jsonrpc: "2.0", ...message })));
    } catch (error) {
      dead = new Error(`the language server stopped: ${error && error.message ? error.message : error}`);
      throw dead;
    }
    for (const reply of replies) {
      if (reply.method !== undefined && reply.id === undefined) {
        for (const handler of handlers) handler(reply.method, reply.params);
      }
    }
    return replies;
  };
  return {
    request(method, params) {
      try {
        const sent = ++id;
        const reply = exchange({ id: sent, method, params }).find((r) => r.id === sent);
        if (!reply) return Promise.reject(new Error(`no reply to ${method}`));
        if (reply.error) return Promise.reject(new Error(reply.error.message));
        return Promise.resolve(reply.result);
      } catch (error) {
        return Promise.reject(error);
      }
    },
    notify(method, params) {
      exchange({ method, params });
    },
    onNotification(handler) {
      handlers.push(handler);
    },
  };
}

/**
 * An editor in `parent` holding `doc`, highlighted at once; Mod-Enter calls
 * `onRun`. connect(handle) adds the language server once the page's runtime
 * has booted. Returns { view, getText, setText, connect }.
 */
function mount(parent, { doc = "", onRun = () => {} } = {}) {
  const server = new state.Compartment();
  const editor = new view.EditorView({
    parent,
    doc,
    extensions: [
      basicSetup,
      relevanceLanguage(CM),
      view.EditorView.lineWrapping,
      view.EditorView.contentAttributes.of({ "aria-label": "Relevance statement" }),
      state.Prec.highest(
        view.keymap.of([
          {
            key: "Mod-Enter",
            run: () => {
              onRun();
              return true;
            },
          },
        ]),
      ),
      server.of([]),
    ],
  });
  let connected = false;
  return {
    view: editor,
    getText: () => editor.state.doc.toString(),
    setText(text) {
      editor.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: text } });
    },
    connect(handle) {
      if (connected) return; // one server per page, initialized once
      connected = true;
      const extensions = relevanceEditor(CM, handleTransport(handle), { documentSync: "client" });
      editor.dispatch({ effects: server.reconfigure(extensions) });
    },
  };
}

window.playgroundEditor = { mount };
