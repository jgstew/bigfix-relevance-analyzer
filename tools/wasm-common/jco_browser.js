// What any jco-transpiled componentize-py component needs to run in a browser:
// the jco and esbuild flags that select the browser shims, the wasi:sockets
// stub, and the check that the bundle came out browser-clean. Shared by the
// playground's build (../playground-wasm/componentize-py/smoke/transpile.mjs)
// and, per #139, the VS Code extension's web server; each caller adds its own
// target-specific flags (the playground's --tla-compat and --base64-cutoff 0).
//
// Build-time only: this file uses Node, and nothing in a page imports it.

import { fileURLToPath } from "node:url";

/** The wasi:sockets stub, for a build to copy next to its transpiled glue. */
export const SOCKETS_STUB = fileURLToPath(new URL("./sockets_stub.js", import.meta.url));

/**
 * The jco transpile flags a browser build needs, given the stub's specifier as
 * seen from the emitted glue (e.g. "../sockets_stub.js").
 *
 * --no-nodejs-compat is REQUIRED, not an optimisation. Without it jco's glue
 *   contains `await import('node:fs/promises')` for loading cores off disk, and
 *   esbuild's browser build cannot resolve it. This is the first hard error you
 *   hit trying to bundle jco output for a browser.
 *
 * --map 'wasi:sockets/*=...' swaps preview2-shim's sockets for the stub.
 *   componentize-py's CPython links the `socket` module, so the component
 *   imports wasi:sockets even though nothing opens one, and preview2-shim's
 *   *browser* build still ships the pre-resource flat-function shape for
 *   wasi:sockets/ip-name-lookup. Without the map, instantiation dies with
 *   "unexpectedly undefined local import 'ResolveAddressStream'". See
 *   sockets_stub.js.
 */
export function jcoBrowserArgs(stubFromGlue) {
  return ["--no-nodejs-compat", "--map", `wasi:sockets/*=${stubFromGlue}#*`];
}

/**
 * The esbuild flags that bundle the glue and preview2-shim for a browser.
 * --conditions=browser is what selects preview2-shim's browser entry (an
 * in-memory virtual filesystem) over its Node one. If it stops taking effect,
 * nodeBuiltinsIn() on the output is what catches it.
 */
export const ESBUILD_BROWSER_ARGS = Object.freeze(["--platform=browser", "--conditions=browser"]);

/**
 * The `node:` specifiers left in a bundle, deduplicated in order of first
 * appearance. Any at all in a browser bundle means the browser condition did
 * not apply and the page would fail at load; do not paper over that with
 * --external.
 */
export function nodeBuiltinsIn(bundleText) {
  return [...new Set(bundleText.match(/node:[a-z_/]+/g) ?? [])];
}
