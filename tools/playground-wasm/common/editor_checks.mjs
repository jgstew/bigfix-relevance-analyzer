// What the playground's editor (#142 C1) must do on both pages, driven through
// a real browser with Playwright: completion after `name of `, hover on
// `operating system`, a diagnostic with its Replace quick fix, fix-all, and
// Mod-Enter still analysing while Enter inserts a newline.
//
// One copy for both browser tests, imported by relative path, for the same
// reason as cases.mjs. Each check returns a failure message or null.

const TIMEOUT = 10_000;

async function setText(page, text, cursor = text.length) {
  await page.evaluate(
    ({ text, cursor }) => {
      const { view } = window.playgroundInput;
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text }, selection: { anchor: cursor } });
      view.focus();
    },
    { text, cursor },
  );
}

const getText = (page) => page.evaluate(() => window.playgroundInput.getText());

/** Hover the mouse over the character at `offset`. */
async function hoverAt(page, offset) {
  await page.mouse.move(0, 0);
  const at = await page.evaluate((offset) => {
    const { view } = window.playgroundInput;
    const box = view.coordsAtPos(offset, 1);
    return { x: (box.left + box.right) / 2 + 1, y: (box.top + box.bottom) / 2 };
  }, offset);
  await page.mouse.move(at.x, at.y);
}

const checks = {
  async "Mod-Enter analyses, Enter inserts a newline"(page) {
    await setText(page, "name of operating system");
    await page.evaluate(() => {
      window.__lastJson = null;
    });
    await page.keyboard.press("ControlOrMeta+Enter");
    await page.waitForFunction(() => window.__lastJson && JSON.parse(window.__lastJson).text === "name of operating system", null, {
      timeout: TIMEOUT,
    });
    await page.keyboard.press("Enter");
    const text = await getText(page);
    return text === "name of operating system\n" ? null : `Enter gave ${JSON.stringify(text)}`;
  },

  async "completion after `name of `"(page) {
    await setText(page, "name of ");
    await page.keyboard.press("Control+Space");
    const options = page.locator(".cm-tooltip-autocomplete li");
    await options.first().waitFor({ timeout: TIMEOUT });
    const labels = await options.allInnerTexts();
    if (labels.length < 10) return `only ${labels.length} completion(s)`;
    if (!labels.some((label) => label.includes("operating system"))) return `no \`operating system\` in ${labels.slice(0, 10)}`;
    await page.keyboard.press("Escape");
    return null;
  },

  async "hover on `operating system`"(page) {
    await setText(page, "name of operating system", 0);
    await hoverAt(page, 12);
    const tooltip = page.locator(".cm-bfr-tooltip");
    await tooltip.waitFor({ timeout: TIMEOUT });
    const text = await tooltip.innerText();
    return text.includes("operating system") && text.includes("inspector") ? null : `hover said ${JSON.stringify(text)}`;
  },

  async "a diagnostic and its Replace quick fix for `nme of oprating system`"(page) {
    await setText(page, "nme of oprating system", 0);
    await page.locator(".cm-bfr-diag").nth(1).waitFor({ timeout: TIMEOUT });
    await hoverAt(page, 10);
    const fix = page.locator(".cm-bfr-tooltip .cm-bfr-action", { hasText: "with `operating system`" }).first();
    await fix.waitFor({ timeout: TIMEOUT });
    await fix.click();
    const text = await getText(page);
    return text === "nme of operating system" ? null : `the quick fix gave ${JSON.stringify(text)}`;
  },

  async "fix-all from the quick-fix menu (Mod-.)"(page) {
    const original = 'exists values of setting "a" of client AND exists values of setting "b" of client';
    const expected = await page.evaluate((text) => JSON.parse(window.analyzeJson(text)).autofix?.fixed, original);
    if (!expected) return "the analyzer offers no fix for the fix-all statement";
    // The cursor inside the first diagnostic (`setting "a" of client`).
    await setText(page, original, original.indexOf("setting") + 3);
    await page.locator(".cm-bfr-diag").nth(1).waitFor({ timeout: TIMEOUT });
    await page.keyboard.press("ControlOrMeta+Period");
    const all = page.locator(".cm-bfr-menu .cm-bfr-action", { hasText: /^Apply \d+ safe fixes/ });
    await all.waitFor({ timeout: TIMEOUT });
    await all.click();
    const text = await getText(page);
    return text === expected ? null : `fix-all gave ${JSON.stringify(text)}, the analyzer's fix is ${JSON.stringify(expected)}`;
  },
};

/** Run every check on a booted page; returns [name, failure-or-null] pairs. */
export async function checkEditor(page) {
  const results = [];
  for (const [name, check] of Object.entries(checks)) {
    try {
      results.push([name, await check(page)]);
    } catch (error) {
      results.push([name, String(error && error.message ? error.message : error).split("\n")[0]]);
    }
  }
  return results;
}
