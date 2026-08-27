"""Tests for the heuristic complexity scorer.

Metrics are asserted with hand-counted numbers on small statements. The score
itself is only asserted *relatively* -- ordering and monotonicity -- because the
weights are provisional and pinning an absolute number would make retuning them
a test-breaking change.
"""

from __future__ import annotations

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.complexity import (
    COST_EXTREME,
    COST_HIGH,
    COST_LOW,
    COST_MODERATE,
    COST_RULES,
    RelevanceComplexity,
    analyze,
    cost_rules_for,
    evaluation_cost_rules,
    score,
)
from bigfix_relevance_analyzer.dialect import Dialect
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


# ---------------------------------------------------------------------------
# Evaluation cost: inspectors known to be heavy on the client eval loop
# ---------------------------------------------------------------------------


def test_ordinary_relevance_costs_nothing() -> None:
    result = analyze("exists file whose (version of it > 1.0)")
    assert result.evaluation_cost == 0.0
    assert result.costly_inspectors == ()


def test_hashing_is_charged_and_named() -> None:
    result = analyze('sha1 of file "/tmp/x" = "abc"')
    assert result.evaluation_cost > 0
    assert "hashing" in result.costly_inspectors


@pytest.mark.parametrize(
    ("statement", "label"),
    [
        ('exists select objects "Name from Win32_Product" of wmi', "wmi query"),
        ('exists descendants of folder "/opt"', "folder recursion"),
        ('exists folders of folders of folder "/opt"', "folder recursion"),
        ("exists image files of processes", "process image files"),
        ('exists scheduled tasks whose (name of it = "x")', "scheduled tasks"),
        ("exists active directory", "active directory"),
        ("exists local users of active directory", "active directory enumeration"),
        ("exists active devices", "active device enumeration"),
        ("exists smbios", "smbios enumeration"),
        ('exists lines of file "/var/log/x"', "file line reading"),
        ("exists packages of rpm", "package database"),
        ("maximum of modification times of files of folder", "modification time"),
        ('exists xpaths "//a" of xml document of file "/tmp/x"', "xpath evaluation"),
    ],
)
def test_each_heavy_inspector_is_recognized(statement: str, label: str) -> None:
    assert label in analyze(statement).costly_inspectors


def test_heavy_inspectors_are_not_all_weighted_equally() -> None:
    """The whole point: hashing a file costs more than reading its lines."""
    hashing = analyze('sha1 of file "/tmp/x"').evaluation_cost
    lines = analyze('lines of file "/tmp/x"').evaluation_cost
    assert hashing > lines > 0


def test_cost_tiers_are_ordered() -> None:
    assert COST_EXTREME > COST_HIGH > COST_MODERATE > COST_LOW > 0


def test_repeated_heavy_inspectors_accumulate() -> None:
    once = analyze('sha1 of file "/a"').evaluation_cost
    twice = analyze('sha1 of file "/a" = sha1 of file "/b"').evaluation_cost
    assert twice > once


def test_heavy_inspectors_inside_string_literals_do_not_count() -> None:
    """Only relevance that evaluates can cost anything to evaluate."""
    result = analyze('name of it = "sha1 of file and descendants of folder"')
    assert result.evaluation_cost == 0.0
    assert result.costly_inspectors == ()


def test_heavy_inspectors_inside_comments_do_not_count() -> None:
    result = analyze("name /* sha1 of file, descendants of folder */ of it")
    assert result.evaluation_cost == 0.0


def test_cost_raises_the_overall_score() -> None:
    cheap = 'exists file "/tmp/x"'
    dear = 'exists file "/tmp/x" whose (sha1 of it = "abc")'
    assert score(dear) > score(cheap)


def test_evaluation_cost_rules_reports_what_matched() -> None:
    matched = evaluation_cost_rules('sha1 of file "/a" of folder "/b"')
    assert [rule.label for rule in matched] == ["hashing"]
    assert matched[0].cost_for(Dialect.CLIENT) == COST_EXTREME
    assert matched[0].why


# ---------------------------------------------------------------------------
# The cost table itself
# ---------------------------------------------------------------------------


def test_every_rule_matches_its_own_example() -> None:
    """A rule whose example no longer matches has silently stopped working."""
    for rule in COST_RULES:
        labels = analyze(rule.example).costly_inspectors
        assert rule.label in labels, (rule.label, rule.example, labels)


def test_rule_labels_are_unique() -> None:
    labels = [rule.label for rule in COST_RULES]
    assert len(labels) == len(set(labels))


def test_every_rule_anchor_is_a_real_inspector() -> None:
    """Anchors ground the table in the QnA dumps instead of in memory."""
    known = inspectors.inspector_names()
    unknown = {anchor for rule in COST_RULES for anchor in rule.anchors if anchor not in known}
    assert unknown == set()


def test_every_rule_has_a_rationale() -> None:
    assert all(rule.why for rule in COST_RULES)


def test_corpus_costs_are_non_negative() -> None:
    for path in corpus_files():
        for site in extract_relevance_from_file(path):
            assert analyze(site.text).evaluation_cost >= 0.0


# ---------------------------------------------------------------------------
# Cost is per-rule dialect-scoped, not one client-or-session partition
# ---------------------------------------------------------------------------


def test_shared_inspectors_are_charged_in_both_dialects() -> None:
    """Hashing a file costs the same whoever evaluates it."""
    for dialect in (Dialect.CLIENT, Dialect.SESSION):
        result = analyze('sha1 of file "/tmp/x"', dialect=dialect)
        assert "hashing" in result.costly_inspectors, dialect


def test_client_only_inspectors_are_not_charged_to_session() -> None:
    statement = 'exists descendants of folder "/opt"'
    assert "folder recursion" in analyze(statement, dialect=Dialect.CLIENT).costly_inspectors
    assert analyze(statement, dialect=Dialect.SESSION).evaluation_cost == 0.0


def test_session_only_inspectors_are_not_charged_to_client() -> None:
    statement = "number of results of bes fixlets"
    assert "result cross product" in analyze(statement, dialect=Dialect.SESSION).costly_inspectors
    assert analyze(statement, dialect=Dialect.CLIENT).evaluation_cost == 0.0


def test_an_unknown_dialect_excludes_nothing() -> None:
    """With no dialect to go on, every rule stays in play."""
    for dialect in (None, Dialect.UNCERTAIN, Dialect.BOTH):
        assert analyze('exists descendants of folder "/x"', dialect=dialect).evaluation_cost > 0
        assert analyze("number of results of bes fixlets", dialect=dialect).evaluation_cost > 0


def test_cost_rules_for_filters_by_dialect() -> None:
    client = {rule.label for rule in cost_rules_for(Dialect.CLIENT)}
    session = {rule.label for rule in cost_rules_for(Dialect.SESSION)}
    assert "wmi query" in client and "wmi query" not in session
    assert "result cross product" in session and "result cross product" not in client
    # The shared ones are in both, which is the whole point.
    assert {"hashing", "active directory"} <= (client & session)


def test_evaluation_cost_rules_honours_dialect() -> None:
    statement = 'exists descendants of folder "/x"'
    assert evaluation_cost_rules(statement, dialect=Dialect.SESSION) == ()
    assert evaluation_cost_rules(statement, dialect=Dialect.CLIENT)


# ---------------------------------------------------------------------------
# The declared dialects must match the dumps, not somebody's recollection
# ---------------------------------------------------------------------------


def test_every_rule_declares_at_least_one_dialect() -> None:
    assert all(rule.dialects for rule in COST_RULES)


# ---------------------------------------------------------------------------
# Active directory: normally cached, but enumeration is a different animal
# ---------------------------------------------------------------------------
#
# The dumps carry `sample time of <active directory group/local computer/local
# user>` -- evidence this is periodically-sampled, cached state, not a live
# domain-controller round trip on every evaluation. A bare reference is cheap.
# Chaining into `local users of`, `groups of`, `logged on users of` an AD
# object walks a collection that can be large on a big domain, which is a
# different cost than the read that produced the object in the first place.


def test_bare_active_directory_reference_is_cheap() -> None:
    result = analyze("exists active directory", dialect=Dialect.CLIENT)
    assert result.costly_inspectors == ("active directory",)
    assert result.evaluation_cost == COST_LOW


def test_active_directory_enumeration_costs_more_than_a_bare_reference() -> None:
    bare = analyze("exists active directory", dialect=Dialect.CLIENT).evaluation_cost
    enumerated = analyze(
        "exists local users of active directory", dialect=Dialect.CLIENT
    ).evaluation_cost
    assert enumerated > bare


@pytest.mark.parametrize(
    "statement",
    [
        "exists local users of active directory",
        "exists local groups of active directory",
        "exists groups of local computer of active directory",
        "exists logged on users of active directory",
    ],
)
def test_each_active_directory_enumeration_shape_is_recognized(statement: str) -> None:
    assert "active directory enumeration" in analyze(statement).costly_inspectors


def test_a_named_lookup_is_not_charged_as_enumeration() -> None:
    """`logged on group <string> of ...` looks up one item by name -- it does
    not walk the collection the way the unindexed forms above do, so it should
    cost no more than the bare reference."""
    result = analyze('exists logged on group "Admins" of active directory')
    assert "active directory enumeration" not in result.costly_inspectors
    assert result.costly_inspectors == ("active directory",)


# ---------------------------------------------------------------------------
# The same inspector can cost different amounts by dialect
# ---------------------------------------------------------------------------
#
# Not every shared rule is symmetric. The dumps show session relevance simply
# has no `sha1 of <file>` -- only `sha1 of <string>` and `sha1 of <x509
# certificate>` -- because session relevance cannot read a file at all, so its
# ceiling for "hashing" is real but far lower than the client's unbounded file
# read. `modification time` inverts the asymmetry: the client signatures are a
# filesystem stat, usually swept across many files, while the session
# signatures are one metadata field on one `bes fixlet` or `bes activation` --
# barely more than a property lookup.


def test_hashing_costs_less_in_session_than_in_client() -> None:
    """Session relevance can only hash a string or a certificate, never a file."""
    client_cost = analyze('sha1 of file "/tmp/x"', dialect=Dialect.CLIENT).evaluation_cost
    session_cost = analyze('sha1 of "some string"', dialect=Dialect.SESSION).evaluation_cost
    assert session_cost > 0
    assert client_cost > session_cost


def test_modification_time_costs_less_in_session_than_in_client() -> None:
    """Client-side is a filesystem stat, usually swept; session is one field."""
    client_cost = analyze("modification time of it", dialect=Dialect.CLIENT).evaluation_cost
    session_cost = analyze("modification time of it", dialect=Dialect.SESSION).evaluation_cost
    assert client_cost > session_cost > 0


def test_cost_for_a_dialect_the_rule_does_not_apply_to_is_zero() -> None:
    rule = next(rule for rule in COST_RULES if rule.label == "wmi query")
    assert rule.cost_for(Dialect.SESSION) == 0.0


def test_cost_for_an_indefinite_dialect_is_the_worst_case() -> None:
    """With no dialect to go on, assume whichever side is more expensive."""
    rule = next(rule for rule in COST_RULES if rule.label == "hashing")
    worst = max(cost for _dialect, cost in rule.costs)
    for dialect in (None, Dialect.UNCERTAIN, Dialect.BOTH):
        assert rule.cost_for(dialect) == worst


def test_every_rule_cost_is_positive() -> None:
    assert all(cost > 0 for rule in COST_RULES for _dialect, cost in rule.costs)


def test_declared_dialects_match_the_inspector_dumps() -> None:
    """A rule applies exactly where the inspectors it names are defined."""
    defined: dict[str, set[Dialect]] = {}
    for inspector in inspectors.properties():
        defined.setdefault(inspector.name, set()).update(inspector.dialects)

    mismatched = {}
    for rule in COST_RULES:
        if not rule.anchors:
            continue
        from_dumps = frozenset().union(*(defined.get(a, set()) for a in rule.anchors))
        if from_dumps != rule.dialects:
            mismatched[rule.label] = (
                sorted(d.value for d in rule.dialects),
                sorted(d.value for d in from_dumps),
            )
    assert mismatched == {}
