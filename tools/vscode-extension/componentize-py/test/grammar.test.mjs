// The highlighting grammars, run through the TextMate engine VS Code itself
// uses (vscode-textmate with vscode-oniguruma). Run with
// `node --test test/grammar.test.mjs`.
//
// tests/test_actionscript_grammar.py checks each rule's regex with Python's
// `re`; this is the authority on how the rules behave together: begin/end and
// begin/while blocks, backreferences, `\G`, and one grammar embedded in
// another. Above all it pins that nothing in an ActionScript or relevance body
// can color past the end of that body, which would recolor the rest of a .bes.
//
// EXTENSION_DIR picks the grammars to test, as in server.test.mjs: this source
// tree by default, the unzipped .vsix in CI.
//
// The .bes grammar defers everything outside its bodies to VS Code's built-in
// XML grammar (`text.xml`), which ships with VS Code, not with this extension.
// The tests run against a copy vendored from VS Code's source in
// test/fixtures/xml/ (see its README), so every run, CI's included, checks the
// interplay with the real thing. VSCODE_XML_GRAMMAR names another copy (say,
// a newer VS Code's), and VSCODE_XML_GRAMMAR=none swaps in an empty stand-in.

import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import oniguruma from "vscode-oniguruma";
import vsctm from "vscode-textmate";

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTENSION = resolve(process.env.EXTENSION_DIR ?? join(HERE, ".."));
const REPO = resolve(HERE, "../../../..");
const require = createRequire(import.meta.url);

const SCOPES = {
  "source.bigfix-relevance": "syntaxes/bigfix-relevance.tmLanguage.json",
  "source.bigfix-actionscript": "syntaxes/bigfix-actionscript.tmLanguage.json",
  "text.xml.bigfix-bes": "syntaxes/bigfix-bes.tmLanguage.json",
};

/** VS Code's own XML grammar, if one is at hand. */
function xmlGrammarPath() {
  if (process.env.VSCODE_XML_GRAMMAR === "none") return undefined;
  return process.env.VSCODE_XML_GRAMMAR || join(HERE, "fixtures/xml/xml.tmLanguage.json");
}

const XML_GRAMMAR = xmlGrammarPath();

const wasm = readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm"));
const onigLib = oniguruma
  .loadWASM(wasm.buffer.slice(wasm.byteOffset, wasm.byteOffset + wasm.byteLength))
  .then(() => ({
    createOnigScanner: (patterns) => new oniguruma.OnigScanner(patterns),
    createOnigString: (text) => new oniguruma.OnigString(text),
  }));

const registry = new vsctm.Registry({
  onigLib,
  async loadGrammar(scopeName) {
    if (scopeName === "text.xml") {
      if (XML_GRAMMAR === undefined) return { scopeName, patterns: [] };
      return vsctm.parseRawGrammar(readFileSync(XML_GRAMMAR, "utf8"), XML_GRAMMAR);
    }
    const path = SCOPES[scopeName];
    if (path === undefined) return null;
    const file = join(EXTENSION, path);
    return vsctm.parseRawGrammar(readFileSync(file, "utf8"), file);
  },
});

/** Each line of `text` as `[{ text, scopes }]` tokens, and the state at the end. */
async function tokenize(scopeName, text) {
  const grammar = await registry.loadGrammar(scopeName);
  assert.ok(grammar, `no grammar for ${scopeName}`);
  let state = vsctm.INITIAL;
  const lines = text.split("\n").map((line) => {
    const result = grammar.tokenizeLine(line, state);
    state = result.ruleStack;
    return result.tokens.map((token) => ({
      text: line.slice(token.startIndex, token.endIndex),
      scopes: token.scopes,
    }));
  });
  return { lines, state };
}

/** The scopes of the token holding `word` on the line that contains `marker`. */
function scopesOf(tokenized, marker, word = marker) {
  const line = tokenized.lines.find((tokens) => tokens.map((t) => t.text).join("").includes(marker));
  assert.ok(line, `no line with ${JSON.stringify(marker)}`);
  const joined = line.map((t) => t.text).join("");
  const at = joined.indexOf(word, joined.indexOf(marker));
  assert.ok(at >= 0, `no ${JSON.stringify(word)} from ${JSON.stringify(marker)} on`);
  let position = 0;
  for (const token of line) {
    if (at < position + token.text.length) return token.scopes;
    position += token.text.length;
  }
  assert.fail(`no ${JSON.stringify(word)} after ${JSON.stringify(marker)}`);
}

const has = (scopes, prefix) => scopes.some((scope) => scope.startsWith(prefix));
const COMMAND = "keyword.other.command.bigfix-actionscript";
const CONTROL = "keyword.control.bigfix-actionscript";
const RELEVANCE = "meta.embedded.line.bigfix-relevance";
const HEREDOC = "string.unquoted.heredoc.bigfix-actionscript";
const AS_BODY = "meta.embedded.block.bigfix-actionscript";
const REL_BODY = "meta.embedded.block.bigfix-relevance";

/** No ActionScript or relevance scope on the line that contains `marker`. */
function assertPlainXml(tokenized, marker) {
  const line = tokenized.lines.find((tokens) => tokens.map((t) => t.text).join("").includes(marker));
  assert.ok(line, marker);
  for (const token of line) {
    assert.ok(
      !token.scopes.some((s) => s.includes("bigfix-actionscript") || s.includes("bigfix-relevance")),
      `${JSON.stringify(token.text)} on ${JSON.stringify(marker)}: ${token.scopes.join(" ")}`
    );
  }
}

// ---------------------------------------------------------------------------
// ActionScript on its own
// ---------------------------------------------------------------------------

test("a verb is colored at line start only, never as a later argument", async () => {
  const t = await tokenize("source.bigfix-actionscript", "wait run.exe\nRUN wait.exe\n  download now as x http://h/x");
  assert.ok(scopesOf(t, "wait run.exe", "wait").includes(COMMAND));
  assert.ok(!scopesOf(t, "wait run.exe", "run").includes(COMMAND));
  assert.ok(scopesOf(t, "RUN wait.exe", "RUN").includes(COMMAND));
  assert.ok(!scopesOf(t, "RUN wait.exe", "wait").includes(COMMAND));
  const download = scopesOf(t, "download now as");
  assert.ok(download.includes(COMMAND));
});

test("a verb is never the prefix of a longer word", async () => {
  const t = await tokenize("source.bigfix-actionscript", "runner x\nrunhidden y");
  assert.ok(!scopesOf(t, "runner", "run").includes(COMMAND));
  assert.ok(scopesOf(t, "runhidden").includes(COMMAND));
});

test("flow control is colored apart from commands, conditions included", async () => {
  const t = await tokenize("source.bigfix-actionscript", 'if{exists file "x"}\nelse\nendif');
  assert.ok(scopesOf(t, "if{", "if").includes(CONTROL));
  assert.ok(scopesOf(t, "else").includes(CONTROL));
  assert.ok(has(scopesOf(t, "if{", "exists"), RELEVANCE));
});

test("a substitution's body is the relevance grammar", async () => {
  const t = await tokenize("source.bigfix-actionscript", 'wait "{pathname of file "x" of system folder}" /s');
  const of = scopesOf(t, "pathname", "of");
  assert.ok(of.includes(RELEVANCE));
  assert.ok(has(of, "keyword.operator.of.bigfix-relevance"));
  assert.ok(has(scopesOf(t, "pathname", '"x"'), "string.quoted.double.bigfix-relevance"));
});

test("doubled braces are literal, and template placeholders open nothing", async () => {
  const t = await tokenize("source.bigfix-actionscript", "x {{ template }} {a }} b}\nrun y");
  assert.ok(!scopesOf(t, "{{ template", "template").includes(RELEVANCE));
  assert.ok(scopesOf(t, "{a", "b").includes(RELEVANCE));
  assert.ok(scopesOf(t, "run y", "run").includes(COMMAND));
});

test("// is a comment at line start only; a URL is not a comment", async () => {
  const t = await tokenize("source.bigfix-actionscript", "// note\ndownload http://h/x.exe // not a comment");
  assert.ok(has(scopesOf(t, "// note"), "comment.line.double-slash"));
  const url = scopesOf(t, "download", "http://h/x.exe");
  assert.ok(has(url, "markup.underline.link"));
  assert.ok(!has(scopesOf(t, "download", "not a comment"), "comment"));
});

test("a string has no escape character", async () => {
  const t = await tokenize("source.bigfix-actionscript", 'run "C:\\Bes\\" /x');
  assert.ok(!has(scopesOf(t, "run", "/x"), "string"));
});

test("an unterminated string or brace stops at its line", async () => {
  const t = await tokenize("source.bigfix-actionscript", 'run "open\nwait x\nrun {exists file\nwait y');
  assert.ok(scopesOf(t, "wait x", "wait").includes(COMMAND));
  assert.ok(!has(scopesOf(t, "wait x", "x"), "string"));
  assert.ok(scopesOf(t, "wait y", "wait").includes(COMMAND));
  assert.ok(!scopesOf(t, "run {exists", "exists").includes(RELEVANCE));
});

test("a heredoc is raw text with substitutions, up to its marker line", async () => {
  const text = [
    "createfile until __END__",
    "run not-a-command // not a comment",
    "{name of operating system}",
    "  __END__  ",
    "run c:\\x.exe",
  ].join("\n");
  const t = await tokenize("source.bigfix-actionscript", text);
  assert.ok(scopesOf(t, "createfile until", "createfile").includes(COMMAND));
  const inside = scopesOf(t, "run not-a-command", "run");
  assert.ok(inside.includes(HEREDOC) && !inside.includes(COMMAND));
  assert.ok(!has(scopesOf(t, "not a comment"), "comment"));
  assert.ok(scopesOf(t, "{name of", "name").includes(RELEVANCE));
  assert.ok(!scopesOf(t, "__END__  ", "__END__").includes(HEREDOC));
  assert.ok(scopesOf(t, "run c:", "run").includes(COMMAND));
});

test("appendfile text is file content", async () => {
  const t = await tokenize("source.bigfix-actionscript", "appendfile run {name of it}\nrun x");
  assert.ok(!scopesOf(t, "appendfile run", "run").includes(COMMAND));
  assert.ok(scopesOf(t, "appendfile run", "name").includes(RELEVANCE));
  assert.ok(scopesOf(t, "run x", "run").includes(COMMAND));
});

test("blank and comment lines inside an override block do not end it", async () => {
  // As pre-commit-bigfix's lint reads the block: only a command line closes it.
  const text = "override wait\nhidden=true\n\n// note\n  \ncompletion=job\nwait foo.exe";
  const t = await tokenize("source.bigfix-actionscript", text);
  assert.ok(has(scopesOf(t, "completion=job", "completion"), "variable.parameter.option"));
  assert.ok(has(scopesOf(t, "// note"), "comment.line.double-slash"));
  assert.ok(scopesOf(t, "wait foo", "wait").includes(COMMAND));
});

test("an override block holds option lines up to its command", async () => {
  const t = await tokenize("source.bigfix-actionscript", "override wait\nhidden=true\nRunAs={x}\nwait cmd.exe\nhidden=x");
  assert.ok(has(scopesOf(t, "hidden=true", "hidden"), "variable.parameter.option"));
  assert.ok(scopesOf(t, "RunAs=", "x").includes(RELEVANCE));
  assert.ok(scopesOf(t, "wait cmd", "wait").includes(COMMAND));
  assert.ok(!has(scopesOf(t, "hidden=x", "hidden"), "variable.parameter.option"));
});

// ---------------------------------------------------------------------------
// BES XML
// ---------------------------------------------------------------------------

const BES = `<?xml version="1.0" encoding="UTF-8"?>
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<Task>
<Title>t</Title>
<Relevance>exists file "x" whose (version of it &lt; "2")</Relevance>
<Relevance><![CDATA[not exists folder "y"]]></Relevance>
<DefaultAction ID="Action1">
<ActionScript MIMEType="application/x-Fixlet-Windows-Shell"><![CDATA[// comment
wait "{pathname of regapp "x"}" /s
]]></ActionScript>
<SuccessCriteria Option="CustomRelevance">exists running application "z"</SuccessCriteria>
</DefaultAction>
<Action ID="Action2">
<ActionScript>run escaped &amp; "{name of it}"</ActionScript>
<ActionScript MIMEType="application/x-sh">run {not relevance}</ActionScript>
<SuccessCriteria Option="OriginalRelevance"></SuccessCriteria>
</Action>
</Task>
<Analysis><Property Name="v" ID="1">version of client</Property></Analysis>
<Title>after the bodies</Title>
</BES>`;

test("CDATA and entity-escaped ActionScript are both ActionScript", async () => {
  const t = await tokenize("text.xml.bigfix-bes", BES);
  assert.ok(has(scopesOf(t, "// comment"), "comment.line.double-slash"));
  assert.ok(scopesOf(t, "// comment").includes(AS_BODY));
  assert.ok(scopesOf(t, 'wait "{', "wait").includes(COMMAND));
  assert.ok(scopesOf(t, 'wait "{', "regapp").includes(RELEVANCE));
  assert.ok(scopesOf(t, "run escaped", "run").includes(COMMAND));
  assert.ok(has(scopesOf(t, "run escaped", "&amp;"), "constant.character.entity.xml"));
});

test("ActionScript of another MIME type stays XML", async () => {
  const t = await tokenize("text.xml.bigfix-bes", BES);
  assertPlainXml(t, "run {not relevance}");
});

test("relevance bodies carry relevance scopes, CDATA or not", async () => {
  const t = await tokenize("text.xml.bigfix-bes", BES);
  assert.ok(scopesOf(t, 'exists file "x"', "whose").includes(REL_BODY));
  assert.ok(has(scopesOf(t, 'exists file "x"', "whose"), "keyword.control.filter.bigfix-relevance"));
  assert.ok(has(scopesOf(t, 'exists file "x"', "&lt;"), "constant.character.entity.xml"));
  assert.ok(scopesOf(t, 'not exists folder', "folder").includes(REL_BODY));
  assert.ok(scopesOf(t, "exists running application", "exists").includes(REL_BODY));
  assert.ok(scopesOf(t, "version of client", "of").includes(REL_BODY));
});

test("the real XML grammar is the one in use, unless the stand-in is asked for", async () => {
  // Guards against a fixture path that quietly falls back to the stand-in.
  const t = await tokenize("text.xml.bigfix-bes", "<BES><Title>t</Title></BES>");
  const tag = has(scopesOf(t, "<BES>", "BES"), "entity.name.tag");
  assert.equal(tag, XML_GRAMMAR !== undefined);
});

test("an ActionScript start tag may span lines", async () => {
  const text = [
    "<BES><Fixlet>",
    "<ActionScript",
    '\tMIMEType="application/x-Fixlet-Windows-Shell"><![CDATA[',
    "wait {x}",
    "]]></ActionScript>",
    "<ActionScript",
    '   ID="2"',
    "   >run y</ActionScript>",
    "<Title>after</Title>",
    "</Fixlet></BES>",
  ].join("\n");
  const t = await tokenize("text.xml.bigfix-bes", text);
  assert.ok(scopesOf(t, "wait {x}", "wait").includes(COMMAND));
  assert.ok(scopesOf(t, "wait {x}", "x").includes(RELEVANCE));
  assert.ok(has(scopesOf(t, "MIMEType=", "MIMEType"), "entity.other.attribute-name"));
  assert.ok(scopesOf(t, ">run y", "run").includes(COMMAND));
  assertPlainXml(t, "<Title>after</Title>");
  assert.equal(t.state.depth, 1);
});

test("another MIME type on a later line of the start tag stays XML", async () => {
  const text = [
    "<BES><Fixlet>",
    "<ActionScript",
    '  MIMEType="application/x-sh"><![CDATA[run {not relevance}',
    "wait x]]></ActionScript>",
    "<Title>after</Title>",
    "</Fixlet></BES>",
  ].join("\n");
  const t = await tokenize("text.xml.bigfix-bes", text);
  assertPlainXml(t, "run {not relevance}");
  assertPlainXml(t, "wait x");
  assertPlainXml(t, "<Title>after</Title>");
  assert.equal(t.state.depth, 1);
});

test("a > inside an attribute value does not end the start tag", async () => {
  const text = [
    '<BES><Fixlet><Relevance Comment="a > b">exists x</Relevance>',
    '<ActionScript Comment="a > b">wait y</ActionScript>',
    '<SuccessCriteria Comment=">" Option="CustomRelevance">exists z</SuccessCriteria>',
    "<Title>after</Title></Fixlet></BES>",
  ].join("\n");
  const t = await tokenize("text.xml.bigfix-bes", text);
  assert.ok(has(scopesOf(t, "exists x", "exists"), "keyword.operator.logical.bigfix-relevance"));
  assert.ok(!scopesOf(t, "<Relevance Comment", " b").includes(REL_BODY));
  assert.ok(scopesOf(t, "wait y", "wait").includes(COMMAND));
  assert.ok(!scopesOf(t, "<ActionScript Comment", " b").includes(AS_BODY));
  assert.ok(scopesOf(t, "exists z", "exists").includes(REL_BODY));
  assertPlainXml(t, "<Title>after</Title>");
});

test("another MIME type's start tag is still colored as a tag", async () => {
  // 26 real PowerShell and text/x-uri action scripts (PR #119 review).
  const text = [
    "<BES><Fixlet>",
    '<ActionScript MIMEType="application/x-Fixlet-Windows-PowerShell" ID="7"><![CDATA[$x = "{y}"',
    "]]></ActionScript>",
    "<Title>after</Title>",
    "</Fixlet></BES>",
  ].join("\n");
  const t = await tokenize("text.xml.bigfix-bes", text);
  assert.ok(has(scopesOf(t, "PowerShell", 'ID'), "entity.other.attribute-name"));
  assert.ok(has(scopesOf(t, '"7">', '>'), "punctuation.definition.tag"));
  assertPlainXml(t, '$x = "{y}"');
  assertPlainXml(t, "<Title>after</Title>");
  assert.equal(t.state.depth, 1);
});

test("a self-closing ActionScript of another MIME type ends its element", async () => {
  const text = '<BES><ActionScript MIMEType="application/x-sh"/>\n<ActionScript>wait x</ActionScript>\n<Title>after</Title></BES>';
  const t = await tokenize("text.xml.bigfix-bes", text);
  assert.ok(scopesOf(t, "wait x", "wait").includes(COMMAND));
  assertPlainXml(t, "<Title>after</Title>");
  assert.equal(t.state.depth, 1);
});

test("a self-closing ActionScript has no body", async () => {
  const t = await tokenize("text.xml.bigfix-bes", "<BES><ActionScript/>\n<ActionScript\n />\n<Title>after</Title></BES>");
  assertPlainXml(t, "<Title>after</Title>");
  assert.equal(t.state.depth, 1);
});

test("a relevance start tag split across lines is left uncolored, without leaking", async () => {
  // A known limitation (README): no real content splits these tags, unlike
  // <ActionScript>, and the Option="CustomRelevance" check needs the whole tag.
  const t = await tokenize("text.xml.bigfix-bes", "<BES><Relevance\n>exists x</Relevance>\n<Title>after</Title></BES>");
  assertPlainXml(t, ">exists x</Relevance>");
  assertPlainXml(t, "<Title>after</Title>");
  assert.equal(t.state.depth, 1);
});

test("XML outside the bodies is left to the XML grammar", async () => {
  const t = await tokenize("text.xml.bigfix-bes", BES);
  for (const marker of ["<Title>t</Title>", "after the bodies", "</BES>", 'Option="OriginalRelevance"']) {
    assertPlainXml(t, marker);
  }
  assert.equal(t.state.depth, 1, "a rule is still open at the end of the file");
});

// The leaks that matter: each broken body below must end at its own
// `]]></ActionScript>`, leaving the next element plain XML.
const BROKEN_BODIES = {
  "unclosed heredoc": "createfile until END\nnever closed",
  "unclosed heredoc on the CDATA line": "createfile until END\nx]]>",
  // The marker itself touching the end of the body (PR #119 review).
  "heredoc marker against the body end": "createfile until END",
  "unterminated string": 'run "open',
  "unclosed substitution": "run {exists file",
  "unclosed substitution string": 'run {exists file "x}',
  "comment on the last line": "// done",
  "appendfile on the last line": "appendfile text",
  "open override": "override wait\nhidden=true",
  "open override ending in a blank line": "override wait\nhidden=true\n",
  "url on the last line": "download http://h/x",
};

for (const [name, body] of Object.entries(BROKEN_BODIES)) {
  for (const cdata of [true, false]) {
    test(`a body with ${name} ends at its element${cdata ? " (CDATA)" : ""}`, async () => {
      const wrapped = cdata && !body.endsWith("]]>") ? `<![CDATA[${body}]]>` : body;
      const text = `<BES><Task>\n<ActionScript>${wrapped}</ActionScript>\n<Title>after</Title>\n</Task></BES>`;
      const t = await tokenize("text.xml.bigfix-bes", text);
      assertPlainXml(t, "<Title>after</Title>");
      assert.equal(t.state.depth, 1);
    });
  }
}

// Relevance strings and comments may span lines (in a .rel file they do), so
// one left open in a .bes body must still end at the body's end tag.
const BROKEN_RELEVANCE = {
  "unterminated string": '<Relevance>exists file "open</Relevance>',
  "unterminated string (CDATA)": '<Relevance><![CDATA[exists file "open]]></Relevance>',
  "unclosed comment": "<Relevance>/* open</Relevance>",
  "unterminated property string": '<Property Name="p" ID="1">name of file "x</Property>',
  "unterminated custom criteria": '<SuccessCriteria Option="CustomRelevance">"x</SuccessCriteria>',
};

for (const [name, element] of Object.entries(BROKEN_RELEVANCE)) {
  test(`relevance with an ${name} ends at its element`, async () => {
    const t = await tokenize("text.xml.bigfix-bes", `<BES><Task>\n${element}\n<Title>"after"</Title>\n</Task></BES>`);
    assertPlainXml(t, '<Title>"after"</Title>');
    assert.equal(t.state.depth, 1);
  });
}

test("a relevance string spanning lines in a body is still one string", async () => {
  const t = await tokenize("text.xml.bigfix-bes", '<Relevance>exists file "a\nb" whose (true)</Relevance>');
  assert.ok(has(scopesOf(t, 'b" whose', "b"), "string.quoted.double.bigfix-relevance"));
  assert.ok(has(scopesOf(t, 'b" whose', "whose"), "keyword.control.filter.bigfix-relevance"));
});

test("every .bes in the repository's tests tokenizes and closes every rule", async () => {
  const examples = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) walk(path);
      else if (entry.name.endsWith(".bes")) examples.push(path);
    }
  };
  const roots = [join(REPO, "tests/examples"), join(REPO, "tests/golden")];
  if (!existsSync(roots[0])) return; // the unzipped .vsix alone has no repository
  for (const root of roots) walk(root);
  assert.ok(examples.length > 0);
  for (const path of examples) {
    const t = await tokenize("text.xml.bigfix-bes", readFileSync(path, "utf8").replace(/\r\n?/g, "\n"));
    assert.equal(t.state.depth, 1, path);
  }
});

test("a large action tokenizes quickly", async () => {
  // About 1 MiB, the size past which the server stops linting a file.
  const body = Array.from({ length: 16000 }, (_, i) =>
    i % 4 === 0 ? `if {exists file "c:\\f${i}.txt"}` : i % 4 === 3 ? "endif" : `download now as f${i} http://h/f${i}`
  ).join("\n");
  const started = performance.now();
  const t = await tokenize("text.xml.bigfix-bes", `<BES><ActionScript><![CDATA[${body}]]></ActionScript></BES>`);
  const elapsed = performance.now() - started;
  assert.equal(t.state.depth, 1);
  assert.ok(elapsed < 10000, `${Math.round(elapsed)} ms`);
});
