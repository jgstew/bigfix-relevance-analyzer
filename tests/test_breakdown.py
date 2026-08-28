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

from bigfix_relevance_analyzer.breakdown import (
    Outcome,
    ProbeKind,
    breakdown_probes,
    interpret_count_results,
)
from bigfix_relevance_analyzer.parser import parse

# The worked example from findings section 5.2. Ground truth from the engine:
# 25 files in the folder, 21 of them over 1000 bytes, 21 names.
WORKED = r'names of files whose (size of it > 1000) of folder "C:\Windows"'
FOLDER = r'folder "C:\Windows"'
FILTERED = r"files whose (size of it > 1000)"


def test_the_worked_examples_levels_are_reported_innermost_first() -> None:
    levels = breakdown_probes(WORKED, parse(WORKED))
    assert [(level.probe.measured, level.probe.context) for level in levels] == [
        (WORKED, None),
        (f"{FILTERED} of it", FOLDER),
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
    assert [level.unfiltered is None for level in levels] == [True, False, True]


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
