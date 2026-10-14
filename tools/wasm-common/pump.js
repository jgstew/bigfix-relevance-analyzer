// The transport-agnostic loop between an LSP client and a componentize-py
// component exporting `handle(message: string) -> string` (a JSON array of the
// messages to send back) and `exitCode() -> number | undefined`.
//
// Shared by the hosts of such a component: the playground page (#142, on the
// main thread) and the VS Code extension's web Worker (#139). All protocol
// logic is inside the component -- the Python package's `Server` -- so this
// knows no LSP beyond "a message has an id". The Node server
// (../vscode-extension/componentize-py/server.js) still has its own copy of
// this loop until #139 bundles it.
//
// Imports nothing, so a browser bundle can take it alone.

const INTERNAL_ERROR = -32603;

/**
 * Feed every message `reader` delivers to `component.handle`, in order, and
 * write each reply.
 *
 * - `reader`: `{ listen(callback) }`, vscode-jsonrpc's MessageReader shape;
 *   whatever its `listen` returns (a disposable) is returned.
 * - `writer`: `{ write(message) }`, returning a promise or nothing.
 * - `exit(code)`: called exactly once, when the component reports an exit code
 *   (the client sent `exit`), or with 1 when anything fails: the component
 *   traps, returns something that is not a JSON array, or a write throws.
 *   Nothing is handled after it.
 * - `options.log`: where a failure is reported (default `console.error`).
 *
 * `handle` is synchronous, so messages are answered strictly in the order they
 * arrive, which is what the Python server assumes.
 *
 * Timing: on a normal `exit`, `exit(code)` is called right after the replies
 * are *handed to* the writer, not after an asynchronous writer has sent them
 * (there are none for `exit`). When a request traps, `exit(1)` waits for its
 * error reply's write to settle, or that reply would be lost.
 */
export function listen(reader, writer, component, exit, { log = console.error } = {}) {
  let stopped = false; // nothing more is handled
  let exited = false; // exit has been called
  const finish = (code) => {
    if (exited) return;
    exited = stopped = true;
    try {
      exit(code);
    } catch (error) {
      log(error);
    }
  };
  return reader.listen((message) => {
    if (stopped) return;
    let replies;
    try {
      replies = JSON.parse(component.handle(JSON.stringify(message)));
      if (!Array.isArray(replies)) throw new TypeError(`handle returned ${JSON.stringify(replies)}, not an array`);
    } catch (error) {
      // The component traps rather than raises on a fault, and a trapped
      // instance cannot be trusted afterwards; let the client restart it.
      log(error);
      if (message.id === undefined) {
        finish(1);
        return;
      }
      stopped = true;
      // Writes may be asynchronous (IPC is): exit once the reply is sent, or it
      // is lost. A failed write exits all the same.
      const reply = { jsonrpc: "2.0", id: message.id, error: { code: INTERNAL_ERROR, message: String(error) } };
      Promise.resolve()
        .then(() => writer.write(reply))
        .catch(() => {})
        .finally(() => finish(1));
      return;
    }
    try {
      for (const reply of replies) {
        writer.write(reply);
        if (stopped) return; // a write delivered `exit` re-entrantly
      }
      const code = component.exitCode();
      if (code !== undefined && code !== null) finish(code);
    } catch (error) {
      log(error);
      finish(1);
    }
  });
}
