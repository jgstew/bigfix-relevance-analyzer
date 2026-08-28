r"""Breakdown probes, pinned against strings a real engine answered.

Nothing in this suite evaluates relevance -- the package deliberately ships no
evaluator. So these are string-equality tests, and their authority comes from
elsewhere: the probes and their answers were executed against `qna.exe`
11.0.6.137 during the investigation in
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_, on a
folder holding 25 files of which 21 are over 1000 bytes. That is the limit of
what is proven here, and it is worth knowing: a change that keeps these tests
green has kept the text identical to text the engine accepted, which is not the
same as having asked the engine again.
"""

from __future__ import annotations

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer.breakdown import (
    Outcome,
    ProbeKind,
    breakdown_probes,
    interpret_count_results,
)
from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.parser import parse, try_parse

# The worked example from findings section 5.2. Ground truth from the engine:
# 25 files in the folder, 21 of them over 1000 bytes, 21 names.
WORKED = r'names of files whose (size of it > 1000) of folder "C:\Windows"'
FOLDER = r'folder "C:\Windows"'
FILTERED = r"files whose (size of it > 1000)"


def test_the_worked_examples_levels_are_reported_innermost_first() -> None:
    """The three levels from 5.2, plus the one inside the filter.

    `size of it` is a level too: it is an `of` chain, it just sits inside a
    `whose` rather than on the outermost chain. Its context is the collection
    *before* filtering, which is what `it` means in there -- 25 candidates
    rather than the 21 that survive.
    """
    levels = breakdown_probes(WORKED, parse(WORKED))
    assert [(level.probe.measured, level.probe.context) for level in levels] == [
        (WORKED, None),
        (f"{FILTERED} of it", FOLDER),
        ("size of it", f"files of {FOLDER}"),
        ("names of it", f"{FILTERED} of {FOLDER}"),
    ]


def test_the_outermost_probe_matches_the_string_the_engine_answered() -> None:
    """Reported as 21 rows of `1` -- one per matching file. Verbatim from 5.2."""
    outermost = breakdown_probes(WORKED, parse(WORKED))[-1]
    assert outermost.probe.relevance == (
        "(if exists it whose (exists number of (names of it)) "
        "then number of (names of it) else -1) "
        r'of files whose (size of it > 1000) of folder "C:\Windows"'
    )


def test_the_unfiltered_pair_matches_the_string_the_engine_answered() -> None:
    """Reported as 25, against the filtered level's 21. Verbatim from 5.3."""
    filtered_level = breakdown_probes(WORKED, parse(WORKED))[1]
    assert filtered_level.unfiltered is not None
    assert filtered_level.unfiltered.relevance == (
        "(if exists it whose (exists number of (files of it)) "
        "then number of (files of it) else -1) "
        r'of folder "C:\Windows"'
    )


def test_a_whose_level_is_paired_so_the_filters_selectivity_is_visible() -> None:
    """A `whose` level counts what survived the filter, so 21 not 25.

    The number alone cannot say how selective the filter was; the pair can.
    """
    levels = breakdown_probes(WORKED, parse(WORKED))
    paired = [level for level in levels if level.unfiltered is not None]
    assert [level.probe.measured for level in paired] == [f"{FILTERED} of it"]
    assert paired[0].unfiltered is not None
    assert paired[0].unfiltered.measured == "files of it"
    assert paired[0].unfiltered.context == paired[0].probe.context


def test_an_unfiltered_level_has_no_pair() -> None:
    levels = breakdown_probes(WORKED, parse(WORKED))
    assert [level.unfiltered is None for level in levels] == [True, False, True, True]


def test_the_measured_expression_is_rewritten_against_it_not_copied() -> None:
    """The failure this guards against is loud, not silent.

    Splicing the raw source gives a probe measuring a bare `files`, and the
    engine rejects it outright: a property without its direct object is not a
    valid expression (`The operator "files" is not defined.`).
    """
    levels = breakdown_probes(WORKED, parse(WORKED))
    for level in levels[1:]:
        assert level.probe.measured.endswith(" of it")
        assert level.probe.context is not None
    assert "(files)" not in "".join(level.probe.relevance for level in levels)


def test_the_value_family_uses_its_own_guard_and_failure_signal() -> None:
    """`(true) of (X)` rather than `exists number of (X)`, and `nothing`, not -1."""
    source = r'name of file "C:\Windows\notepad.exe"'
    levels = breakdown_probes(source, parse(source), kind=ProbeKind.VALUE)
    assert levels[-1].probe.relevance == (
        "(if exists it whose ((true) of (name of it)) then (name of it) else nothing) "
        r'of file "C:\Windows\notepad.exe"'
    )
    assert all(level.probe.kind is ProbeKind.VALUE for level in levels)


def test_the_contextless_root_form_is_used_for_the_whole_expression() -> None:
    source = r'number of folders of folder "C:\Windows"'
    root = breakdown_probes(source, parse(source))[0]
    assert root.probe.context is None
    assert root.probe.relevance.startswith("(if exists true whose ")


def test_a_reference_alone_is_a_single_contextless_level() -> None:
    levels = breakdown_probes("processors", parse("processors"))
    assert len(levels) == 1
    assert levels[0].probe.context is None


def test_levels_carry_the_span_of_the_source_they_measure() -> None:
    levels = breakdown_probes(WORKED, parse(WORKED))
    for level in levels:
        assert WORKED[level.span.start : level.span.end] == level.label


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        pytest.param(["21"], [(Outcome.COUNT, 21)], id="a-count"),
        pytest.param(["0"], [(Outcome.EMPTY_OR_ERROR, 0)], id="zero-is-not-a-plain-count"),
        pytest.param(["-1"], [(Outcome.NOT_EVALUABLE, None)], id="the-sentinel"),
        pytest.param(["1"] * 21, [(Outcome.COUNT, 1)] * 21, id="one-row-per-context-object"),
        pytest.param(
            [" 3 ", "-1", "0"],
            [(Outcome.COUNT, 3), (Outcome.NOT_EVALUABLE, None), (Outcome.EMPTY_OR_ERROR, 0)],
            id="mixed-rows-are-read-positionally",
        ),
        pytest.param([], [], id="no-rows"),
    ],
)
def test_interpret_count_results(
    rows: list[str], expected: list[tuple[Outcome, int | None]]
) -> None:
    assert [(o.outcome, o.count) for o in interpret_count_results(rows)] == expected


def test_a_non_integer_row_is_refused_rather_than_coerced() -> None:
    """Silently coercing would report a count the engine never gave."""
    with pytest.raises(ValueError, match="not a count probe result"):
        interpret_count_results(["notepad.exe"])


def test_unverified_nested_it_on_the_object_side() -> None:
    """[unverified] `A of it of B` puts an `it` in the measured expression.

    `of` is right-associative, so this parses as `Of(name, Of(it, file "x"))`
    and the inner level's measured text comes out as `it of it`. Recorded as
    what the implementation does; it has not been put to a real evaluator.
    """
    source = 'name of it of file "x"'
    levels = breakdown_probes(source, parse(source))
    assert [level.probe.measured for level in levels] == [
        source,
        "it of it",
        "name of it",
    ]


def test_the_specialised_of_forms_are_still_measured_as_levels() -> None:
    """Splitting `number of` and `item N of` out of `Of` changed the taxonomy,
    not what gets probed. These levels read exactly as they did before.
    """
    source = r'number of files whose (size of it > 1000) of folder "C:\Windows"'
    levels = breakdown_probes(source, parse(source))
    assert [(level.probe.measured, level.probe.context) for level in levels] == [
        (source, None),
        (f"{FILTERED} of it", FOLDER),
        ("size of it", f"files of {FOLDER}"),
        ("number of it", f"{FILTERED} of {FOLDER}"),
    ]


def test_a_tuple_subscript_is_a_level() -> None:
    source = "item 0 of (a, b)"
    levels = breakdown_probes(source, parse(source))
    assert [(level.probe.measured, level.probe.context) for level in levels] == [
        (source, None),
        ("item 0 of it", "(a, b)"),
    ]


def test_a_specialised_levels_head_is_sliced_from_source_verbatim() -> None:
    """`NumberOf` and `ItemOf` keep no node for their head the way `Of` keeps a
    `prop`, so it is recovered from the source -- comments and spacing included,
    because the result has to be relevance the engine will still accept."""
    source = "number  /*why*/  of x"
    assert breakdown_probes(source, parse(source))[-1].probe.measured == "number  /*why*/ of it"


def test_error_fallback_is_not_a_level_but_its_operands_are_walked() -> None:
    """`|` is a compound value, not a step in an object chain -- so it is not a
    level itself. The `of` chain inside its left operand still is one."""
    source = 'size of file "c:\\nope" | 42'
    levels = breakdown_probes(source, parse(source))
    assert [(level.probe.measured, level.probe.context) for level in levels] == [
        (source, None),
        ("size of it", 'file "c:\\nope"'),
    ]


# ---------------------------------------------------------------------------
# Levels found off the outermost chain
# ---------------------------------------------------------------------------


def test_the_engine_verified_probes_survive_the_widened_walk() -> None:
    """The guard that makes widening safe.

    Finding more levels must not change the ones already checked against a real
    engine. These three strings were run against `qna.exe` 11.0.6.137; they are
    asserted here as a subset, so new levels may appear around them but none of
    them may drift by a character.
    """
    levels = breakdown_probes(WORKED, parse(WORKED))
    emitted = {level.probe.relevance for level in levels}
    emitted |= {level.unfiltered.relevance for level in levels if level.unfiltered is not None}

    verified = {
        # 5.2, the outermost level: 21 rows of `1`.
        (
            "(if exists it whose (exists number of (names of it)) "
            "then number of (names of it) else -1) "
            rf"of {FILTERED} of {FOLDER}"
        ),
        # 5.3, the unfiltered pair: 25.
        (
            "(if exists it whose (exists number of (files of it)) "
            "then number of (files of it) else -1) "
            rf"of {FOLDER}"
        ),
        # The contextless root: 21.
        f"(if exists true whose (exists number of ({WORKED})) then number of ({WORKED}) else -1)",
    }
    assert verified <= emitted


def test_a_context_is_never_a_bare_it() -> None:
    """`... else -1) of it` has nothing to bind `it` to and the engine refuses it.

    This was emitted for any `of` nested on the property side, because a node's
    source text was taken as self-contained when it is only written relative to
    wherever it sits.
    """
    source = '(name of it) of file "x"'
    contexts = [level.probe.context for level in breakdown_probes(source, parse(source))]
    assert contexts == [None, 'file "x"', 'file "x"']


def test_a_context_keeps_its_own_direct_object() -> None:
    """Probing `b` without the `c` it is written against gives
    `The operator "b" is not defined.` -- section 5.1's failure, one level in."""
    source = "(a of b) of c"
    assert [level.probe.context for level in breakdown_probes(source, parse(source))] == [
        None,
        "c",
        "b of c",
    ]


def test_a_level_inside_a_filter_is_measured_against_the_unfiltered_collection() -> None:
    """[unverified] `it` in a filter is an element of the collection *before*
    filtering, so that -- composed with its own context -- is the probe's
    context. Reasoned from the mechanism; not run against an engine."""
    level = breakdown_probes(WORKED, parse(WORKED))[2]
    assert level.probe.measured == "size of it"
    assert level.probe.context == rf"files of {FOLDER}"
    assert level.probe.relevance == (
        "(if exists it whose (exists number of (size of it)) "
        "then number of (size of it) else -1) "
        rf"of files of {FOLDER}"
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            'if exists x then name of file "a" else name of file "b"',
            [None, 'file "a"', 'file "b"'],
            id="both-if-branches",
        ),
        pytest.param(
            '(name of file "a", size of file "b")',
            [None, 'file "a"', 'file "b"'],
            id="tuple-items",
        ),
        pytest.param(
            'name of file "a" = name of file "b"',
            [None, 'file "a"', 'file "b"'],
            id="both-operands-of-a-comparison",
        ),
        pytest.param(
            'not exists name of file "a"',
            [None, 'file "a"'],
            id="through-a-prefix-operator",
        ),
        pytest.param(
            'key (name of file "a") of registry',
            [None, "registry", 'file "a"'],
            id="inside-a-reference-index",
        ),
    ],
)
def test_levels_are_found_throughout_the_expression(
    source: str, expected: list[str | None]
) -> None:
    """[unverified] Not only along the outermost `of` chain. The debugger
    reports "a query per AST node", and its value panel is reached by clicking
    any sub-expression, so a chain inside an operand is a level like any other.
    """
    assert [level.probe.context for level in breakdown_probes(source, parse(source))] == expected


def test_no_site_in_the_example_corpus_gets_an_unusable_context() -> None:
    """The corpus-wide form of the two bugs above.

    A context of `it`, or one that is empty, cannot be evaluated. This held
    silently false before contexts were composed.
    """
    offenders = [
        (path.name, level.probe.measured, level.probe.context)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
        for level in breakdown_probes(site.text, parsed.node)
        if level.probe.context is not None and level.probe.context.strip() in ("", "it")
    ]
    assert offenders == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            'files whose (name of file "a" = "x")',
            [None, 'file "a"'],
            id="absolute-inside-a-filter",
        ),
        pytest.param(
            'key (name of file "a") of registry',
            [None, "registry", 'file "a"'],
            id="absolute-inside-an-index",
        ),
        pytest.param(
            'if exists x then name of file "a" else name of file "b"',
            [None, 'file "a"', 'file "b"'],
            id="absolute-inside-an-if-branch",
        ),
    ],
)
def test_an_absolute_sub_expression_is_not_composed_onto_its_context(
    source: str, expected: list[str | None]
) -> None:
    """`file "a"` means the same thing wherever it sits.

    A filter, an index and an `if` branch are *ambient* positions: the context
    is reachable from them through `it`, but nothing in them is applied to it.
    Composing there would produce `file "a" of files`, which is not what the
    author wrote and not valid relevance.
    """
    assert [level.probe.context for level in breakdown_probes(source, parse(source))] == expected


def test_a_sub_expression_applied_to_an_object_is_composed_onto_it() -> None:
    """Below an `of`'s property the opposite holds: everything there *is*
    applied to the object, so `b` in `(a of b) of c` really is `b of c`."""
    source = "(a of b) of c"
    assert [level.probe.context for level in breakdown_probes(source, parse(source))] == [
        None,
        "c",
        "b of c",
    ]


def test_a_free_it_is_replaced_by_the_context_rather_than_composed_onto_it() -> None:
    """[unverified] When a sub-expression reaches its context through `it`, the
    context is spliced in at that `it` -- composing as well would name it twice.
    """
    source = 'files whose (name of parent folder of it = "x")'
    contexts = [level.probe.context for level in breakdown_probes(source, parse(source))]
    assert contexts == [None, "files", "parent folder of files"]

    source = "(a of b of it) of c"
    contexts = [level.probe.context for level in breakdown_probes(source, parse(source))]
    assert contexts == [None, "c", "c", "b of c"]


def test_only_a_free_it_is_substituted() -> None:
    """An `it` bound inside the sub-expression already means something there."""
    source = 'files whose (exists folders whose (name of it = "x") of it)'
    contexts = [level.probe.context for level in breakdown_probes(source, parse(source))]
    # The inner `it` binds the inner `folders`, so it is left alone; only the
    # outer `of it` is replaced by the collection.
    assert contexts == [None, "files", "folders of files"]


def test_substitution_is_by_span_not_by_text() -> None:
    """Replacing the characters `it` would also hit a string literal, or the
    middle of a longer word."""
    source = 'files whose (name of it = "it")'
    assert [level.probe.context for level in breakdown_probes(source, parse(source))] == [
        None,
        "files",
    ]
    assert 'name of it = "it"' in breakdown_probes(source, parse(source))[0].probe.measured
