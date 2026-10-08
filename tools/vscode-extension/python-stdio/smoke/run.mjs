#!/usr/bin/env node
// End-to-end smoke test for PoC 1, in a real VS Code with no person involved.
//
//     node smoke/run.mjs [--code <VS Code executable>] [--server <command> [args...]]
//
// Starts an isolated VS Code instance (throwaway user-data and extensions
// directories, so nothing of yours is read or changed) with this extension
// under development and smoke/suite.js as its test runner. suite.js opens two
// files and waits for the language server's diagnostics. A window opens
// briefly while it runs.
//
// The server defaults to this checkout's own `.venv/bin/bigfix-relevance-lsp`
// (from `uv sync`), so the run tests the working tree, not whatever is on PATH.
//
// No @vscode/test-electron: that downloads a separate VS Code build, which is
// what CI would want but more than a proof of concept needs. Point --code at an
// installed VS Code instead. It defaults to the standard macOS location.

import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTENSION = resolve(HERE, "..");
const REPO = resolve(EXTENSION, "..", "..", "..");
const PREFIX = JSON.parse(readFileSync(join(EXTENSION, "package.json"), "utf8")).settingsPrefix;

const argv = process.argv.slice(2);
let code = "/Applications/Visual Studio Code.app/Contents/MacOS/Code";
let server = [join(REPO, ".venv", "bin", "bigfix-relevance-lsp")];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === "--code") code = argv[++i];
  else if (argv[i] === "--server") server = argv.slice(i + 1), (i = argv.length);
  else throw new Error(`unknown argument ${argv[i]}`);
}
if (!existsSync(code)) throw new Error(`no VS Code at ${code}; pass --code`);

const scratch = mkdtempSync(join(tmpdir(), "bigfix-relevance-smoke-"));
try {
  const workspace = join(scratch, "workspace");
  mkdirSync(join(workspace, ".vscode"), { recursive: true });
  writeFileSync(join(workspace, "broken.rel"), 'exists file "unterminated\n');
  writeFileSync(
    join(workspace, "fenced.md"),
    "# Example\n\n```relevance\ntotally bogus made up inspector\n```\n"
  );
  writeFileSync(
    join(workspace, ".vscode", "settings.json"),
    JSON.stringify({
      [`${PREFIX}.server.command`]: server[0],
      [`${PREFIX}.server.args`]: server.slice(1),
    })
  );
  const result = join(scratch, "result.json");

  const run = spawnSync(
    code,
    [
      workspace,
      `--extensionDevelopmentPath=${EXTENSION}`,
      `--extensionTestsPath=${join(HERE, "suite.js")}`,
      `--user-data-dir=${join(scratch, "user-data")}`,
      `--extensions-dir=${join(scratch, "extensions")}`,
      "--disable-workspace-trust",
      "--skip-welcome",
      "--skip-release-notes",
      "--new-window",
    ],
    {
      stdio: ["ignore", "inherit", "inherit"],
      env: { ...process.env, SMOKE_RESULT: result, ELECTRON_RUN_AS_NODE: undefined },
      timeout: 180_000,
    }
  );
  if (run.error) throw run.error;
  if (!existsSync(result)) {
    console.error(`smoke test failed: VS Code exited ${run.status} without a result`);
    process.exit(1);
  }
  console.log(readFileSync(result, "utf8"));
  if (run.status !== 0) {
    console.error(`smoke test failed: VS Code exited ${run.status}`);
    process.exit(1);
  }
  console.log("smoke test passed");
} finally {
  rmSync(scratch, { recursive: true, force: true });
}
