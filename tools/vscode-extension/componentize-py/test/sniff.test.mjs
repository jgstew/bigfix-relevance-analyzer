// Unit tests for sniff.js, which tells a BES XML document by its text, so an
// unsaved tab a fixlet is pasted into can be switched to BigFix BES XML
// (issue #132). Run with `node --test test/sniff.test.mjs`.
//
// EXTENSION_DIR picks which copy to test, as in server.test.mjs: this source
// tree by default, the unzipped .vsix in CI.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTENSION = resolve(process.env.EXTENSION_DIR ?? join(HERE, ".."));
const { isBesXml } = createRequire(import.meta.url)(join(EXTENSION, "sniff.js"));

const DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>';
const SCHEMA = 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd"';
const TASK = "<Task><Title>t</Title></Task>\n</BES>\n";

test("the usual layout: the declaration, then <BES on line 2", () => {
  assert.equal(isBesXml(`${DECLARATION}\n<BES ${SCHEMA}>\n${TASK}`), true);
});

test("CRLF line endings", () => {
  assert.equal(isBesXml(`${DECLARATION}\r\n<BES ${SCHEMA}>\r\n${TASK.replaceAll("\n", "\r\n")}`), true);
});

test("the declaration and <BES on one line, as SaaS exports them", () => {
  assert.equal(isBesXml(`${DECLARATION}<BES ${SCHEMA}>${TASK}`), true);
});

test("a comment between the declaration and <BES", () => {
  assert.equal(isBesXml(`${DECLARATION}\n<!-- vim: set syntax=xml: -->\n<BES>\n${TASK}`), true);
  assert.equal(isBesXml(`${DECLARATION}\n<!-- one -->\n<!--\n two\n-->\n<BES>\n${TASK}`), true);
});

test("no declaration", () => {
  assert.equal(isBesXml(`<BES>\n${TASK}`), true);
  assert.equal(isBesXml(`<!-- c -->\n<BES>\n${TASK}`), true);
  assert.equal(isBesXml(`\n\n  <BES>\n${TASK}`), true);
});

test("a leading byte order mark", () => {
  assert.equal(isBesXml(`\uFEFF${DECLARATION}\n<BES>\n${TASK}`), true);
});

test("every way the root tag can end", () => {
  assert.equal(isBesXml("<BES>"), true);
  assert.equal(isBesXml(`<BES ${SCHEMA}>`), true);
  assert.equal(isBesXml("<BES\n  xmlns:xsi='x'>"), true);
  assert.equal(isBesXml("<BES/>"), true);
});

test("another root, even one starting BES, is not BES XML", () => {
  assert.equal(isBesXml(`${DECLARATION}\n<BESAPI>\n<Fixlet/>\n</BESAPI>\n`), false);
  assert.equal(isBesXml(`${DECLARATION}\n<BESX>\n</BESX>\n`), false);
  assert.equal(isBesXml(`${DECLARATION}\n<project>\n</project>\n`), false);
  assert.equal(isBesXml("<bes>\n</bes>\n"), false);
});

test("<BES only after the first 8 KiB is not looked for", () => {
  const comment = `<!-- ${"x".repeat(9000)} -->\n`;
  assert.equal(isBesXml(`${DECLARATION}\n${comment}<BES>\n${TASK}`), false);
});

test("<BES after other text is not a root", () => {
  assert.equal(isBesXml("notes\n<BES>\n</BES>\n"), false);
  assert.equal(isBesXml(`${DECLARATION}\n<p>see <BES></p>\n`), false);
});

test("relevance, ActionScript, and nothing at all are not BES XML", () => {
  assert.equal(isBesXml('exists file "C:\\Windows\\notepad.exe"'), false);
  assert.equal(isBesXml('names of bes computers whose (name of it contains "BES")'), false);
  assert.equal(isBesXml('action uses wow64 redirection false\nwait cmd /c echo "<BES>"\n'), false);
  assert.equal(isBesXml(""), false);
});

test("a real public fixlet is BES XML", () => {
  const repo = resolve(HERE, "..", "..", "..", "..");
  const fixlet = join(repo, "tests", "examples", "client_relevance", "fixlets", "fixlet_multi_clause_relevance.bes");
  assert.equal(isBesXml(readFileSync(fixlet, "utf8")), true);
});
