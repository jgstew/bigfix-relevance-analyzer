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
instead of a tree. The reader for this format lives in ``tests/_corpus.py``.
"""

from __future__ import annotations

import pytest
from _corpus import CorpusCase, corpus_cases, parsed_corpus_sites

from bigfix_relevance_analyzer.nodes import Node, Of, Reference, to_mermaid, to_sexpr, walk
from bigfix_relevance_analyzer.parser import ParseError, parse, try_parse
from bigfix_relevance_analyzer.tokenizer import code_tokens

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


def _misgrouped(text: str, root: Node) -> list[str]:
    """Each ``Of`` whose parenthesized flag disagrees with the source.

    A parenthesized ``prop``'s span is widened to its parentheses, so it must
    start with `(`. And a bare name can only start with `(` if it was
    parenthesized. Issue #57 broke the first rule: a freed node's address
    passed its mark to `name`, and `name of operating system` W600'd."""
    wrong: list[str] = []
    for node in walk(root):
        if not isinstance(node, Of):
            continue
        starts_with_paren = text[node.prop.span.start] == "("
        if node.prop_grouped and not starts_with_paren:
            wrong.append(f"marked grouped but bare: {text[node.span.start : node.span.end]!r}")
        if isinstance(node.prop, Reference) and starts_with_paren and not node.prop_grouped:
            wrong.append(f"parenthesized but unmarked: {text[node.span.start : node.span.end]!r}")
    return wrong


def test_corpus_parenthesized_props_match_the_source() -> None:
    wrong = [
        f"{case.id}: {problem}"
        for case in corpus_cases()
        if not case.expected.startswith("ERROR")
        for problem in _misgrouped(case.source, parse(case.source))
    ]
    assert not wrong, "\n".join(wrong)


def test_example_parenthesized_props_match_the_source() -> None:
    wrong = [
        f"{path.name}:{site.line}: {problem}"
        for path, site, node in parsed_corpus_sites()
        for problem in _misgrouped(site.text, node)
    ]
    assert not wrong, "\n".join(wrong)
