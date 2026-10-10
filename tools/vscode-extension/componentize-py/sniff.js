// Whether a document's text is BES XML, judged by its root element (issue
// #132). extension.js uses it to switch an unsaved tab a fixlet is pasted or
// typed into to BigFix BES XML: VS Code makes a pasted fixlet `xml` (from
// line 1's `<?xml`) and a typed one `markdown` (its ML detector), and no
// `firstLine` pattern can see the `<BES` on line 2 or 3.
//
// Measured over 5,975 BES files: every one with a <BES> root detected, and no
// false positives in 22,000+ samples of relevance, ActionScript, other XML,
// prose and code. <BESAPI> roots are out of scope.
//
// No `vscode` import, so test/sniff.test.mjs runs it in plain Node.

"use strict";

// A <BES> root: an optional BOM, XML declaration, comments and whitespace first.
const BES_ROOT = /^\uFEFF?\s*(?:<\?xml[^>]*\?>\s*)?(?:<!--[\s\S]*?-->\s*)*<BES[\s>/]/;
// Enough for any real preamble, and it bounds the work on a large paste.
const HEAD_CHARS = 8192;

/** Whether `text` is a BES XML document, judged by its first 8 KiB. */
function isBesXml(text) {
  return BES_ROOT.test(text.slice(0, HEAD_CHARS));
}

module.exports = { isBesXml };
