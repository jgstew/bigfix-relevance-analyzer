// Whether an open document is worth starting the language server for, decided
// in Node before any WebAssembly loads. extension.js activates at startup in
// every window but starts the server (a ~170 MiB process) only once a document
// it would lint passes this check.
//
// Only documents the client's document selector already covers reach here.
// BigFix file types and the relevance language always pass. Markdown and HTML
// are in nearly every repository, so they pass only when their text has
// relevance the analyzer would read. The check may let through text the
// analyzer then finds nothing in (that only starts the server), but must never
// miss what it would read. The tables in server-gate.json are the extractor's
// own, held there by tests/test_vscode_extension_layout.py; the patterns here
// mirror src/bigfix_relevance_analyzer/extract.py.
//
// No `vscode` import, so test/gate.test.mjs runs it in plain Node.

"use strict";

const path = require("node:path");
const { markdownSuffixes, markdownFenceTags, htmlSuffixes } = require("./server-gate.json");

// extract._FENCE_RE plus the tag rule: three or more backticks or tildes, then
// an info string that is exactly one tag, ignoring case and surrounding space.
const FENCE = new RegExp(
  String.raw`^[ \t]*(?:\`{3,}|~{3,})[ \t]*(?:${markdownFenceTags.join("|")})[ \t]*\r?$`,
  "im"
);
// extract._PI_OPEN_RE, and a looser extract._JS_CALL_RE (no lookbehinds):
// matching more than the extractor costs a server start, never a diagnostic.
const HTML = /<\?relevance\b|Relevance\s*\(/i;

/**
 * @param {{ fileName: string, getText(): string }} document a vscode.TextDocument,
 *   or anything shaped like one; the text is read only for Markdown and HTML.
 */
function needsServer(document) {
  const suffix = path.extname(document.fileName).toLowerCase();
  if (markdownSuffixes.includes(suffix)) return FENCE.test(document.getText());
  if (htmlSuffixes.includes(suffix)) return HTML.test(document.getText());
  return true;
}

module.exports = { needsServer };
