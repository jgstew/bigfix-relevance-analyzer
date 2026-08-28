"""The parse-tree corpus: input relevance to expected S-expression.

This corpus is the primary asset of the parser milestone. The parser is
correct exactly when every record here passes, and a future port (the README
names Rust) is proven equivalent by running the same files. Keep records
small and single-purpose; put the decision being pinned in the title.

Record format (``tests/corpus/*.rlvcorpus``)::

    ==== title of the case
    relevance source, which may span lines
    ----
    (of (ref "name") it)

The expected side is compared structurally, so it can be indented freely.
An expected side of ``ERROR line L column C`` pins a ParseError position
instead of a tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from bigfix_relevance_analyzer.nodes import to_mermaid, to_sexpr
from bigfix_relevance_analyzer.parser import ParseError, parse, try_parse
from bigfix_relevance_analyzer.tokenizer import code_tokens

CORPUS_DIR = Path(__file__).parent / "corpus"

# ---------------------------------------------------------------------------
# Corpus loading
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


# ---------------------------------------------------------------------------
# A tiny S-expression reader, so expected trees can be written free-form
# ---------------------------------------------------------------------------

Sexpr = str | tuple["Sexpr", ...]


def read_sexpr(text: str) -> Sexpr:
    tokens = _sexpr_tokens(text)
    value, rest = _read_one(tokens)
    assert not rest, f"trailing content in s-expression: {rest[:3]!r}"
    return value


def _sexpr_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    at = 0
    while at < len(text):
        char = text[at]
        if char.isspace():
            at += 1
        elif char in "()":
            tokens.append(char)
            at += 1
        elif char == '"':
            end = at + 1
            while text[end] != '"':
                end += 2 if text[end] == "\\" else 1
            tokens.append(text[at : end + 1])
            at = end + 1
        else:
            end = at
            while end < len(text) and not text[end].isspace() and text[end] not in '()"':
                end += 1
            tokens.append(text[at:end])
            at = end
    return tokens


def _read_one(tokens: list[str]) -> tuple[Sexpr, list[str]]:
    assert tokens, "unexpected end of s-expression"
    head, rest = tokens[0], tokens[1:]
    if head == "(":
        items: list[Sexpr] = []
        while rest and rest[0] != ")":
            item, rest = _read_one(rest)
            items.append(item)
        assert rest, "unclosed ( in s-expression"
        return tuple(items), rest[1:]
    assert head != ")", "unbalanced ) in s-expression"
    return head, rest


# ---------------------------------------------------------------------------
# The corpus tests themselves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", corpus_cases(), ids=lambda case: case.id)
def test_corpus_case(case: CorpusCase) -> None:
    if case.expected.startswith("ERROR"):
        _, _, line, _, column = case.expected.split()
        with pytest.raises(ParseError) as info:
            parse(case.source)
        assert (info.value.line, info.value.column) == (int(line), int(column)), str(info.value)
    else:
        actual = to_sexpr(parse(case.source))
        assert read_sexpr(actual) == read_sexpr(case.expected), f"\nactual: {actual}"


@pytest.mark.parametrize("case", corpus_cases(), ids=lambda case: case.id)
def test_corpus_case_root_span_covers_the_statement(case: CorpusCase) -> None:
    """Whatever tree comes out, its span must cover all the code tokens."""
    if case.expected.startswith("ERROR"):
        pytest.skip("error case has no tree")
    tokens = list(code_tokens(case.source))
    node = parse(case.source)
    assert node.span.start == tokens[0].offset
    assert node.span.end == tokens[-1].offset + len(tokens[-1].text)


def test_corpus_serialization_is_deterministic_and_reparseable() -> None:
    for case in corpus_cases():
        if case.expected.startswith("ERROR"):
            continue
        first = to_sexpr(parse(case.source))
        second = to_sexpr(parse(case.source))
        assert first == second, case.id
        assert read_sexpr(first) is not None


def test_corpus_mermaid_rendering_is_deterministic() -> None:
    for case in corpus_cases():
        if case.expected.startswith("ERROR"):
            continue
        first = to_mermaid(parse(case.source))
        second = to_mermaid(parse(case.source))
        assert first == second, case.id
        assert first.startswith("flowchart TD\n"), case.id


def test_try_parse_never_raises_on_corpus_inputs_or_their_truncations() -> None:
    """The conservative interface must hold even for broken input.

    Truncating at every token boundary is a deterministic mutation set that
    produces realistic broken relevance (extraction truncates text too).
    """
    for case in corpus_cases():
        tokens = list(code_tokens(case.source))
        for cut in range(len(tokens) + 1):
            end = len(case.source) if cut == len(tokens) else tokens[cut].offset
            result = try_parse(case.source[:end])
            assert result.ok is (result.error is None), case.id
