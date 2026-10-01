"""The test suite's two corpora, read once, shared by every module that walks them.

* ``tests/examples/`` -- real documents with embedded relevance, read through
  the extractor: :func:`corpus_files`, :func:`corpus_sites`,
  :func:`parsed_corpus_sites`.
* ``tests/corpus/*.rlvcorpus`` -- the parse-tree corpus, relevance paired with
  its expected S-expression: :func:`corpus_cases`. Its record format is
  documented in ``test_parser_corpus``, which is what holds the parser to it.

A plain module rather than ``conftest.py`` fixtures because
``tools/perf/parity.py`` imports these readers by path -- one corpus, one
reader, which ``test_perf_tools`` asserts by identity.

Extraction and parsing are cached: both are pure, and their results are frozen
dataclasses, so sharing one read between tests changes nothing a test can
observe -- it only stops each module re-reading the same files.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path

from bigfix_relevance_analyzer.extract import RelevanceSite, extract_relevance_from_file
from bigfix_relevance_analyzer.nodes import Node
from bigfix_relevance_analyzer.parser import try_parse

EXAMPLES = Path(__file__).parent / "examples"
CORPUS_DIR = Path(__file__).parent / "corpus"


# ---------------------------------------------------------------------------
# tests/examples/
# ---------------------------------------------------------------------------


def corpus_files() -> list[Path]:
    """Every example document the extractor is pointed at."""
    return sorted(
        path
        for path in EXAMPLES.rglob("*")
        if path.is_file()
        and path.name != "README.md"
        # Raw inspector-name dumps for the analyzer's inspector tables, not
        # documents with embedded relevance to extract - see
        # relevance_inspectors/README.md.
        and "relevance_inspectors" not in path.relative_to(EXAMPLES).parts
    )


@functools.cache
def extracted_sites() -> tuple[tuple[Path, RelevanceSite], ...]:
    """Every relevance site in the example corpus, with the file it came from."""
    sites = tuple(
        (path, site) for path in corpus_files() for site in extract_relevance_from_file(path)
    )
    # Most corpus tests assert "no offenders", which an empty corpus satisfies
    # vacuously; refuse that here rather than in every test.
    assert sites, f"no relevance extracted from {EXAMPLES}"
    return sites


def corpus_sites() -> list[tuple[str, str]]:
    """Every extracted statement as ``(label, text)``, labelled ``file:line``."""
    return [(f"{path.name}:{site.line}", site.text) for path, site in extracted_sites()]


@functools.cache
def parsed_corpus_sites() -> tuple[tuple[Path, RelevanceSite, Node], ...]:
    """Every extracted site that parses, with its tree."""
    parsed_sites = tuple(
        (path, site, parsed.node)
        for path, site in extracted_sites()
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
    )
    assert parsed_sites, "no example-corpus site parses"  # see extracted_sites
    return parsed_sites


# ---------------------------------------------------------------------------
# tests/corpus/*.rlvcorpus
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CorpusCase:
    file: Path
    index: int
    title: str
    source: str
    expected: str

    @property
    def id(self) -> str:
        return f"{self.file.stem}:{self.index}:{self.title}"


def load_corpus_file(path: Path) -> list[CorpusCase]:
    cases: list[CorpusCase] = []
    title: str | None = None
    source_lines: list[str] = []
    expected_lines: list[str] = []
    in_expected = False

    def flush() -> None:
        nonlocal title, source_lines, expected_lines, in_expected
        if title is None:
            return
        assert in_expected, f"{path.name}: record {title!r} has no ---- separator"
        source = "\n".join(source_lines).strip()
        expected = "\n".join(expected_lines).strip()
        assert source, f"{path.name}: record {title!r} has an empty source"
        assert expected, f"{path.name}: record {title!r} has an empty expected side"
        cases.append(CorpusCase(path, len(cases), title, source, expected))
        title, source_lines, expected_lines, in_expected = None, [], [], False

    for line in path.read_text().splitlines():
        if line.startswith("===="):
            flush()
            title = line.removeprefix("====").strip() or "untitled"
        elif line.startswith("----"):
            assert title is not None, f"{path.name}: ---- before any ===="
            in_expected = True
        elif title is not None:
            (expected_lines if in_expected else source_lines).append(line)
    flush()
    return cases


def corpus_cases() -> list[CorpusCase]:
    files = sorted(CORPUS_DIR.glob("*.rlvcorpus"))
    assert files, "no corpus files found"
    return [case for path in files for case in load_corpus_file(path)]
