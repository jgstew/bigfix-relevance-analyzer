"""The type model, the narrowing, and the checker slice.

Everything here derives from the inspector dumps -- a snapshot of one build --
and nothing in this suite runs a relevance engine. That is exactly why the
checker is built to stay quiet: a name it cannot find yields `None`, and `None`
never becomes an error. Findings drawn from the issue #8 investigation are
tagged where they have not been confirmed against a real evaluator.
"""

from __future__ import annotations

import pathlib
import re

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer import inspectors, typecheck
from bigfix_relevance_analyzer.binding import resolve_it_bindings
from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS, Origin
from bigfix_relevance_analyzer.dialect import Dialect, is_definite
from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.nodes import If, Node
from bigfix_relevance_analyzer.parser import parse, try_parse
from bigfix_relevance_analyzer.typecheck import (
    Plurality,
    TypeEnvironment,
    check,
    resolve_property,
)

ALL_PLATFORMS = {"debian", "macos", "rhel", "ubuntu", "windows"}

# Two casts from a string literal that exist on disjoint platforms. They are the
# only way to reach a narrowed platform set without property resolution, which
# is what makes the union rule testable end to end inside this slice.
WINDOWS_ONLY = '"x" as windows display time'
LINUX_ONLY = '"x" as strverscmp version'


@pytest.fixture
def env() -> TypeEnvironment:
    return TypeEnvironment.create(Dialect.CLIENT)


def types_of(source: str, env: TypeEnvironment) -> set[str] | None:
    value = check(parse(source), env).value
    return None if value.types is None else set(value.types)


# ---------------------------------------------------------------------------
# Narrowing
# ---------------------------------------------------------------------------


def test_a_name_resolves_to_every_type_it_could_have(env: TypeEnvironment) -> None:
    """`drives` is three different things depending on the platform, and with no
    platform selected all three stay in play."""
    value = resolve_property("drives", None, env)
    assert value.types is not None
    assert set(value.types) == {"drive", "filesystem", "volume"}
    assert set(value.platforms) == ALL_PLATFORMS
    assert value.plurality is Plurality.PLURAL


@pytest.mark.parametrize(
    ("name", "expected_types", "expected_platforms"),
    [
        pytest.param(
            "block size", {"integer"}, {"debian", "rhel", "ubuntu"}, id="narrows-to-linux"
        ),
        pytest.param("allocation block count", {"integer"}, {"macos"}, id="narrows-to-macos"),
        pytest.param("free space", {"integer"}, ALL_PLATFORMS, id="narrows-nothing"),
    ],
)
def test_a_downstream_property_narrows_the_set(
    name: str, expected_types: set[str], expected_platforms: set[str], env: TypeEnvironment
) -> None:
    """The point of carrying a set: the next inspector says which reading held.

    Platform coverage falls out as a side effect -- `block size of drives of it`
    can only be Linux, and nobody had to say so.
    """
    drives = resolve_property("drives", None, env)
    value = resolve_property(name, drives.types, env)
    assert value.types is not None
    assert set(value.types) == expected_types
    assert set(value.platforms) == expected_platforms


def test_a_name_no_candidate_type_defines_resolves_to_empty(env: TypeEnvironment) -> None:
    """A real finding: not "unknown property" but "no possible type defines it"."""
    assert resolve_property("block size", frozenset({"drive"}), env).types == frozenset()


def test_a_name_absent_from_the_snapshot_resolves_to_none(env: TypeEnvironment) -> None:
    """Absence proves nothing -- new BigFix versions add inspectors, and the
    dumps only cover what someone captured. This must never become an error."""
    assert resolve_property("nonexistent inspector", frozenset({"file"}), env).types is None


def test_resolution_walks_the_ancestor_chain(env: TypeEnvironment) -> None:
    """`size` is declared on `file`, so resolving it for `application` finds
    nothing without the walk. This is required, not an optimisation."""
    assert inspectors.ancestors("client") == ("client", "application", "file", "filesystem object")
    assert resolve_property("size", frozenset({"application"}), env).types == frozenset({"integer"})


def test_plurality_comes_from_which_written_form_was_used(env: TypeEnvironment) -> None:
    """`name` and `names` are the same rows, read singular and plural."""
    assert resolve_property("name", frozenset({"file"}), env).plurality is Plurality.SINGULAR
    assert resolve_property("names", frozenset({"folder"}), env).plurality is Plurality.PLURAL


def test_selecting_a_platform_restricts_resolution() -> None:
    windows = TypeEnvironment.create(Dialect.CLIENT, "windows")
    macos = TypeEnvironment.create(Dialect.CLIENT, "macos")
    assert resolve_property("drives", None, windows).types == frozenset({"drive"})
    assert resolve_property("drives", None, macos).types == frozenset({"volume"})


# ---------------------------------------------------------------------------
# Platform coverage is reported, never enforced
# ---------------------------------------------------------------------------


def test_if_branches_union_their_platforms_rather_than_intersecting(env: TypeEnvironment) -> None:
    """The rule that keeps real content from being called broken.

    A statement guards platform-specific relevance behind a condition the wrong
    platform never satisfies, so its branches are alternatives. These two have
    *disjoint* platform support -- intersecting would give the empty set and
    call a perfectly good statement impossible.
    """
    windows = check(parse(WINDOWS_ONLY), env)
    linux = check(parse(LINUX_ONLY), env)
    assert set(windows.platforms) == {"windows"}
    assert set(linux.platforms) == {"debian", "rhel", "ubuntu"}
    assert not (windows.platforms & linux.platforms)

    both = check(parse(f"if true then ({WINDOWS_ONLY}) else ({LINUX_ONLY})"), env)
    assert set(both.platforms) == {"windows", "debian", "rhel", "ubuntu"}
    assert both.diagnostics == ()


def test_error_fallback_unions_its_platforms_too(env: TypeEnvironment) -> None:
    """[unverified] `|` is an alternative by definition -- the right side runs
    only when the left one errors. No example in the corpus uses it to guard
    platforms, so this rule is reasoned from the semantics, not observed."""
    result = check(parse(f"({WINDOWS_ONLY}) | ({LINUX_ONLY})"), env)
    assert set(result.platforms) == {"windows", "debian", "rhel", "ubuntu"}


def test_a_chain_intersects_its_platforms(env: TypeEnvironment) -> None:
    """Within one reading, everything has to hold at once."""
    drives = resolve_property("drives", None, env)
    assert resolve_property("block size", drives.types, env).platforms < drives.platforms


def _corpus_diagnostics(env: TypeEnvironment) -> list[tuple[str, int, str, str]]:
    return [
        (path.name, site.line, diagnostic.code, diagnostic.message)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
        for diagnostic in check(parsed.node, env).diagnostics
    ]


def test_no_example_site_is_reported_broken(env: TypeEnvironment) -> None:
    """The false-positive guard, over every real statement in the corpus.

    The corpus contains 12 `if` statements whose branches differ in platform
    support; an intersecting model would flag them. Nothing here may claim
    shipped content is broken.

    `singular-over-plural-object` is exempt because it does not make that
    claim: it reports a risk the author may have ruled out, and shipped
    content takes it on deliberately -- see the test below.
    """
    offenders = [
        entry for entry in _corpus_diagnostics(env) if entry[2] != "singular-over-plural-object"
    ]
    assert offenders == []


def test_the_corpus_takes_the_non_unique_risk_deliberately(env: TypeEnvironment) -> None:
    """What survives all three exemptions, over every statement in the corpus.

    Shipped content collapses plurals constantly, and almost always says so:
    `free space of drives of system folders | 0` hedges with a fallback, the
    dashboards wrap a whole chain in `... | "<link ... />"`, `unique value of`
    and `set of` are the idioms for asserting a collection is one, and the rest
    feed an operator that required a singular anyway. Twenty-four of the
    twenty-six sites this rule once reported are one of those.

    These two are not. Both are a bare `pathname of <plural>` with nothing
    guarding it, which is exactly what the rule is for -- so this pins the
    rule's reach as a decision, and would catch a future exemption that
    over-reached and silenced it entirely.
    """
    risks = {(name, line) for name, line, code, _ in _corpus_diagnostics(env)}
    assert risks == {
        ("task_time_based_relevance.bes", 28),
        ("fixlet_description_relevance_via_javascript.bes", 114),
    }


def test_operand_incompatibility_holds_across_the_corpus_under_each_sites_own_dialect() -> None:
    """The ancestor fix, checked over real content rather than isolated cases.

    `test_no_example_site_is_reported_broken` checks every corpus site under a
    single hardcoded `Dialect.CLIENT`, which is exactly why the bug this
    guards against went unnoticed there: a session-only property resolves to
    `None` under the wrong dialect, so `operand-types-incompatible`/
    `if-branch-types-incompatible` never even ran on the session-only sites
    that actually trigger it. Checking each site under its own resolved
    dialect instead -- confirmed live in
    `dashboard_session_relevance_html_table.ojo` and
    `webreport_relevance_via_javascript.besrpt`, both session-only, both
    turning a `unique value`/`unique values` result (`... with multiplicity`)
    against a bare string literal with `|` -- is what actually exercises it.

    Scoped to these two codes rather than every diagnostic, so an unrelated,
    legitimate finding elsewhere in the corpus (there is at least one: a `&`
    singularity error) does not make this test brittle against content this
    fix has nothing to do with.
    """
    watched = {"operand-types-incompatible", "if-branch-types-incompatible"}
    offenders = [
        (path.name, site.line, diagnostic.code, diagnostic.message)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
        for diagnostic in check(
            parsed.node,
            TypeEnvironment.create(site.dialect if is_definite(site.dialect) else Dialect.CLIENT),
        ).diagnostics
        if diagnostic.code in watched
    ]
    assert offenders == []


def test_the_corpus_really_does_contain_platform_divergent_branches() -> None:
    """Guards the test above from passing vacuously if the corpus changes."""

    def branches(node: Node) -> int:
        found = 0
        stack: list[object] = [node]
        while stack:
            current = stack.pop()
            if isinstance(current, If):
                found += 1
            for name in getattr(current, "__slots__", ()):
                if name == "span":
                    continue
                child: object = getattr(current, name, None)
                if isinstance(child, tuple):
                    stack.extend(item for item in child if hasattr(item, "span"))
                elif child is not None and hasattr(child, "span"):
                    stack.append(child)
        return found

    total = sum(
        branches(parsed.node)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
    )
    assert total >= 12


# ---------------------------------------------------------------------------
# The checker slice
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("42", {"integer"}),
        ("99999999999999999999999", {"large integer"}),
        ("1.5", {"floating point"}),
        ('"a"', {"string"}),
        ("1 + 2", {"integer"}),
        ('"a" & "b"', {"string"}),
        ("1 < 2", {"boolean"}),
        ("1 > 2", {"boolean"}),
        ('"abc" contains "b"', {"boolean"}),
        ('exists file "x"', {"boolean"}),
        ("number of (1, 2)", {"integer"}),
        ("not true", {"boolean"}),
        ("-1", {"integer"}),
        ("item 0 of (1, 2, 3)", {"integer"}),
        ("if true then 1 else 2", {"integer"}),
    ],
)
def test_typing(source: str, expected: set[str], env: TypeEnvironment) -> None:
    assert types_of(source, env) == expected


def test_a_swapped_operator_resolves_through_its_defined_form(env: TypeEnvironment) -> None:
    """The engine defines no `>`: `a > b` is `b < a`, and looking `>` up
    directly finds nothing."""
    assert not [e for e in inspectors.binary_operators() if e.name == ">"]
    assert types_of("1 > 2", env) == {"boolean"}


@pytest.mark.parametrize(
    ("source", "code"),
    [
        pytest.param('1 + "a"', "binary-operator-not-defined", id="no-such-overload"),
        pytest.param("if 1 then 2 else 3", "if-condition-not-singular-boolean", id="if-condition"),
        pytest.param("item 5 of (1, 2, 3)", "tuple-index-out-of-range", id="tuple-bounds"),
        pytest.param('"a" | 42', "operand-types-incompatible", id="bar-still-type-checked"),
        pytest.param("1 as bogus cast", "cast-not-defined", id="no-such-cast"),
    ],
)
def test_findings(source: str, code: str, env: TypeEnvironment) -> None:
    result = check(parse(source), env)
    assert [d.code for d in result.diagnostics] == [code]
    assert result.diagnostics[0].span.start >= 0


def test_findings_use_the_engines_own_wording(env: TypeEnvironment) -> None:
    assert check(parse('1 + "a"'), env).diagnostics[0].message == (
        "the operator '+' is not defined for the types '<integer> + <string>'"
    )


def test_bar_message_leads_with_the_evaluators_own_wording(env: TypeEnvironment) -> None:
    """`|` has no operator-table row, so unlike `+` there is no recovered
    type-checker string to quote -- only the runtime's terse "Incompatible
    types." The message leads with that confirmed string verbatim, then adds
    the types the runtime message alone doesn't provide."""
    assert check(parse('"a" | 42'), env).diagnostics[0].message == (
        "Incompatible types: the types in '<string> | <integer>' are not compatible"
    )


def test_a_too_large_tuple_index_leads_with_the_evaluators_own_wording(
    env: TypeEnvironment,
) -> None:
    """`item <large integer> of (...)` errors identically to a non-literal
    index on a real evaluator (confirmed live against qna 11.0.6.137) even
    though the token *is* an integer literal, just too big to index with. The
    message leads with that confirmed sentence, then adds the accurate detail
    the runtime string omits."""
    result = check(parse("item 99999999999999999999999 of (1, 2, 3)"), env)
    assert [d.code for d in result.diagnostics] == ["tuple-index-unreasonable"]
    assert result.diagnostics[0].message == (
        "This expression contained a tuple index which was not an integer "
        "literal: the tuple index '99999999999999999999999' is too big "
        "(it's quite unreasonably large)"
    )


def test_a_numeral_beyond_the_engines_parse_ceiling_is_its_own_finding(
    env: TypeEnvironment,
) -> None:
    """Past `MAX_LARGE_INTEGER` the engine cannot parse the numeral into any
    type at all, in any context -- confirmed live: a bare literal this size
    and a tuple index of the same size fail identically, with the same
    message, distinct from both `tuple-index-unreasonable` and
    `tuple-index-not-literal`."""
    too_large = "999999999999999999999999999999999999999999999999999999"

    bare = check(parse(too_large), env)
    assert [d.code for d in bare.diagnostics] == ["integer-constant-too-large"]

    as_index = check(parse(f"item {too_large} of (1, 2, 3)"), env)
    assert [d.code for d in as_index.diagnostics] == ["integer-constant-too-large"]
    assert as_index.diagnostics[0].message == bare.diagnostics[0].message


def test_a_too_large_constant_still_types_as_integer_for_a_sibling_finding(
    env: TypeEnvironment,
) -> None:
    """A too-large numeral is ruled out for its *own* purposes -- nothing can
    be done with a value the engine refuses to parse -- but it is not the same
    kind of ruled-out as `1 + "a"`'s `<none>`: the token is still, visibly, an
    integer literal. Typing it `integer` rather than wiping it to `frozenset()`
    lets an independent problem next to it still get its own finding, instead
    of being silently swallowed by `_ruled_out`'s cascade guard -- confirmed
    live, `|` does not rescue either finding here (contrast a genuine runtime
    failure like `1/0`, which `|` really does catch and fall back from)."""
    too_large = "999999999999999999999999999999999999999999999999999999"
    result = check(parse(f'{too_large} | "string"'), env)
    assert [d.code for d in result.diagnostics] == [
        "integer-constant-too-large",
        "operand-types-incompatible",
    ]
    assert result.diagnostics[1].message == (
        "Incompatible types: the types in '<integer> | <string>' are not compatible"
    )


def test_a_tuple_index_is_zero_based(env: TypeEnvironment) -> None:
    assert types_of("item 0 of (1, 2, 3)", env) == {"integer"}
    assert types_of('item 2 of (1, 2, "c")', env) == {"string"}
    assert (
        check(parse("item 3 of (1, 2, 3)"), env).diagnostics[0].code == "tuple-index-out-of-range"
    )


def test_one_bad_if_branch_is_tolerated_but_two_are_not(env: TypeEnvironment) -> None:
    """The engine's own rule: `at most one branch of an if-statement may have
    type errors`. It is deliberate tolerance, and it is what lets a statement
    carry a branch that only makes sense on another platform."""
    one = check(parse('if true then (1 + "a") else 2'), env)
    assert one.diagnostics == ()

    two = check(parse('if true then (1 + "a") else ("b" + 1)'), env)
    assert "both-if-branches-have-type-errors" in {d.code for d in two.diagnostics}


@pytest.mark.parametrize("source", ['bogusproperty of file "x"', '"a" & bogus thing'])
def test_a_name_absent_from_the_snapshot_stays_silent(source: str, env: TypeEnvironment) -> None:
    """`None` propagates without ever becoming a finding.

    The tables are a snapshot: a name they do not contain may simply postdate
    them. Only a name they *do* contain, used on a direct object none of its
    rows accept, is positive evidence of a mistake.
    """
    result = check(parse(source), env)
    assert result.value.types is None
    assert result.diagnostics == ()


# ---------------------------------------------------------------------------
# Property resolution: `of`, `whose` and `it`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("processors", {"processor"}),
        ('file "c:\\x.txt"', {"file"}),
        ('name of file "c:\\x.txt"', {"string"}),
        ('size of file "c:\\x.txt"', {"integer"}),
        ('files of folder "c:\\"', {"file"}),
        # `of` binds `it`, which is what makes the inner `name` resolve.
        ('name of it of file "c:\\x.txt"', {"string"}),
        ('exists file "c:\\x.txt"', {"boolean"}),
        # A `whose` keeps its collection's type and drops its filter.
        ('files whose (size of it > 1) of folder "c:\\"', {"file"}),
    ],
)
def test_a_property_types_through_its_direct_object(
    source: str, expected: set[str], env: TypeEnvironment
) -> None:
    result = check(parse(source), env)
    assert result.diagnostics == ()
    assert types_of(source, env) == expected


def test_a_chain_narrows_its_platforms_as_it_resolves(env: TypeEnvironment) -> None:
    """The narrowing `resolve_property` documents, reached through real syntax."""
    assert set(check(parse("block size of drives"), env).platforms) == {
        "debian",
        "rhel",
        "ubuntu",
    }
    assert set(check(parse("allocation block count of drives"), env).platforms) == {"macos"}


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('name of file "x"', Plurality.SINGULAR),
        ('names of files of folder "c:\\"', Plurality.PLURAL),
        # The written form of the property settles the phrase, whatever the
        # object's own plurality. `name of files of folders "/"` answers with
        # one name and `E: Singular expression refers to non-unique object.`
        # -- a *runtime* complaint about the object, not a static plurality.
        ('name of files of folder "c:\\"', Plurality.SINGULAR),
        ('name of files "x" of folder "c:\\"', Plurality.SINGULAR),
        ('files whose (size of it > 1) of folder "c:\\"', Plurality.PLURAL),
        # A cast as the property has no written form of its own, so the object
        # still decides: `it` is singular here and the phrase is not.
        ('(it as string) of files of folder "c:\\"', Plurality.PLURAL),
    ],
)
def test_plurality_propagates_along_a_chain(
    source: str, expected: Plurality, env: TypeEnvironment
) -> None:
    assert check(parse(source), env).value.plurality is expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        # The reported bug: `results` is plural, `value of results` is not.
        (
            'value of results from (bes property "X") of bes computers',
            Plurality.SINGULAR,
        ),
        (
            'values of results from (bes property "X") of bes computers',
            Plurality.PLURAL,
        ),
    ],
)
def test_the_written_form_settles_plurality_in_session_relevance(
    source: str, expected: Plurality
) -> None:
    env = TypeEnvironment.create(Dialect.SESSION)
    assert check(parse(source), env).value.plurality is expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        # `unique value of ("a";"b")` answers `a` and then errors on the
        # non-unique object; `unique values of` the same collection answers
        # both. The singular form is singular either way.
        ('unique value of ("a";"b")', Plurality.SINGULAR),
        ('unique value of ("a";"a")', Plurality.SINGULAR),
        ('unique values of ("a";"b")', Plurality.PLURAL),
    ],
)
def test_an_aggregate_written_singular_is_singular(
    source: str, expected: Plurality, env: TypeEnvironment
) -> None:
    """Held by the same rule that `_collapses` used to special-case."""
    assert check(parse(source), env).value.plurality is expected


def test_a_singular_form_over_a_plural_object_is_not_an_operand_error() -> None:
    """The engine's static `A singular expression is required.` does not apply:
    `value of results` is a singular expression."""
    env = TypeEnvironment.create(Dialect.SESSION)
    source = '"a" & (value of results from (bes property "X") of bes computers)'
    codes = {d.code for d in check(parse(source), env).diagnostics}
    assert "right-operand-not-singular" not in codes


def test_a_singular_form_over_a_plural_object_is_reported_as_a_risk() -> None:
    """What the runtime *does* complain about, kept separate from the static
    rule: the object may yield more than one value."""
    env = TypeEnvironment.create(Dialect.SESSION)
    source = 'value of results from (bes property "X") of bes computers'
    found = [
        d for d in check(parse(source), env).diagnostics if d.code == "singular-over-plural-object"
    ]
    assert len(found) == 1
    # The engine's own `Singular expression refers to non-unique object.` is
    # deliberately *not* quoted here: this is a risk, and leading with the
    # error text reads as a report that it already happened.
    assert found[0].message == (
        "'value' is written singular over an object that may be plural, "
        "and errors at evaluation if it is"
    )


def test_a_runtime_risk_does_not_make_the_statement_fail_to_type_check() -> None:
    """`ok` answers "does this type-check", not "is this without risk"."""
    env = TypeEnvironment.create(Dialect.SESSION)
    result = check(parse('value of results from (bes property "X") of bes computers'), env)
    assert [d.code for d in result.diagnostics] == ["singular-over-plural-object"]
    assert result.ok
    assert result.to_dict()["ok"] is True

    broken = check(parse('1 + "a"'), TypeEnvironment.create(Dialect.CLIENT))
    assert not broken.ok


@pytest.mark.parametrize(
    "source",
    [
        'unique value of ("a";"b")',
        'concatenation of ("a";"b")',
        "maximum of (1;2)",
        "minimum of (1;2)",
        "sum of (1;2)",
        "set of (1;2)",
    ],
)
def test_an_aggregate_is_not_a_non_unique_risk(source: str, env: TypeEnvironment) -> None:
    """Consuming a collection is what these are *for*.

    `unique value of X` is the point most sharply: it dedups first, so it
    succeeds where a bare singular form over the same object would not. Warning
    that an aggregate was handed a plural is warning that it was used.
    """
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert "singular-over-plural-object" not in codes


def test_every_aggregate_name_is_a_name_the_tables_define(env: TypeEnvironment) -> None:
    """The exemption set is curated, so it can rot; this is what notices.

    It cannot be inferred: the tables record an aggregate's operand as the
    *element* type (`unique values of <bes action>`), never as the collection,
    so "takes a plural by declaration" is not a question the data answers. The
    nearest type-shape predicate -- return type equal to the operand type, or
    to it with multiplicity, or to a set of it -- matches 70 names, among them
    `parent`, `first child` and `absolute value`, which genuinely distribute
    and must keep warning.
    """
    for name in typecheck.AGGREGATES:
        rows = inspectors.lookup(name, kind=inspectors.InspectorKind.PROPERTY)
        assert rows, f"{name!r} matches no property row"
        assert all(entry.multivalued for entry in rows), f"{name!r} is not multivalued"


@pytest.mark.parametrize(
    "source",
    [
        pytest.param('"a" & (name of files of folder "c:\\")', id="binary-right"),
        pytest.param('(name of files of folder "c:\\") = "x"', id="binary-left"),
        pytest.param("-(free space of drives)", id="unary-argument"),
        # The shape the reported webreport had: the collapse is two levels down
        # inside the operand, and still the reason the operand is legal.
        pytest.param(
            '"a" & ((it as trimmed string) of name of files of folder "c:\\")',
            id="nested-under-a-cast",
        ),
    ],
)
def test_a_collapse_that_an_operator_required_is_not_a_risk(
    source: str, env: TypeEnvironment
) -> None:
    """An operator demands a singular, so the collapse is what makes the
    expression legal at all. Reporting it says the author should have written
    something they had no way to write."""
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert "singular-over-plural-object" not in codes


def test_a_collapse_under_an_error_fallback_is_not_a_risk(env: TypeEnvironment) -> None:
    """`a | b` yields `b` when `a` errored, so this exact failure is handled.

    The corpus writes it that way deliberately -- `free space of drives of
    system folders | 0` is one of its own statements, and the dashboards wrap a
    whole collapsing chain in `... | "<link ... />"`. An author who wrote the
    fallback has answered the question the rule asks.
    """
    codes = [
        d.code for d in check(parse("free space of drives of system folders | 0"), env).diagnostics
    ]
    assert "singular-over-plural-object" not in codes


def test_a_collapse_nothing_asked_for_is_still_a_risk(env: TypeEnvironment) -> None:
    """The other half, and the more important one: the same collapse standing
    on its own, demanded by nothing, still reports."""
    for source in ('name of files of folder "c:\\"', "free space of drives of system folders"):
        codes = [d.code for d in check(parse(source), env).diagnostics]
        assert codes == ["singular-over-plural-object"], source


def test_a_singular_form_over_a_singular_object_is_silent() -> None:
    assert (
        check(parse('name of file "x"'), TypeEnvironment.create(Dialect.CLIENT)).diagnostics == ()
    )


def test_a_property_used_on_the_wrong_direct_object_is_a_finding(env: TypeEnvironment) -> None:
    """`size` is real and `string` is a real type; no row joins them."""
    result = check(parse('size of "a"'), env)
    assert [d.code for d in result.diagnostics] == ["property-not-defined"]
    assert result.diagnostics[0].message == "the property 'size of <string>' is not defined"
    assert result.value.types == frozenset()


def test_the_property_message_names_the_index_it_was_given(env: TypeEnvironment) -> None:
    result = check(parse('key "a" of "b"'), env)
    assert result.diagnostics[0].message == (
        "the property 'key <string> of <string>' is not defined"
    )


@pytest.mark.parametrize(
    "source",
    [
        "it",
        # `if` passes its enclosing context through; it introduces none.
        "if true then it else it",
        # The object of an `of` sees the enclosing context, not its own.
        'name of file "x" of it',
    ],
)
def test_it_without_a_context_is_a_finding(source: str, env: TypeEnvironment) -> None:
    found = [d for d in check(parse(source), env).diagnostics if d.code == "used-without-context"]
    assert found
    assert found[0].message == "'it' used without context"


def test_it_is_singular_even_when_its_context_is_plural(env: TypeEnvironment) -> None:
    """`A of B` evaluates `A` once per element of `B`, so `it` is one element."""
    result = check(parse('name of files of folder "c:\\"'), env)
    # The chain carries a `singular-over-plural-object` risk of its own; the
    # rule under test here is the `it` binding, which is unrelated.
    assert [d.code for d in result.diagnostics] == ["singular-over-plural-object"]
    assert types_of('size of it of files of folder "c:\\"', env) == {"integer"}


def test_the_checker_and_the_binding_pass_agree(env: TypeEnvironment) -> None:
    """Two passes over the same rule must not drift apart."""
    source = 'name of it of file "x"'
    bindings = resolve_it_bindings(parse(source))
    assert [binding.context is not None for binding in bindings] == [True]
    assert check(parse(source), env).diagnostics == ()


# ---------------------------------------------------------------------------
# The plurality rules the engine enforces
# ---------------------------------------------------------------------------


def test_a_whose_filter_may_be_plural_but_must_be_boolean(env: TypeEnvironment) -> None:
    """The asymmetry against `if`: a filter may be plural, a condition may not."""
    # `conjunctions of <boolean>` is a real row that returns a *plural* boolean,
    # which is the only way to reach a plural filter -- an operator would impose
    # its own singularity rule first and fail before the filter was reached.
    plural = check(parse('files whose (conjunctions of (name of it = "x")) of folder "c:\\"'), env)
    assert plural.diagnostics == ()
    assert check(parse('files whose (name of it = "x") of folder "c:\\"'), env).diagnostics == ()

    wrong = check(parse('files whose (size of it) of folder "c:\\"'), env)
    assert [d.code for d in wrong.diagnostics] == ["whose-filter-not-boolean"]
    assert wrong.diagnostics[0].message == (
        "a whose filter must have type 'boolean' (it has type 'integer' now)"
    )


@pytest.mark.parametrize(
    ("source", "code"),
    [
        pytest.param(
            'sizes of files of folder "c:\\" > 1000',
            "left-operand-not-singular",
            id="binary-left",
        ),
        pytest.param(
            '1000 < sizes of files of folder "c:\\"',
            "right-operand-not-singular",
            id="binary-right",
        ),
        pytest.param(
            '-(sizes of files of folder "c:\\")', "argument-not-singular", id="unary-argument"
        ),
        pytest.param(
            'true and sizes of files of folder "c:\\"',
            "right-operand-not-boolean",
            id="and-right",
        ),
        pytest.param(
            'if names of files of folder "c:\\" then 1 else 2',
            "if-condition-not-singular-boolean",
            id="if-condition",
        ),
    ],
)
def test_an_operand_that_must_be_singular_and_is_not(
    source: str, code: str, env: TypeEnvironment
) -> None:
    result = check(parse(source), env)
    assert code in {d.code for d in result.diagnostics}


def test_a_plural_operand_inside_a_filter_fails_on_the_operator(env: TypeEnvironment) -> None:
    """The engine answers `sizes of it > 1000` inside a `whose` with `A singular
    expression is required.` -- the *operator's* rule. The filter itself is
    innocent: it may be plural, and it is boolean either way."""
    result = check(parse('files whose (sizes of it > 1000) of folder "c:\\"'), env)
    assert [d.code for d in result.diagnostics] == ["left-operand-not-singular"]


def test_a_tuple_index_must_be_an_integer_literal(env: TypeEnvironment) -> None:
    """A string index parses as `item <string> of ...`, a real property. It is
    a finding only because no row defines that property on a tuple."""
    result = check(parse('item "a" of (1, 2, 3)'), env)
    assert [d.code for d in result.diagnostics] == ["tuple-index-not-literal"]
    assert result.diagnostics[0].message == "the tuple index '\"a\"' is not an integer literal"


def test_unknown_operands_do_not_produce_findings(env: TypeEnvironment) -> None:
    """Half-known is not enough to complain about."""
    assert check(parse('bogusproperty of file "x" + "a"'), env).diagnostics == ()


def test_a_ruled_out_value_does_not_cascade(env: TypeEnvironment) -> None:
    """One mistake, one finding.

    Everything downstream of a ruled-out value can only restate it in worse
    words -- `<none> as trimmed string`, `<none> != <string>` -- so the value
    silences the checks it feeds. It stays empty rather than becoming unknown,
    because the statement really is broken and `ok` has to keep saying so.
    """
    result = check(parse('exists (it as trimmed string) whose (it != "") of size of "a"'), env)
    assert [d.code for d in result.diagnostics] == ["property-not-defined"]
    assert not result.ok


@pytest.mark.parametrize(
    "source",
    [
        pytest.param('if true then "a" else nothing', id="if-branch"),
        pytest.param(
            'if windows of operating system then "a" else nothings', id="if-branch-plural"
        ),
        pytest.param("(1) | nothing", id="bar"),
        pytest.param("nothing as string", id="cast"),
    ],
)
def test_nothing_is_compatible_with_whatever_it_is_held_against(
    source: str, env: TypeEnvironment
) -> None:
    """`undefined` is an absence of type information, not a type that conflicts.

    The tables give it to `nil`, `null` and `error` -- written `nothing`,
    `nothings`, `null value` and `error` -- and `if X then Y else nothings` is
    ordinary shipped content the evaluator accepts. Compared as an ordinary
    type name it unified with nothing, which accounted for 41 of the 46 type
    errors over a 1,108-file corpus of real content.
    """
    assert [d.code for d in check(parse(source), env).diagnostics] == []


def test_plurality_still_answers_for_itself_over_an_undefined_value(
    env: TypeEnvironment,
) -> None:
    """Type and plurality are separate axes, and only the type one is widened here.

    `nothing` is recorded plural, so `-nothing` keeps reporting that its
    argument is not singular -- the operator lookup it used to fail first is
    what stopped.
    """
    assert [d.code for d in check(parse("-nothing"), env).diagnostics] == ["argument-not-singular"]


def test_an_undefined_operand_does_not_silence_a_real_mismatch(env: TypeEnvironment) -> None:
    """The short-circuit is per-comparison, not a blanket amnesty: only the side
    actually typed `undefined` stops counting."""
    assert [d.code for d in check(parse('if true then 1 else "a"'), env).diagnostics] == [
        "if-branch-types-incompatible"
    ]
    assert [d.code for d in check(parse('"a" | 42'), env).diagnostics] == [
        "operand-types-incompatible"
    ]


def test_branches_no_single_platform_shares_may_differ_in_type(env: TypeEnvironment) -> None:
    """The type axis answers to the platform axis.

    `if 1 then 2 else "a"` is a mistake; two branches that exist on disjoint
    platforms differing in type is the idiom itself, and is covered by
    `test_if_branches_union_their_platforms_rather_than_intersecting`.
    """
    result = check(parse('if true then 1 else "a"'), env)
    assert [d.code for d in result.diagnostics] == ["if-branch-types-incompatible"]
    assert result.diagnostics[0].message == (
        "the types in 'then <integer> else <string>' are not compatible"
    )
    assert check(parse(f"({WINDOWS_ONLY}) | ({LINUX_ONLY})"), env).diagnostics == ()


def test_bar_allows_a_type_and_its_with_multiplicity_form(env: TypeEnvironment) -> None:
    """`<T with multiplicity>` is `T`'s own child type, not an unrelated one.

    Confirmed live against a real QnA: `unique value of "a" | "b"` evaluates
    cleanly (returning `"a"`, never reaching the fallback), so the checker
    must not treat `string with multiplicity` and `string` as incompatible --
    they share the ancestor `string`, the same is-a relationship
    `combine_cast`/`combine_binary`/`combine_unary` already resolve through
    `inspectors.ancestors`.
    """
    assert check(parse('unique value of "a" | "b"'), env).diagnostics == ()


def test_if_branches_allow_a_type_and_its_with_multiplicity_form(env: TypeEnvironment) -> None:
    """Same rule as the `|` case above, for `if`/`then`/`else`.

    Confirmed live: `if true then (unique value of "a") else "b"` evaluates
    cleanly.
    """
    assert check(parse('if true then (unique value of "a") else "b"'), env).diagnostics == ()


def test_bar_allows_unrelated_siblings_under_a_common_ancestor(env: TypeEnvironment) -> None:
    """Compatibility is "shares an ancestor", not merely "one is a subtype of
    the other" -- `file` and `folder` are unrelated siblings, both children of
    `filesystem object`, and share no more than that.

    Confirmed live: `(file "/tmp/a") | (folder "/tmp")` evaluates cleanly (it
    fails only at runtime, on the nonexistent path, never on type)."""
    assert check(parse('(file "/tmp/a") | (folder "/tmp")'), env).diagnostics == ()


def test_bar_still_rejects_types_with_no_shared_ancestor(env: TypeEnvironment) -> None:
    """The ancestor-aware fix must not go too far the other way.

    `integer` and `string` share no ancestor at all -- confirmed live, `1 |
    "b"` really does fail with `Incompatible types.` -- so this must keep
    firing exactly as `test_bar_message_leads_with_the_evaluators_own_wording`
    above already pins.
    """
    assert [d.code for d in check(parse('1 | "b"'), env).diagnostics] == [
        "operand-types-incompatible"
    ]


def test_every_type_check_diagnostic_is_reachable() -> None:
    """The catalog and the checker must not drift apart.

    `diagnostics.py` records the engine's vocabulary; this holds the checker to
    emitting all of it, minus the entries that provably cannot be decided
    without running the engine. A new orphan fails here rather than sitting
    unnoticed as a message nothing ever produces.
    """
    source = pathlib.Path(typecheck.__file__).read_text(encoding="utf-8")
    emitted = set(re.findall(r'"([a-z][a-z0-9-]+)"', source))
    catalog = {code for code, entry in DIAGNOSTICS.items() if entry.origin is Origin.TYPE_CHECK}
    # `item 0 of <not a tuple>`: the engine settles this by evaluating, and the
    # parser only builds an `ItemOf` for a literal tuple in the first place, so
    # the checker never has a case to report. Kept in the catalog as vocabulary.
    assert catalog - emitted == {"argument-not-a-tuple"}


def test_a_wide_expression_does_not_exhaust_the_python_stack(env: TypeEnvironment) -> None:
    """A left-associative chain is shallow to parse and deep in the tree.

    `MAX_PARSE_DEPTH` bounds how deeply *nested* an expression the parser will
    return, but not how *wide* one is: the parser builds `1 + 1 + 1 ...`
    iteratively, so a generated `x = 1 or x = 2 or ...` of a few thousand terms
    parses fine and arrives here as a few thousand levels of left-nested
    `Binary`. A recursive checker overflows on it well before the parser would
    have objected.
    """
    assert check(parse("1" + " + 1" * 5000), env).value.types == frozenset({"integer"})
    assert check(parse("true" + " or true" * 5000), env).value.types == frozenset({"boolean"})
