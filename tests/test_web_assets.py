"""Tests for the browser editor files the wheel ships (#142): ``web/*.js``.

``web/relevance_editor.js`` is the shared CodeMirror 6 client (Layer 3), and
``web/relevance_language.js`` the highlighter generated from the TextMate
grammar's tables (Layer 4). Both are package data, versioned with the server,
and loaded by pages that bring their own CodeMirror: the debugger's NiceGUI app
and the playground. Their behaviour is tested in Node (``tools/editor-client``);
these hold what the Python side owns: that the wheel carries them, that they
import nothing, that they ask for no CodeMirror name NiceGUI 3.18's bundle
lacks, that the generated one is current, and that the test package follows
this repo's npm policy.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest
from _helpers import REPO_ROOT, load_tool

WEB = REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "web"
CLIENT = WEB / "relevance_editor.js"
LANGUAGE = WEB / "relevance_language.js"
SHIPPED = (CLIENT, LANGUAGE)
GENERATOR = REPO_ROOT / "tools" / "generate_tmlanguage.py"
TEST_PACKAGE = REPO_ROOT / "tools" / "editor-client"
DEPENDABOT = REPO_ROOT / ".github" / "dependabot.yml"
TEST_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test.yaml"

NICEGUI_CM = {
    "@codemirror/language": "6.11.2",
    "@codemirror/state": "6.5.2",
    "@codemirror/view": "6.38.1",
}
"""What NiceGUI 3.18 bundles: the oldest CodeMirror the client supports."""

TEXTMATE_ENGINE = ("vscode-oniguruma", "vscode-textmate")
"""The TextMate engine the highlighter's parity test runs the grammar through."""

NICEGUI_EXPORTS = frozenset(
    {
        "Decoration",
        "EditorState",
        "EditorView",
        "GutterMarker",
        "Prec",
        "RangeSetBuilder",
        "StateEffect",
        "StateField",
        "StreamLanguage",
        "ViewPlugin",
        "closeHoverTooltips",
        "gutter",
        "hoverTooltip",
        "keymap",
        "showTooltip",
    }
)
"""Names NiceGUI 3.18's CodeMirror bundle is known to export that the client
uses (checked in bigfix-relevance-debugger against that bundle). A name added
to ``REQUIRED_CM`` must be checked there first, then added here: the bundle
exports neither ``@codemirror/lint`` nor ``@codemirror/autocomplete``."""


def _source(path: Path = CLIENT) -> str:
    return path.read_text(encoding="utf-8")


def _required_cm(path: Path = CLIENT) -> list[str]:
    match = re.search(r"export const REQUIRED_CM = \[(.*?)\];", _source(path), re.S)
    assert match, "REQUIRED_CM not found"
    return re.findall(r'"(\w+)"', match.group(1))


# --- the shipped files --------------------------------------------------------------


@pytest.mark.parametrize("path", SHIPPED, ids=lambda path: path.name)
def test_a_shipped_file_imports_nothing(path: Path) -> None:
    """The page injects its CodeMirror: one copy of @codemirror/state, any bundle."""
    source = _source(path)
    assert not re.search(r"^\s*import\b", source, re.M)
    assert not re.search(r"^\s*export\b[^;]*\bfrom\s*[\"']", source, re.M)
    assert "import(" not in source
    assert "require(" not in source


@pytest.mark.parametrize("path", SHIPPED, ids=lambda path: path.name)
def test_a_shipped_file_asks_only_for_names_nicegui_exports(path: Path) -> None:
    required = _required_cm(path)
    assert required == sorted(required)
    assert set(required) <= NICEGUI_EXPORTS, set(required) - NICEGUI_EXPORTS


@pytest.mark.parametrize("path", SHIPPED, ids=lambda path: path.name)
def test_every_codemirror_name_a_shipped_file_uses_is_required(path: Path) -> None:
    """Each checks its REQUIRED_CM up front, so a name used but not listed
    would fail later, inside a page, instead of at construction."""
    used = set(re.findall(r"\bCM\.(\w+)", _source(path)))
    assert used
    assert used <= set(_required_cm(path)), used - set(_required_cm(path))


@pytest.mark.parametrize("path", SHIPPED, ids=lambda path: path.name)
def test_a_shipped_file_is_ascii(path: Path) -> None:
    """Non-ASCII is written as escapes, so no repo hook rewrites it."""
    assert _source(path).isascii()


def test_the_committed_highlighter_is_what_the_generator_produces() -> None:
    """Generated from the TextMate grammar's own rules, never hand-edited:
    run `uv run python tools/generate_tmlanguage.py` after changing grammar.py."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    path, text = generator.render_codemirror()
    assert REPO_ROOT / path == LANGUAGE
    assert _source(LANGUAGE) == text, f"{LANGUAGE.name} is stale; rerun {GENERATOR.name}"


@pytest.mark.parametrize(
    "pattern",
    [
        r"\Afoo",
        r"foo\z",
        r"\Gfoo",
        r"\hfoo",
        r"a?+",
        r"(?>a)",
        r"[[:alpha:]]",
        r"[\-a]",
        r"\Kx",
        r"[a&&b]",  # intersection in Oniguruma, two ampersands in JavaScript
        r"(?i:a)b",  # an inline flag group: a load error on Node 22
        r"x(?-i)y",
        r"a.b",  # `.` stops at \r and U+2028 too in JavaScript
        "foo\\",  # a lone trailing backslash
    ],
)
def test_the_generator_refuses_what_javascript_would_read_differently(pattern: str) -> None:
    """Oniguruma syntax that JavaScript reads as something else, or not at all,
    fails generation instead of loading as a different pattern."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    with pytest.raises(SystemExit):
        generator._js_regex(pattern)


def test_every_generated_pattern_is_unicode_mode() -> None:
    """With the `u` flag, a stray escape throws in JavaScript instead of
    silently matching a letter."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    assert generator._js_regex(r"\b(?:of)\b")[1] == "u"
    assert generator._js_regex(r"!=|\&|\-") == ("!=|&|-", "u")
    assert generator._js_regex(r"is\s+not")[0] == r"is\p{White_Space}+not"
    found = re.findall(r'new RegExp\(("(?:[^"\\]|\\.)*"), "(\w+)"\)', _source(LANGUAGE))
    assert len(found) >= 15, len(found)
    for _, flags in found:
        assert "u" in flags


def test_the_highlighter_has_a_rule_for_every_textmate_match_rule() -> None:
    """Every TextMate match rule, with its pattern translated (the stale-file
    test above holds their order)."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    grammar = generator.relevance_grammar()
    repository = grammar["repository"]
    matches = [
        entry["match"]
        for include in grammar["patterns"]
        for rule in [repository[include["include"].lstrip("#")]]
        if "begin" not in rule  # comments and strings: begin/end, tokenized by hand
        for entry in rule.get("patterns", [rule])
    ]
    assert len(matches) > 10
    source = _source(LANGUAGE)
    for match in matches:
        pattern, flags = generator._js_regex(match)
        assert f"new RegExp({json.dumps(pattern)}, {json.dumps(flags + 'y')})" in source, match


# --- the wheel ------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("uv") is None, reason="needs uv to build the wheel")
def test_the_built_wheel_contains_the_web_files(tmp_path: Path) -> None:
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path), str(REPO_ROOT)],
        check=True,
        capture_output=True,
    )
    (wheel,) = tmp_path.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        for path in SHIPPED:
            shipped = archive.read(f"bigfix_relevance_analyzer/web/{path.name}")
            assert shipped == path.read_bytes(), path.name


def test_the_client_is_found_through_importlib_resources() -> None:
    """How a consumer (the debugger) finds it in the installed package."""
    from importlib.resources import files

    web = files("bigfix_relevance_analyzer") / "web"
    assert "export function relevanceEditor" in (web / CLIENT.name).read_text(encoding="utf-8")
    assert "export function relevanceLanguage" in (web / LANGUAGE.name).read_text(encoding="utf-8")


# --- its test package: this repo's npm policy ------------------------------------------


def test_the_test_package_pins_codemirror_at_nicegui_s_and_the_rest_exactly() -> None:
    """CodeMirror at NiceGUI's versions (dependabot leaves those alone); the
    TextMate engine exactly too, at whatever version dependabot last moved it
    to, with the lockfile agreeing."""
    package = json.loads((TEST_PACKAGE / "package.json").read_text(encoding="utf-8"))
    assert package["private"] is True
    pins = package["devDependencies"]
    assert {name: pins.get(name) for name in NICEGUI_CM} == NICEGUI_CM
    assert set(pins) == {*NICEGUI_CM, *TEXTMATE_ENGINE}
    assert all(re.fullmatch(r"\d+\.\d+\.\d+", version) for version in pins.values()), pins
    assert "dependencies" not in package
    assert package["engines"]["npm"] == ">=11.10.0"
    script = package["scripts"]["test"]
    assert "CM_MODULE=./cm.mjs" in script
    # Node 22 (CI's) runs a bare directory argument as a module and fails with
    # MODULE_NOT_FOUND; it takes files or a quoted glob.
    assert "'test/**/*.test.mjs'" in script
    assert not re.search(r"--test\s+\S*/(?:\s|$)", script), script
    lock = json.loads((TEST_PACKAGE / "package-lock.json").read_text(encoding="utf-8"))
    for name, version in pins.items():
        assert lock["packages"][f"node_modules/{name}"]["version"] == version, name


def test_the_test_bundle_re_exports_the_three_packages() -> None:
    text = (TEST_PACKAGE / "cm.mjs").read_text(encoding="utf-8")
    for name in NICEGUI_CM:
        assert f'export * from "{name}";' in text


@pytest.fixture
def git_checkout() -> None:
    """Skip outside a git checkout (an unpacked sdist), as the layout tests do."""
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")


def _tracked_npm_packages() -> list[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "*package.json"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    return sorted(REPO_ROOT / Path(path).parent for path in listed)


@pytest.mark.usefixtures("git_checkout")
def test_every_npm_package_in_the_repo_has_the_cooldown_and_dependabot() -> None:
    """Repo-wide, so a package added anywhere (this one is outside
    tools/playground-wasm and tools/vscode-extension) cannot slip past the
    per-area tests: an .npmrc refusing week-old releases, and a dependabot
    entry with its cooldown."""
    packages = _tracked_npm_packages()
    assert TEST_PACKAGE in packages
    dependabot = DEPENDABOT.read_text(encoding="utf-8")
    entries = dependabot.split("  - package-ecosystem:")[1:]
    for package in packages:
        npmrc = (package / ".npmrc").read_text(encoding="utf-8")
        assert re.search(r"^min-release-age=7$", npmrc, re.M), package
        relative = "/" + package.relative_to(REPO_ROOT).as_posix()
        (entry,) = (e for e in entries if f'directory: "{relative}"' in e)
        assert re.search(r"cooldown:\s*\n\s*default-days: 7\b", entry), relative


def test_ci_runs_the_node_tests() -> None:
    text = TEST_WORKFLOW.read_text(encoding="utf-8")
    job = text[text.index("  editor-client:") :]
    following = re.search(r"\n  [\w-]+:\n", job[1:])
    job = job[: following.start() + 1] if following else job
    assert "working-directory: tools/editor-client" in job
    assert "npm ci" in job
    assert "npm test" in job
