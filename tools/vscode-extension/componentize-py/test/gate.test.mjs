// Unit tests for gate.js, which decides in Node, before any WebAssembly loads,
// whether an open document is worth starting the language server for. Run
// with `node --test test/gate.test.mjs`.
//
// EXTENSION_DIR picks which copy to test, as in server.test.mjs: this source
// tree by default, the unzipped .vsix in CI.

import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const EXTENSION = resolve(
  process.env.EXTENSION_DIR ?? join(dirname(fileURLToPath(import.meta.url)), "..")
);
const { needsServer } = createRequire(import.meta.url)(join(EXTENSION, "gate.js"));

// The shape of a vscode.TextDocument that the gate reads: text through
// getText(), as VS Code provides it (a TextDocument has no `text` property).
const doc = (fileName, text = "") => ({ fileName, getText: () => text });

test("a BigFix file type always needs the server, whatever its text", () => {
  for (const name of ["a.bes", "a.bes.xml", "a.ojo", "a.besrpt", "a.beswrpt", "a.webreport", "a.rel", "a.bsr"]) {
    assert.equal(needsServer(doc(`/w/${name}`)), true, name);
  }
});

test("an unsaved buffer in the relevance language needs the server", () => {
  // Only the language brings it to the gate (the document selector); its
  // name has no suffix.
  assert.equal(needsServer(doc("Untitled-1")), true);
});

test("Markdown needs it only with a fence tagged as relevance", () => {
  assert.equal(needsServer(doc("/w/a.md", "# Notes\n\nplain prose about relevance\n")), false);
  assert.equal(needsServer(doc("/w/a.md", "```python\nprint(1)\n```\n")), false);
  assert.equal(needsServer(doc("/w/a.md", "```relevance\nexists file\n```\n")), true);
  assert.equal(needsServer(doc("/w/a.markdown", "  ~~~~ Session_Relevance \nnames of bes computers\n~~~~\n")), true);
  assert.equal(needsServer(doc("/w/A.MD", "```client_relevance\nexists file\n```\n")), true);
});

test("a fence whose info string the extractor would skip does not count", () => {
  // The extractor takes a fence only when its whole info string is a tag.
  assert.equal(needsServer(doc("/w/a.md", "```relevance foo\nexists file\n```\n")), false);
});

test("HTML needs it only with a processing instruction or a Relevance call", () => {
  assert.equal(needsServer(doc("/w/a.html", "<p>relevance is a language</p>")), false);
  assert.equal(needsServer(doc("/w/a.html", "<p><?Relevance name of operating system?></p>")), true);
  assert.equal(needsServer(doc("/w/a.htm", '<script>Relevance("version of client")</script>')), true);
  assert.equal(needsServer(doc("/w/A.HTML", '<script>EvaluateRelevance ("x", cb)</script>')), true);
});

test("the Markdown fence tags are the extractor's", async () => {
  const { markdownFenceTags } = createRequire(import.meta.url)(join(EXTENSION, "server-gate.json"));
  assert.deepEqual(markdownFenceTags, ["client_relevance", "relevance", "session_relevance"]);
});
