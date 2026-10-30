"""Tests for :func:`~bigfix_relevance_analyzer.highlight.highlight`, the
parse-aware highlighter.

Relevance has no reserved words, so a word list cannot colour it: ``starts``
is an inspector in ``starts of ranges`` and half of an operator in ``starts
with``. These pin that the parse tree decides, hold the spans to the token
stream over every corpus statement, check the classification against a
brute-force :func:`~bigfix_relevance_analyzer.nodes.node_at` oracle, and guard
the single-walk design against going quadratic.
"""

from __future__ import annotations

import time
from itertools import pairwise

import pytest
from _corpus import corpus_cases, corpus_sites

import bigfix_relevance_analyzer as package
from bigfix_relevance_analyzer import nodes
from bigfix_relevance_analyzer.highlight import HighlightKind, HighlightSpan, highlight
from bigfix_relevance_analyzer.parser import try_parse
from bigfix_relevance_analyzer.tokenizer import TokenKind, tokenize

K = HighlightKind


def kinds(text: str) -> list[tuple[str, HighlightKind]]:
    """Every span as ``(its text, its kind)``, punctuation included."""
    return [(text[span.start : span.end], span.kind) for span in highlight(text)]


def words(text: str) -> list[tuple[str, HighlightKind]]:
    """:func:`kinds` without punctuation, which is what the cases below are about."""
    return [pair for pair in kinds(text) if pair[1] is not K.PUNCTUATION]


# The issue's table, then the node kinds it did not cover.
CASES = [
    (
        'names of bes computers whose (name of operating system of it starts with "Win")',
        [
            ("names", K.PROPERTY),
            ("of", K.KEYWORD),
            ("bes", K.PROPERTY),
            ("computers", K.PROPERTY),
            ("whose", K.KEYWORD),
            ("name", K.PROPERTY),
            ("of", K.KEYWORD),
            ("operating", K.PROPERTY),
            ("system", K.PROPERTY),
            ("of", K.KEYWORD),
            ("it", K.KEYWORD),
            ("starts", K.OPERATOR),
            ("with", K.OPERATOR),
            ('"Win"', K.STRING),
        ],
    ),
    (
        # `starts` is the plural `start` inspector here, not `starts with`.
        "starts of ranges whose (it contains now)",
        [
            ("starts", K.PROPERTY),
            ("of", K.KEYWORD),
            ("ranges", K.PROPERTY),
            ("whose", K.KEYWORD),
            ("it", K.KEYWORD),
            ("contains", K.OPERATOR),
            ("now", K.PROPERTY),
        ],
    ),
    (
        "(name of it as lowercase, version of it) of operating system",
        [
            ("name", K.PROPERTY),
            ("of", K.KEYWORD),
            ("it", K.KEYWORD),
            ("as", K.KEYWORD),
            ("lowercase", K.TYPE),
            ("version", K.PROPERTY),
            ("of", K.KEYWORD),
            ("it", K.KEYWORD),
            ("of", K.KEYWORD),
            ("operating", K.PROPERTY),
            ("system", K.PROPERTY),
        ],
    ),
    (
        'exists file "/etc/os-release" and not exists key "HKLM\\x" of registry',
        [
            ("exists", K.KEYWORD),
            ("file", K.PROPERTY),
            ('"/etc/os-release"', K.STRING),
            ("and", K.OPERATOR),
            ("not", K.KEYWORD),
            ("exists", K.KEYWORD),
            ("key", K.PROPERTY),
            ('"HKLM\\x"', K.STRING),
            ("of", K.KEYWORD),
            ("registry", K.PROPERTY),
        ],
    ),
    (
        'if (1 = 1) then "a" else "b"',
        [
            ("if", K.KEYWORD),
            ("1", K.NUMBER),
            ("=", K.OPERATOR),
            ("1", K.NUMBER),
            ("then", K.KEYWORD),
            ('"a"', K.STRING),
            ("else", K.KEYWORD),
            ('"b"', K.STRING),
        ],
    ),
    (
        # Does not parse: the token-level fallback.
        "name of (it",
        [("name", K.PROPERTY), ("of", K.KEYWORD), ("it", K.KEYWORD)],
    ),
    (
        # Aggregation and tuple indexing are grammar, not inspectors.
        "number of items 0 of (1, 2)",
        [
            ("number", K.KEYWORD),
            ("of", K.KEYWORD),
            ("items", K.KEYWORD),
            ("0", K.NUMBER),
            ("of", K.KEYWORD),
            ("1", K.NUMBER),
            ("2", K.NUMBER),
        ],
    ),
    (
        # A chained cast, and a type name of two words.
        '"1" as floating point as string',
        [
            ('"1"', K.STRING),
            ("as", K.KEYWORD),
            ("floating", K.TYPE),
            ("point", K.TYPE),
            ("as", K.KEYWORD),
            ("string", K.TYPE),
        ],
    ),
    (
        # Symbolic operators, word operators, and the error fallback.
        "-1 + 2 mod 3 | 4",
        [
            ("-", K.OPERATOR),
            ("1", K.NUMBER),
            ("+", K.OPERATOR),
            ("2", K.NUMBER),
            ("mod", K.OPERATOR),
            ("3", K.NUMBER),
            ("|", K.OPERATOR),
            ("4", K.NUMBER),
        ],
    ),
    (
        # A multi-word operator whose middle word is also a structural word.
        'name of it does not contain "x"',
        [
            ("name", K.PROPERTY),
            ("of", K.KEYWORD),
            ("it", K.KEYWORD),
            ("does", K.OPERATOR),
            ("not", K.OPERATOR),
            ("contain", K.OPERATOR),
            ('"x"', K.STRING),
        ],
    ),
    (
        # An index argument is its own node, not part of the name.
        'file (name of it) of folder "x"',
        [
            ("file", K.PROPERTY),
            ("name", K.PROPERTY),
            ("of", K.KEYWORD),
            ("it", K.KEYWORD),
            ("of", K.KEYWORD),
            ("folder", K.PROPERTY),
            ('"x"', K.STRING),
        ],
    ),
    (
        # A comment is coloured; an article is trivia, like whitespace.
        '/* why */ exists the file "x"',
        [
            ("/* why */", K.COMMENT),
            ("exists", K.KEYWORD),
            ("file", K.PROPERTY),
            ('"x"', K.STRING),
        ],
    ),
    (
        # Unparsed, so the parser's operator trie decides from the tokens:
        # `starts with` is a whole operator here, and any other word a name.
        'name of it starts with "a" (',
        [
            ("name", K.PROPERTY),
            ("of", K.KEYWORD),
            ("it", K.KEYWORD),
            ("starts", K.OPERATOR),
            ("with", K.OPERATOR),
            ('"a"', K.STRING),
        ],
    ),
    (
        # An unterminated string is an error token, and never raises.
        'exists file "unterminated',
        [("exists", K.KEYWORD), ("file", K.PROPERTY), ('"unterminated', K.ERROR)],
    ),
]


@pytest.mark.parametrize(("text", "expected"), CASES, ids=[case[0] for case in CASES])
def test_each_word_is_classified_by_the_parse_tree(
    text: str, expected: list[tuple[str, HighlightKind]]
) -> None:
    assert words(text) == expected


def test_parentheses_commas_and_semicolons_are_punctuation() -> None:
    assert [pair for pair in kinds("(1, 2; 3)") if pair[1] is K.PUNCTUATION] == [
        ("(", K.PUNCTUATION),
        (",", K.PUNCTUATION),
        (";", K.PUNCTUATION),
        (")", K.PUNCTUATION),
    ]


def test_the_empty_statement_and_pure_trivia_have_no_spans() -> None:
    assert highlight("") == []
    assert highlight("  \n\t the  ") == []


def test_a_span_is_frozen_and_its_kind_is_a_string() -> None:
    (span,) = highlight("it")
    assert span == HighlightSpan(0, 2, K.KEYWORD)
    assert span.kind == "keyword"
    with pytest.raises(AttributeError):
        span.kind = K.TYPE  # type: ignore[misc]


def test_offsets_are_characters_not_code_units() -> None:
    """A non-BMP character is one character here: UTF-16 is the LSP layer's job."""
    text = f'"{chr(0x1F600)}" = name'
    assert kinds(text) == [
        (f'"{chr(0x1F600)}"', K.STRING),
        ("=", K.OPERATOR),
        ("name", K.PROPERTY),
    ]
    assert highlight(text)[-1] == HighlightSpan(6, 10, K.PROPERTY)


def test_it_is_exported_from_the_package() -> None:
    assert package.highlight is highlight
    assert package.HighlightSpan is HighlightSpan
    assert package.HighlightKind is HighlightKind
    assert {"highlight", "HighlightSpan", "HighlightKind"} <= set(package.__all__)


# ---------------------------------------------------------------------------
# Over every statement the suite has
# ---------------------------------------------------------------------------


def _all_statements() -> list[str]:
    return [text for _, text in corpus_sites()] + [case.source for case in corpus_cases()]


ALL_STATEMENTS = _all_statements()


def test_spans_cover_every_meaningful_token_exactly_once_in_order() -> None:
    """Whitespace and articles get no span; every other token gets exactly one,
    over exactly its text, so spans are sorted and never overlap."""
    offenders = []
    for text in ALL_STATEMENTS:
        expected = [
            (token.offset, token.offset + len(token.text))
            for token in tokenize(text)
            if token.kind not in (TokenKind.WHITESPACE, TokenKind.ARTICLE)
        ]
        spans = highlight(text)
        if [(span.start, span.end) for span in spans] != expected:
            offenders.append(text)
        assert all(a.end <= b.start for a, b in pairwise(spans)), text
    assert not offenders, offenders[:5]


def _oracle(root: nodes.Node, text: str, offset: int) -> HighlightKind | None:
    """What the issue's per-token prototype says a word is, through
    :func:`~bigfix_relevance_analyzer.nodes.node_at`: slow, but obviously right
    for the node kinds it decides."""
    node = nodes.node_at(root, offset)
    if isinstance(node, nodes.Reference):
        return K.PROPERTY
    if isinstance(node, nodes.It):
        return K.KEYWORD
    if isinstance(node, nodes.Cast) and offset > node.operand.span.end:
        return K.KEYWORD if text.lower() == "as" else K.TYPE
    return None


def test_names_types_and_it_agree_with_a_node_at_oracle() -> None:
    """Every word the oracle can decide, decided the same way, over every
    statement that parses, and no other word called a name or a type: the
    single tree walk loses nothing to the per-token lookup it replaces."""
    checked = 0
    for text in ALL_STATEMENTS:
        parsed = try_parse(text)
        if parsed.node is None:
            continue
        spans = {span.start: span.kind for span in highlight(text)}
        for token in tokenize(text):
            if token.kind is not TokenKind.WORD:
                continue
            wanted = _oracle(parsed.node, token.text, token.offset)
            got = spans[token.offset]
            if wanted is not None:
                assert got is wanted, (text, token)
                checked += 1
            else:
                # And nothing the tree does not call a name or a type is one.
                assert got not in (K.PROPERTY, K.TYPE), (text, token)
    assert checked > 1000


@pytest.mark.parametrize(
    "text",
    ["name of (it whose (", "))) of of of", "\x00\x01", '"a" "b', "/* open", "!", "1.5", "of"],
)
def test_unparsable_input_never_raises_and_still_classifies(text: str) -> None:
    spans = highlight(text)
    assert all(isinstance(span.kind, HighlightKind) for span in spans)


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


def _best_of(runs: int, call: object) -> float:
    assert callable(call)
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        call()
        best = min(best, time.perf_counter() - start)
    return best


def test_highlighting_costs_little_more_than_parsing() -> None:
    """One tree walk and one merge pass, not a root-down lookup per token.

    A long ``or`` chain is the worst case for a per-token lookup: the tree is
    as deep as the chain is long, so each lookup walks most of it and the
    total goes quadratic -- over a hundred times the parse at this size. The
    factor allowed is loose enough for a noisy CI machine and still nowhere
    near that.
    """
    text = " or ".join(f'name of file "f{i}" of folder "d{i}" = "x"' for i in range(1500))
    assert try_parse(text).ok
    parse_time = _best_of(3, lambda: try_parse(text))
    highlight_time = _best_of(3, lambda: highlight(text))
    assert highlight_time < 4 * parse_time, (highlight_time, parse_time)
