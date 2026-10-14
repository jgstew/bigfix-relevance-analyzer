// The language-server script both playground pages run (#142 H1): the parity
// test compares the two pages' replies byte for byte, and both browser tests
// check what an editor needs from them.
//
// One copy, imported by relative path, for the same reason as cases.mjs.
//
// runLspScript runs *inside the page* (page.evaluate serializes it), so it must
// stay self-contained: no imports, no closures, only window.lspHandle and
// window.lspExitCode, the seam each page's boot() sets.

/** Statements the script opens, beyond the shared cases: one per editor feature. */
export const LSP_STATEMENTS = [
  "name of operating system", // hover inside a multi-word name
  "name of ", // completion after `of `
  "nme of oprating system", // unknown-inspector diagnostics and Replace quick fixes
  'exists values of setting "_BESClient_Resource_SleepIdle" of client', // fix-all
  "names of bes computers", // a session statement
  "(name of operating system\n  , version of client)", // two lines
  'exists file "unterminated', // a parse error
  "name of operating system \u{1F600}", // a character two UTF-16 units wide
  'name of "\u{1F600}" & nme of client', // positions after a character two UTF-16 units wide
];

/**
 * Open each statement and ask what an editor asks: hover at every word,
 * completion at the end and after every `of `, code actions over the whole
 * statement (with its diagnostics) and fix-all; then change it, close it, and
 * finally shut the server down. Returns `[{ step, message, reply }]`, `reply`
 * being the raw string `lspHandle` returned, and the exit code.
 */
export function runLspScript(statements) {
  const transcript = [];
  let id = 0;
  const send = (step, message) => {
    const text = JSON.stringify({ jsonrpc: "2.0", ...message });
    const reply = window.lspHandle(text);
    transcript.push({ step, message: text, reply });
    return JSON.parse(reply);
  };
  const request = (step, method, params) => send(step, { id: ++id, method, params });
  const notify = (step, method, params) => send(step, { method, params });
  const position = (text, offset) => {
    const before = text.slice(0, offset).split("\n");
    return { line: before.length - 1, character: before[before.length - 1].length };
  };

  request("initialize", "initialize", {
    processId: null,
    rootUri: null,
    capabilities: {
      textDocument: {
        codeAction: { codeActionLiteralSupport: { codeActionKind: { valueSet: ["quickfix", "source"] } } },
        completion: { completionItem: { snippetSupport: false } },
      },
      workspace: { workspaceEdit: { documentChanges: false } },
    },
  });
  notify("initialized", "initialized", {});

  statements.forEach((text, n) => {
    const uri = `untitled:statement-${n}`;
    const textDocument = { uri };
    const opened = notify(`${n} didOpen`, "textDocument/didOpen", {
      textDocument: { uri, languageId: "bigfix-relevance", version: 1, text },
    });
    const diagnostics = opened.find((m) => m.method === "textDocument/publishDiagnostics")?.params.diagnostics ?? [];
    for (const match of text.matchAll(/\S+/g)) {
      request(`${n} hover @${match.index}`, "textDocument/hover", { textDocument, position: position(text, match.index) });
    }
    const completeAt = [text.length, ...[...text.matchAll(/\bof /g)].map((m) => m.index + 3)];
    for (const offset of completeAt) {
      request(`${n} completion @${offset}`, "textDocument/completion", { textDocument, position: position(text, offset) });
    }
    const whole = { start: { line: 0, character: 0 }, end: position(text, text.length) };
    request(`${n} codeAction`, "textDocument/codeAction", { textDocument, range: whole, context: { diagnostics } });
    request(`${n} fixAll`, "textDocument/codeAction", {
      textDocument,
      range: whole,
      context: { diagnostics: [], only: ["source.fixAll.bigfix-relevance"] },
    });
    notify(`${n} didChange`, "textDocument/didChange", {
      textDocument: { uri, version: 2 },
      contentChanges: [{ text: `${text} ` }],
    });
    notify(`${n} didClose`, "textDocument/didClose", { textDocument });
  });

  request("shutdown", "shutdown", null);
  notify("exit", "exit", null);
  return { transcript, exitCode: window.lspExitCode() };
}

/**
 * What an editor needs from the replies to `runLspScript(LSP_STATEMENTS)`.
 * Returns a list of failures (empty when all is well).
 */
export function checkLspTranscript({ transcript, exitCode }) {
  const failures = [];
  const reply = (step) => {
    const entry = transcript.find((e) => e.step === step);
    if (!entry) failures.push(`no step ${step}`);
    return entry ? JSON.parse(entry.reply) : [];
  };
  const result = (step) => reply(step)[0]?.result;
  const index = (text) => LSP_STATEMENTS.indexOf(text);
  const expect = (ok, what) => ok || failures.push(what);

  // The page's editor initializes the page's one server at boot (#142 C1), so
  // the script's own initialize is answered "already initialized"; the
  // editor's checks (editor_checks.mjs) cover what its capabilities enable.
  const [init] = reply("initialize");
  const editorInitialized = init?.error?.message === "already initialized";
  for (const entry of transcript) {
    if (entry.step === "initialize" && editorInitialized) continue;
    for (const message of JSON.parse(entry.reply)) {
      expect(!message.error, `${entry.step}: error ${JSON.stringify(message.error)}`);
    }
  }
  if (!editorInitialized) {
    const capabilities = init?.result?.capabilities ?? {};
    expect(capabilities.hoverProvider, "initialize: no hoverProvider");
    expect(capabilities.completionProvider, "initialize: no completionProvider");
    expect(capabilities.codeActionProvider, "initialize: no codeActionProvider");
  }

  const name = index("name of operating system");
  const hover = result(`${name} hover @8`);
  expect(JSON.stringify(hover ?? "").includes("operating system"), "hover on `operating system` is empty");

  const after = index("name of ");
  const completion = result(`${after} completion @8`);
  const items = Array.isArray(completion) ? completion : completion?.items ?? [];
  expect(items.length > 10, `completion after \`name of \` offered ${items.length} item(s)`);

  const typo = index("nme of oprating system");
  const diagnostics = reply(`${typo} didOpen`).find((m) => m.method === "textDocument/publishDiagnostics");
  expect(diagnostics?.params.diagnostics.length > 0, "no diagnostics for `nme of oprating system`");
  const actions = result(`${typo} codeAction`) ?? [];
  expect(
    actions.some((a) => a.kind === "quickfix" && /^Replace /.test(a.title)),
    `no Replace quick fix for \`nme of oprating system\`: ${JSON.stringify(actions.map((a) => a.title))}`
  );

  const fixable = index('exists values of setting "_BESClient_Resource_SleepIdle" of client');
  const fixAll = result(`${fixable} fixAll`) ?? [];
  expect(
    fixAll.some((a) => a.kind === "source.fixAll.bigfix-relevance" && a.edit),
    "no fix-all action for the setting statement"
  );

  expect(exitCode === 0, `exit code after shutdown + exit is ${exitCode}, not 0`);
  return failures;
}

/**
 * A few steps through any `handle(string) -> string`, for the Node smoke tests:
 * initialize, open a statement with a typo, hover. Returns a list of failures.
 */
export function lspSmoke(handle, exitCode, expectedVersion) {
  const failures = [];
  let id = 0;
  const send = (message) => JSON.parse(handle(JSON.stringify({ jsonrpc: "2.0", ...message })));
  const [init] = send({ id: ++id, method: "initialize", params: { capabilities: {} } });
  const version = init?.result?.serverInfo?.version;
  if (version !== expectedVersion) failures.push(`initialize: serverInfo.version ${version}, not ${expectedVersion}`);
  const uri = "untitled:smoke";
  const text = "nme of oprating system";
  const [published] = send({
    method: "textDocument/didOpen",
    params: { textDocument: { uri, languageId: "bigfix-relevance", version: 1, text } },
  });
  if (!published?.params?.diagnostics?.length) failures.push(`didOpen: no diagnostics for ${JSON.stringify(text)}`);
  const [hover] = send({
    id: ++id,
    method: "textDocument/hover",
    params: { textDocument: { uri }, position: { line: 0, character: 1 } },
  });
  if (hover?.error) failures.push(`hover: ${JSON.stringify(hover.error)}`);
  const [bad] = JSON.parse(handle("{not json"));
  if (bad?.error?.code !== -32700) failures.push(`unparsable JSON: ${JSON.stringify(bad)}`);
  const code = exitCode();
  if (code !== undefined && code !== null) failures.push(`exit code ${code} before exit`);
  return failures;
}
