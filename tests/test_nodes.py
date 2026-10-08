"""Tests for looking nodes up by source position: :func:`nodes_at` / :func:`node_at`.

What an editor asks on hover: "which node is under this offset". Each answer is
checked against a brute-force oracle over :func:`walk`, so the lookup is held
to the spans the parser actually records, not to a hand-drawn tree.
"""

from __future__ import annotations

from itertools import pairwise

import pytest
from _helpers import CLIENT

from bigfix_relevance_analyzer.nodes import (
    Node,
    Of,
    Reference,
    StringLiteral,
    node_at,
    nodes_at,
    walk,
)
from bigfix_relevance_analyzer.parser import parse

STATEMENTS = (
    'name of file "a" of folder "b"',
    CLIENT,
    'if exists file "x" then (1 + 2) else 3',
    '(1, "a"; 2, "b")',
    'names of processes whose (name of it as lowercase contains "bes")',
    'not exists keys "x" of registry | false',
    "item 0 of (1, 2)",
)


def contains(node: Node, offset: int) -> bool:
    return node.span.start <= offset < node.span.end


def oracle(root: Node, offset: int) -> set[int]:
    """Every node containing ``offset``, by exhaustive search (as ``id``s:
    equal-valued nodes can recur in one tree)."""
    return {id(node) for node in walk(root) if contains(node, offset)}


@pytest.mark.parametrize("text", STATEMENTS)
def test_every_offset_agrees_with_the_brute_force_oracle(text: str) -> None:
    """The chain is *every* node covering the offset, each inside the last.

    Which also pins the tree property the lookup relies on: the nodes covering
    any one offset are nested, never siblings that overlap.
    """
    root = parse(text)
    for offset in range(-1, len(text) + 2):
        chain = nodes_at(root, offset)
        assert {id(node) for node in chain} == oracle(root, offset)
        assert len({id(node) for node in chain}) == len(chain)
        for outer, inner in pairwise(chain):
            assert outer.span.start <= inner.span.start
            assert inner.span.end <= outer.span.end
        if chain:
            assert chain[0] is root
            assert node_at(root, offset) is chain[-1]
        else:
            assert node_at(root, offset) is None


def test_innermost_node_is_the_leaf_under_the_cursor() -> None:
    text = 'name of file "a" of folder "b"'
    root = parse(text)
    leaf = node_at(root, text.index('"a"') + 1)
    assert isinstance(leaf, StringLiteral)
    assert leaf.text == '"a"'

    name = node_at(root, 0)
    assert isinstance(name, Reference)
    assert name.phrase == "name"


def test_offset_between_children_lands_on_their_parent() -> None:
    """The `of` keyword belongs to no child, so the `Of` joining them is the answer."""
    text = "name of operating system"
    root = parse(text)
    node = node_at(root, text.index(" of ") + 1)
    assert isinstance(node, Of)
    assert node is root


def test_span_end_is_exclusive() -> None:
    """A cursor just past a token is not on it -- the same half-open
    convention :class:`Span` documents."""
    text = '"a" & "b"'
    root = parse(text)
    first = node_at(root, 0)
    assert isinstance(first, StringLiteral)
    assert node_at(root, first.span.end) is not first


def test_offsets_outside_the_statement_find_nothing() -> None:
    root = parse(CLIENT)
    assert nodes_at(root, -1) == ()
    assert nodes_at(root, len(CLIENT)) == ()
    assert node_at(root, len(CLIENT) + 10) is None


def test_a_tree_deeper_than_the_recursion_limit_does_not_crash() -> None:
    """Left-associative chains build trees far deeper than CPython recurses."""
    text = " or ".join(["true"] * 3000)
    root = parse(text)
    leaf = node_at(root, len(text) - 1)
    assert leaf is not None
    assert leaf.span.end == len(text)
