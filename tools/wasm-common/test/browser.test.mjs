// browser.js: what any jco-transpiled componentize-py component needs to run in
// a browser, shared by the playground build and (later) the VS Code web server.

import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

import { ESBUILD_BROWSER_ARGS, SOCKETS_STUB, jcoBrowserArgs, nodeBuiltinsIn } from "../browser.js";

test("the jco flags drop the Node fallback and map wasi:sockets to the stub", () => {
  const args = jcoBrowserArgs("../sockets_stub.js");
  assert.ok(args.includes("--no-nodejs-compat"));
  const map = args.indexOf("--map");
  assert.notEqual(map, -1);
  assert.equal(args[map + 1], "wasi:sockets/*=../sockets_stub.js#*");
});

test("the esbuild flags select preview2-shim's browser build", () => {
  assert.ok(ESBUILD_BROWSER_ARGS.includes("--platform=browser"));
  assert.ok(ESBUILD_BROWSER_ARGS.includes("--conditions=browser"));
});

test("the stub exists and exports every wasi:sockets interface jco's glue imports", async () => {
  assert.ok(existsSync(SOCKETS_STUB), SOCKETS_STUB);
  const stub = await import(new URL(`file://${SOCKETS_STUB}`).href);
  for (const name of ["network", "instanceNetwork", "ipNameLookup", "tcp", "tcpCreateSocket", "udp", "udpCreateSocket"]) {
    assert.equal(typeof stub[name], "object", name);
  }
  assert.equal(typeof stub.ipNameLookup.ResolveAddressStream, "function");
  assert.throws(() => stub.tcpCreateSocket.createTcpSocket(), /not available in this page/);
});

test("node: specifiers left in a browser bundle are found", () => {
  assert.deepEqual(nodeBuiltinsIn('import("node:fs/promises");import a from "node:path";import("node:fs/promises")'), [
    "node:fs/promises",
    "node:path",
  ]);
  assert.deepEqual(nodeBuiltinsIn("const x = 1;"), []);
});

test("pump.js imports nothing, so a browser Worker can bundle it alone", () => {
  const source = readFileSync(new URL("../pump.js", import.meta.url), "utf8");
  assert.doesNotMatch(source, /^\s*import\b/m);
  assert.doesNotMatch(source, /\brequire\(/);
});
