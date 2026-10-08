#!/usr/bin/env node
// End-to-end smoke test for either VS Code extension, in a real VS Code, with no
// person involved. Both extensions run the same check, so their results compare
// directly.
//
//     cd tools/vscode-extension/common/smoke && npm ci
//     node run.mjs <extension-dir> [--code <VS Code executable>] [--server <command> [args...]]
//
// @vscode/test-electron does the VS Code part. It downloads the version pinned
// as `vscodeVersion` in this directory's package.json into ./.vscode-test/
// (gitignored; reused on later runs), retrying a failed download and checking
// it against the SHA-256 the update server publishes. Then it starts that VS
// Code with the extension under development and suite.js as the test runner,
// in a throwaway profile, so nothing of yours is read or changed. A window
// opens briefly; in CI, xvfb-run provides the display.
//
// Scenarios, one VS Code launch each (suite.js reads SMOKE_SCENARIO):
//
//   lint  a workspace with a .rel and a fenced .md: the extension activates,
//         and the language server's diagnostics reach both files (and an
//         unsaved buffer, for an extension contributing the relevance language).
//   idle  only for an extension contributing that language (the primary
//         one): Markdown and HTML with no relevance in them must leave its
//         language server unstarted, and then a relevance-fenced Markdown file
//         must start it and get diagnostics.
//
// --code skips the download and uses an installed VS Code instead.
//
// --server applies only to an extension that starts an external server
// (python-stdio/, through `<prefix>.server.command`). It defaults to this
// checkout's own `.venv/bin/bigfix-relevance-lsp` (from `uv sync`), so the run
// tests the working tree rather than whatever is on PATH. The componentize-py/
// extension needs its component built first; see its build-component/.

import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { runTests } from "@vscode/test-electron";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..", "..", "..", "..");
const { vscodeVersion } = JSON.parse(readFileSync(join(HERE, "package.json"), "utf8"));

const [extensionArg, ...argv] = process.argv.slice(2);
if (!extensionArg) {
  throw new Error("usage: node run.mjs <extension-dir> [--code <path>] [--server <command> [args...]]");
}
const EXTENSION = resolve(extensionArg);
const manifest = JSON.parse(readFileSync(join(EXTENSION, "package.json"), "utf8"));
const PREFIX = manifest.settingsPrefix;
const SETTINGS = manifest.contributes.configuration.properties;

let code;
// uv puts a venv's scripts in Scripts\ with an .exe suffix on Windows.
let server = [
  process.platform === "win32"
    ? join(REPO, ".venv", "Scripts", "bigfix-relevance-lsp.exe")
    : join(REPO, ".venv", "bin", "bigfix-relevance-lsp"),
];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === "--code") code = argv[++i];
  else if (argv[i] === "--server") (server = argv.slice(i + 1)), (i = argv.length);
  else throw new Error(`unknown argument ${argv[i]}`);
}

const UNTITLED_LANGUAGE = manifest.contributes.languages?.[0]?.id ?? "";

const scenarios = {
  lint: {
    "broken.rel": 'exists file "unterminated\n',
    "fenced.md": "# Example\n\n```relevance\ntotally bogus made up inspector\n```\n",
  },
  ...(UNTITLED_LANGUAGE
    ? {
        idle: {
          "plain.md": "# Notes\n\n```python\nprint('relevance')\n```\n",
          "page.html": "<html><body><p>Relevance is a language.</p></body></html>\n",
          "fenced.md": "# Example\n\n```relevance\ntotally bogus made up inspector\n```\n",
        },
      }
    : {}),
};

/** Launch VS Code on a fresh workspace holding `files`; true when the suite passes. */
async function launch(scenario, files) {
  const scratch = mkdtempSync(join(tmpdir(), "bigfix-relevance-smoke-"));
  try {
    const workspace = join(scratch, "workspace");
    mkdirSync(join(workspace, ".vscode"), { recursive: true });
    for (const [name, text] of Object.entries(files)) writeFileSync(join(workspace, name), text);
    const settings = {};
    if (`${PREFIX}.server.command` in SETTINGS) {
      settings[`${PREFIX}.server.command`] = server[0];
      settings[`${PREFIX}.server.args`] = server.slice(1);
    }
    writeFileSync(join(workspace, ".vscode", "settings.json"), JSON.stringify(settings));
    const result = join(scratch, "result.json");

    const started = Date.now();
    let failure;
    try {
      await runTests({
        version: vscodeVersion,
        cachePath: join(HERE, ".vscode-test"),
        vscodeExecutablePath: code,
        extensionDevelopmentPath: EXTENSION,
        extensionTestsPath: join(HERE, "suite.js"),
        // An extension that contributes the relevance language also gets an
        // untitled buffer in it, which needs that language to reach the server.
        extensionTestsEnv: {
          SMOKE_SCENARIO: scenario,
          SMOKE_RESULT: result,
          SMOKE_UNTITLED_LANGUAGE: UNTITLED_LANGUAGE,
          SMOKE_EXTENSION_ID: `${manifest.publisher}.${manifest.name}`,
        },
        // A throwaway profile per run, rather than test-electron's default of
        // one shared under the cache directory.
        launchArgs: [
          workspace,
          `--user-data-dir=${join(scratch, "user-data")}`,
          `--extensions-dir=${join(scratch, "extensions")}`,
          "--new-window",
        ],
      });
    } catch (error) {
      failure = error;
    }
    const seconds = ((Date.now() - started) / 1000).toFixed(1);
    try {
      console.log(readFileSync(result, "utf8"));
    } catch {
      console.error(`smoke test (${scenario}) failed: VS Code produced no result`);
    }
    if (failure) {
      console.error(`smoke test (${scenario}) failed after ${seconds} s: ${failure.message ?? failure}`);
      return false;
    }
    console.log(
      `smoke test (${scenario}) passed: ${manifest.displayName} in VS Code ${vscodeVersion} ` +
        `(${seconds} s, including any download)`
    );
    return true;
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}

for (const [scenario, files] of Object.entries(scenarios)) {
  if (!(await launch(scenario, files))) process.exitCode = 1;
}
