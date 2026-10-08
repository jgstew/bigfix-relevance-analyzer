"""The layout and contract of ``tools/vscode-extension/``.

The proof-of-concept VS Code extensions for the language server (issue 10) sit
side by side, one directory each:

* ``python-stdio/`` -- PoC 1: launches ``bigfix-relevance-lsp`` over stdio from
  a Python on the user's machine;
* ``componentize-py/`` -- PoC 2, planned: the same server compiled into a
  WebAssembly component the extension runs itself, so no Python is needed.

Nothing here is part of the published wheel, and only these tests run in CI, so
they hold what would otherwise rot silently. That means the same supply-chain
rules as every other npm package in the repo, and a shared contract. Both
extensions offer the analyzer the same files, and both can be installed at once
to compare them, which needs distinct names and settings.

Pure and cheap, like ``test_playground_layout.py``: paths and text, never a build.
"""

from __future__ import annotations

import inspect
import json
import re
import shutil
import subprocess
import tomllib
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import pytest
from _helpers import load_tool

from bigfix_relevance_analyzer.extract import _RECOGNIZED_SUFFIXES, _is_recognized

REPO_ROOT = Path(__file__).resolve().parent.parent
VSCODE_EXTENSION = REPO_ROOT / "tools" / "vscode-extension"
DEPENDABOT = REPO_ROOT / ".github" / "dependabot.yml"
MIN_RELEASE_AGE_DAYS = 7

# The npm that first enforces `min-release-age`; older ones ignore it silently.
MIN_NPM = ">=11.10.0"


def _extension_dirs() -> list[Path]:
    return sorted(
        path.parent
        for path in VSCODE_EXTENSION.glob("*/package.json")
        if "node_modules" not in path.parts
    )


def _manifest(extension: Path) -> dict[str, Any]:
    manifest: dict[str, Any] = json.loads((extension / "package.json").read_text("utf-8"))
    return manifest


def _settings(extension: Path) -> dict[str, Any]:
    properties: dict[str, Any] = _manifest(extension)["contributes"]["configuration"]["properties"]
    return properties


EXTENSIONS = _extension_dirs()


PRIMARY = VSCODE_EXTENSION / "componentize-py"
POC_PYTHON = VSCODE_EXTENSION / "python-stdio"
COMMON_SMOKE = VSCODE_EXTENSION / "common" / "smoke"


NPM_PACKAGES = [*EXTENSIONS, COMMON_SMOKE]
"""Every npm package here: both extensions, and the shared smoke test."""


def test_both_extensions_exist() -> None:
    """Guard the parametrized tests below against passing on an empty list."""
    assert EXTENSIONS == [PRIMARY, POC_PYTHON]


def test_the_wasm_extension_is_the_primary_one() -> None:
    """It needs nothing installed, so it gets the plain name and settings."""
    manifest = _manifest(PRIMARY)
    assert manifest["name"] == "bigfix-relevance-developer"
    assert manifest["displayName"] == "BigFix Relevance Developer"
    assert manifest["settingsPrefix"] == "bigfixRelevance"


def test_the_python_extension_is_labelled_a_proof_of_concept() -> None:
    assert "PoC" in _manifest(POC_PYTHON)["displayName"]
    assert _manifest(POC_PYTHON)["settingsPrefix"] == "bigfixRelevancePython"


def test_the_component_world_exports_what_server_js_calls() -> None:
    wit = (PRIMARY / "build-component" / "wit" / "lsp.wit").read_text("utf-8")
    for export in (
        "export handle: func(message: string) -> string;",
        "export exit-code: func() -> option<s32>;",
        "export version: func() -> string;",
    ):
        assert export in wit
    assert (PRIMARY / "build-component" / "app.py").is_file()
    assert (PRIMARY / "build-component" / "build_component.py").is_file()


def test_the_built_component_is_never_committed() -> None:
    """~22 MiB, rebuilt from the wheel: ``build_component.py`` writes it under ``dist/``."""
    git = shutil.which("git")
    if git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    probe = PRIMARY / "dist" / "lsp.wasm"
    result = subprocess.run(
        [git, "check-ignore", "-q", str(probe)], cwd=REPO_ROOT, capture_output=True
    )
    assert result.returncode == 0, f"{probe} is not gitignored"


def test_both_extensions_share_one_smoke_test() -> None:
    """The same files and the same expectations, so the two PoCs compare directly."""
    assert (COMMON_SMOKE / "run.mjs").is_file()
    assert (COMMON_SMOKE / "suite.js").is_file()
    for extension in EXTENSIONS:
        assert not (extension / "smoke").exists(), f"{extension.name} has its own smoke/"


def test_the_directory_readme_describes_both_proofs_of_concept() -> None:
    text = (VSCODE_EXTENSION / "README.md").read_text("utf-8")
    assert "python-stdio/" in text
    assert "componentize-py/" in text


# ---------------------------------------------------------------------------
# Supply chain: the same rules as tools/playground-wasm/
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("extension", NPM_PACKAGES, ids=lambda path: path.name)
def test_every_extension_enforces_a_release_age_cooldown(extension: Path) -> None:
    """npm reads ``.npmrc`` from the working directory only, so one per package."""
    npmrc = extension / ".npmrc"
    settings = dict(
        line.split("=", 1)
        for line in npmrc.read_text("utf-8").splitlines()
        if "=" in line and not line.lstrip().startswith(("#", ";"))
    )
    assert settings.get("min-release-age") == str(MIN_RELEASE_AGE_DAYS)
    assert _manifest(extension)["engines"]["npm"] == MIN_NPM


@pytest.mark.parametrize("extension", NPM_PACKAGES, ids=lambda path: path.name)
def test_every_extension_pins_exactly_and_has_a_lockfile(extension: Path) -> None:
    manifest = _manifest(extension)
    assert manifest["private"] is True, "a proof of concept, never published to npm"
    assert (extension / "package-lock.json").is_file()
    for section in ("dependencies", "devDependencies"):
        for name, spec in manifest.get(section, {}).items():
            assert spec[0].isdigit(), f"{name} is {spec!r}, which is not an exact pin"


@pytest.mark.parametrize("extension", NPM_PACKAGES, ids=lambda path: path.name)
def test_every_extension_is_watched_by_dependabot(extension: Path) -> None:
    relative = "/" + str(extension.relative_to(REPO_ROOT))
    assert f'directory: "{relative}"' in DEPENDABOT.read_text("utf-8")


# ---------------------------------------------------------------------------
# The extension itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
def test_the_entry_points_exist_and_parse(extension: Path) -> None:
    scripts = [extension / _manifest(extension)["main"]]
    if extension == PRIMARY:
        scripts.append(extension / "server.js")
    scripts += sorted(COMMON_SMOKE.glob("*.*js"))
    for script in scripts:
        assert script.is_file(), script
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    for script in scripts:
        result = subprocess.run([node, "--check", str(script)], capture_output=True, text=True)
        assert result.returncode == 0, f"{script}: {result.stderr}"


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
def test_the_document_patterns_are_exactly_what_the_analyzer_reads(extension: Path) -> None:
    """Every suffix the extractor recognizes, and nothing it would skip.

    The server decides the file type from the URI's suffix, so a pattern the
    analyzer does not recognize would start the server for nothing, and a
    missing one would leave a file type unlinted in the editor.
    """
    patterns: list[str] = json.loads((extension / "document-patterns.json").read_text("utf-8"))
    for pattern in patterns:
        assert pattern.startswith("**/*."), pattern
        assert _is_recognized(Path(pattern.replace("**/*", "x"))), pattern
    for suffix in _RECOGNIZED_SUFFIXES:
        assert any(fnmatch(f"dir/x{suffix}", pattern) for pattern in patterns), suffix
    assert any(fnmatch("dir/x.bes.xml", pattern) for pattern in patterns)


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
def test_every_setting_is_under_the_extensions_own_prefix(extension: Path) -> None:
    prefix = _manifest(extension)["settingsPrefix"]
    for key in _settings(extension):
        assert key.startswith(f"{prefix}."), key


def test_extensions_can_be_installed_side_by_side() -> None:
    """Distinct names and settings, so both PoCs can run at once and be compared."""
    names = [_manifest(extension)["name"] for extension in EXTENSIONS]
    assert len(set(names)) == len(names)
    keys = [key for extension in EXTENSIONS for key in _settings(extension)]
    assert len(set(keys)) == len(keys)


def test_poc_1_launches_the_console_script_by_default() -> None:
    extension = POC_PYTHON
    prefix = _manifest(extension)["settingsPrefix"]
    default = _settings(extension)[f"{prefix}.server.command"]["default"]
    scripts = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text("utf-8"))["project"]["scripts"]
    assert default in scripts
    assert scripts[default] == "bigfix_relevance_analyzer.lsp.__main__:main"


# ---------------------------------------------------------------------------
# Packaging and CI: .github/workflows/vscode-extension.yaml
# ---------------------------------------------------------------------------

WORKFLOW = REPO_ROOT / ".github" / "workflows" / "vscode-extension.yaml"
SERVER_TEST = PRIMARY / "test" / "server.test.mjs"


def test_the_primary_extension_packages_with_a_pinned_vsce() -> None:
    assert _manifest(PRIMARY)["devDependencies"]["@vscode/vsce"][0].isdigit()


def test_the_package_leaves_out_build_inputs_but_keeps_the_component() -> None:
    """``dist/`` is gitignored, and the built component in it must still ship.

    vsce reads ``.vscodeignore``, not ``.gitignore``, so the component is
    packaged unless excluded here; everything else under ``dist/`` is a build
    input that only bloats the package.
    """
    ignored = {
        line.strip()
        for line in (PRIMARY / ".vscodeignore").read_text("utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    for build_only in ("build-component/**", "dist/work/**", "dist/wheel/**", "test/**"):
        assert build_only in ignored, build_only
    for pattern in ignored:
        assert not pattern.startswith("dist/**"), pattern
        if pattern.startswith("dist/component"):
            assert pattern.endswith(".d.ts"), f"{pattern} would drop part of the component"


def test_the_build_copies_the_project_license_into_the_extension(tmp_path: Path) -> None:
    """vsce packages the LICENSE beside package.json. It is copied there at build
    time rather than committed, so there is one license file in the repository."""
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    copied = build.copy_license(tmp_path)
    assert copied == tmp_path / "LICENSE"
    assert copied.read_bytes() == (REPO_ROOT / "LICENSE").read_bytes()


def test_the_copied_license_is_never_committed() -> None:
    git = shutil.which("git")
    if git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    result = subprocess.run(
        [git, "check-ignore", "-q", str(PRIMARY / "LICENSE")], cwd=REPO_ROOT, capture_output=True
    )
    assert result.returncode == 0, "the build's copy of LICENSE is not gitignored"


def test_the_server_has_a_node_test_of_its_own() -> None:
    assert SERVER_TEST.is_file()


def test_the_workflow_builds_packages_uploads_and_tests_the_vsix() -> None:
    text = WORKFLOW.read_text("utf-8")
    for step in (
        "build-component/build_component.py",
        "vsce package",
        "actions/upload-artifact@",
        ".vsix",
        "node --test",
    ):
        assert step in text, step


def test_the_workflow_runs_the_shared_smoke_test_on_the_packaged_extension() -> None:
    """A real, headless VS Code, against the unzipped ``.vsix`` -- what ships.

    VS Code comes from ``@vscode/test-electron`` through ``run.mjs``, not a
    hand-written download, and the cache is keyed on the smoke package's
    ``package.json``, where the VS Code version is pinned.
    """
    text = WORKFLOW.read_text("utf-8")
    assert "xvfb-run" in text
    assert "tools/vscode-extension/common/smoke/run.mjs" in text
    assert "working-directory: tools/vscode-extension/common/smoke" in text
    assert "path: tools/vscode-extension/common/smoke/.vscode-test" in text
    assert "hashFiles('tools/vscode-extension/common/smoke/package.json')" in text
    assert "curl" not in text
    assert "permissions:\n  contents: read" in text


def test_the_smoke_test_pins_test_electron_and_the_vscode_version() -> None:
    manifest = _manifest(COMMON_SMOKE)
    assert manifest["dependencies"]["@vscode/test-electron"][0].isdigit()
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["vscodeVersion"])
    run = (COMMON_SMOKE / "run.mjs").read_text("utf-8")
    assert 'from "@vscode/test-electron"' in run
    assert "vscodeVersion" in run


def test_the_downloaded_vscode_is_never_committed() -> None:
    git = shutil.which("git")
    if git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    probe = COMMON_SMOKE / ".vscode-test" / "vscode-linux-x64-1.0.0" / "code"
    result = subprocess.run([git, "check-ignore", "-q", str(probe)], cwd=REPO_ROOT)
    assert result.returncode == 0, f"{probe} is not gitignored"


def test_the_workflow_pins_every_action_to_a_commit() -> None:
    uses = re.findall(r"uses:\s*(\S+)", WORKFLOW.read_text("utf-8"))
    assert uses
    for action in uses:
        assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", action), action


def test_the_workflow_runs_only_when_an_input_of_the_extension_changes() -> None:
    """Every input the build reads, on both triggers; manual runs stay possible."""
    text = WORKFLOW.read_text("utf-8")
    for path in (
        '"src/**"',
        '"pyproject.toml"',
        '"uv.lock"',
        '"tools/vscode-extension/**"',
        '"tools/playground-wasm/componentize-py/build-playground/**"',
        '".github/workflows/vscode-extension.yaml"',
    ):
        assert path in text, path
    assert "paths: *inputs" in text
    assert "workflow_dispatch:" in text


# ---------------------------------------------------------------------------
# Releases: tag_and_release.yaml attaches the .vsix, built from the release's wheel
# ---------------------------------------------------------------------------

RELEASE = REPO_ROOT / ".github" / "workflows" / "tag_and_release.yaml"


def test_the_build_can_take_a_given_wheel(tmp_path: Path) -> None:
    """A release builds from the wheel it publishes, not from a rebuild of the tree."""
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    assert inspect.signature(build.build).parameters["wheel"].default is None
    with pytest.raises(SystemExit, match=r"missing\.whl"):
        build.main(["--wheel", str(tmp_path / "missing.whl")])


def test_the_build_checks_the_component_against_the_wheels_version() -> None:
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    wheel = Path("dist/bigfix_relevance_analyzer-1.19.0-py3-none-any.whl")
    assert build.wheel_version(wheel) == "1.19.0"


def test_the_workflow_is_callable_for_a_release() -> None:
    """Same shape as wasm-html.yaml: the release hands over its dist/ as an artifact."""
    text = WORKFLOW.read_text("utf-8")
    assert "workflow_call:" in text
    assert "release_artifact:" in text
    assert "sha256sum -c SHA256SUMS.txt" in text
    assert "--wheel" in text
    # Under workflow_call, github.workflow is the caller's name, so a release run
    # and this workflow's own push-to-main run cannot cancel each other.
    assert "group: vscode-extension-${{ github.workflow }}-${{ github.ref }}" in text


def test_a_release_runs_only_the_quick_unit_tests() -> None:
    """The headless VS Code job would hold up a release; the node tests do not."""
    text = WORKFLOW.read_text("utf-8")
    e2e = text[text.index("  e2e:") :]
    assert "if: inputs.release_artifact == ''" in e2e.split("steps:")[0]
    package = text[text.index("  package:") : text.index("  e2e:")]
    assert "if:" not in package.split("steps:")[0], "the package job must run for a release"
    assert "node --test" in package


def test_the_release_attaches_the_vsix() -> None:
    text = RELEASE.read_text("utf-8")
    assert "uses: ./.github/workflows/vscode-extension.yaml" in text
    job = text[text.index("  vscode-extension:") :]
    assert "release_artifact: release-dist" in job.split("\n\n")[0]
    finalize = text[text.index("  finalize:") :]
    assert "vscode-extension" in finalize.split("steps:")[0]
    assert "name: bigfix-relevance-developer-vsix" in finalize
    assert "bigfix-relevance-developer.vsix assets/" in finalize


def test_the_extension_takes_the_version_of_the_wheel_it_was_built_from(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The .vsix version is the analyzer version inside it, and the self-check
    expects that same version. package.json in the tree is never rewritten."""
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    glue = tmp_path / "lsp.js"
    checked: list[str] = []
    commands: list[list[str]] = []
    monkeypatch.setattr(build, "build", lambda wheel=None: (glue, "9.8.7"))
    monkeypatch.setattr(build, "smoke", lambda glue, version: checked.append(version))
    monkeypatch.setattr(build, "_run", lambda argv, label, cwd=None: commands.append(argv))
    out = tmp_path / "out" / "bigfix-relevance-developer.vsix"

    assert build.main(["--package", str(out)]) == 0

    assert checked == ["9.8.7"]
    (vsce,) = (argv for argv in commands if "vsce" in argv)
    assert vsce[vsce.index("package") + 1] == "9.8.7"
    for flag in ("--no-git-tag-version", "--no-update-package-json"):
        assert flag in vsce
    assert vsce[vsce.index("--out") + 1] == str(out)
    assert out.parent.is_dir(), "vsce does not create the --out directory itself"


def test_the_workflow_packages_through_the_build_script() -> None:
    """One packaging path, so CI and a release stamp the version the same way."""
    text = WORKFLOW.read_text("utf-8")
    assert "--package" in text
    assert "npx vsce package" not in text


# ---------------------------------------------------------------------------
# jco and preview2-shim move together
# ---------------------------------------------------------------------------

SHIM_PACKAGES = [PRIMARY, REPO_ROOT / "tools" / "playground-wasm" / "componentize-py" / "smoke"]
"""Every npm package whose jco-generated glue imports @bytecodealliance/preview2-shim."""


@pytest.mark.parametrize("package", SHIM_PACKAGES, ids=lambda path: path.parent.name)
def test_the_glue_loads_the_shim_version_jco_is_built_against(package: Path) -> None:
    """jco's transpiler declares the preview2-shim its output targets; the glue
    imports the top-level copy. For 0.x, a different minor is a breaking change."""
    packages = json.loads((package / "package-lock.json").read_text("utf-8"))["packages"]
    wanted = packages["node_modules/@bytecodealliance/jco-transpile"]["dependencies"][
        "@bytecodealliance/preview2-shim"
    ]
    loaded = packages["node_modules/@bytecodealliance/preview2-shim"]["version"]
    major, minor = (int(part) for part in wanted.lstrip("^~=").split(".")[:2])
    assert (major, minor) == tuple(int(part) for part in loaded.split(".")[:2]), (
        f"glue loads preview2-shim {loaded}; jco-transpile wants {wanted}"
    )


@pytest.mark.parametrize("package", SHIM_PACKAGES, ids=lambda path: path.parent.name)
def test_dependabot_updates_jco_and_the_shim_together(package: Path) -> None:
    """Separate PRs for the two broke a lockfile once (#89 and #90)."""
    text = DEPENDABOT.read_text("utf-8")
    entry = text[text.index(f'directory: "/{package.relative_to(REPO_ROOT)}"') :]
    entry = entry.split("- package-ecosystem:")[0]
    assert "groups:" in entry
    assert '"@bytecodealliance/*"' in entry


# ---------------------------------------------------------------------------
# build_component.py --wheel: one wheel, resolved clearly, never inside dist/
# ---------------------------------------------------------------------------


def _build_module(monkeypatch: pytest.MonkeyPatch, dist: Path) -> Any:
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    monkeypatch.setattr(build, "DIST", dist)
    monkeypatch.setattr(build, "build", lambda wheel=None: pytest.fail("built anyway"))
    return build


def test_a_wheel_inside_the_build_output_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The build starts by deleting dist/, which would delete that wheel first."""
    dist = tmp_path / "dist"
    wheel = dist / "wheel" / "bigfix_relevance_analyzer-1.0.0-py3-none-any.whl"
    wheel.parent.mkdir(parents=True)
    wheel.touch()
    build = _build_module(monkeypatch, dist)
    with pytest.raises(SystemExit, match="inside"):
        build.main(["--wheel", str(wheel)])


@pytest.mark.parametrize(("count", "message"), [(0, "no wheel found"), (2, "exactly one wheel")])
def test_a_wheel_pattern_must_match_exactly_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, count: int, message: str
) -> None:
    for version in range(count):
        (tmp_path / f"bigfix_relevance_analyzer-1.0.{version}-py3-none-any.whl").touch()
    build = _build_module(monkeypatch, tmp_path / "dist")
    with pytest.raises(SystemExit, match=message):
        build.main(["--wheel", str(tmp_path / "*.whl")])


def test_the_workflow_passes_the_wheel_pattern_quoted() -> None:
    """The script resolves it, so zero or two wheels fail with a clear message
    rather than as argparse errors about stray arguments."""
    assert "--wheel 'dist/*.whl'" in WORKFLOW.read_text("utf-8")


@pytest.mark.parametrize("package", SHIM_PACKAGES, ids=lambda path: path.parent.name)
def test_dependabot_never_moves_the_shim_past_jco_on_its_own(package: Path) -> None:
    """The group moves both to their latest, and the latest jco can still target
    an older shim minor (#92, #93). Only patch updates of the shim are proposed;
    a jco that targets a new minor fails the test above until the shim is
    bumped with it, by hand."""
    text = DEPENDABOT.read_text("utf-8")
    entry = text[text.index(f'directory: "/{package.relative_to(REPO_ROOT)}"') :]
    entry = entry.split("- package-ecosystem:")[0]
    ignored = entry[entry.index("ignore:") :]
    assert 'dependency-name: "@bytecodealliance/preview2-shim"' in ignored
    for update_type in ("version-update:semver-major", "version-update:semver-minor"):
        assert update_type in ignored
    assert "version-update:semver-patch" not in ignored


# ---------------------------------------------------------------------------
# The BigFix Relevance language: contribution, configuration and grammars
# ---------------------------------------------------------------------------

GENERATOR = REPO_ROOT / "tools" / "generate_tmlanguage.py"


def _language(extension: Path) -> dict[str, Any]:
    (language,) = _manifest(extension)["contributes"]["languages"]
    found: dict[str, Any] = language
    return found


def test_the_primary_extension_contributes_the_relevance_language() -> None:
    """Whole-file relevance, in the id the server falls back on for untitled buffers."""
    from bigfix_relevance_analyzer.extract import _SESSION_TEXT_SUFFIXES, _UNTYPED_TEXT_SUFFIXES
    from bigfix_relevance_analyzer.lsp.linter import LANGUAGE_ID

    language = _language(PRIMARY)
    assert language["id"] == LANGUAGE_ID
    assert sorted(language["extensions"]) == sorted(_SESSION_TEXT_SUFFIXES | _UNTYPED_TEXT_SUFFIXES)
    assert (PRIMARY / language["configuration"]).is_file()
    # VS Code (1.74+) activates on a contributed language by itself; listing
    # `onLanguage:` too is redundant.
    assert f"onLanguage:{LANGUAGE_ID}" not in _manifest(PRIMARY)["activationEvents"]


def test_only_one_extension_defines_the_language() -> None:
    """Two installed extensions defining the same language would conflict."""
    for extension in EXTENSIONS:
        contributes = _manifest(extension)["contributes"]
        if extension != PRIMARY:
            assert "languages" not in contributes
            assert "grammars" not in contributes


def test_the_language_configuration_matches_relevance_syntax() -> None:
    """Block comments only (the tokenizer knows no line comment); parentheses; quotes."""
    config = json.loads((PRIMARY / _language(PRIMARY)["configuration"]).read_text("utf-8"))
    assert config["comments"] == {"blockComment": ["/*", "*/"]}
    assert config["brackets"] == [["(", ")"]]
    pairs = {(pair["open"], pair["close"]) for pair in config["autoClosingPairs"]}
    assert pairs == {("(", ")"), ('"', '"')}
    # Typing `(` in "Program Files (x86)" or a comment must not add a `)`.
    for pair in config["autoClosingPairs"]:
        assert pair["notIn"] == ["string", "comment"], pair


def test_every_contributed_grammar_exists_and_is_registered_correctly() -> None:
    from bigfix_relevance_analyzer.lsp.linter import LANGUAGE_ID

    grammars = _manifest(PRIMARY)["contributes"]["grammars"]
    by_scope = {grammar["scopeName"]: grammar for grammar in grammars}
    assert by_scope["source.bigfix-relevance"]["language"] == LANGUAGE_ID
    injection = by_scope["markdown.bigfix-relevance.codeblock"]
    assert injection["injectTo"] == ["text.html.markdown"]
    assert injection["embeddedLanguages"] == {"meta.embedded.block.bigfix-relevance": LANGUAGE_ID}
    for grammar in grammars:
        on_disk = json.loads((PRIMARY / grammar["path"]).read_text("utf-8"))
        assert on_disk["scopeName"] == grammar["scopeName"]


def test_the_committed_grammars_are_what_the_generator_produces() -> None:
    """The grammars are generated from grammar.py and extract.py, never hand-edited:
    run `uv run python tools/generate_tmlanguage.py` after changing either."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    for path, grammar in generator.render().items():
        committed = json.loads((REPO_ROOT / path).read_text("utf-8"))
        assert committed == grammar, f"{path} is stale; rerun {GENERATOR.name}"


def _grammar_regexes(*names: str) -> list[re.Pattern[str]]:
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    repository = generator.relevance_grammar()["repository"]
    patterns: list[re.Pattern[str]] = []
    for name in names:
        rule = repository[name]
        for entry in rule.get("patterns", [rule]):
            patterns.append(re.compile(entry["match"]))
    return patterns


def test_the_grammar_colors_every_operator_and_structural_word_the_parser_knows() -> None:
    """Checked against the grammar's own regexes (Python's `re` reads these
    patterns the same way), in any case and with articles between the words."""
    from bigfix_relevance_analyzer.grammar import PUNCT_INFIX, STRUCTURAL_WORDS, WORD_INFIX

    words = _grammar_regexes("word-operator", "structural")
    phrases = [" ".join(spelling) for spelling in WORD_INFIX] + sorted(STRUCTURAL_WORDS)
    for phrase in phrases:
        for written in (phrase, phrase.upper(), phrase.replace(" ", " the ", 1)):
            assert any(p.fullmatch(written) for p in words), written
    (punctuation,) = _grammar_regexes("punctuation-operator")
    for op in PUNCT_INFIX:
        assert punctuation.fullmatch(op), op


def test_a_multi_word_operator_wins_over_its_first_word() -> None:
    """`is not equal to` is one comparison, not `is` then a logical `not`."""
    (comparison,) = (p for p in _grammar_regexes("word-operator") if "contained" in p.pattern)
    match = comparison.search("x is not equal to y")
    assert match is not None and match.group() == "is not equal to"


def test_the_grammar_does_not_color_inside_a_longer_word() -> None:
    """Word boundaries: `ofs`, `island`, `orange` are not `of`, `is`, `or`."""
    words = _grammar_regexes("word-operator", "structural")
    for text in ("ofs", "island", "orange", "itself", "android"):
        assert not any(p.search(text) for p in words), text


MARKDOWN_SAMPLES = {
    "plain": "```relevance\nname of it\n```\n",
    "tilde, dialect tag, any case": "~~~Session_Relevance\nnumber of bes computers\n~~~\n",
    "info after the tag": "```relevance foo\nnot read\n```\n",
    "other language": "```python\nnot read\n```\n",
    "longer opener, shorter closer": "````relevance\nfour\n```\nafter the fence\n",
    "longer closer, trailing space": "```relevance\nlonger\n```` \nafter\n",
    "other fence character inside": "```relevance\nE\n~~~\nF\n```\n",
    "indented": "  ```relevance  \nindented\n  ```\n",
    "two blocks": "```python\nx\n```\n\n```RELEVANCE\nsecond\n```\n",
}


def _anchored(pattern: str) -> re.Pattern[str]:
    """A TextMate pattern for Python's `re`: `\\G` (continue where the last
    match ended) only ever appears as `(^|\\G)` at line start here."""
    return re.compile(pattern.replace(r"(^|\G)", "^"))


def _injected_blocks(markdown: str) -> list[str]:
    """The text the injection grammar colors as relevance, block by block,
    following its begin/end rules line by line as the TextMate engine does."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    grammar = generator.markdown_injection()
    rules = [
        grammar["repository"][include["include"].removeprefix("#")]
        for include in grammar["patterns"]
    ]
    blocks: list[str] = []
    open_rule: dict[str, Any] | None = None
    end: re.Pattern[str] | None = None
    body: list[str] = []
    for line in markdown.split("\n"):
        if open_rule is None:
            for rule in rules:
                begin = _anchored(rule["begin"]).match(line)
                if begin:
                    open_rule = rule
                    # No backreferences: each end pattern stands alone, so
                    # this simulation need not resolve them against `begin`.
                    assert not re.search(r"\\\d", rule["end"]), rule["end"]
                    end = _anchored(rule["end"])
                    body = []
                    break
        elif end is not None and end.match(line):
            text = "\n".join(body).strip()
            if text:
                blocks.append(text)
            open_rule = None
        else:
            body.append(line)
    return blocks


@pytest.mark.parametrize("name", MARKDOWN_SAMPLES)
def test_the_markdown_injection_colors_exactly_the_fences_the_extractor_reads(name: str) -> None:
    from bigfix_relevance_analyzer.extract import extract_relevance_from_markdown

    markdown = MARKDOWN_SAMPLES[name]
    read = [site.text for site in extract_relevance_from_markdown(markdown)]
    assert _injected_blocks(markdown) == read


def test_the_embedded_block_continues_past_a_fence_of_the_other_character() -> None:
    """Inside a backtick block a `~~~` line is relevance to the extractor, so
    the embedded content must not stop there either (and vice versa)."""
    generator = load_tool(GENERATOR, "_generate_tmlanguage")
    repository = generator.markdown_injection()["repository"]
    for rule in repository.values():
        (inner,) = rule["patterns"]
        keep_going = _anchored(inner["while"])
        own = "```" if "`" in rule["begin"] else "~~~"
        other = "~~~" if own == "```" else "```"
        assert keep_going.match(other), rule["begin"]
        assert not keep_going.match(own), rule["begin"]


def test_the_extension_sends_relevance_buffers_whatever_their_scheme() -> None:
    """A document selector by language, not only by file pattern, is what makes
    VS Code send an unsaved `untitled:` buffer to the server."""
    text = (PRIMARY / "extension.js").read_text("utf-8")
    assert "{ language: LANGUAGE_ID }" in text


# ---------------------------------------------------------------------------
# What VS Code shows for the extension: README and manifest text
# ---------------------------------------------------------------------------

# Words that describe how the extension is built, not what it does for a user.
IMPLEMENTATION_WORDS = ("python", "webassembly", "wasm", "componentize", "proof of concept")


def test_the_primary_extension_has_a_readme_that_ships() -> None:
    """vsce packages the README beside package.json; VS Code shows it as Details."""
    readme = PRIMARY / "README.md"
    assert readme.is_file()
    ignored = (PRIMARY / ".vscodeignore").read_text("utf-8")
    assert "README" not in ignored


def test_the_readme_covers_every_file_type_setting_and_command() -> None:
    text = (PRIMARY / "README.md").read_text("utf-8")
    patterns: list[str] = json.loads((PRIMARY / "document-patterns.json").read_text("utf-8"))
    for pattern in patterns:
        suffix = pattern.removeprefix("**/*")
        assert f"`{suffix}`" in text, suffix
    for setting in _settings(PRIMARY):
        assert f"`{setting}`" in text, setting
    for command in _manifest(PRIMARY)["contributes"]["commands"]:
        assert command["title"] in text, command["title"]


def test_the_user_facing_text_leaves_out_how_the_extension_is_built() -> None:
    manifest = _manifest(PRIMARY)
    for text in (manifest["description"], (PRIMARY / "README.md").read_text("utf-8")):
        lowered = text.lower()
        for word in IMPLEMENTATION_WORDS:
            assert word not in lowered, word


def test_the_manifest_files_the_extension_where_people_look() -> None:
    manifest = _manifest(PRIMARY)
    assert {"Linters", "Programming Languages"} <= set(manifest["categories"])
    assert "bigfix" in manifest["keywords"]
