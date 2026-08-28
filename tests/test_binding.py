"""What `it` refers to, pinned against a real evaluator's behavior.

Every expectation here was executed against `qna.exe` 11.0.6.137 during the
investigation recorded in
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_, so
these are observations, not readings of the documentation -- which matters,
because the engine's own error message (`"It" used outside of "whose" clause.`)
describes a narrower rule than the engine implements.

Bindings are asserted as source ranges rather than node identity: a range is
what an editor needs, and it survives any later change to the node classes.
"""

from __future__ import annotations

import pytest

from bigfix_relevance_analyzer.binding import Binder, resolve_it_bindings
from bigfix_relevance_analyzer.nodes import It, Node, Of, Reference, Span
from bigfix_relevance_analyzer.parser import parse

# The doubly-nested case: the inner `it` must reach the inner `folder`, not the
# outer one. Long enough to be worth naming once.
NESTED = (
    'number of files whose (exists folder whose (name of it = "x") of folder "C:\\") '
    'of folder "C:\\Windows"'
)


def bindings_as_text(source: str) -> list[tuple[str, str | None, Binder | None]]:
    """Each `it` in `source` as (its text, its context's text, the binder)."""
    return [
        (
            source[binding.it.span.start : binding.it.span.end],
            None
            if binding.context is None
            else source[binding.context.span.start : binding.context.span.end],
            binding.binder,
        )
        for binding in resolve_it_bindings(parse(source))
    ]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            "(it, it) of 5",
            [("it", "5", Binder.OF), ("it", "5", Binder.OF)],
            id="of-binds-it-despite-the-whose-wording",
        ),
        pytest.param(
            'name of it of file "C:\\Windows\\notepad.exe"',
            [("it", 'file "C:\\Windows\\notepad.exe"', Binder.OF)],
            id="of-binds-it-through-a-chain",
        ),
        pytest.param("it", [("it", None, None)], id="a-bare-it-has-no-context"),
        pytest.param(
            "if true then it else it",
            [("it", None, None), ("it", None, None)],
            id="if-introduces-no-context",
        ),
        pytest.param(
            "files whose (size of it > 1000)",
            [("it", "files", Binder.WHOSE)],
            id="whose-binds-it-to-the-collection",
        ),
        pytest.param(
            "key (name of it) of registry",
            [("it", "registry", Binder.OF)],
            id="an-index-is-evaluated-in-its-references-context",
        ),
    ],
)
def test_it_binds_to_the_nearest_context_introducing_construct(
    source: str, expected: list[tuple[str, str | None, Binder | None]]
) -> None:
    assert bindings_as_text(source) == expected


def test_nesting_resolves_innermost_first() -> None:
    """The engine evaluates NESTED without a binding error, so its `it` binds.

    Two `whose` clauses are in scope and the `it` sits inside both. It must
    reach the inner `folder`, not the outer `files` -- an outer-first walk
    resolves this expression to something the engine does not agree with.
    """
    assert bindings_as_text(NESTED) == [("it", "folder", Binder.WHOSE)]


def test_the_object_of_an_of_is_not_evaluated_in_its_own_context() -> None:
    """`A of B`: only `A` sees `B`. `B` sees whatever encloses the whole `of`.

    Reversing this is the easiest way to write a resolver that looks right on
    flat expressions and binds the wrong node on every nested one.
    """
    source = "files whose (name of it of parent folder of it = 1)"
    contexts = [context for _text, context, _binder in bindings_as_text(source)]
    assert contexts == ["parent folder of it", "files"]


def test_bindings_come_back_in_source_order() -> None:
    source = 'files whose (name of it = "a" and size of it > 1 and version of it = "2")'
    starts = [binding.it.span.start for binding in resolve_it_bindings(parse(source))]
    assert starts == sorted(starts)
    assert len(starts) == 3


def test_an_unbound_it_is_reported_rather_than_raised() -> None:
    """A resolver that stops at the first bad `it` is useless to an editor."""
    resolved = resolve_it_bindings(parse('(it, name of it of file "x")'))
    assert [binding.context is None for binding in resolved] == [True, False]


def test_a_tree_with_no_it_resolves_to_nothing() -> None:
    assert resolve_it_bindings(parse('number of files of folder "C:\\Windows"')) == ()


def test_deep_nesting_does_not_exhaust_the_python_stack() -> None:
    """Relevance allows expression trees 1000 levels deep.

    The tree is built directly rather than parsed: `parser` is itself recursive
    and gives up well before this depth, and that is a separate limitation from
    the one being pinned here. What this asserts is that the resolver's own walk
    is iterative, so it stays total on any tree it is handed.
    """
    span = Span(start=0, end=2, line=1, column=1)
    tree: Node = It(span=span)
    for _ in range(2000):
        tree = Of(span=span, prop=tree, obj=Reference(span=span, phrase="x"))

    assert len(resolve_it_bindings(tree)) == 1


def test_the_specialised_of_forms_introduce_no_context() -> None:
    """`number of` aggregates and `item N of` subscripts; neither rebinds `it`.

    A tuple index is an integer literal, so there is nothing inside one to
    bind, and aggregation measures its operand without changing what `it`
    means. Both were `Of` before the taxonomy change and neither bound `it`
    then either -- this pins that the split did not quietly alter scoping.
    """
    assert bindings_as_text('number of files whose (name of it = "x")') == [
        ("it", "files", Binder.WHOSE)
    ]
    assert bindings_as_text("item 0 of (1, 2)") == []
    assert bindings_as_text("number of it") == [("it", None, None)]


def test_error_fallback_passes_its_context_through_to_both_sides() -> None:
    """`|` chooses between its operands at runtime; it is not a context."""
    assert bindings_as_text("files whose (size of it | version of it)") == [
        ("it", "files", Binder.WHOSE),
        ("it", "files", Binder.WHOSE),
    ]
    assert bindings_as_text("size of it | 42") == [("it", None, None)]
