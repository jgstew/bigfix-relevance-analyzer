"""The layout invariants of ``tools/playground-wasm/`` and its build scripts.

The playground pipelines are CI-only: nothing here is imported by the package,
and the only thing that exercises them is
``.github/workflows/pyodide.yaml``. That makes them the part of the repo most
likely to rot silently -- a directory rename that misses one path reference
still passes ``pytest`` and only fails minutes into a CI run, or worse, builds a
page against the wrong runtime version.

These tests are cheap and pure: they resolve paths and read text, never run a
build. Style follows ``tests/test_generate_client_dumps.py``, which loads a
``tools/`` script the same way.

Two runtimes live side by side under ``tools/playground-wasm/``:

* ``componentize-py/`` -- the preferred path (see the workflow header for the
  measurements behind that);
* ``pyodide/`` -- retained as the parity baseline, because comparing the two
  built pages byte-for-byte is the strongest correctness check available for the
  analyzer in a WASM host.

Both are laid out identically -- ``build-playground/``, ``smoke/``,
``browser-test/`` -- and these tests are what hold that symmetry in place. Note
the stage is *not* called ``build/``: ``.gitignore`` line 11 is a bare
``build/``, which would silently swallow the whole directory.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAYGROUND_WASM = REPO_ROOT / "tools" / "playground-wasm"

# Every runtime is expected to have the same three stages. `build-playground`
# renders the single-file page, `smoke` proves the wheel runs under that runtime
# in Node, `browser-test` drives the built page in a real headless browser.
#
# `build-playground` rather than the more obvious `build` because .gitignore
# line 11 is a bare `build/` -- named `build`, none of these files could be
# committed at all. test_nothing_under_playground_wasm_is_gitignored is what
# holds that.
STAGES = ("build-playground", "smoke", "browser-test")

# The directory names under tools/playground-wasm/ that are runtimes rather
# than shared support code.
RUNTIMES = ("componentize-py", "pyodide")

# Not a runtime: it drives both built pages at once and compares their output.
PARITY_TEST = "parity-test"

# Paths that the pre-restructure layout used. Nothing tracked may mention them
# again: a leftover reference is the exact failure mode these tests exist for.
RETIRED_PATHS = (
    "tools/pyodide-playground",
    "tools/pyodide-playground-test",
    "tools/pyodide-smoke",
    # The workflow was renamed once it stopped being Pyodide-only.
    "workflows/pyodide.yaml",
)

# The workflow that builds and tests both playgrounds. Named for what it
# produces (WASM-backed HTML pages) rather than for either runtime, so adding or
# swapping a runtime does not make the filename a lie again.
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wasm-html.yaml"
DEPENDABOT = REPO_ROOT / ".github" / "dependabot.yml"

# The npm equivalent of `[tool.uv] exclude-newer` in pyproject.toml: refuse to
# resolve any version published less than this many days ago, because a release
# published minutes ago is the likeliest to be a compromised one. Same number as
# uv's and as dependabot's cooldown, on purpose -- one policy, not three.
MIN_RELEASE_AGE_DAYS = 7


def _load_script(path: Path, name: str) -> ModuleType:
    """Import a ``tools/`` script by path, the way test_generate_client_dumps does."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _tracked_text_files() -> list[Path]:
    """Every tracked file worth grepping, without shelling out to git.

    Walking the tree and skipping the usual generated/vendored directories is
    enough here and keeps the test runnable in a source export with no .git.
    """
    skip = {".git", "node_modules", "__pycache__", ".venv", "dist", "playground", ".ruff_cache"}
    this_file = Path(__file__).resolve()
    out = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or any(part in skip for part in path.parts):
            continue
        # This module names the retired paths as data, in RETIRED_PATHS.
        if path.resolve() == this_file:
            continue
        if path.suffix in {".py", ".mjs", ".js", ".html", ".json", ".yaml", ".yml", ".md", ".toml"}:
            out.append(path)
    return out


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("stage", STAGES)
def test_every_runtime_has_every_stage(runtime: str, stage: str) -> None:
    """The two runtimes stay symmetric, so one can be read against the other."""
    assert (PLAYGROUND_WASM / runtime / stage).is_dir()


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_build_stage_has_a_script_and_a_template(runtime: str) -> None:
    build = PLAYGROUND_WASM / runtime / "build-playground"
    assert (build / "build_playground.py").is_file()
    assert (build / "template.html").is_file()


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("stage", ("smoke", "browser-test"))
def test_node_stages_are_pinned_npm_packages(runtime: str, stage: str) -> None:
    """Exact-pinned deps, and a lockfile beside every package.json.

    A caret or tilde here would let CI silently drift onto a different runtime
    build than the one the page was measured against.
    """
    package_json = PLAYGROUND_WASM / runtime / stage / "package.json"
    assert package_json.is_file()
    assert (PLAYGROUND_WASM / runtime / stage / "package-lock.json").is_file()

    manifest = json.loads(package_json.read_text(encoding="utf-8"))
    assert manifest.get("private") is True, "these are CI-only, never published"
    for name, spec in manifest.get("dependencies", {}).items():
        assert spec[0].isdigit(), f"{name} is {spec!r}, which is not an exact pin"


def test_pyodide_build_script_finds_its_version_pin() -> None:
    """The cross-check in build_playground.py resolves after the restructure.

    ``_check_pinned_version_matches`` compares the script's own PYODIDE_VERSION
    against the smoke package's pin so the browser page and the Node smoke test
    cannot end up exercising two different Pyodide releases. It reads that
    package.json through a relative path, which is exactly what a directory
    move breaks -- and it would break by raising, not by returning a wrong
    answer, so calling it is the whole test.
    """
    script = PLAYGROUND_WASM / "pyodide" / "build-playground" / "build_playground.py"
    module = _load_script(script, "_pyodide_build_playground")

    assert module.PACKAGE_JSON.is_file(), f"pin cross-check points at {module.PACKAGE_JSON}"
    module._check_pinned_version_matches()


def test_no_tracked_file_references_the_retired_paths() -> None:
    """A missed path reference is the failure mode of a directory rename."""
    offenders = []
    for path in _tracked_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for retired in RETIRED_PATHS:
            if retired in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)} -> {retired}")
    assert not offenders, "stale path references:\n  " + "\n  ".join(sorted(offenders))


def test_nothing_under_playground_wasm_is_gitignored() -> None:
    """Source under tools/playground-wasm/ must actually be committable.

    Existing on disk is not enough. ``.gitignore`` carries broad, generic
    patterns -- a bare ``build/`` on line 11, plus ``dist/`` and ``node_modules/``
    -- and a stage directory whose name collides with one of them is invisible
    to git while looking perfectly fine locally. That is how this suite's own
    ``build/`` stage had to be renamed to ``build-playground/``.

    ``git check-ignore`` is the authority here rather than a hand-rolled matcher:
    reimplementing gitignore semantics is exactly the kind of near-miss this
    test is meant to catch.
    """
    git = shutil.which("git")
    if git is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("needs a git checkout")

    # node_modules and __pycache__ are meant to be ignored; everything else
    # under here is source.
    generated = {"node_modules", "__pycache__"}
    candidates = [
        path
        for path in PLAYGROUND_WASM.rglob("*")
        if path.is_file() and not generated.intersection(path.parts)
    ]
    assert candidates, "nothing found to check"

    # check-ignore exits 0 and echoes back whichever paths are ignored.
    result = subprocess.run(
        [git, "check-ignore", "--", *(str(p) for p in candidates)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    ignored = [line for line in result.stdout.splitlines() if line.strip()]
    assert not ignored, "gitignored source under tools/playground-wasm/:\n  " + "\n  ".join(
        str(Path(line).relative_to(REPO_ROOT)) if Path(line).is_absolute() else line
        for line in sorted(ignored)
    )


def test_the_parity_test_exists_and_is_a_pinned_npm_package() -> None:
    """The parity stage is what justifies keeping two runtimes at all.

    It loads both built pages in one browser and compares their JSON output as
    strings. Without it there is no reason to keep the Pyodide pipeline alive,
    so its absence is a structural failure rather than a missing nicety.
    """
    parity = PLAYGROUND_WASM / PARITY_TEST
    assert parity.is_dir()
    assert (parity / "test_parity.mjs").is_file()

    package_json = parity / "package.json"
    assert package_json.is_file()
    assert (parity / "package-lock.json").is_file()
    manifest = json.loads(package_json.read_text(encoding="utf-8"))
    assert manifest.get("private") is True
    for name, spec in manifest.get("dependencies", {}).items():
        assert spec[0].isdigit(), f"{name} is {spec!r}, which is not an exact pin"


def test_the_shared_cases_are_the_only_copy() -> None:
    """Neither browser test may carry its own case list.

    Two pages held to two separately-maintained expectation lists could both
    pass while disagreeing with each other, which would defeat the entire point
    of building the second playground.
    """
    for runtime in RUNTIMES:
        test_file = PLAYGROUND_WASM / runtime / "browser-test" / "test_playground.mjs"
        text = test_file.read_text(encoding="utf-8")
        assert "../../common/cases.mjs" in text, f"{test_file} does not import the shared cases"
        assert "const CASES = [" not in text, f"{test_file} declares its own CASES"


def test_the_workflow_exists_and_drives_both_runtimes() -> None:
    """Both runtimes and the parity gate are actually wired into CI.

    Everything under tools/playground-wasm/ is CI-only -- nothing imports it and
    no other test runs it -- so a stage that exists but is never invoked is
    indistinguishable from a stage that works. This checks each one is named in
    the workflow.
    """
    assert WORKFLOW.is_file(), f"{WORKFLOW} is missing"
    text = WORKFLOW.read_text(encoding="utf-8")
    for runtime in RUNTIMES:
        for stage in STAGES:
            path = f"tools/playground-wasm/{runtime}/{stage}"
            assert path in text, f"{WORKFLOW.name} never mentions {path}"
    assert f"tools/playground-wasm/{PARITY_TEST}" in text


def _npm_package_dirs() -> list[Path]:
    """Every directory under tools/playground-wasm/ holding a package.json."""
    return sorted(
        path.parent
        for path in PLAYGROUND_WASM.rglob("package.json")
        if "node_modules" not in path.parts
    )


def test_there_are_npm_packages_to_check() -> None:
    """Guard the two tests below against silently passing on an empty list."""
    assert len(_npm_package_dirs()) >= 5


@pytest.mark.parametrize("package_dir", _npm_package_dirs(), ids=lambda p: p.name)
def test_every_npm_package_enforces_a_release_age_cooldown(package_dir: Path) -> None:
    """Every npm package here refuses freshly-published versions.

    This is the npm counterpart of `[tool.uv] exclude-newer = "7 days"` in
    pyproject.toml, and it exists for the same reason: the window in which a
    compromised release is live and undetected is measured in hours, so simply
    not installing anything published this week removes most of that exposure.

    `npm ci` is unaffected -- it installs what the lockfile already pins -- so
    this guards the moment a version is *chosen*: a developer running
    `npm install` or `npm update` in one of these directories. Automated bumps
    are covered separately, by dependabot's cooldown.

    Note the setting is per-directory: npm reads `.npmrc` from the current
    working directory and does not walk up to parents, so a single file at the
    repo root would not cover these.
    """
    npmrc = package_dir / ".npmrc"
    assert npmrc.is_file(), f"{package_dir.name} has no .npmrc"
    settings = dict(
        line.split("=", 1)
        for line in npmrc.read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.lstrip().startswith(("#", ";"))
    )
    assert settings.get("min-release-age") == str(MIN_RELEASE_AGE_DAYS), (
        f"{npmrc} should set min-release-age={MIN_RELEASE_AGE_DAYS}, got "
        f"{settings.get('min-release-age')!r}"
    )


@pytest.mark.parametrize("package_dir", _npm_package_dirs(), ids=lambda p: p.name)
def test_every_npm_package_is_watched_by_dependabot(package_dir: Path) -> None:
    """A package dependabot does not know about never gets a security bump.

    Each of these directories is its own npm project with its own lockfile, and
    dependabot only looks where it is told, so adding a stage without adding an
    entry here silently leaves it unwatched.
    """
    relative = "/" + str(package_dir.relative_to(REPO_ROOT))
    text = DEPENDABOT.read_text(encoding="utf-8")
    assert f'directory: "{relative}"' in text, f"{DEPENDABOT.name} has no npm entry for {relative}"
