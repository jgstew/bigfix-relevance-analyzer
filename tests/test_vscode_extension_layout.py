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

import json
import shutil
import subprocess
import tomllib
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import pytest

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


def test_poc_1_exists() -> None:
    """Guard the parametrized tests below against passing on an empty list."""
    assert VSCODE_EXTENSION / "python-stdio" in EXTENSIONS


def test_the_directory_readme_describes_both_proofs_of_concept() -> None:
    text = (VSCODE_EXTENSION / "README.md").read_text("utf-8")
    assert "python-stdio/" in text
    assert "componentize-py/" in text


# ---------------------------------------------------------------------------
# Supply chain: the same rules as tools/playground-wasm/
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
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


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
def test_every_extension_pins_exactly_and_has_a_lockfile(extension: Path) -> None:
    manifest = _manifest(extension)
    assert manifest["private"] is True, "a proof of concept, never published to npm"
    assert (extension / "package-lock.json").is_file()
    for section in ("dependencies", "devDependencies"):
        for name, spec in manifest.get(section, {}).items():
            assert spec[0].isdigit(), f"{name} is {spec!r}, which is not an exact pin"


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
def test_every_extension_is_watched_by_dependabot(extension: Path) -> None:
    relative = "/" + str(extension.relative_to(REPO_ROOT))
    assert f'directory: "{relative}"' in DEPENDABOT.read_text("utf-8")


# ---------------------------------------------------------------------------
# The extension itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("extension", EXTENSIONS, ids=lambda path: path.name)
def test_the_entry_point_exists_and_parses(extension: Path) -> None:
    main = extension / _manifest(extension)["main"]
    assert main.is_file()
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    result = subprocess.run([node, "--check", str(main)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


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
    extension = VSCODE_EXTENSION / "python-stdio"
    prefix = _manifest(extension)["settingsPrefix"]
    default = _settings(extension)[f"{prefix}.server.command"]["default"]
    scripts = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text("utf-8"))["project"]["scripts"]
    assert default in scripts
    assert scripts[default] == "bigfix_relevance_analyzer.lsp.__main__:main"
