"""Tests for the heuristic complexity scorer.

Metrics are asserted with hand-counted numbers on small statements. The score
itself is only asserted *relatively* -- ordering and monotonicity -- because the
weights are provisional and pinning an absolute number would make retuning them
a test-breaking change.
"""

from __future__ import annotations

from itertools import pairwise

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.complexity import (
    COST_EXTREME,
    COST_HIGH,
    COST_LOW,
    COST_MODERATE,
    COST_RULES,
    DEPTH_EXPONENT,
    RelevanceComplexity,
    analyze,
    cost_rules_for,
    depth_cost,
    evaluation_cost_rules,
    score,
)
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.tokenizer import code_tokens

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_empty_text_is_all_zeros() -> None:
    result = analyze("")
    assert result == RelevanceComplexity()
    assert result.score == 0.0


def test_contributions_is_empty_for_zero_score() -> None:
    assert analyze("").contributions == ()


def test_contributions_sums_back_to_score() -> None:
    result = analyze('exists files whose (name of it starts with "bes") of folder "/tmp"')
    assert result.contributions
    assert sum(value for _name, value in result.contributions) == pytest.approx(result.score)


def test_contributions_omits_zero_metrics_and_orders_largest_first() -> None:
    result = analyze("windows of operating system")
    names = [name for name, _value in result.contributions]
    assert "whose_clauses" not in names  # zero for this statement
    assert "boolean_operators" not in names
    values = [value for _name, value in result.contributions]
    assert values == sorted(values, reverse=True)


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


# ---------------------------------------------------------------------------
# Conditionals: depth matters more than count
# ---------------------------------------------------------------------------
#
# A run of unnested `if`s reads linearly and costs a reader little; one `if`
# inside another's branch makes them hold both conditions at once. So there are
# two metrics, the same way `of` has both a count and a longest chain: the flat
# count carries a small weight, the nesting depth a larger one.
#
# Depth is inferred from parenthesis depth at each `if`, because the tokenizer
# does not parse and so cannot see where a branch ends. That makes an `else if`
# chain -- which stays at one depth -- flat, which is the right answer for
# readability even though a parser would nest it.


def test_a_single_conditional_is_counted() -> None:
    result = analyze('if windows of operating system then "a" else "b"')
    assert result.conditional_branches == 1
    assert result.max_conditional_depth == 1


def test_no_conditional_counts_zero() -> None:
    result = analyze("windows of operating system")
    assert result.conditional_branches == 0
    assert result.max_conditional_depth == 0


def test_sequential_conditionals_stay_shallow() -> None:
    result = analyze('(if a then "x" else "y"); (if b then "p" else "q")')
    assert result.conditional_branches == 2
    assert result.max_conditional_depth == 1


def test_an_else_if_chain_is_flat() -> None:
    """A chain reads linearly, so it is not nesting even though it is `if`s."""
    result = analyze('if a then "x" else if b then "p" else "q"')
    assert result.conditional_branches == 2
    assert result.max_conditional_depth == 1


def test_a_nested_conditional_reports_depth_two() -> None:
    result = analyze('if a then (if b then "p" else "q") else "r"')
    assert result.conditional_branches == 2
    assert result.max_conditional_depth == 2


def test_deeper_nesting_reports_deeper_depth() -> None:
    statement = 'if a then (if b then (if c then "x" else "y") else "z") else "w"'
    assert analyze(statement).max_conditional_depth == 3


def test_nested_conditionals_outscore_the_same_number_sequentially() -> None:
    """The point: depth is what costs, not the raw number of branches."""
    sequential = '(if a then "x" else "y"); (if b then "p" else "q")'
    nested = 'if a then (if b then "p" else "q") else "r"'
    flat = analyze(sequential)
    deep = analyze(nested)
    assert flat.conditional_branches == deep.conditional_branches
    assert deep.max_conditional_depth > flat.max_conditional_depth


def test_conditionals_in_string_literals_do_not_count() -> None:
    result = analyze('name of it = "if a then b else c"')
    assert result.conditional_branches == 0
    assert result.max_conditional_depth == 0


def test_conditionals_in_comments_do_not_count() -> None:
    result = analyze("name /* if a then b else c */ of it")
    assert result.conditional_branches == 0


def test_adding_a_conditional_raises_the_score() -> None:
    """Same operands, with and without the branching around them."""
    assert score('if a then "x" else "y"') > score('a "x" "y"')


# ---------------------------------------------------------------------------
# Depth is charged slightly above linearly -- but not for `of`
# ---------------------------------------------------------------------------
#
# Holding nine enclosing conditions in mind is worse than three times holding
# three, so paren and conditional depth are raised to DEPTH_EXPONENT rather
# than multiplied. `of` chains are deliberately left linear: chaining
# properties is how relevance is ordinarily written -- `names of processes of
# it` is idiomatic, not a smell -- so charging depth there would flag routine
# code. The exponent leaves depth 1 untouched (1 ** n == 1) and only diverges
# as nesting grows.


def test_depth_exponent_is_slightly_above_linear() -> None:
    assert 1.0 < DEPTH_EXPONENT < 2.0


def test_depth_cost_at_one_is_just_the_weight() -> None:
    """Nothing changes for unnested code."""
    assert depth_cost(1, 4.0) == 4.0
    assert depth_cost(0, 4.0) == 0.0


def test_depth_cost_grows_faster_than_linearly() -> None:
    single = depth_cost(1, 1.0)
    assert depth_cost(2, 1.0) > 2 * single
    assert depth_cost(9, 1.0) > 3 * depth_cost(3, 1.0)


def test_parenthesis_depth_is_charged_superlinearly() -> None:
    scores = [score("(" * n + "a" + ")" * n) for n in (1, 2, 3, 4)]
    deltas = [b - a for a, b in pairwise(scores)]
    assert deltas == sorted(deltas)
    assert deltas[-1] > deltas[0]


def test_conditional_depth_is_charged_superlinearly() -> None:
    def nested(n: int) -> str:
        text = '"leaf"'
        for i in range(n):
            text = f'if c{i} then ({text}) else "e{i}"'
        return text

    scores = [score(nested(n)) for n in (1, 2, 3, 4)]
    deltas = [b - a for a, b in pairwise(scores)]
    assert deltas == sorted(deltas)


def test_of_chains_stay_linear() -> None:
    """Chaining properties is ordinary relevance, not a complexity smell."""
    scores = [score(" of ".join(f"p{i}" for i in range(n))) for n in (2, 3, 4, 5)]
    deltas = [b - a for a, b in pairwise(scores)]
    assert deltas[0] == pytest.approx(deltas[-1])


def test_nine_nested_is_more_than_three_times_three_nested() -> None:
    def nested(n: int) -> str:
        text = '"leaf"'
        for i in range(n):
            text = f'if c{i} then ({text}) else "e{i}"'
        return text

    assert score(nested(9)) > 3 * score(nested(3))


# ---------------------------------------------------------------------------
# Conditional nesting is read from keywords, not from parentheses
# ---------------------------------------------------------------------------
#
# Relevance does not require parentheses around a conditional's branches, but
# they make a deep one easier to follow -- so writing them must not cost
# anything. Nesting is therefore detected from `then`/`else`, and a `(` that
# exists only to wrap a nested `if` is scaffolding: it contributes neither
# parenthesis depth nor tokens, because the nesting it marks is already charged
# once as conditional depth.
#
# Residual, pinned below rather than fixed: parentheses around a *condition*
# (`if (a and b) then ...`) are still charged. Whether they are redundant
# depends on the token after the `)`, which a single pass cannot know when it
# commits the depth at the `(`.


def nested_conditional(n: int, *, parens: bool) -> str:
    """`n` conditionals nested in each other's `then` branch, with or without parens.

    Only a branch that is itself a conditional gets parenthesized -- wrapping the
    innermost leaf too would compare against a paren that is plain grouping, not
    conditional scaffolding, and is charged for on purpose.
    """
    text = '"leaf"'
    for i in range(n):
        branch = f"({text})" if parens and i else text
        text = f'if c{i} then {branch} else "e{i}"'
    return text


def test_unparenthesized_nesting_is_seen() -> None:
    """The bug: without parens to infer from, nesting used to report depth 1."""
    assert analyze(nested_conditional(2, parens=False)).max_conditional_depth == 2


def test_deep_unparenthesized_nesting_is_seen() -> None:
    assert analyze(nested_conditional(3, parens=False)).max_conditional_depth == 3


@pytest.mark.parametrize("depth", [2, 3])
def test_parentheses_around_a_nested_conditional_do_not_change_the_score(depth: int) -> None:
    """The regression test: the clearer form must not cost more than the terser one."""
    assert score(nested_conditional(depth, parens=True)) == pytest.approx(
        score(nested_conditional(depth, parens=False))
    )


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_parentheses_never_raise_the_score_of_a_nesting(n: int) -> None:
    assert score(nested_conditional(n, parens=True)) <= score(nested_conditional(n, parens=False))


def test_conditional_scaffolding_adds_no_parenthesis_depth() -> None:
    result = analyze('if a then (if b then "p" else "q") else "r"')
    assert result.max_conditional_depth == 2
    assert result.max_paren_depth == 0
    assert result.conditional_parens == 1


def test_token_count_excludes_conditional_scaffolding() -> None:
    """The exclusion stays auditable: the raw lexical count is recoverable."""
    text = 'if a then (if b then "p" else "q") else "r"'
    result = analyze(text)
    assert result.conditional_parens == 1
    assert result.token_count + 2 * result.conditional_parens == len(list(code_tokens(text)))


# -- chains stay flat -------------------------------------------------------


def test_a_parenthesized_else_if_chain_is_still_flat() -> None:
    result = analyze('if a then "x" else (if b then "p" else "q")')
    assert result.max_conditional_depth == 1


@pytest.mark.parametrize(
    "statement",
    [
        'if a then (if b then "p" else "q") else if c then "r" else "s"',
        'if a then if b then "p" else "q" else if c then "r" else "s"',
    ],
)
def test_a_chain_after_a_nesting_returns_to_sibling_depth(statement: str) -> None:
    """Without a closing rule the chain link would report depth 3, not 2."""
    result = analyze(statement)
    assert result.conditional_branches == 3
    assert result.max_conditional_depth == 2


# -- parentheses that are not scaffolding still count -----------------------


def test_parens_that_group_a_branch_expression_still_count() -> None:
    """Real grouping is not scaffolding, even inside a branch."""
    assert analyze("if a then (b and (c or d)) else e").max_paren_depth == 2


def test_parens_around_a_condition_still_count() -> None:
    """Pins the documented residual, so removing it later is a deliberate act."""
    assert analyze('if (a and b) then "x" else "y"').max_paren_depth == 1


def test_a_whose_paren_is_not_conditional_scaffolding() -> None:
    assert analyze('exists files whose (if a then "x" else "y")').max_paren_depth == 1


def test_a_conditional_buried_in_a_branch_still_nests() -> None:
    result = analyze('if a then ("x" & (if b then "p" else "q")) else "z"')
    assert result.max_conditional_depth == 2
    assert result.max_paren_depth == 2


def test_a_conditional_in_a_condition_nests() -> None:
    result = analyze('if (if a then b else c) then "x" else "y"')
    assert result.max_conditional_depth == 2


def test_unbalanced_conditional_parens_are_scored_not_raised() -> None:
    result = analyze('if a then (if b then "x"')
    assert result.max_conditional_depth == 2
    assert result.score > 0


# -- pinned scores, so recalibration is always a deliberate act -------------


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        ("((a) and (b and (c)))", 35.5885),
        # 27.5 before WEIGHT_WHOSE_CLAUSE dropped 5.0 -> 1.5, so that filtering
        # a cross product stops costing more than leaving it unfiltered.
        ('exists files whose (name of it starts with "bes")', 24.0),
        ("(a and b) or (c and d)", 24.0),
        ("a) b) c", 8.0),
    ],
)
def test_pinned_scores(statement: str, expected: float) -> None:
    assert score(statement) == pytest.approx(expected, abs=1e-3)


# ---------------------------------------------------------------------------
# Tuples: cross products are charged, filters are not punished
# ---------------------------------------------------------------------------
#
# A relevance tuple expands to a cross product: (10 items, 10 items, 10 items)
# is 1000 tuples. `whose` filters cut that down -- an outer whose tames the
# whole product, a member-level whose tames one factor -- so the scorer must
# never reward deleting them. Unfiltered tuple commas are charged (linearly in
# total, superlinearly on the worst single tuple); a filtered, projected
# (`(...) of x`), or all-literal tuple charges nothing.
#
# Accepted heuristic limits, pinned below rather than fixed: `whose (true)`
# waives (junk filters are not detectable without a parser); a cast between
# the tuple and its whose defeats the waiver (chasing casts needs unbounded
# lookahead); a member-only filter with a large body can still cost slightly
# more than deleting it, because it tames only one factor of the product.


def test_an_unfiltered_tuple_is_charged() -> None:
    result = analyze("(items a, items b, items c)")
    assert result.tuple_commas == 2
    assert result.unfiltered_tuple_commas == 2
    assert result.max_unfiltered_tuple_commas == 2


def test_an_outer_whose_waives_the_whole_tuple() -> None:
    result = analyze('(items a, items b, items c) whose (item 0 of it = "x")')
    assert result.tuple_commas == 2
    assert result.unfiltered_tuple_commas == 0


def test_a_member_filter_waives_one_comma() -> None:
    result = analyze("((items a) whose (it > 1), items b, items c)")
    assert result.tuple_commas == 2
    assert result.unfiltered_tuple_commas == 1


def test_member_and_outer_filters_together_waive_everything() -> None:
    """The motivating example: filters in both places, nothing charged."""
    statement = '((items a) whose (it > 1), items b, items c) whose (item 0 of it = "x")'
    assert analyze(statement).unfiltered_tuple_commas == 0


def test_a_projection_tuple_is_not_charged() -> None:
    """`(a, b) of x` expands linearly with x, not multiplicatively."""
    result = analyze("(id of it, name of it) of x")
    assert result.tuple_commas == 1
    assert result.unfiltered_tuple_commas == 0


def test_all_literal_tuples_are_not_charged() -> None:
    """Argument tuples of plain literals expand nothing."""
    assert analyze('substrings separated by ("a", "b") of x').unfiltered_tuple_commas == 0
    result = analyze("(1, 2, 3)")
    assert result.tuple_commas == 2
    assert result.unfiltered_tuple_commas == 0


def test_a_mixed_literal_tuple_is_still_a_tuple() -> None:
    assert analyze('("a", items b)').unfiltered_tuple_commas == 1


def test_a_wrapped_tuple_is_still_waived_by_whose() -> None:
    assert analyze("((items a, items b)) whose (it > 1)").unfiltered_tuple_commas == 0


def test_a_bare_toplevel_tuple_is_charged() -> None:
    """An outer whose is impossible without parens, so bare commas charge."""
    result = analyze("items a, items b, items c")
    assert result.tuple_commas == 2
    assert result.unfiltered_tuple_commas == 2


def test_an_unbalanced_tuple_charges_at_end_of_input() -> None:
    assert analyze("(items a, items b").unfiltered_tuple_commas == 1


def test_commas_in_strings_and_comments_are_not_tuples() -> None:
    assert analyze('"a, b, c"').tuple_commas == 0
    assert analyze("x /* a, b */").tuple_commas == 0


def test_a_trivial_whose_still_waives() -> None:
    """Accepted gaming: junk filters need a parser to detect."""
    assert analyze("(items a, items b) whose (true)").unfiltered_tuple_commas == 0


def test_a_cast_between_tuple_and_whose_defeats_the_waiver() -> None:
    """Pinned limit: only an *immediate* whose or `of` waives."""
    statement = '(items a, items b) as string whose (it = "x")'
    assert analyze(statement).unfiltered_tuple_commas == 1


# -- the incentive must point the right way ----------------------------------


def filterable_tuple(members: int) -> str:
    return "(" + ", ".join(f"items i{k}" for k in range(members)) + ")"


@pytest.mark.parametrize("members", [2, 3, 4, 5])
def test_filtering_a_tuple_never_raises_the_score(members: int) -> None:
    """True at every width, narrowest included -- the whole point of the weight."""
    unfiltered = filterable_tuple(members)
    filtered = f'{unfiltered} whose (item 0 of it = "x")'
    assert score(filtered) < score(unfiltered)


def test_a_filter_body_can_still_outweigh_what_it_waives() -> None:
    """The honest limit: the waiver is finite, so a sprawling filter body still
    costs more than it saves. That is reading cost the score is meant to show,
    not the perverse incentive the fan-out charge exists to prevent."""
    unfiltered = filterable_tuple(2)
    sprawling = " and ".join(f'name of item 0 of it != "v{k}"' for k in range(6))
    assert score(f"{unfiltered} whose ({sprawling})") > score(unfiltered)


def test_wider_unfiltered_tuples_cost_increasingly_more() -> None:
    scores = [score(filterable_tuple(n)) for n in (2, 3, 4, 5)]
    deltas = [b - a for a, b in pairwise(scores)]
    assert deltas == sorted(deltas)
    assert deltas[-1] > deltas[0]


# -- member filters and an outer filter stack --------------------------------
#
# An outer `whose` runs *after* the cross product is built, so it bounds what
# flows onward but not the expansion the engine paid for. A member `whose`
# narrows a factor *before* the product, so it makes the expansion itself
# smaller. They are therefore credited against different terms and stack:
# together they beat either alone.


def test_member_and_outer_filters_stack_on_fanout() -> None:
    three = "(items a, items b, items c)"
    member = "((items a) whose (it > 1), items b, items c)"
    assert analyze(three).max_unfiltered_tuple_commas == 2
    assert analyze(f'{three} whose (it = "x")').max_unfiltered_tuple_commas == 1
    assert analyze(member).max_unfiltered_tuple_commas == 1
    assert analyze(f'{member} whose (it = "x")').max_unfiltered_tuple_commas == 0


def test_filtering_a_member_pays_off_even_under_an_outer_filter() -> None:
    """The gap this closes: a member filter used to add cost and waive nothing."""
    outer_only = '(items a, items b, items c) whose (item 0 of it = "x")'
    both = '((items a) whose (it > 1), items b, items c) whose (item 0 of it = "x")'
    assert score(both) < score(outer_only)


def test_an_outer_filter_still_beats_no_filter() -> None:
    three = "(items a, items b, items c)"
    assert score(f'{three} whose (item 0 of it = "x")') < score(three)
