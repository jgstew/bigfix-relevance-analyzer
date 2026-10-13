// Tests for src/bigfix_relevance_analyzer/web/relevance_language.js, the
// CodeMirror 6 highlighter generated from the same tables as the TextMate
// grammar (#142, Layer 4; tools/generate_tmlanguage.py writes both).
//
// The authority is the TextMate grammar as VS Code runs it: vscode-textmate
// with vscode-oniguruma. Every statement in tests/corpus is tokenized by both,
// and every character must get the same class: the CodeMirror token the
// generator pairs with the TextMate scope (TEXTMATE_TOKENS), or none for none.
// CodeMirror's side runs through the real StreamLanguage, from CM_MODULE as in
// relevance_editor.test.mjs.
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

import oniguruma from "vscode-oniguruma";
import vsctm from "vscode-textmate";

import {
  REQUIRED_CM,
  TEXTMATE_TOKENS,
  relevanceLanguage,
} from "../../../src/bigfix_relevance_analyzer/web/relevance_language.js";

const cmPath = process.env.CM_MODULE;
assert.ok(cmPath, "set CM_MODULE to a CodeMirror 6 bundle");
const CM = await import(cmPath.startsWith("file:") ? cmPath : pathToFileURL(cmPath).href);

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "../../..");
const GRAMMAR = join(
  REPO,
  "tools/vscode-extension/componentize-py/syntaxes/bigfix-relevance.tmLanguage.json",
);
const SCOPE = "source.bigfix-relevance";
const require = createRequire(import.meta.url);

const wasm = readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm"));
const registry = new vsctm.Registry({
  onigLib: oniguruma
    .loadWASM(wasm.buffer.slice(wasm.byteOffset, wasm.byteOffset + wasm.byteLength))
    .then(() => ({
      createOnigScanner: (patterns) => new oniguruma.OnigScanner(patterns),
      createOnigString: (text) => new oniguruma.OnigString(text),
    })),
  loadGrammar: async (scopeName) =>
    scopeName === SCOPE ? vsctm.parseRawGrammar(readFileSync(GRAMMAR, "utf8"), GRAMMAR) : null,
});
const textmate = await registry.loadGrammar(SCOPE);

/** Each character's class from the TextMate grammar: its innermost scope, mapped. */
function textmateClasses(text) {
  const classes = [];
  let state = vsctm.INITIAL;
  const lines = text.split("\n");
  lines.forEach((line, index) => {
    const result = textmate.tokenizeLine(line, state);
    state = result.ruleStack;
    for (const token of result.tokens) {
      const scope = token.scopes.at(-1);
      const name = scope === SCOPE ? null : TEXTMATE_TOKENS[scope];
      assert.ok(name !== undefined, `no CodeMirror token for TextMate scope ${scope}`);
      for (let i = token.startIndex; i < Math.min(token.endIndex, line.length); i++) classes.push(name);
    }
    if (index < lines.length - 1) classes.push(null); // the line break
  });
  return classes;
}

/** Each character's class from the generated StreamLanguage, through CodeMirror. */
function codemirrorClasses(text) {
  const state = CM.EditorState.create({ doc: text, extensions: [relevanceLanguage(CM)] });
  const tree = CM.ensureSyntaxTree(state, state.doc.length, 5000);
  assert.ok(tree, "the stream parser did not finish");
  const classes = new Array(text.length).fill(null);
  tree.iterate({
    enter(node) {
      if (node.type.isTop) return;
      for (let i = node.from; i < node.to; i++) classes[i] = node.type.name.replace(/_/g, " ");
    },
  });
  return classes;
}

function corpus() {
  const dir = join(REPO, "tests/corpus");
  const cases = [];
  for (const file of readdirSync(dir).filter((name) => name.endsWith(".rlvcorpus")).sort()) {
    let title = null;
    let source = [];
    let inExpected = false;
    const flush = () => {
      if (title !== null) cases.push({ id: `${file}: ${title}`, text: source.join("\n").trim() });
      title = null;
      source = [];
      inExpected = false;
    };
    for (const line of readFileSync(join(dir, file), "utf8").split(/\r?\n/)) {
      if (line.startsWith("====")) {
        flush();
        title = line.slice(4).trim() || "untitled";
      } else if (line.startsWith("----")) inExpected = true;
      else if (title !== null && !inExpected) source.push(line);
    }
    flush();
  }
  return cases;
}

function assertSameClasses(text, id = text) {
  // CodeMirror splits lines on \r as well; TextMate here only on \n.
  assert.ok(!text.includes("\r"), `${id}: no carriage returns in parity inputs`);
  const expected = textmateClasses(text);
  const actual = codemirrorClasses(text);
  for (let i = 0; i < text.length; i++) {
    if (actual[i] !== expected[i]) {
      assert.fail(
        `${id}: character ${i} (${JSON.stringify(text[i])}) in ${JSON.stringify(text)}: ` +
          `TextMate ${expected[i]}, CodeMirror ${actual[i]}`,
      );
    }
  }
}

// --- parity with the TextMate grammar ------------------------------------------------

test("every corpus statement gets the TextMate grammar's classes, character for character", () => {
  const cases = corpus();
  assert.ok(cases.length > 150, `only ${cases.length} corpus cases`);
  for (const { id, text } of cases) assertSameClasses(text, id);
});

test("comments and strings carry over line breaks, as in TextMate", () => {
  for (const text of [
    'exists file "a\nb" whose (it = "x")',
    "1 /* a\ncomment */ + 2",
    "/* unterminated\nand still a comment",
    '"unterminated\nstring and %41 more',
  ]) {
    assertSameClasses(text);
  }
});

test("operators match in any case, with articles between their words", () => {
  for (const text of [
    "1 IS NOT EQUAL TO 2",
    "x is not the equal to y",
    "a Does Not Contain b",
    "if it then true else FALSE",
    "names of bes computers whose (exists it)",
    "1 mod 2 starts with 3",
  ]) {
    assertSameClasses(text);
  }
});

test("words that merely contain an operator are not operators", () => {
  for (const text of ["origin of operand", "android of iterator", "isnot", "x1 + 1x", "a_and_b"]) {
    assertSameClasses(text);
  }
});

test("word boundaries are Unicode's, as in Oniguruma", () => {
  // JavaScript's own \\b knows only ASCII word characters: `\u00e9and` (an
  // e-acute, then `and`) would be read as a letter then the operator `and`.
  // Escapes, so the repo's ASCII hook leaves the letters alone.
  const E = "\u00e9"; // e-acute
  for (const text of [
    `${E}t${E} and x`,
    `${E}and x`,
    `x and${E}`,
    "na\u00efve or b",
    `1${E}`,
    `${E}1`,
    "\u017f is x", // long s: folds to `s` under case-insensitive matching
  ]) {
    assertSameClasses(text);
  }
});

test("word characters are Oniguruma's, not just letters and numbers", () => {
  // A circled letter is a word character to Oniguruma (Alphabetic); a circled
  // digit is not (No, not And); superscript two is.
  for (const text of ["\u24b6and x", "x \u2460and y", "False\u2460", "1\u00b2 and 2", "x and\u00b2"]) {
    assertSameClasses(text);
  }
});

test("white space inside an operator is Oniguruma's: NEL is, U+FEFF is not", () => {
  for (const text of ["is\u0085not x", "is\ufeffnot x", "is\u00a0not x", "1 is\tnot   equal  to 2", "a does  not\tcontain b"]) {
    assertSameClasses(text);
  }
});

test("a line past CodeMirror's 10,000 characters leaves the next line right", () => {
  // CodeMirror stops asking for tokens 10,000 characters into a line (VS Code
  // at 20,000). The rest of the line goes uncolored, but the state it ends in
  // must still be the true one: here a string closes past the cut.
  const long = "x ".repeat(5000) + 'xx"a" and 1';
  const next = 'exists file "b" and true';
  const text = `${long}\n${next}`;
  const expected = textmateClasses(text).slice(long.length + 1);
  const actual = codemirrorClasses(text).slice(long.length + 1);
  assert.deepEqual(actual, expected);
  assert.ok(codemirrorClasses(text).slice(10001, long.length).every((c) => c === null));
});

test("a long string of escapes tokenizes in linear time", () => {
  // Each escape once searched to the string's end: quadratic, about 9 s for
  // this 1 MB line (now well under 0.1 s). The bound leaves a slow CI runner
  // plenty of room and still fails the quadratic version.
  const line = '"' + "%41".repeat(333334) + '" and x';
  const started = performance.now();
  const state = CM.EditorState.create({ doc: line, extensions: [relevanceLanguage(CM)] });
  assert.ok(CM.ensureSyntaxTree(state, state.doc.length, 60000));
  const elapsed = performance.now() - started;
  assert.ok(elapsed < 3000, `${Math.round(elapsed)} ms for a 1 MB string of escapes`);
});

test("percent escapes inside a string, and not outside one", () => {
  assertSameClasses('"100%25 sure" & %41 & "%zz"');
});

// --- the module ------------------------------------------------------------------------

test("every TextMate scope of the relevance grammar has a CodeMirror token", () => {
  const grammar = JSON.parse(readFileSync(GRAMMAR, "utf8"));
  const scopes = new Set();
  const visit = (rule) => {
    if (rule.name) scopes.add(rule.name);
    for (const child of rule.patterns || []) visit(child);
  };
  for (const rule of Object.values(grammar.repository)) visit(rule);
  assert.deepEqual([...scopes].filter((scope) => !(scope in TEXTMATE_TOKENS)), []);
});

test("every token name is a highlighting tag CodeMirror knows", () => {
  const warnings = [];
  const warn = console.warn;
  console.warn = (...args) => warnings.push(args.join(" "));
  try {
    codemirrorClasses(
      'if exists it then "a%41" & /* c */ 1 else (true, false) ; x whose (it as string contains "y")',
    );
  } finally {
    console.warn = warn;
  }
  assert.deepEqual(warnings, []);
});

test("relevanceLanguage names what CM lacks", () => {
  assert.throws(() => relevanceLanguage({}), /CM lacks StreamLanguage/);
  assert.deepEqual(REQUIRED_CM.filter((name) => !(name in CM)), []);
});

test("the language comments in relevance's own block comments", () => {
  const state = CM.EditorState.create({ doc: "now", extensions: [relevanceLanguage(CM)] });
  assert.deepEqual(state.languageDataAt("commentTokens", 0), [{ block: { open: "/*", close: "*/" } }]);
});
