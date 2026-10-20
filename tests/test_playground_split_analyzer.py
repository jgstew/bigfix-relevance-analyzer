"""The split analyzer set: ``build_split.py`` and the contract it publishes.

The set is the componentize-py analyzer as separate files in one flat folder,
always-latest, with a ``manifest.json`` naming the version and keeping the jco
glue and its core modules matched. ``tools/playground-wasm/SPLIT_ANALYZER.md``
is the canonical contract; these tests pin the producer's half of it from the
same tiny fake inputs ``test_playground_component_build.py`` uses, and pin how
CI builds, tests and releases the set.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import tomllib
import zipfile
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from _helpers import REPO_ROOT, load_tool
from test_playground_component_build import FAKE_CORES, FAKE_EDITOR, FAKE_GLUE, make_inputs

BUILD_DIR = REPO_ROOT / "tools" / "playground-wasm" / "componentize-py" / "build-playground"
CONTRACT = REPO_ROOT / "tools" / "playground-wasm" / "SPLIT_ANALYZER.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wasm-html.yaml"
RELEASE = REPO_ROOT / ".github" / "workflows" / "tag_and_release.yaml"
BROWSER_TEST = REPO_ROOT / "tools" / "playground-wasm" / "componentize-py" / "browser-test"

ZIP_NAME = "bigfix-relevance-analyzer-analyzer.zip"
CORE_FILES = {f"{name}.gz" for name in FAKE_CORES}
SET_FILES = {"manifest.json", "index.html", "editor.js", "glue.mjs", *CORE_FILES}


@pytest.fixture(scope="module")
def split() -> ModuleType:
    return load_tool(BUILD_DIR / "build_split.py", "_component_build_split")


def build(split: ModuleType, root: Path, **kwargs: Any) -> Path:
    work, editor = make_inputs(root)
    out = root / "analyzer"
    split.build(work, editor, out, **kwargs)
    return out


def manifest_of(out: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    return data


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package_version() -> str:
    version: str = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text("utf-8"))["project"][
        "version"
    ]
    return version


# --- the folder ------------------------------------------------------------


def test_the_folder_holds_exactly_the_set(split: ModuleType, tmp_path: Path) -> None:
    out = build(split, tmp_path)
    assert {p.name for p in out.iterdir()} == SET_FILES
    assert all(p.is_file() for p in out.iterdir()), "flat: no subdirectories"


def test_the_manifest_has_the_contract_fields_in_order(split: ModuleType, tmp_path: Path) -> None:
    manifest = manifest_of(build(split, tmp_path))
    assert list(manifest) == ["format", "package", "version", "editor", "glue", "cores"]
    assert manifest["format"] == 1
    assert manifest["package"] == "bigfix-relevance-analyzer"
    assert manifest["version"] == package_version()
    assert list(manifest["editor"]) == ["path", "size", "sha256"]
    assert list(manifest["glue"]) == ["path", "size", "sha256"]
    assert manifest["editor"]["path"] == "editor.js"
    assert manifest["glue"]["path"] == "glue.mjs"
    for core in manifest["cores"]:
        assert list(core) == ["name", "path", "encoding", "size", "sha256"]
        assert core["path"] == core["name"] + ".gz"
        assert core["encoding"] == "gzip"


def test_a_version_can_be_given_explicitly(split: ModuleType, tmp_path: Path) -> None:
    assert manifest_of(build(split, tmp_path, version="9.8.7"))["version"] == "9.8.7"


def test_every_size_and_sha256_is_of_the_published_bytes(split: ModuleType, tmp_path: Path) -> None:
    out = build(split, tmp_path)
    manifest = manifest_of(out)
    entries = [manifest["editor"], manifest["glue"], *manifest["cores"]]
    for entry in entries:
        data = (out / entry["path"]).read_bytes()
        assert entry["size"] == len(data), entry["path"]
        assert entry["sha256"] == sha256(data), entry["path"]
        assert "/" not in entry["path"] and ".." not in entry["path"]


def test_editor_and_glue_are_copied_unmodified(split: ModuleType, tmp_path: Path) -> None:
    out = build(split, tmp_path)
    assert (out / "editor.js").read_bytes() == FAKE_EDITOR.encode()
    assert (out / "glue.mjs").read_bytes() == FAKE_GLUE.encode()


def test_cores_are_gzip_level_9_mtime_0_like_the_single_file_page(
    split: ModuleType, tmp_path: Path
) -> None:
    out = build(split, tmp_path)
    for name, data in FAKE_CORES.items():
        packed = (out / f"{name}.gz").read_bytes()
        assert packed == gzip.compress(data, compresslevel=9, mtime=0), name
        assert gzip.decompress(packed) == data


def test_core_entries_match_the_glue_exactly(split: ModuleType, tmp_path: Path) -> None:
    manifest = manifest_of(build(split, tmp_path))
    names = [core["name"] for core in manifest["cores"]]
    assert names == sorted(FAKE_CORES)


def test_a_core_the_glue_names_but_transpile_did_not_write_fails(
    split: ModuleType, tmp_path: Path
) -> None:
    work, editor = make_inputs(tmp_path)
    (work / "transpiled" / "analyzer.core2.wasm").unlink()
    with pytest.raises(SystemExit, match=r"analyzer\.core2\.wasm"):
        split.build(work, editor, tmp_path / "analyzer")


def test_a_core_the_glue_never_names_fails(split: ModuleType, tmp_path: Path) -> None:
    work, editor = make_inputs(tmp_path)
    (work / "transpiled" / "analyzer.core3.wasm").write_bytes(b"\x00asm\x01\x00\x00\x00")
    with pytest.raises(SystemExit, match=r"analyzer\.core3\.wasm"):
        split.build(work, editor, tmp_path / "analyzer")


def test_the_manifest_is_written_last(
    split: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    written: list[str] = []
    real_write = split._write

    def recording_write(path: Path, data: bytes) -> None:
        written.append(path.name)
        real_write(path, data)

    monkeypatch.setattr(split, "_write", recording_write)
    build(split, tmp_path)
    assert set(written) == SET_FILES
    assert written[-1] == "manifest.json"


def test_a_rebuild_of_unchanged_input_is_byte_identical(split: ModuleType, tmp_path: Path) -> None:
    first = build(split, tmp_path / "a", zip_path=tmp_path / "a.zip")
    second = build(split, tmp_path / "b", zip_path=tmp_path / "b.zip")
    for name in SET_FILES:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
    assert (tmp_path / "a.zip").read_bytes() == (tmp_path / "b.zip").read_bytes()


def test_a_rebuild_removes_files_left_from_an_older_set(split: ModuleType, tmp_path: Path) -> None:
    out = tmp_path / "analyzer"
    out.mkdir()
    (out / "analyzer.core99.wasm.gz").write_bytes(b"stale")
    build(split, tmp_path)
    assert {p.name for p in out.iterdir()} == SET_FILES


def test_a_failed_build_leaves_the_previous_set_untouched(
    split: ModuleType, tmp_path: Path
) -> None:
    out = build(split, tmp_path / "good")
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    work, editor = make_inputs(tmp_path / "bad")
    (work / "transpiled" / "analyzer.core2.wasm").unlink()
    with pytest.raises(SystemExit):
        split.build(work, editor, out)
    assert {p.name: p.read_bytes() for p in out.iterdir()} == before


def test_the_editor_bundle_is_checked_like_the_single_file_build(
    split: ModuleType, tmp_path: Path
) -> None:
    work, editor = make_inputs(tmp_path)
    editor.write_text("not the editor\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="playgroundEditor"):
        split.build(work, editor, tmp_path / "analyzer")


# --- index.html --------------------------------------------------------------


def test_index_html_fetches_the_set_instead_of_embedding_it(
    split: ModuleType, tmp_path: Path
) -> None:
    page = (build(split, tmp_path) / "index.html").read_text(encoding="utf-8")
    assert "manifest.json" in page
    assert FAKE_EDITOR.strip() not in page
    assert FAKE_GLUE.strip() not in page
    assert "%%" not in page
    # The same UI as the single-file page: the shared partials are all in it.
    embed = split.embed
    for placeholder in ("%%SHARED_STYLE%%", "%%SHARED_PREFLIGHT%%"):
        partial_only = tmp_path / "partial.html"
        partial_only.write_text(placeholder, encoding="utf-8")
        assert embed.render(partial_only, {}) in page, placeholder
    assert "function runBoot(" in page
    assert page.isascii()


# --- the release zip --------------------------------------------------------


def test_the_zip_is_the_folder_flat_with_the_manifest_last(
    split: ModuleType, tmp_path: Path
) -> None:
    out = build(split, tmp_path, zip_path=tmp_path / ZIP_NAME)
    with zipfile.ZipFile(tmp_path / ZIP_NAME) as archive:
        names = archive.namelist()
        assert set(names) == SET_FILES
        assert names[-1] == "manifest.json"
        for name in names:
            assert archive.read(name) == (out / name).read_bytes(), name


# --- the contract, CI and the release ---------------------------------------


def test_the_contract_doc_names_every_manifest_field() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for field in ('"format"', '"package"', '"version"', '"editor"', '"glue"', '"cores"'):
        assert field in text, field
    for field in ('"name"', '"path"', '"encoding"', '"size"', '"sha256"'):
        assert field in text, field
    assert ZIP_NAME in text


def test_the_workflow_builds_and_browser_tests_the_set() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    job = text[text.index("  componentize-py:") : text.index("  parity:")]
    steps = job.split("      - ")[1:]

    def step(name: str) -> str:
        (found,) = (s for s in steps if f"name: {name}" in s.split("\n")[0])
        return found

    build_step = step("build the split analyzer set")
    assert "build-playground/build_split.py" in build_step
    assert "--out playground/analyzer" in build_step
    assert f"--zip playground/{ZIP_NAME}" in build_step
    assert "if:" not in build_step, "the release needs the set too"

    test_step = step("test the split analyzer set in a real browser")
    assert "node test_split_analyzer.mjs ../../../../playground/analyzer" in test_step
    assert "if: inputs.release_artifact == ''" in test_step
    assert f"path: playground/{ZIP_NAME}" in job


def test_the_release_attaches_the_zip_and_checksums_it() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    finalize = text[text.index("  finalize:") : text.index("  marketplace:")]
    assert "name: bigfix-relevance-analyzer-analyzer" in finalize
    assert f"assets/{ZIP_NAME}" in finalize
    # SHA256SUMS.txt is computed over every file in assets/, after the copy.
    assert finalize.index(f"assets/{ZIP_NAME}") < finalize.index("sha256sum ./*")


def test_the_browser_test_lives_beside_the_single_file_one() -> None:
    script = BROWSER_TEST / "test_split_analyzer.mjs"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    for shared in ("../../common/cases.mjs", "../../common/editor_checks.mjs"):
        assert shared in text, shared
    assert "../../common/lsp_script.mjs" in text
