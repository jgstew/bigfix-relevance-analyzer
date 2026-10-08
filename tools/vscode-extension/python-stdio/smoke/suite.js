// Runs inside the VS Code extension host that run.mjs starts: VS Code loads
// this file as the --extensionTestsPath and calls run(). Rejecting fails the
// run, and VS Code exits non-zero.
//
// It opens two real files from the workspace run.mjs prepared and waits for the
// language server's diagnostics on each. That proves the whole chain: the
// extension activates, starts the configured server, sends the document, and
// the server's diagnostics reach VS Code.

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vscode = require("vscode");

const SOURCE = "bigfix-relevance-analyzer";
const TIMEOUT_MS = 60_000;

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

async function run() {
  const folder = vscode.workspace.workspaceFolders[0].uri.fsPath;
  const broken = vscode.Uri.file(path.join(folder, "broken.rel"));
  const fenced = vscode.Uri.file(path.join(folder, "fenced.md"));

  const started = Date.now();
  await vscode.window.showTextDocument(broken);
  const brokenFound = await waitFor(broken, (found) => found.length > 0);
  const firstMs = Date.now() - started;

  await vscode.window.showTextDocument(fenced);
  const fencedFound = await waitFor(fenced, (found) => found.length > 0);

  const summary = (found) =>
    found.map((d) => ({
      code: typeof d.code === "object" ? d.code.value : d.code,
      severity: vscode.DiagnosticSeverity[d.severity],
      line: d.range.start.line + 1,
      message: d.message,
    }));
  const result = {
    vscode: vscode.version,
    firstDiagnosticsMs: firstMs,
    "broken.rel": summary(brokenFound),
    "fenced.md": summary(fencedFound),
  };
  fs.writeFileSync(process.env.SMOKE_RESULT, JSON.stringify(result, null, 2));

  const codes = new Set(brokenFound.map((d) => (typeof d.code === "object" ? d.code.value : d.code)));
  if (!codes.has("error-token")) {
    throw new Error(`broken.rel: expected an error-token diagnostic, got ${[...codes]}`);
  }
  // The fence opens on line 3, so its statement is on line 4: proves line
  // mapping from an extracted site back to the document.
  if (!fencedFound.some((d) => d.range.start.line === 3)) {
    throw new Error(`fenced.md: expected a diagnostic on line 4, got ${JSON.stringify(summary(fencedFound))}`);
  }
}

module.exports = { run };
