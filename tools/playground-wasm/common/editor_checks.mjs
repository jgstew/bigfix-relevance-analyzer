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

/** WCAG contrast ratio of two CSS rgb()/rgba() colors (alpha ignored). */
function contrast(a, b) {
  const lum = (css) => {
    const [r, g, bl] = css.match(/[\d.]+/g).slice(0, 3).map(Number);
    const lin = (c) => ((c /= 255) <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(bl);
  };
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
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

  async "Enter after a typed word inserts a newline, even with completions open"(page) {
    await setText(page, "");
    await page.keyboard.type("exists file", { delay: 20 });
    await page.locator(".cm-tooltip-autocomplete li").first().waitFor({ timeout: TIMEOUT });
    await page.waitForTimeout(400); // the list settled: a user reading it, then pressing Enter
    await page.keyboard.press("Enter");
    const text = await getText(page);
    return text === "exists file\n" ? null : `Enter gave ${JSON.stringify(text)}`;
  },

  async "Mod-Enter closes an open completion list"(page) {
    await setText(page, "");
    await page.keyboard.type("name of op", { delay: 20 });
    await page.locator(".cm-tooltip-autocomplete li").first().waitFor({ timeout: TIMEOUT });
    await page.keyboard.press("ControlOrMeta+Enter");
    await page.locator(".cm-tooltip-autocomplete").waitFor({ state: "detached", timeout: TIMEOUT });
    return null;
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
    // Keyboard users must see which button has focus.
    const focus = await page.evaluate(() => {
      const button = document.activeElement;
      if (!button || !button.matches(".cm-bfr-action")) return null;
      const style = getComputedStyle(button);
      return { outline: style.outlineStyle, background: style.backgroundColor };
    });
    if (!focus) return "Mod-. did not focus a quick fix";
    if (focus.outline === "none" && /rgba\(0, 0, 0, 0\)|transparent/.test(focus.background)) {
      return "the focused quick fix looks like the others";
    }
    await all.click();
    const text = await getText(page);
    return text === expected ? null : `fix-all gave ${JSON.stringify(text)}, the analyzer's fix is ${JSON.stringify(expected)}`;
  },
};

/** In the dark color scheme: the cursor, a selection and the colored tokens
 * are all readable against the editor's background. */
async function checkDark(page) {
  await page.emulateMedia({ colorScheme: "dark" });
  try {
    await setText(page, 'exists file "x" whose (size of it > 10) /* c */', 0);
    await page.evaluate(() => {
      const { view } = window.playgroundInput;
      view.dispatch({ selection: { anchor: 0, head: 6 } });
      view.focus();
    });
    await page.waitForTimeout(100);
    const colors = await page.evaluate(() => {
      const editor = document.querySelector("#input .cm-editor");
      const style = (el) => getComputedStyle(el);
      const tokens = [...editor.querySelectorAll(".cm-line span")].map((el) => [el.textContent, style(el).color]);
      return {
        background: style(editor).backgroundColor,
        text: style(editor.querySelector(".cm-content")).color,
        caret: style(editor.querySelector(".cm-content")).caretColor,
        cursor: editor.querySelector(".cm-cursor") ? style(editor.querySelector(".cm-cursor")).borderLeftColor : null,
        selection: editor.querySelector(".cm-selectionBackground") ? style(editor.querySelector(".cm-selectionBackground")).backgroundColor : null,
        tokens,
      };
    });
    const problems = [];
    const need = (what, ratio, min) => ratio < min && problems.push(`${what} ${ratio.toFixed(2)}:1 < ${min}:1`);
    need("text", contrast(colors.text, colors.background), 4.5);
    if (colors.cursor) need("cursor", contrast(colors.cursor, colors.background), 3);
    if (colors.selection) need("selected text", contrast(colors.text, colors.selection), 4.5);
    for (const [token, color] of colors.tokens) need(`\`${token}\``, contrast(color, colors.background), 4.5);
    return problems.length ? problems.join("; ") : null;
  } finally {
    await page.emulateMedia({ colorScheme: "light" });
  }
}

/** Run every check on a booted page; returns [name, failure-or-null] pairs. */
export async function checkEditor(page) {
  const results = [];
  for (const [name, check] of [...Object.entries(checks), ["readable in the dark color scheme", checkDark]]) {
    try {
      results.push([name, await check(page)]);
    } catch (error) {
      results.push([name, String(error && error.message ? error.message : error).split("\n")[0]]);
    }
  }
  return results;
}
