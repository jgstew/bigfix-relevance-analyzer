// The transport-agnostic loop between an LSP client and a componentize-py
// component exporting `handle(message: string) -> string` (a JSON array of the
// messages to send back) and `exitCode() -> number | undefined`.
//
// Shared by the hosts of such a component: the playground page (#142, on the
// main thread) and the VS Code extension's web Worker (#139). All protocol
// logic is inside the component -- the Python package's `Server` -- so this
// knows no LSP beyond "a message has an id".
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
 * - `exit(code)`: called once, when the component reports an exit code (the
 *   client sent `exit`) or traps. Nothing is handled after it.
 * - `options.log`: where a trap is reported (default `console.error`).
 *
 * `handle` is synchronous, so messages are answered strictly in the order they
 * arrive, which is what the Python server assumes.
 */
export function listen(reader, writer, component, exit, { log = console.error } = {}) {
  let done = false;
  const finish = (code) => {
    done = true;
    exit(code);
  };
  return reader.listen((message) => {
    if (done) return;
    let replies;
    try {
      replies = JSON.parse(component.handle(JSON.stringify(message)));
    } catch (error) {
      // The component traps rather than raises on a fault, and a trapped
      // instance cannot be trusted afterwards; let the client restart it.
      log(error);
      done = true;
      if (message.id === undefined) {
        exit(1);
        return;
      }
      // Writes may be asynchronous (IPC is): exit once the reply is sent, or it
      // is lost. A failed write exits all the same.
      const reply = { jsonrpc: "2.0", id: message.id, error: { code: INTERNAL_ERROR, message: String(error) } };
      Promise.resolve()
        .then(() => writer.write(reply))
        .catch(() => {})
        .finally(() => exit(1));
      return;
    }
    for (const reply of replies) writer.write(reply);
    const code = component.exitCode();
    if (code !== undefined && code !== null) finish(code);
  });
}
