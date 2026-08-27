"""Tests for the heuristic complexity scorer.

Metrics are asserted with hand-counted numbers on small statements. The score
itself is only asserted *relatively* -- ordering and monotonicity -- because the
weights are provisional and pinning an absolute number would make retuning them
a test-breaking change.
"""

from __future__ import annotations

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer.complexity import RelevanceComplexity, analyze, score
from bigfix_relevance_analyzer.extract import extract_relevance_from_file

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_empty_text_is_all_zeros() -> None:
    result = analyze("")
    assert result == RelevanceComplexity()
    assert result.score == 0.0


def test_a_simple_property_chain() -> None:
    result = analyze("windows of operating system")
    assert result.token_count == 4
    assert result.of_count == 1
    assert result.max_of_chain == 1
    assert result.unique_identifiers == 3  # windows, operating, system -- not `of`
    assert result.boolean_operators == 0
    assert result.whose_clauses == 0


def test_a_whose_filter() -> None:
    result = analyze('exists files whose (name of it starts with "bes")')
    assert result.token_count == 11
    assert result.max_paren_depth == 1
    assert result.whose_clauses == 1
    assert result.iteration_keywords == 1  # `it`
    assert result.string_literals == 1
    assert result.of_count == 1
    assert result.unique_identifiers == 4  # files, name, starts, with


def test_boolean_operators_are_counted() -> None:
    assert analyze("a and b or not c").boolean_operators == 3


def test_nested_parentheses_report_max_depth() -> None:
    assert analyze("((a) and (b and (c)))").max_paren_depth == 3


def test_unbalanced_parentheses_do_not_go_negative() -> None:
    assert analyze("a) b) c").max_paren_depth == 0


def test_of_chains() -> None:
    assert analyze("a of b of c of d").max_of_chain == 3
    # A parenthesis ends a chain: the `of`s are not one run.
    assert analyze("(a of b) of c").max_of_chain == 1
    assert analyze("(a of b) of c").of_count == 2


def test_semicolon_clauses_count_clauses_not_separators() -> None:
    assert analyze("a").semicolon_clauses == 0
    assert analyze("a; b").semicolon_clauses == 2
    assert analyze("a; b; c").semicolon_clauses == 3


def test_unique_identifiers_are_deduplicated_case_insensitively() -> None:
    assert analyze("name of Name of it").unique_identifiers == 1


# ---------------------------------------------------------------------------
# Only code counts
# ---------------------------------------------------------------------------


def test_keywords_inside_string_literals_do_not_count() -> None:
    result = analyze('x = "and or whose of it"')
    assert result.boolean_operators == 0
    assert result.whose_clauses == 0
    assert result.of_count == 0
    assert result.string_literals == 1


def test_keywords_inside_comments_do_not_count() -> None:
    result = analyze("x /* and whose of */ = y")
    assert result.boolean_operators == 0
    assert result.whose_clauses == 0
    assert result.of_count == 0


def test_whitespace_does_not_change_anything() -> None:
    assert analyze("a of b") == analyze("a   of\n  b")


# ---------------------------------------------------------------------------
# Errors are surfaced, never raised
# ---------------------------------------------------------------------------


def test_unterminated_string_is_scored_not_raised() -> None:
    result = analyze('exists "abc')
    assert result.error_tokens == 1
    assert result.score > 0


# ---------------------------------------------------------------------------
# The score
# ---------------------------------------------------------------------------


def test_score_matches_the_dataclass_property() -> None:
    statement = "exists files whose (name of it as lowercase starts with %22a%22)"
    assert score(statement) == analyze(statement).score


@pytest.mark.parametrize(
    ("simpler", "harder"),
    [
        ("exists file", "exists file whose (size of it > 0)"),
        ("a of b", "a of b of c"),
        ("a", "(a and b) or (c and d)"),
        ('x = "y"', 'x = "y" and z = "w"'),
    ],
)
def test_adding_structure_raises_the_score(simpler: str, harder: str) -> None:
    assert score(simpler) < score(harder)


def test_score_is_never_negative() -> None:
    assert score("") == 0.0
    assert score(")") >= 0.0


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------


def corpus_sites() -> list[tuple[str, str]]:
    return [
        (f"{path.name}:{site.line}", site.text)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
    ]


def test_every_corpus_site_scores() -> None:
    for label, text in corpus_sites():
        result = analyze(text)
        assert result.token_count > 0, label
        assert result.score > 0, label
        assert result.error_tokens == 0, label


def test_the_most_complex_corpus_site_outscores_the_simplest() -> None:
    scores = sorted(score(text) for _label, text in corpus_sites())
    assert scores[0] < scores[-1]
