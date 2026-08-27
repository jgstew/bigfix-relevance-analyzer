"""Hold the generated inspector tables to the dumps they came from.

``src/bigfix_relevance_analyzer/_inspector_data.py`` is a generated copy of data
that lives under ``tests/``: the wheel packages ``src/`` only, so a table the
library needs at runtime has to be embedded. The duplication is deliberate, and
this module is what keeps it honest -- if someone adds a dump, edits one, or
hand-edits the generated module, the first test here fails and names the fix.

Style follows ``tests/test_dialect_markers.py``: white-box, reading the real
reference data rather than fixtures.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from bigfix_relevance_analyzer import _inspector_data

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "tools" / "generate_inspector_data.py"
DUMPS = REPO_ROOT / "tests" / "examples" / "relevance_inspectors"


def _load_generator() -> ModuleType:
    """Import the generator script, which lives outside any package."""
    spec = importlib.util.spec_from_file_location("_generate_inspector_data", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_the_generated_module_matches_the_dumps() -> None:
    """The one test that matters: regenerate in memory and compare.

    If this fails, run ``python tools/generate_inspector_data.py`` and commit
    the result -- do not hand-edit the generated module.
    """
    generator = _load_generator()
    expected = generator.render(*generator.collect())
    actual = (REPO_ROOT / "src" / "bigfix_relevance_analyzer" / "_inspector_data.py").read_text(
        encoding="utf-8"
    )
    assert actual == expected, "generated inspector data is stale; re-run the generator"


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("client_relevance_properties_windows.txt", ("client", "properties", "windows")),
        ("session_relevance_properties_web_reports.txt", ("session", "properties", "web_reports")),
        ("session_relevance_casts_rest_api.txt", ("session", "casts", "rest_api")),
        # `unary_operators` must not read as category `unary` + context `operators`.
        ("client_relevance_unary_operators_windows.txt", ("client", "unary_operators", "windows")),
        (
            "session_relevance_binary_operators_rest_api.txt",
            ("session", "binary_operators", "rest_api"),
        ),
        # A category with no context segment is still well-formed.
        ("session_relevance_casts.txt", ("session", "casts", "")),
    ],
)
def test_dump_filenames_carry_their_provenance(
    filename: str, expected: tuple[str, str, str]
) -> None:
    assert _load_generator().parse_dump_filename(filename) == expected


@pytest.mark.parametrize(
    "filename",
    [
        "properties_windows.txt",  # no dialect
        "client_relevance_widgets_windows.txt",  # unknown category
        "client_properties_windows.txt",  # missing `_relevance_`
    ],
)
def test_unparsable_dump_filenames_are_rejected(filename: str) -> None:
    """A typo'd filename must fail loudly, not be silently skipped."""
    with pytest.raises(ValueError):
        _load_generator().parse_dump_filename(filename)


def test_every_dump_is_accounted_for_by_the_generator() -> None:
    """No dump is silently ignored because its name did not parse."""
    generator = _load_generator()
    for path in DUMPS.glob("*.txt"):
        dialect, category, _context = generator.parse_dump_filename(path.name)
        assert dialect in generator.DIALECTS
        assert category in generator.CATEGORIES


def test_empty_dumps_do_not_become_sources() -> None:
    """A 0-byte placeholder means "not captured", not "captured, found nothing".

    Registering it would add a source bit no row ever sets, which a consumer
    would read as positive evidence of absence.
    """
    generator = _load_generator()
    empty = [p for p in DUMPS.glob("*.txt") if not p.read_text(encoding="utf-8").strip()]
    labels = set(_inspector_data.SOURCES)
    for path in empty:
        dialect, _category, context = generator.parse_dump_filename(path.name)
        label = generator.source_label(dialect, context)
        # The label may still exist via a *non-empty* dump of another category.
        non_empty_siblings = [
            p
            for p in DUMPS.glob(f"{dialect}_relevance_*.txt")
            if p.read_text(encoding="utf-8").strip()
            and generator.source_label(*generator.parse_dump_filename(p.name)[::2]) == label
        ]
        if not non_empty_siblings:
            assert label not in labels, f"{path.name} is empty but {label!r} is a source"


def test_every_dump_matches_the_format_its_category_implies() -> None:
    """`types` dumps are bare names; every other category is `signature: type`.

    Derived from each filename's own category rather than a hard-coded list, so
    a newly captured dump is checked the moment it lands.
    """
    generator = _load_generator()
    for path in sorted(DUMPS.glob("*.txt")):
        _dialect, category, _context = generator.parse_dump_filename(path.name)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            where = f"{path.name}:{number}"
            if category == "types":
                assert ": " not in line, f"{where}: a type dump holds bare names, got {line!r}"
            else:
                assert ": " in line, f"{where}: expected `signature: type`, got {line!r}"
                assert line.count(": ") == 1, f"{where}: ambiguous split in {line!r}"


def test_source_labels_are_all_dialect_qualified() -> None:
    """Every label is `dialect:context`, so `platforms` can be derived from it."""
    for label in _inspector_data.SOURCES:
        dialect, separator, context = label.partition(":")
        assert dialect in ("client", "session"), label
        assert separator == ":" and context, f"{label!r} has no context segment"
