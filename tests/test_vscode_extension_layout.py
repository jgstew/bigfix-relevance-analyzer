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
