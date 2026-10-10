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

import codecs
import inspect
import json
import re
import shutil
import struct
import subprocess
import tomllib
import zipfile
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import pytest
from _helpers import BES_BROKEN, BROKEN, load_tool

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


def test_the_server_takes_the_filesystem_away_before_the_component_loads() -> None:
    """preview2-shim preopens the whole host filesystem unless told otherwise.

    server.js clears it on the very shim module instance the glue imports
    (resolved from the glue's own location), before importing the glue, so the
    component never sees a directory. test/server.test.mjs checks the result.
    """
    server = (PRIMARY / "server.js").read_text("utf-8")
    assert "createRequire(COMPONENT)" in server
    cleared = server.index("_clearPreopens()")
    assert cleared < server.index("await import(pathToFileURL(COMPONENT)")


def test_the_server_takes_the_environment_away_before_the_component_loads() -> None:
    """preview2-shim passes the host's environment variables through by default."""
    server = (PRIMARY / "server.js").read_text("utf-8")
    assert server.index("_setEnv({})") < server.index("await import(pathToFileURL(COMPONENT)")


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


def test_the_package_leaves_out_the_native_filesystem_helper() -> None:
    """One .vsix for every platform: no per-platform native builds inside it.

    npm installs only the build of ``@bytecodealliance/jco-node-fs`` for the
    machine it runs on, so a .vsix packaged on Linux would carry a Linux binary
    to Windows and macOS. The shim loads that helper only for a WASI ``advise``
    call, which the server never makes (issue #96, item 8).
    """
    ignored = (PRIMARY / ".vscodeignore").read_text("utf-8").splitlines()
    assert "node_modules/@bytecodealliance/jco-node-fs-*/**" in ignored


def _vsix(path: Path, names: list[str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, "")
    return path


def test_a_package_holding_a_native_build_is_refused(tmp_path: Path) -> None:
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    native = (
        "extension/node_modules/@bytecodealliance/"
        "jco-node-fs-linux-x64-gnu/jco-node-fs.linux-x64-gnu.node"
    )
    vsix = _vsix(tmp_path / "native.vsix", ["extension/server.js", native])
    with pytest.raises(SystemExit, match=re.escape(native)):
        build.check_portable(vsix)


def test_a_package_without_native_builds_passes(tmp_path: Path) -> None:
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    vsix = _vsix(
        tmp_path / "portable.vsix",
        ["extension/server.js", "extension/dist/component/lsp.core.wasm"],
    )
    build.check_portable(vsix)


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


def _manifest_icons(extension: Path) -> list[str]:
    """Every icon path package.json names: the extension's own, and each language's."""
    manifest = _manifest(extension)
    icons = [manifest["icon"]] if "icon" in manifest else []
    for language in manifest["contributes"].get("languages", []):
        icons.extend(language.get("icon", {}).values())
    return [icon.removeprefix("./") for icon in icons]


def test_the_extension_names_an_icon_and_a_relevance_file_icon() -> None:
    manifest = _manifest(PRIMARY)
    assert manifest["icon"].endswith(".png"), "Marketplace and Open VSX need a PNG icon"
    (relevance,) = (
        lang for lang in manifest["contributes"]["languages"] if lang["id"] == "bigfix-relevance"
    )
    # VS Code takes a file icon per theme kind; both are the light logo.
    assert set(relevance["icon"]) == {"light", "dark"}
    assert relevance["icon"]["light"] == relevance["icon"]["dark"]


def test_the_build_copies_every_icon_the_manifest_names_from_the_logo(tmp_path: Path) -> None:
    """The logo lives once, in docs/images/; the build copies it beside
    package.json for vsce, as it does the LICENSE."""
    build = load_tool(PRIMARY / "build-component" / "build_component.py", "_build_component")
    copied = build.copy_icons(tmp_path)
    logos = {path.read_bytes(): path.name for path in (REPO_ROOT / "docs" / "images").glob("logo*")}
    for icon in _manifest_icons(PRIMARY):
        assert tmp_path / icon in copied, icon
        logo = logos.get((tmp_path / icon).read_bytes())
        assert logo is not None, icon
        # The light logo everywhere (the dark one is kept but not used), and
        # each icon in its own format.
        assert "dark" not in logo, (icon, logo)
        assert Path(icon).suffix == Path(logo).suffix, (icon, logo)
    # vsce and Open VSX take only a PNG of at least 128x128.
    icon = (tmp_path / _manifest(PRIMARY)["icon"]).read_bytes()
    assert icon.startswith(b"\x89PNG\r\n\x1a\n")
    width, height = struct.unpack(">II", icon[16:24])
    assert width >= 128 and height >= 128, (width, height)


def test_the_copied_icons_are_never_committed() -> None:
    git = shutil.which("git")
    if git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    for icon in _manifest_icons(PRIMARY):
        result = subprocess.run(
            [git, "check-ignore", "-q", str(PRIMARY / icon)], cwd=REPO_ROOT, capture_output=True
        )
        assert result.returncode == 0, f"the build's copy of {icon} is not gitignored"


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
        '"docs/images/**"',
        '".pre-commit-config.yaml"',
        '".github/workflows/vscode-extension.yaml"',
    ):
        assert path in text, path
    assert "paths: *inputs" in text
    assert "workflow_dispatch:" in text


# ---------------------------------------------------------------------------
# Releases: tag_and_release.yaml attaches the .vsix, built from the release's wheel
# ---------------------------------------------------------------------------

RELEASE = REPO_ROOT / ".github" / "workflows" / "tag_and_release.yaml"


PUBLISH = REPO_ROOT / ".github" / "workflows" / "publish-vscode-extension.yaml"


def _job(workflow: str, name: str) -> str:
    """The text of the top-level job ``name`` in ``workflow``: up to the next job."""
    match = re.search(
        rf"^  {name}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)", workflow, re.MULTILINE | re.DOTALL
    )
    assert match, name
    return match.group(1)


def test_the_release_passes_the_open_vsx_token_to_the_publish_workflow() -> None:
    """A called workflow gets an environment secret only when its caller passes
    it, by name or with `secrets: inherit`; otherwise it is an empty string
    with no error. The v1.29.0 release's Open VSX job failed exactly so."""
    marketplace = _job(RELEASE.read_text("utf-8"), "marketplace")
    assert "uses: ./.github/workflows/publish-vscode-extension.yaml" in marketplace
    assert re.search(
        r"^    secrets:\n      OVSX_PAT: \$\{\{ secrets\.OVSX_PAT \}\}$", marketplace, re.MULTILINE
    )
    # By name, not every secret the repository has.
    assert not re.search(r"^    secrets: inherit", marketplace, re.MULTILINE)
    # ...and a caller that forgets it fails to start rather than running blind.
    publish = PUBLISH.read_text("utf-8")
    call = publish.split("  workflow_call:\n", 1)[1].split("  workflow_dispatch:\n", 1)[0]
    assert re.search(
        r"^    secrets:\n      OVSX_PAT:\n(?:        #.*\n)*        required: true$",
        call,
        re.MULTILINE,
    )


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


def _e2e_job() -> str:
    text = WORKFLOW.read_text("utf-8")
    return text[text.index("  e2e:") :]


def test_the_e2e_test_runs_on_linux_and_windows() -> None:
    """The one .vsix is meant for every platform, so it is tested on more than one.

    ``fail-fast: false`` so a failure on one platform still reports the other.
    """
    e2e = _e2e_job()
    assert "runs-on: ${{ matrix.os }}" in e2e
    assert re.search(r"os: \[ubuntu-latest, windows-latest\]", e2e)
    assert "fail-fast: false" in e2e


def test_the_e2e_test_needs_a_virtual_display_only_on_linux() -> None:
    """xvfb-run exists only on Linux; Windows runners have a desktop already."""
    e2e = _e2e_job()
    assert "xvfb-run" in e2e
    assert "RUNNER_OS" in e2e
    assert "shell: bash" in e2e


def test_the_e2e_test_unzips_the_vsix_without_unzip() -> None:
    """``unzip`` is not on every runner; Python's zipfile is."""
    e2e = _e2e_job()
    assert "python -m zipfile -e" in e2e
    assert "unzip -q" not in e2e


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
    portable: list[Path] = []
    monkeypatch.setattr(build, "check_portable", portable.append)
    out = tmp_path / "out" / "bigfix-relevance-developer.vsix"

    assert build.main(["--package", str(out)]) == 0

    assert checked == ["9.8.7"]
    (vsce,) = (argv for argv in commands if "vsce" in argv)
    assert vsce[vsce.index("package") + 1] == "9.8.7"
    for flag in ("--no-git-tag-version", "--no-update-package-json"):
        assert flag in vsce
    assert vsce[vsce.index("--out") + 1] == str(out)
    assert out.parent.is_dir(), "vsce does not create the --out directory itself"
    assert portable == [out], "every packaged .vsix is checked for native builds"


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


def _language(extension: Path, language_id: str = "bigfix-relevance") -> dict[str, Any]:
    (language,) = (
        language
        for language in _manifest(extension)["contributes"]["languages"]
        if language["id"] == language_id
    )
    found: dict[str, Any] = language
    return found


ACTIONSCRIPT_ID = "bigfix-actionscript"
BES_ID = "bigfix-bes"


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


def test_the_relevance_language_is_listed_first() -> None:
    """extension.js reads `contributes.languages[0]` as the relevance language."""
    assert "manifest.contributes.languages[0].id" in (PRIMARY / "extension.js").read_text("utf-8")
    assert _manifest(PRIMARY)["contributes"]["languages"][0]["id"] == "bigfix-relevance"


def test_the_primary_extension_contributes_exactly_three_languages() -> None:
    ids = [language["id"] for language in _manifest(PRIMARY)["contributes"]["languages"]]
    assert ids == ["bigfix-relevance", ACTIONSCRIPT_ID, BES_ID]
    for language_id in ids:
        assert (PRIMARY / _language(PRIMARY, language_id)["configuration"]).is_file()


def test_the_bes_language_takes_exactly_the_files_the_extractor_reads_as_bes_xml() -> None:
    """Highlighting and linting never disagree about which files are BES."""
    from bigfix_relevance_analyzer.extract import _BES_XML_SUFFIXES, _is_bes_xml

    extensions = _language(PRIMARY, BES_ID)["extensions"]
    for extension in extensions:
        assert _is_bes_xml(Path(f"x{extension}")), extension
    assert set(_BES_XML_SUFFIXES) <= set(extensions)
    assert ".bes.xml" in extensions


def test_raw_actionscript_files_are_highlighted_but_not_linted() -> None:
    """`.actionscript` (the console's own `parent:file = <*.ActionScript>`;
    never `.as`, which is Adobe's). Linting raw ActionScript is a separate
    decision, so the suffix stays out of the analyzer's document patterns."""
    extensions = _language(PRIMARY, ACTIONSCRIPT_ID)["extensions"]
    assert extensions == [".actionscript"]
    patterns: list[str] = json.loads((PRIMARY / "document-patterns.json").read_text("utf-8"))
    assert not any(fnmatch("dir/x.actionscript", pattern) for pattern in patterns)


def test_the_actionscript_configuration_matches_actionscript_syntax() -> None:
    """Line comments only; `{` closes itself even inside a string, where a
    substitution is most often written."""
    config = json.loads(
        (PRIMARY / _language(PRIMARY, ACTIONSCRIPT_ID)["configuration"]).read_text("utf-8")
    )
    assert config["comments"] == {"lineComment": "//"}
    pairs = {pair["open"]: pair for pair in config["autoClosingPairs"]}
    assert pairs["{"]["close"] == "}" and "string" not in pairs["{"].get("notIn", [])
    assert pairs['"']["notIn"] == ["string", "comment"]


def test_the_bes_configuration_keeps_the_xml_conveniences() -> None:
    """Registering `.bes` as its own language drops VS Code's XML language
    configuration, so the one shipped here carries what XML had."""
    config = json.loads((PRIMARY / _language(PRIMARY, BES_ID)["configuration"]).read_text("utf-8"))
    assert config["comments"] == {"blockComment": ["<!--", "-->"]}
    assert ["<", ">"] in config["brackets"]
    opens = {pair["open"] for pair in config["autoClosingPairs"]}
    assert {"<!--", '"', "'", "{", "("} <= opens
    surrounds = {pair[0] for pair in config["surroundingPairs"]}
    assert opens - {"<!--"} <= surrounds


XML_FIXTURE = PRIMARY / "test" / "fixtures" / "xml"


def test_the_grammar_test_runs_against_a_vendored_vscode_xml_grammar() -> None:
    """CI has no VS Code in the package job, so the .bes grammar's interplay
    with VS Code's XML grammar is tested against a copy of it, from VS Code's
    MIT-licensed source, with both licenses it carries (PR #119 review)."""
    grammar = json.loads((XML_FIXTURE / "xml.tmLanguage.json").read_text("utf-8"))
    assert grammar["scopeName"] == "text.xml"
    readme = (XML_FIXTURE / "README.md").read_text("utf-8")
    assert "microsoft/vscode" in readme and "atom/language-xml" in readme
    assert re.search(r"\b[0-9a-f]{40}\b", readme), "record the commit it came from"
    for license_file in ("LICENSE-vscode.txt", "LICENSE-atom-language-xml.md"):
        assert "Permission is hereby granted" in (XML_FIXTURE / license_file).read_text("utf-8")
    assert "fixtures/xml/xml.tmLanguage.json" in (PRIMARY / "test" / "grammar.test.mjs").read_text(
        "utf-8"
    )
    # Never packaged: `.vscodeignore` leaves out test/**.
    assert "test/**" in (PRIMARY / ".vscodeignore").read_text("utf-8").splitlines()


def test_the_grammars_and_language_files_are_packaged() -> None:
    ignored = [
        line.strip()
        for line in (PRIMARY / ".vscodeignore").read_text("utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    contributes = _manifest(PRIMARY)["contributes"]
    paths = [grammar["path"] for grammar in contributes["grammars"]]
    paths += [language["configuration"] for language in contributes["languages"]]
    for path in paths:
        relative = path.removeprefix("./")
        assert not any(fnmatch(relative, pattern) for pattern in ignored), relative


GATE = PRIMARY / "server-gate.json"


def test_the_primary_extension_activates_cheaply_and_starts_its_server_lazily() -> None:
    """Activation loads no language client and no WebAssembly: gate.js decides,
    per open document, whether to start the server (issue #96, item 9).

    So it can activate at startup everywhere, which also covers a single file
    opened outside any folder, and the ~170 MiB server process exists only in
    windows with something to lint.
    """
    assert _manifest(PRIMARY)["activationEvents"] == ["onStartupFinished"]
    extension = (PRIMARY / "extension.js").read_text("utf-8")
    assert 'require("./gate")' in extension
    for line in extension.splitlines():
        if "vscode-languageclient" in line and "require(" in line:
            assert line.startswith(" "), f"loaded at activation: {line.strip()}"


def test_the_gate_reads_the_extractors_own_tables() -> None:
    from bigfix_relevance_analyzer.extract import (
        _CLIENTUI_HTML_SUFFIXES,
        _MARKDOWN_RELEVANCE_TAGS,
        _MARKDOWN_SUFFIXES,
    )

    gate = json.loads(GATE.read_text("utf-8"))
    assert gate["markdownFenceTags"] == sorted(_MARKDOWN_RELEVANCE_TAGS)
    assert gate["markdownSuffixes"] == sorted(_MARKDOWN_SUFFIXES)
    assert gate["htmlSuffixes"] == sorted(_CLIENTUI_HTML_SUFFIXES)


GATE_CHECK = """
const { needsServer } = require(process.argv[1]);
const fs = require("node:fs");
const paths = JSON.parse(fs.readFileSync(0, "utf8"));
const text = (fileName) => fs.readFileSync(fileName, "utf8");
const docs = paths.map((fileName) => ({ fileName, getText: () => text(fileName) }));
console.log(JSON.stringify(docs.map(needsServer)));
"""


def test_the_gate_never_holds_back_a_file_the_extractor_reads() -> None:
    """Every tracked Markdown and HTML file in this repository with relevance in
    it, by the extractor's own reading, passes the gate: a miss would leave the
    file unlinted until something else started the server."""
    from bigfix_relevance_analyzer.extract import extract_relevance_from_file

    node, git = shutil.which("node"), shutil.which("git")
    if node is None or git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("needs node and a git checkout")
    listed = subprocess.run(
        [git, "ls-files", "*.md", "*.markdown", "*.html", "*.htm"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    paths = [str(REPO_ROOT / name) for name in listed]
    with_sites = {path for path in paths if extract_relevance_from_file(path)}
    assert with_sites, "no tracked Markdown or HTML file has relevance to check against"
    result = subprocess.run(
        [node, "-e", GATE_CHECK, str(PRIMARY / "gate.js")],
        input=json.dumps(paths),
        capture_output=True,
        text=True,
        check=True,
    )
    passed = dict(zip(paths, json.loads(result.stdout), strict=True))
    assert sorted(path for path in with_sites if not passed[path]) == []


def test_the_gate_ships_and_is_tested_in_ci() -> None:
    assert (PRIMARY / "gate.js").is_file()
    assert "test/gate.test.mjs" in WORKFLOW.read_text("utf-8")
    assert '"gate.js"' in SERVER_TEST.read_text("utf-8")
    assert '"server-gate.json"' in SERVER_TEST.read_text("utf-8")


def test_the_smoke_test_checks_the_server_waits_for_relevance() -> None:
    """A second VS Code run: Markdown and HTML without relevance leave the
    server unstarted; opening a relevance-fenced Markdown file starts it."""
    run = (COMMON_SMOKE / "run.mjs").read_text("utf-8")
    suite = (COMMON_SMOKE / "suite.js").read_text("utf-8")
    assert "SMOKE_SCENARIO" in run
    for scenario in ("lint", "idle"):
        assert f'scenario === "{scenario}"' in suite, scenario
    assert "serverRunning" in suite


def test_the_smoke_test_opens_a_bes_file_in_the_bes_language() -> None:
    """Registering `.bes` as its own language must not cost it its diagnostics:
    the server picks the extractor by file suffix, and by `languageId` only for
    a name no extractor reads (see `_document_path` in lsp/linter.py). The
    unsaved buffers of issue #120 are that case: one is switched to the BES
    language the way a pasted fixlet would be."""
    run = (COMMON_SMOKE / "run.mjs").read_text("utf-8")
    suite = (COMMON_SMOKE / "suite.js").read_text("utf-8")
    assert '"task.bes"' in run
    assert "SMOKE_BES_LANGUAGE" in run and "SMOKE_BES_LANGUAGE" in suite
    assert "languageId" in suite
    assert "setTextDocumentLanguage" in suite


def _js_string_constant(source: str, name: str) -> str:
    """The value of ``const <name> = '...' + "..." ...;`` in ``source``: plain
    ASCII literals with backslash escapes, concatenated."""
    match = re.search(rf"^const {name} =(.*?);$", source, re.MULTILINE | re.DOTALL)
    assert match, name
    literals = re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", match.group(1))
    return "".join(codecs.decode(single or double, "unicode_escape") for single, double in literals)


def test_the_smoke_bes_fixture_is_the_unit_tests_fixture() -> None:
    """Review of #133: the smoke test checks the same document the unit tests
    do, and expects the unterminated string where that document has it."""
    suite = (COMMON_SMOKE / "suite.js").read_text("utf-8")
    assert _js_string_constant(suite, "BES_BROKEN") == BES_BROKEN
    line = next(i for i, text in enumerate(BES_BROKEN.splitlines()) if BROKEN in text)
    character = BES_BROKEN.splitlines()[line].index(BROKEN) + BROKEN.index('"')
    assert f"const BES_BROKEN_ERROR = {{ line: {line}, character: {character} }};" in suite
    # ...and the checks use it, not numbers of their own.
    assert "character !== 24" not in suite
    assert suite.count("BES_BROKEN_ERROR.") >= 3


def test_the_grammar_test_runs_in_ci() -> None:
    """The real TextMate engine is the authority on the grammars (issue #116)."""
    assert (PRIMARY / "test" / "grammar.test.mjs").is_file()
    assert "test/grammar.test.mjs" in WORKFLOW.read_text("utf-8")
    dev = _manifest(PRIMARY)["devDependencies"]
    assert dev["vscode-textmate"][0].isdigit() and dev["vscode-oniguruma"][0].isdigit()


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
    actionscript = by_scope["source.bigfix-actionscript"]
    assert actionscript["language"] == ACTIONSCRIPT_ID
    assert actionscript["embeddedLanguages"] == {"meta.embedded.line.bigfix-relevance": LANGUAGE_ID}
    bes = by_scope["text.xml.bigfix-bes"]
    assert bes["language"] == BES_ID
    assert bes["embeddedLanguages"] == {
        "meta.embedded.block.bigfix-actionscript": ACTIONSCRIPT_ID,
        "meta.embedded.block.bigfix-relevance": LANGUAGE_ID,
        "meta.embedded.line.bigfix-relevance": LANGUAGE_ID,
    }
    for grammar in grammars:
        on_disk = json.loads((PRIMARY / grammar["path"]).read_text("utf-8"))
        assert on_disk["scopeName"] == grammar["scopeName"]
        # Every embedded scope the grammar uses is mapped to its language.
        used = set(re.findall(r"meta\.embedded\.[a-z]+\.bigfix-[a-z]+", json.dumps(on_disk)))
        assert used <= set(grammar.get("embeddedLanguages", {})), grammar["scopeName"]


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


def test_the_server_falls_back_on_the_bes_language_the_extension_contributes() -> None:
    """Issue #120: the id an unsaved BES XML buffer arrives with is the one the
    server reads as BES XML."""
    from bigfix_relevance_analyzer.lsp.linter import BES_LANGUAGE_ID

    (bes,) = (
        language
        for language in _manifest(PRIMARY)["contributes"]["languages"]
        if ".bes" in language.get("extensions", [])
    )
    assert BES_LANGUAGE_ID == bes["id"] == BES_ID


def test_the_extension_sends_bes_buffers_only_as_files_or_unsaved() -> None:
    """Issue #120. Unsaved BES XML buffers are sent, but not every scheme: a
    bare language selector would also lint a `git:` diff view of every `.bes`."""
    text = (PRIMARY / "extension.js").read_text("utf-8")
    assert '{ language: BES_LANGUAGE_ID, scheme: "file" }' in text
    assert '{ language: BES_LANGUAGE_ID, scheme: "untitled" }' in text
    assert "{ language: BES_LANGUAGE_ID }" not in text
    # Found by its `.bes` extension, not by a second positional contract.
    assert '.includes(".bes")' in text
    assert "languages[2]" not in text


def test_a_manifest_without_the_bes_language_costs_only_bes() -> None:
    """Review of #133: the lookup runs when VS Code loads extension.js, so a
    `.id` of nothing would stop relevance linting too, not just BES."""
    text = (PRIMARY / "extension.js").read_text("utf-8")
    assert ")?.id;" in text
    assert "...(BES_LANGUAGE_ID" in text


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
    for language in _manifest(PRIMARY)["contributes"]["languages"]:
        for extension in language["extensions"]:
            assert f"`{extension}`" in text, extension
    assert "ActionScript" in text
    assert "files.associations" in text
    examples = [
        json.loads(example) for example in re.findall(r'"files\.associations": (\{[^}]*\})', text)
    ]
    # The way back to XML covers every suffix the BES language takes.
    (to_xml,) = (found for found in examples if "xml" in found.values())
    for extension in _language(PRIMARY, BES_ID)["extensions"]:
        assert to_xml.get(f"*{extension}") == "xml", extension
    # ...and the way in, for BES saved under another name (#120), names the
    # language by the id it really has.
    (to_bes,) = (found for found in examples if "xml" not in found.values())
    assert set(to_bes.values()) == {BES_ID}


def test_the_readme_documents_quick_fixes_and_fix_on_save() -> None:
    """The kind is the server's (FIX_ALL_KIND), and fix on save is opt-in (#113)."""
    from bigfix_relevance_analyzer.lsp.linter import FIX_ALL_KIND

    text = (PRIMARY / "README.md").read_text("utf-8")
    assert "### Quick fixes" in text
    assert f'"{FIX_ALL_KIND}": "explicit"' in text
    assert "editor.codeActionsOnSave" in text
    examples = re.findall(r'"editor\.codeActionsOnSave": (\{[^}]*\})', text)
    assert [json.loads(example) for example in examples] == [
        {FIX_ALL_KIND: "explicit"},
        {"source.fixAll": "explicit"},
    ]
    assert "does not offer fixes" not in text
    # Kinds are hierarchical: the generic key other fixers suggest runs these too,
    # so the README says so and gives the way out.
    assert '"source.fixAll": "explicit"' in text
    assert f'"{FIX_ALL_KIND}": "never"' in text


def test_the_readme_documents_completion() -> None:
    """Completion shipped in #127: the README says where it works and how to
    ask for it, and no longer lists it as missing."""
    text = (PRIMARY / "README.md").read_text("utf-8")
    assert "### Completion" in text
    assert "Completion is not available yet" not in text
    for place in ("`of`", "`whose (`", "start of a statement"):
        assert place in text, place
    assert "Ctrl+Space" in text


def test_the_manifest_and_root_readme_mention_completion() -> None:
    assert "completion" in _manifest(PRIMARY)["description"].lower()
    root = (REPO_ROOT / "README.md").read_text("utf-8")
    assert "Diagnostics, hover, completion and quick fixes" in root
    assert "textDocument/completion" in root


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
    assert "actionscript" in manifest["keywords"]
    assert "ActionScript" in manifest["description"]
