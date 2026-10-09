// Runs inside the VS Code extension host that run.mjs starts: VS Code loads
// this file as the --extensionTestsPath and calls run(). Rejecting fails the
// run, and VS Code exits non-zero.
//
// SMOKE_SCENARIO picks the check (run.mjs describes both):
//
//   lint  opens two real files from the workspace run.mjs prepared and waits
//         for the language server's diagnostics on each. That proves the whole
//         chain: the extension activates, starts the configured server, sends
//         the document, and the server's diagnostics reach VS Code.
//   idle  opens Markdown and HTML with no relevance in them and checks the
//         extension has not started its language server (its activate()
//         returns `serverRunning()`), then opens a relevance-fenced Markdown
//         file and checks that starts it and gets diagnostics.

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vscode = require("vscode");

const SOURCE = "bigfix-relevance-analyzer";
const TIMEOUT_MS = 60_000;
// How long the idle scenario gives the server to (wrongly) start.
const IDLE_MS = 3_000;

function ours(uri) {
  return vscode.languages.getDiagnostics(uri).filter((d) => d.source === SOURCE);
}

/** Resolves with this file's diagnostics once `ready` accepts them. */
function waitFor(uri, ready) {
  return new Promise((resolve, reject) => {
    const check = () => {
      const found = ours(uri);
      if (ready(found)) {
        clearTimeout(timer);
        subscription.dispose();
        resolve(found);
      }
    };
    const timer = setTimeout(() => {
      subscription.dispose();
      reject(new Error(`no diagnostics for ${uri.fsPath} within ${TIMEOUT_MS} ms`));
    }, TIMEOUT_MS);
    const subscription = vscode.languages.onDidChangeDiagnostics(check);
    check();
  });
}

const summary = (found) =>
  found.map((d) => ({
    code: typeof d.code === "object" ? d.code.value : d.code,
    severity: vscode.DiagnosticSeverity[d.severity],
    line: d.range.start.line + 1,
    characters: [d.range.start.character, d.range.end.character],
    message: d.message,
  }));

async function lint() {
  const folder = vscode.workspace.workspaceFolders[0].uri.fsPath;
  const broken = vscode.Uri.file(path.join(folder, "broken.rel"));
  const fenced = vscode.Uri.file(path.join(folder, "fenced.md"));

  const started = Date.now();
  await vscode.window.showTextDocument(broken);
  const brokenFound = await waitFor(broken, (found) => found.length > 0);
  const firstMs = Date.now() - started;

  await vscode.window.showTextDocument(fenced);
  const fencedFound = await waitFor(fenced, (found) => found.length > 0);

  // Hover (issue #96, item 2), on the unknown name the diagnostic is about.
  const hovers = await vscode.commands.executeCommand(
    "vscode.executeHoverProvider",
    fenced,
    new vscode.Position(3, 9)
  );
  const hoverText = hovers
    .flatMap((hover) => hover.contents)
    .map((content) => (typeof content === "string" ? content : content.value))
    .join("\n");
  const hoverRange = hovers[0]?.range;

  // An unsaved buffer has no file name, so only its language says it is
  // relevance (see LANGUAGE_ID in src/bigfix_relevance_analyzer/lsp/linter.py).
  let untitledFound;
  const language = process.env.SMOKE_UNTITLED_LANGUAGE;
  if (language) {
    const untitled = await vscode.workspace.openTextDocument({
      language,
      content: 'exists file "unterminated',
    });
    await vscode.window.showTextDocument(untitled);
    untitledFound = await waitFor(untitled.uri, (found) => found.length > 0);
  }

  const result = {
    vscode: vscode.version,
    firstDiagnosticsMs: firstMs,
    "broken.rel": summary(brokenFound),
    "fenced.md": summary(fencedFound),
    "fenced.md hover": hoverText,
    "fenced.md hover range": hoverRange && [
      [hoverRange.start.line, hoverRange.start.character],
      [hoverRange.end.line, hoverRange.end.character],
    ],
    ...(untitledFound ? { [`untitled (${language})`]: summary(untitledFound) } : {}),
  };
  fs.writeFileSync(process.env.SMOKE_RESULT, JSON.stringify(result, null, 2));

  const codeOf = (d) => (typeof d.code === "object" ? d.code.value : d.code);
  const codes = new Set(brokenFound.map(codeOf));
  if (!codes.has("error-token")) {
    throw new Error(`broken.rel: expected an error-token diagnostic, got ${[...codes]}`);
  }
  // Precise ranges (issue #96, item 1): the unterminated string, not the line.
  for (const [name, found] of [["broken.rel", brokenFound], ["untitled", untitledFound]]) {
    if (!found) continue;
    const token = found.find((d) => codeOf(d) === "error-token");
    if (!token || token.range.start.character !== 12) {
      throw new Error(`${name}: expected error-token from character 12, got ${JSON.stringify(summary(found))}`);
    }
  }
  // The fence opens on line 3, so its statement is on line 4: proves line
  // mapping from an extracted site back to the document.
  if (!fencedFound.some((d) => d.range.start.line === 3)) {
    throw new Error(`fenced.md: expected a diagnostic on line 4, got ${JSON.stringify(summary(fencedFound))}`);
  }
  // ...and the column: the unknown name, after `exists `, within the fence.
  const unknown = fencedFound.find((d) => codeOf(d) === "unknown-inspector");
  if (!unknown || unknown.range.start.line !== 3 || unknown.range.start.character !== 7) {
    throw new Error(`fenced.md: expected unknown-inspector at line 4, character 7, got ${JSON.stringify(summary(fencedFound))}`);
  }
  // Hover (issue #96, item 2) on that same unknown name: its text, and a range
  // over exactly the name (characters 7 to 38), mapped back through the fence.
  if (!hoverText.includes("`totally bogus made up inspector`") || !hoverText.includes("not defined")) {
    throw new Error(`fenced.md: expected a hover on the unknown name, got ${JSON.stringify(hoverText)}`);
  }
  const expectedRange = [[3, 7], [3, 38]];
  if (JSON.stringify(result["fenced.md hover range"]) !== JSON.stringify(expectedRange)) {
    throw new Error(`fenced.md: expected the hover over ${JSON.stringify(expectedRange)}, got ${JSON.stringify(result["fenced.md hover range"])}`);
  }
}

async function idle() {
  const id = process.env.SMOKE_EXTENSION_ID;
  const extension = vscode.extensions.getExtension(id);
  if (!extension) throw new Error(`extension ${id} is not loaded`);
  const api = await extension.activate();
  const folder = vscode.workspace.workspaceFolders[0].uri.fsPath;
  const uri = (name) => vscode.Uri.file(path.join(folder, name));
  const quiet = [uri("plain.md"), uri("page.html")];
  for (const file of quiet) await vscode.window.showTextDocument(file);
  await new Promise((resolve) => setTimeout(resolve, IDLE_MS));
  const result = {
    vscode: vscode.version,
    serverRunningWithoutRelevance: api?.serverRunning?.(),
    diagnosticsWithoutRelevance: quiet.flatMap((file) => summary(ours(file))),
  };
  const write = () => fs.writeFileSync(process.env.SMOKE_RESULT, JSON.stringify(result, null, 2));
  if (result.serverRunningWithoutRelevance !== false || result.diagnosticsWithoutRelevance.length) {
    write();
    throw new Error("the server started for Markdown and HTML with no relevance in them");
  }

  const fenced = uri("fenced.md");
  await vscode.window.showTextDocument(fenced);
  result["fenced.md"] = summary(await waitFor(fenced, (found) => found.length > 0));
  result.serverRunningAfterFence = api.serverRunning();
  write();
  if (!result.serverRunningAfterFence) throw new Error("serverRunning() is false after diagnostics arrived");
}

function run() {
  const scenario = process.env.SMOKE_SCENARIO;
  if (scenario === "lint") return lint();
  if (scenario === "idle") return idle();
  return Promise.reject(new Error(`unknown SMOKE_SCENARIO ${scenario}`));
}

module.exports = { run };
