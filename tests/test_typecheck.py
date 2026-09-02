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

ALL_PLATFORMS = {
    context
    for source in inspectors.sources()
    for context in [source.partition(":")[2]]
    if source.startswith("client:")
}
ALL_SESSION_CONTEXTS = {source for source in inspectors.sources() if source.startswith("session:")}
ALL_CONTEXTS = ALL_PLATFORMS | ALL_SESSION_CONTEXTS

# One name per corner of the dialect axis, verified against the dumps: `bes
# computers` exists only server-side, `casts` is the introspection meta-layer
# every client platform and every session context defines.
SESSION_ONLY = "bes computers"
BOTH_DIALECTS = "casts"

# Two casts from a string literal that exist on disjoint platforms. They are the
# only way to reach a narrowed platform set without property resolution, which
# is what makes the union rule testable end to end inside this slice.
WINDOWS_ONLY = '"x" as windows display time'
LINUX_ONLY = '"x" as strverscmp version'


@pytest.fixture
def env() -> TypeEnvironment:
    return TypeEnvironment.create(Dialect.CLIENT)


@pytest.fixture
def session_env() -> TypeEnvironment:
    return TypeEnvironment.create(Dialect.SESSION)


def types_of(source: str, env: TypeEnvironment) -> set[str] | None:
    value = check(parse(source), env).value
    return None if value.types is None else set(value.types)


def codes_of(source: str, env: TypeEnvironment) -> list[str]:
    return [diagnostic.code for diagnostic in check(parse(source), env).diagnostics]


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
    # Both casts also exist in the REST API dump, so the sets are not disjoint
    # across the whole axis. The divergence this rule is about is the client
    # half of it: no one endpoint can take both branches.
    assert set(windows.platforms) & ALL_PLATFORMS == {"windows"}
    assert set(linux.platforms) & ALL_PLATFORMS == {"debian", "rhel", "ubuntu"}
    assert not (windows.platforms & linux.platforms & ALL_PLATFORMS)

    both = check(parse(f"if true then ({WINDOWS_ONLY}) else ({LINUX_ONLY})"), env)
    assert set(both.platforms) == set(windows.platforms) | set(linux.platforms)
    assert set(both.platforms) & ALL_PLATFORMS == {"windows", "debian", "rhel", "ubuntu"}
    assert both.diagnostics == ()


def test_error_fallback_unions_its_platforms_too(env: TypeEnvironment) -> None:
    """[unverified] `|` is an alternative by definition -- the right side runs
    only when the left one errors. No example in the corpus uses it to guard
    platforms, so this rule is reasoned from the semantics, not observed."""
    result = check(parse(f"({WINDOWS_ONLY}) | ({LINUX_ONLY})"), env)
    assert set(result.platforms) & ALL_PLATFORMS == {"windows", "debian", "rhel", "ubuntu"}


def test_a_chain_intersects_its_platforms(env: TypeEnvironment) -> None:
    """Within one reading, everything has to hold at once."""
    drives = resolve_property("drives", None, env)
    assert resolve_property("block size", drives.types, env).platforms < drives.platforms


# A fixed-type result -- `exists` answers boolean whatever it wraps -- still only
# evaluates where its operand does. Every rule in this block was settled against
# the client engine rather than argued from semantics; each test names its probe.
WINDOWS_PROPERTY = 'key "x" of registry'


def test_exists_keeps_its_operands_platforms(env: TypeEnvironment) -> None:
    """`exists` swallows a *runtime* nonexistent object, not a missing inspector.

    qna 11.0.6.137 on macOS, where `registry` does not exist:
    `exists (1/0)` answers `False`, but `exists key "x" of registry` is
    `E: The operator "key" is not defined.` -- so the guard is not viable there,
    however boolean-shaped its type is.
    """
    operand = check(parse(WINDOWS_PROPERTY), env)
    assert set(operand.platforms) & ALL_PLATFORMS == {"windows"}
    assert check(parse(f"exists {WINDOWS_PROPERTY}"), env).platforms == operand.platforms


def test_number_of_keeps_its_operands_platforms(env: TypeEnvironment) -> None:
    """qna: `number of applications of registry` is `E: The operator
    "applications" is not defined.` on macOS -- the count is an integer
    everywhere it can be taken, and it can only be taken where the collection
    resolves."""
    operand = check(parse("applications of registry"), env)
    assert set(operand.platforms) & ALL_PLATFORMS == {"windows"}
    assert check(parse("number of applications of registry"), env).platforms == operand.platforms


def test_not_keeps_its_operands_platforms(env: TypeEnvironment) -> None:
    """qna: `not (1 = 1/0)` errors rather than answering -- `not` evaluates its
    operand, so it inherits where that operand can run."""
    result = check(parse(f"not (exists {WINDOWS_PROPERTY})"), env)
    assert set(result.platforms) & ALL_PLATFORMS == {"windows"}


def test_a_tuple_intersects_its_items_platforms(env: TypeEnvironment) -> None:
    """qna: `(1, 1/0)` errors -- a tuple is every element at once, so it runs
    only where all of them do."""
    result = check(parse(f"({WINDOWS_ONLY}, {LINUX_ONLY})"), env)
    assert not set(result.platforms) & ALL_PLATFORMS


def test_a_collection_intersects_its_items_platforms(env: TypeEnvironment) -> None:
    """`;` looks tolerant and is not, for the failure that matters here.

    qna: `(1; 1/0)` answers `1` *and* reports the error -- the runtime failure
    of one element does not take the collection down. But
    `(1; keys of registry)` on macOS is `E: The operator "keys" is not
    defined.`, and a platform that lacks the inspector is exactly that second
    case, not the first.
    """
    result = check(parse(f"({WINDOWS_ONLY}; {LINUX_ONLY})"), env)
    assert not set(result.platforms) & ALL_PLATFORMS


def test_and_takes_only_its_left_operands_platforms(env: TypeEnvironment) -> None:
    """The guard idiom, which intersecting would call viable nowhere.

    qna: `false and (1 = 1/0)` answers `False` -- `and` short-circuits, so the
    right operand is conditional and cannot narrow the whole. This is what lets
    `<platform test> and <platform-specific relevance>` be written at all.
    """
    guarded = check(parse(f"(exists {WINDOWS_PROPERTY}) and ({LINUX_ONLY} = {LINUX_ONLY})"), env)
    assert set(guarded.platforms) & ALL_PLATFORMS == {"windows"}


def test_or_takes_only_its_left_operands_platforms(env: TypeEnvironment) -> None:
    """qna: `true or (1 = 1/0)` answers `True`; `false or (1 = 1/0)` errors.
    The right side runs only sometimes, so only the left side narrows."""
    guarded = check(parse(f"(exists {WINDOWS_PROPERTY}) or ({LINUX_ONLY} = {LINUX_ONLY})"), env)
    assert set(guarded.platforms) & ALL_PLATFORMS == {"windows"}


def test_an_if_intersects_its_condition_with_its_branches(env: TypeEnvironment) -> None:
    """The condition always runs; the branches are alternatives.

    qna: `if false then (exists key "x" of registry) else true` answers `True`
    on macOS -- the untaken branch's missing inspector is tolerated, which is
    the union rule. The condition gets no such tolerance.
    """
    result = check(parse(f'if (exists {WINDOWS_PROPERTY}) then "a" else "b"'), env)
    assert set(result.platforms) & ALL_PLATFORMS == {"windows"}


def test_a_literal_is_viable_everywhere(env: TypeEnvironment) -> None:
    """Characterisation: nothing above may narrow a bare literal, which has no
    operand to inherit from and runs wherever the statement does."""
    for source in ('"x"', "1", "true"):
        assert set(check(parse(source), env).platforms) == set(env.universe)


def test_session_relevance_reports_its_own_contexts(session_env: TypeEnvironment) -> None:
    """Session is an axis too. The dumps name three server-side surfaces, and a
    session-only inspector is defined in the ones that sampled it -- an empty
    set said nothing at all."""
    expected = {source for source in inspectors.lookup(SESSION_ONLY)[0].sources}
    assert expected <= ALL_SESSION_CONTEXTS
    value = resolve_property(SESSION_ONLY, None, session_env)
    assert set(value.platforms) == expected


def test_something_defined_in_both_dialects_reports_both(
    env: TypeEnvironment, session_env: TypeEnvironment
) -> None:
    """The answer the report could not give: this runs on every client platform
    *and* in every session context, and saying so needs one axis, not two."""
    for environment in (env, session_env):
        value = resolve_property(BOTH_DIALECTS, None, environment)
        assert set(value.platforms) == ALL_CONTEXTS


def test_an_operator_does_not_collapse_a_session_statement_to_the_rest_api(
    session_env: TypeEnvironment,
) -> None:
    """End to end over the gap: an everyday session statement uses an operator,
    and only the REST API dump captured session operators. Narrowing on that
    silence would report every such statement as REST-API-only."""
    source = f"{SESSION_ONLY} whose (id of it = 2)"
    assert set(check(parse(source), session_env).platforms) == ALL_SESSION_CONTEXTS


def test_selecting_a_session_context_restricts_resolution() -> None:
    """`--platform session:console` narrows the way `--platform windows` does."""
    console = TypeEnvironment.create(Dialect.SESSION, "session:console")
    assert resolve_property(SESSION_ONLY, None, console).known
    assert set(resolve_property(SESSION_ONLY, None, console).platforms) == {"session:console"}
    assert not resolve_property("drives", None, console).known


def test_session_branches_still_answer_for_their_types(session_env: TypeEnvironment) -> None:
    """The guard on the one behaviour the axis change must not move.

    Session relevance gained a context set, but the coexistence rule still
    ignores it: the three session dumps are sampled unevenly, so contexts two
    branches do not share are a gap in the data rather than proof that no one
    surface sees both. Every session branch coexists, exactly as before, and a
    genuine type disagreement between them is still reported."""
    source = f'if true then (number of {SESSION_ONLY}) else ("x")'
    codes = [diagnostic.code for diagnostic in check(parse(source), session_env).diagnostics]
    assert codes == ["if-branch-types-incompatible"]


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
    `filtered-singular-spelling` is exempt for a stronger reason: it does not
    even claim a risk, only that a plural spelling would read better.
    """
    allowed = {"singular-over-plural-object", "filtered-singular-spelling"}
    offenders = [entry for entry in _corpus_diagnostics(env) if entry[2] not in allowed]
    assert offenders == []


def test_the_corpus_takes_the_non_unique_risk_deliberately(env: TypeEnvironment) -> None:
    """What survives all three exemptions, over every statement in the corpus.

    Shipped content collapses plurals constantly, and almost always says so:
    `free space of drives of system folders | 0` hedges with a fallback, the
    dashboards wrap a whole chain in `... | "<link ... />"`, `unique value of`
    and `set of` are the idioms for asserting a collection is one, and the rest
    feed an operator that required a singular anyway. Nearly every site this
    rule could fire on is one of those.

    These two are not, and they are two different findings. The first is a
    bare `pathname of <plural>` with nothing guarding it, which is exactly
    what the risk rule is for. The second -- `pathname of file
    "UninstallMSI_Tasks.bes" whose (...) of folder ...` -- cannot match
    twice, since the index makes it unique, and lands on the shape rule
    instead. That is the distinction worth pinning: one shape, sorted by
    whether it can actually collapse several into one.

    The corpus's `exists key "HKEY_LOCAL_MACHINE\\HARDWARE\\...\\BIOS" whose
    (...) of registry` used to be pinned here too, and stopped firing when
    the shape rule learned that a direct `exists` answers `False` where the
    empty case would have erred (see `_FILTERED_SPELLING`).
    """
    risks = {(name, line, code) for name, line, code, _ in _corpus_diagnostics(env)}
    assert risks == {
        ("task_time_based_relevance.bes", 28, "singular-over-plural-object"),
        (
            "fixlet_description_relevance_via_javascript.bes",
            114,
            "filtered-singular-spelling",
        ),
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
        # No decimal-point numeral syntax exists to type directly -- a
        # `floating point` value only ever comes from a cast.
        ('"1.5" as floating point', {"floating point"}),
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


def test_the_plural_spelling_indexes_the_same_tuple(env: TypeEnvironment) -> None:
    """`items <integer> of` is a subscript, not the plural written form of the
    `item <string> of <folder>` property -- which would type every element as a
    filesystem object."""
    assert types_of('items 1 of (1, "c")', env) == {"string"}


def test_a_filtered_tuple_is_still_indexed_by_position(env: TypeEnvironment) -> None:
    """A `whose` picks tuples out of the set without changing what any one
    position holds, so the index still names an element's type -- plurally now,
    since filtering yields a set of tuples."""
    source = 'items 1 of (creation time of file "a", file "a") whose (exists item 1 of it)'
    value = check(parse(source), env).value
    assert value.types is not None
    assert set(value.types) == {"file"}
    assert value.plurality is Plurality.PLURAL


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
        "'value' is written singular over an object that may be plural; "
        "a singular context errors at evaluation if it is"
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


# ---------------------------------------------------------------------------
# The sibling risk: singular form of a multivalued property
# ---------------------------------------------------------------------------


def test_a_singular_form_of_a_multivalued_property_is_a_risk(env: TypeEnvironment) -> None:
    """`file of folder "c:\\"` is `Singular expression refers to non-unique
    object.` the moment a second file exists -- the object is singular, and
    the *property* is what may answer with several. The message names the
    plural spelling, because that is the fix."""
    result = check(parse('file of folder "c:\\"'), env)
    assert [d.code for d in result.diagnostics] == ["singular-of-multivalued-property"]
    assert result.diagnostics[0].message == (
        "'file' can hold several values; a singular context errors at "
        "evaluation when it does -- the plural 'files' is preferred"
    )
    # A risk, not a type error: the expression types cleanly.
    assert result.ok
    assert result.value.plurality is Plurality.SINGULAR


def test_a_single_valued_property_written_singular_is_not_a_risk(env: TypeEnvironment) -> None:
    """The gate is the tables' own `multivalued` flag, not the existence of a
    plural spelling -- `name of operating system` has the plural form `names`
    yet answers exactly one value, and warning there would put a style note on
    most of the relevance ever written."""
    assert check(parse("name of operating system"), env).diagnostics == ()


def test_the_two_collapse_risks_do_not_double_fire(env: TypeEnvironment) -> None:
    """A plural object hands the finding to `singular-over-plural-object`;
    this rule speaks only where the object is singular."""
    codes = [d.code for d in check(parse('file of folders of folder "c:\\"'), env).diagnostics]
    assert codes == ["singular-over-plural-object"]


def test_a_multivalued_singular_inside_a_whose_predicate_is_not_a_risk(
    env: TypeEnvironment,
) -> None:
    """Inside the predicate the collection is handled one element at a time,
    so the singular form is the natural spelling there -- the maintainer's
    stated exemption. `boolean value of it` is multivalued and would report
    anywhere else; no comparison or `exists` is involved, so this isolates the
    `whose` retraction itself."""
    source = '(wmi select "x") whose (boolean value of it)'
    assert check(parse(source), env).diagnostics == ()


def test_the_collection_side_of_a_whose_still_reports(env: TypeEnvironment) -> None:
    """Only the predicate is exempt: a collapse in the collection being
    filtered happened before `whose` ever saw an element."""
    codes = [d.code for d in check(parse('(file of folder "c:\\") whose (true)'), env).diagnostics]
    assert codes == ["singular-of-multivalued-property"]


def test_a_multivalued_singular_under_exists_is_not_a_risk(env: TypeEnvironment) -> None:
    """Under `exists` the non-unique error never fires -- confirmed live in
    qna, over a singular and a plural object alike: `exists file of folder
    "/"` and `exists file of folders "/"` both answer `True`, no error,
    however many files exist. Not ideal relevance, but not the error this
    rule warns about, so it cannot stand here."""
    assert check(parse('exists file of folder "c:\\"'), env).diagnostics == ()


@pytest.mark.parametrize(
    "source",
    [
        pytest.param('(file of folder "c:\\" as string) = "x"', id="binary-left"),
        pytest.param('"a" & (file of folder "c:\\" as string)', id="binary-right"),
        pytest.param('if (exists file of folder "c:\\") then 1 else 2', id="if-condition"),
    ],
)
def test_a_multivalued_collapse_something_required_is_not_a_risk(
    source: str, env: TypeEnvironment
) -> None:
    """The same retraction `singular-over-plural-object` gets: where a
    singular is required, the collapse is the only way to write it."""
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert "singular-of-multivalued-property" not in codes


def test_a_multivalued_collapse_under_an_error_fallback_is_not_a_risk(
    env: TypeEnvironment,
) -> None:
    """`a | b` yields `b` when `a` errored, so the author has answered for the
    non-unique case already."""
    codes = [d.code for d in check(parse('file of folder "c:\\" | "none"'), env).diagnostics]
    assert "singular-of-multivalued-property" not in codes


def test_a_multivalued_singular_in_a_tuple_element_is_not_a_risk(env: TypeEnvironment) -> None:
    """A tuple element's plurality is load-bearing -- plural items multiply
    the tuples out -- so suggesting the plural would change what the
    expression means. A `;` collection element is the same statement said
    safely, so there the risk stands."""
    tupled = check(parse('(file of folder "c:\\" as string, 1)'), env)
    assert tupled.diagnostics == ()
    pooled = check(parse('(file of folder "c:\\" as string; "x")'), env)
    assert [d.code for d in pooled.diagnostics] == ["singular-of-multivalued-property"]


def test_no_multivalued_risk_survives_in_the_corpus(env: TypeEnvironment) -> None:
    """The noise report, pinned: shipped content spells these plural, feeds
    them to `exists`, or guards them, so today the rule reports nothing there.
    A future exemption change that starts flagging real content shows up here
    first."""
    hits = [
        entry
        for entry in _corpus_diagnostics(env)
        if entry[2] == "singular-of-multivalued-property"
    ]
    assert hits == []


# ---------------------------------------------------------------------------
# The filtered risk: a singular spelling with a `whose` on it
# ---------------------------------------------------------------------------


def test_a_filter_does_not_make_a_singular_spelling_plural(env: TypeEnvironment) -> None:
    """The engine settles `X whose (P)` by the spelling that was written, the
    same rule `of` follows -- confirmed live in qna, filtering one file::

        Q: (line whose (it contains "<text on one line>") of file "<f>") as string contains "text"
        A: True

    and the same filter over 34 matching lines answers, then raises
    `Singular expression refers to non-unique object.` So it is singular, and
    at risk -- not the static `A singular expression is required.` that
    calling it plural would claim."""
    result = check(parse('file whose (size of it > 1) of folder "c:\\"'), env)
    assert result.value.plurality is Plurality.SINGULAR
    assert [d.code for d in result.diagnostics] == ["singular-of-filtered-collection"]
    assert result.diagnostics[0].message == (
        "'file whose (...)' asserts the filter matches exactly one; a singular "
        "context errors at evaluation when more than one does -- filter the "
        "plural 'files' instead"
    )
    # A risk, not a type error.
    assert result.ok


def test_a_filter_over_a_plural_spelling_is_still_plural(env: TypeEnvironment) -> None:
    """The other half of the same rule, and why the singular case cannot just
    be waved through: the plural spelling in a singular position *is* the
    static error, in qna as here -- `(lines whose (...) of file "<f>") as
    string contains "text"` answers `E: A singular expression is required.`"""
    filtered = check(parse('files whose (size of it > 1) of folder "c:\\"'), env)
    assert filtered.value.plurality is Plurality.PLURAL
    codes = [
        d.code
        for d in check(
            parse('(files whose (size of it > 1) of folder "c:\\") as string = "x"'), env
        ).diagnostics
    ]
    assert codes == ["left-operand-not-singular"]


def test_the_filtered_risk_survives_a_singular_context(env: TypeEnvironment) -> None:
    """Unlike its two siblings, which `accept_collapse` withdraws here. The
    author of a filter always had a safe spelling available -- `exists files
    whose (... and ...)` -- and the collapse is silent when it happens, so the
    singular context does not excuse it. This is the shape that made the whole
    rule matter: 611 sites across one shipped content site were reported as
    type errors the engine does not raise."""
    source = '(file whose (size of it > 1) of folder "c:\\" as string) = "x"'
    result = check(parse(source), env)
    assert [d.code for d in result.diagnostics] == ["singular-of-filtered-collection"]
    assert result.ok


def test_the_filtered_risk_is_exempt_directly_under_exists_and_only_there(
    env: TypeEnvironment,
) -> None:
    """`exists` flattens the collapse it sits directly on, and nothing
    further. One cast in between and the error is back -- qna, over a filter
    matching 34 lines::

        Q: exists (line whose (it contains "e") of file "<f>")
        A: True
        Q: exists ((line whose (it contains "e") of file "<f>") as string)
        E: Singular expression refers to non-unique object.

    which is why the retraction matches the operand's span exactly instead of
    containing it."""
    direct = check(parse('exists (file whose (size of it > 1) of folder "c:\\")'), env)
    assert direct.diagnostics == ()
    wrapped = check(parse('exists (file whose (size of it > 1) of folder "c:\\" as string)'), env)
    assert [d.code for d in wrapped.diagnostics] == ["singular-of-filtered-collection"]


def test_the_filtered_risk_stands_under_an_error_fallback(env: TypeEnvironment) -> None:
    """`|` rescues the two sibling risks but not this one: qna answers the
    first line *and* the non-unique error for `((line whose (it contains "e")
    of file "<f>") as string) | "fallback"`, so the fallback never runs."""
    source = '(file whose (size of it > 1) of folder "c:\\" as string) | "none"'
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert codes == ["singular-of-filtered-collection"]


def test_a_filter_over_a_plural_object_is_the_same_risk_unfiltered_is(
    env: TypeEnvironment,
) -> None:
    """`key whose (P) of <plural keys>` carries exactly what `key of <plural
    keys>` does, and qna agrees, filtering 49 folders::

        Q: names of (file whose (name of it contains "READ") of folders of folder "<d>")
        A: <one name>
        E: Singular expression refers to non-unique object.

    `exists key whose (...) of (keys "A" of it; keys "B" of it) of registry`
    is a shipped idiom -- one content site holds 45,000 -- and the `exists`
    does flatten the error, which is why this warns rather than errors. Take
    the `exists` off, or let a second key appear, and it is the real thing."""
    source = 'exists key whose (name of it = "x") of (keys "A" of it; keys "B" of it) of registry'
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert codes == ["singular-over-plural-object"]


def test_an_indexed_singular_with_a_filter_is_the_other_rule(env: TypeEnvironment) -> None:
    """The index is what makes it unique, and a filter cannot make a folder
    hold two files of one name -- so the *non-unique* hazard cannot fire, and
    this lands on the shape rule instead, naming what the maintainer prefers:
    stay plural, and collapse once at the end with `unique value of`. This is
    the corpus's own `pathname of file "UninstallMSI_Tasks.bes" whose (...) of
    folder ...`.

    Not hazard-free, which is the other half of why it is worth saying -- a
    filter that matches nothing has nothing to be singular about, and qna
    raises for it where the plural spelling answers 0::

        Q: (file "README.md" whose (size of it > 99999999) of folder "<d>") as string
        E: Singular expression refers to nonexistent object.
        Q: number of (files "README.md" whose (size of it > 99999999) of folder "<d>")
        A: 0
    """
    source = 'pathname of file "x.bes" whose (size of it > 1) of folder "c:\\"'
    result = check(parse(source), env)
    assert [d.code for d in result.diagnostics] == ["filtered-singular-spelling"]
    assert result.diagnostics[0].message == (
        "'file whose (...)' writes a filter on a singular spelling and errors "
        "when the filter matches nothing; prefer 'files whose (...)' and, "
        "where a singular is required, 'unique value of' at the end of the chain"
    )
    assert result.ok


def test_the_shape_rule_is_withdrawn_left_of_a_pipe(env: TypeEnvironment) -> None:
    """The reported false positive, verbatim from BES Client Info - Universal.

    Left of a `|`, the empty case erroring is the point: the fallback runs
    *because* `setting "..." whose (value of it = "1") of client` raises
    `Singular expression refers to nonexistent object.` when the filter
    matches nothing. The suggested plural spelling would answer 0 rows without
    erroring, the `ERROR "command polling disabled"` arm would never run, and
    the expression would answer nothing at all -- so the singular here is
    required, and the shape rule is retracted (see `_FILTERED_SPELLING`).

    Only the shape rule, and only on the left: the same form as the right
    operand keeps firing, since nothing there needs the error.
    """
    source = (
        '(value of setting "_BESClient_Comm_CommandPollIntervalSeconds" of client'
        ' | "not set - default 900")'
        ' of setting "_BESClient_Comm_CommandPollEnable" whose (value of it = "1")'
        ' of client | ERROR "command polling disabled"'
    )
    assert [d.code for d in check(parse(source), env).diagnostics] == []

    right = '"x" | pathname of file "x.bes" whose (size of it > 1) of folder "c:\\"'
    assert [d.code for d in check(parse(right), env).diagnostics] == ["filtered-singular-spelling"]


def test_the_shape_rule_is_withdrawn_under_a_direct_exists(env: TypeEnvironment) -> None:
    """The reported false positive: `exists name whose (length of it = 12 AND
    it as lowercase ends with ".log") of it` inside a `files whose (...)`
    predicate, from BES Client Info - Universal. Under a direct `exists`
    neither thing the shape rule names holds -- the empty case answers `False`
    rather than erroring, and `exists <singular> whose (P) of it` is the idiom
    for testing a singular against a predicate. Confirmed live in qna::

        Q: exists name whose (length of it = 99) of file "/etc/hosts"
        A: False

    Exact-span, the same boundary `_FILTERED_RISK` walks: one cast between
    the `exists` and the filtered form and the nonexistent error is back::

        Q: exists ((name whose (length of it = 99) of file "/etc/hosts") as string)
        E: Singular expression refers to nonexistent object.
    """
    direct = 'exists name whose (length of it = 12) of file "x" of folder "c:\\"'
    assert [d.code for d in check(parse(direct), env).diagnostics] == []

    cast = 'exists ((name whose (length of it = 12) of file "x" of folder "c:\\") as string)'
    assert [d.code for d in check(parse(cast), env).diagnostics] == ["filtered-singular-spelling"]


def test_both_operands_of_a_pipe_must_be_singular(env: TypeEnvironment) -> None:
    """`|` is not merely happier with a singular -- it *requires* one, on both
    sides, and the engine refuses a plural before evaluating anything. The
    absent `T:` line marks a compile-time refusal rather than a runtime error::

        Q: (names of files of folder "/etc") | "x"
        E: A singular expression is required.
        Q: "x" | (names of files of folder "/etc")
        E: A singular expression is required.

    Session agrees on both sides, so this is not dialect-gated::

        (1;2) | 3   -> A singular expression is required.
        3 | (1;2)   -> A singular expression is required.

    This is what makes the error-fallback idiom inherently singular: the
    "missing" case has to arrive as an *error* to trip the fallback, and a
    plural that finds nothing answers 0 values instead of erroring.
    """
    left = '(names of files of folder "/etc") | "x"'
    result = check(parse(left), env)
    assert [d.code for d in result.diagnostics] == ["left-operand-not-singular"]
    assert result.diagnostics[0].message == "the left operand of '|' must be singular"

    right = '"x" | (names of files of folder "/etc")'
    assert [d.code for d in check(parse(right), env).diagnostics] == ["right-operand-not-singular"]

    # A collection is plural however short it is, and reaches the same refusal.
    assert [d.code for d in check(parse("(1;2) | 3"), env).diagnostics] == [
        "left-operand-not-singular"
    ]
    assert [d.code for d in check(parse("3 | (1;2)"), env).diagnostics] == [
        "right-operand-not-singular"
    ]

    # `nothing` is an *empty plural*, not a singular null -- it answers no
    # values at all (`T:` with no `A:`) -- so it cannot be a `|` operand
    # either, on either engine::
    #
    #     Q: nothing
    #     T: 31
    #     Q: (1) | nothing
    #     E: A singular expression is required.
    #     Q: (nothing) | 1
    #     E: A singular expression is required.
    #
    # The singular undefined-typed spelling is `ERROR "..."`, which the engine
    # accepts (`(1) | ERROR "x"` answers `1`) and which the fallback idiom
    # actually uses.
    assert [d.code for d in check(parse("(1) | nothing"), env).diagnostics] == [
        "right-operand-not-singular"
    ]
    assert [d.code for d in check(parse('(1) | ERROR "x"'), env).diagnostics] == []


def test_a_pipe_distributed_over_a_plural_object_is_clean(env: TypeEnvironment) -> None:
    """The false positive this rule must not create, and the documented idiom
    in `syntax.md`: `(name of it | "unknown") of bes computers`.

    The `of` distributes, so each `|` sees one element at a time and both its
    operands are singular; only the whole expression is plural. Both engines
    run it happily -- client answers one line per file, session one per
    computer::

        Q: number of ((name of it | "unknown") of files of folder "/etc")
        A: 58
        (session) number of ((name of it | "unknown") of bes computers) -> 2

    Also clean for the corpus's own `free space of drives of system folders |
    0`: `free space` is a singular *spelling*, whatever the object holds, so
    the operand is singular and the collapse risk it raises is retracted by
    the `|` requiring one (see `accept_collapse`).
    """
    distributed = '(name of it | "unknown") of files of folder "/etc"'
    assert [d.code for d in check(parse(distributed), env).diagnostics] == []

    corpus = "free space of drives of system folders | 0"
    assert [d.code for d in check(parse(corpus), env).diagnostics] == []

    session = TypeEnvironment.create(Dialect.SESSION)
    idiom = '(name of it | "unknown") of bes computers'
    assert [d.code for d in check(parse(idiom), session).diagnostics] == []


def test_a_property_used_on_the_wrong_direct_object_is_a_finding(env: TypeEnvironment) -> None:
    """`size` is real and `string` is a real type; no row joins them."""
    result = check(parse('size of "a"'), env)
    assert [d.code for d in result.diagnostics] == ["property-not-defined"]
    assert result.diagnostics[0].message == "the property 'size of <string>' is not defined"
    assert result.value.types == frozenset()


def test_a_world_reference_known_only_with_a_direct_object_is_the_softer_finding(
    env: TypeEnvironment,
) -> None:
    """The reported false positive: `devices` is a top-level plural in the
    proxy agent context the dumps do not cover, and the name collides with the
    captured `device of <grub file location>`. A bare world reference the
    dumps know only with a direct object is the same epistemic state as a name
    no dump defines, so it gets its own diagnostic -- which `lint` demotes to
    `unknown-inspector` -- and the value carries on as unknown rather than
    ruled out, so nothing downstream cascades."""
    result = check(parse("devices"), env)
    assert [d.code for d in result.diagnostics] == ["world-property-not-defined"]
    assert (
        result.diagnostics[0].message
        == "no dump defines the property 'devices' without a direct object"
    )
    assert result.value.types is None
    assert result.ok

    # The shipped MDM Devices group relevance, whole: the unknown `devices`
    # must not earn `management statuses` a second finding on top of it.
    whole = check(parse("(in proxy agent context) AND exists management statuses of devices"), env)
    assert [d.code for d in whole.diagnostics] == ["world-property-not-defined"]


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


# ---------------------------------------------------------------------------
# Tuple types
# ---------------------------------------------------------------------------


def test_a_tuple_resolves_a_property_declared_on_the_tuple_type(
    env: TypeEnvironment,
) -> None:
    """The reported false positive. `attr lists of <( string, string )>` is the
    only row in either dialect whose direct object is a tuple, and flattening
    the pair to its element type made the lookup ask for `attr lists of
    <string>`, which nothing defines."""
    result = check(parse('attr lists of ("title", "Locked")'), env)
    assert result.diagnostics == ()
    assert result.value.types == frozenset({"html attribute list"})


def test_a_tuple_keeps_its_spelling_through_an_applied_context(
    env: TypeEnvironment,
) -> None:
    """`of` is right-associative, so in the webreport that reported this the
    tuple is the *property* of an inner `of`, not the object of the outer one:
    `attr lists of (("title", it) of <string>)`. The spelling has to survive
    that hop or the outer lookup flattens again."""
    result = check(parse('attr lists of ("title", it) of "Desktop"'), env)
    assert result.diagnostics == ()
    assert result.value.types == frozenset({"html attribute list"})


def test_a_tuple_element_of_the_wrong_type_is_still_a_finding(
    env: TypeEnvironment,
) -> None:
    """The spelling is built from the elements, so a boolean second element
    asks for `( string, boolean )` -- which no row declares. The fix removes a
    wrong message, not the check."""
    result = check(parse('attr lists of ("title", it) of true'), env)
    assert [d.code for d in result.diagnostics] == ["property-not-defined"]
    assert (
        result.diagnostics[0].message
        == "the property 'attr lists of <( string, boolean )>' is not defined"
    )


def test_a_tuple_spelling_multiplies_out_over_a_union_element(
    env: TypeEnvironment,
) -> None:
    """An element whose own type is a union offers every combination, so the
    reading that matches a row is found even when a sibling reading does not.
    An `if` whose branches disagree is the cheapest way to build one."""
    value = check(parse('("a", (if true then "b" else 1))'), env).value
    assert value.tuple_types == frozenset({"( string, string )", "( string, integer )"})
    # One of the two readings matches the row, so the lookup succeeds -- the
    # only finding left is the incompatible `if`, which is its own rule.
    result = check(parse('attr lists of ("a", (if true then "b" else 1))'), env)
    assert [d.code for d in result.diagnostics] == ["if-branch-types-incompatible"]
    assert result.value.types == frozenset({"html attribute list"})


def test_a_semicolon_collection_is_not_given_a_tuple_spelling(
    env: TypeEnvironment,
) -> None:
    """`;` pools values -- `(a; b)` is two values of one type, not one value of
    a pair type -- so it must not resolve a tuple-typed row."""
    assert check(parse('("title"; "Locked")'), env).value.tuple_types == frozenset()
    result = check(parse('attr lists of ("title"; "Locked")'), env)
    assert [d.code for d in result.diagnostics] == ["property-not-defined"]


def test_a_collection_of_tuples_pools_the_items_spellings(
    env: TypeEnvironment,
) -> None:
    """The reported false positive, one hop out: `;` mints no spelling of its
    own, but each element of `(("a", it); ("b", "c"))` is still a `( string,
    string )`, and the row matches. Verified in qna 11.0.6.137: the engine
    evaluates this, aggregating every pair into one attribute list -- the
    Dashboard Variables dashboard builds its `attr lists` exactly this way."""
    value = check(parse('(("onclick", "x"); ("href", "y"))'), env).value
    assert value.tuple_types == frozenset({"( string, string )"})
    result = check(parse('attr lists of (("onclick", "x"); ("href", "y"))'), env)
    assert result.diagnostics == ()
    assert result.value.types == frozenset({"html attribute list"})


def test_the_flattened_reading_survives_beside_the_tuple_spelling(
    env: TypeEnvironment,
) -> None:
    """The spelling is additive. The operator tables carry no tuple rows at
    all, so a value that answered only to `( string, string )` would turn a
    working comparison into a fresh false positive."""
    assert check(parse('("a", "b") = ("c", "d")'), env).diagnostics == ()


def test_an_untyped_tuple_element_yields_no_spelling(env: TypeEnvironment) -> None:
    """`None` is "the tables said nothing", and a spelling built around a guess
    would be exactly the fabrication the rest of this module refuses."""
    assert check(parse('("a", bogusproperty)'), env).value.tuple_types == frozenset()


def test_a_tuple_wider_than_the_cap_falls_back_to_the_flattened_reading(
    env: TypeEnvironment,
) -> None:
    """The guard degrades to what this module did before spellings existed --
    a lost match, never a wrong one."""
    element = '(if true then "a" else 1)'
    source = "(" + ", ".join([element] * 4) + ")"
    assert check(parse(source), env).value.tuple_types == frozenset()


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
        pytest.param('(1) | ERROR "x"', id="bar"),
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

    The `|` case spells its undefined operand `ERROR "x"` rather than
    `nothing`, which this test used to hold: `nothing` is an *empty plural*
    (`nothing` alone answers no values at all), and `|` requires singular
    operands, so both engines refuse `(1) | nothing` on a plurality ground
    that has nothing to do with the type question asked here. `ERROR "x"` is
    the singular undefined-typed spelling, and the engine runs it::

        Q: (1) | ERROR "x"
        A: 1

    See `test_both_operands_of_a_pipe_must_be_singular` for the plurality half.
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


def test_a_risk_in_both_if_branches_is_not_a_type_error(env: TypeEnvironment) -> None:
    """ "At most one branch may have *type errors*" means what it says, and a
    runtime risk is not one -- the line `CheckResult.ok` draws by origin.

    Counting risks here turned an ordinary platform-guarded statement into a
    reported type error: 164 sites in one shipped content site, every one of
    them an `if (x64 of operating system) then (...) else (...)` whose two
    branches say the same risky thing about the 32- and 64-bit registry."""
    source = (
        'if (x64 of operating system) then (exists key whose (name of it = "a") of keys "A" of it '
        'of registry) else (exists key whose (name of it = "b") of keys "B" of it of registry)'
    )
    result = check(parse(source), env)
    assert [d.code for d in result.diagnostics] == ["singular-over-plural-object"] * 2
    assert result.ok


def test_a_branches_risks_survive_it_even_though_its_errors_do_not(env: TypeEnvironment) -> None:
    """The tolerance is for *errors*: one branch may fail to type because it is
    the branch this platform never runs. A risk is about the code as written,
    so it is not swallowed with them -- two of this repo's own corpus sites
    only surfaced once it stopped being."""
    source = 'if true then (file of folder "c:\\" as string) else "b"'
    assert [d.code for d in check(parse(source), env).diagnostics] == [
        "singular-of-multivalued-property"
    ]


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


def test_a_fallback_after_a_comparisons_right_side_is_not_a_type_error(
    env: TypeEnvironment,
) -> None:
    """`|` binds tighter than `=`, so the fallback belongs to the right
    operand, not to the comparison's boolean result.

    Confirmed live: `0 = exit code of action | 999` evaluates to `False`
    (the fallback's 999 compared against 0), where the old parse -- `(0 =
    exit code of action) | 999` -- would have yielded `999` and a `<boolean>
    | <integer>` incompatibility this checker used to report falsely.
    """
    assert check(parse("0 = exit code of action | 999"), env).diagnostics == ()


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


# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------
#
# Both rules below encode behaviour confirmed against a live client engine and
# a live session engine (2026-08-30), recorded with the transcripts in
# `docs/universal_relevance.md`. They are the only checks here that fire on
# relevance the engine accepts and answers: the statement is well-typed, and the
# answer is simply wrong. That is why they are worth a warning at all.


@pytest.mark.parametrize(
    ("source", "code"),
    [
        # No version anywhere: the engine compares these as strings, and
        # `"2.10.1" < "2.3.3"` because `'1' < '3'` at the third character.
        pytest.param('"2.10.1" > "2.3.3"', "version-like-string-compare", id="bare-strings"),
        pytest.param('"1.9" < "1.10"', "version-like-string-compare", id="bare-strings-crossing"),
        pytest.param('"1.2" = "1.2.3"', "version-like-string-compare", id="bare-strings-equality"),
        # Truncation makes the engine call unequal versions equal, so only the
        # operators that flip at equality in the direction of the dropped tail
        # are wrong. Every expectation below was read off a live engine.
        # Left side longer -- `>` and `<=` break.
        pytest.param(
            'version "1.2.3" > version "1.2"',
            "version-truncating-compare",
            id="left-longer-gt",
        ),
        pytest.param(
            'version "1.2.3" <= version "1.2"',
            "version-truncating-compare",
            id="left-longer-le",
        ),
        # Right side longer -- `>=` and `<` break.
        pytest.param(
            'version "1.2" >= version "1.2.3"',
            "version-truncating-compare",
            id="right-longer-ge",
        ),
        pytest.param(
            'version "1.2" < version "1.2.3"',
            "version-truncating-compare",
            id="right-longer-lt",
        ),
        # Equality is wrong whichever side is longer.
        pytest.param(
            'version "1.2.3" = version "1.2"',
            "version-truncating-compare",
            id="equality",
        ),
        pytest.param(
            'version "1.2.3" != version "1.2"',
            "version-truncating-compare",
            id="inequality",
        ),
        # The verified real-world defect: `False` on a 14.6.1 host, where the
        # author asked for "newer than 14". The property's count is unknown and
        # is taken to be the longer side.
        pytest.param(
            'version of operating system > version "14"',
            "version-truncating-compare",
            id="property-against-shorter-literal",
        ),
        pytest.param(
            '"1.2.3" as version <= version "1.2"',
            "version-truncating-compare",
            id="cast-form",
        ),
    ],
)
def test_version_comparison_findings(source: str, code: str, env: TypeEnvironment) -> None:
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert code in codes, codes


@pytest.mark.parametrize(
    "source",
    [
        # `pad of` on both sides is the fix, and must not then be nagged about.
        pytest.param('pad of version "1.2" > pad of version "1.2.3"', id="both-padded"),
        pytest.param(
            'pad of version of operating system > pad of version "14"',
            id="both-padded-property",
        ),
        # Same component count on both sides: nothing is truncated away.
        pytest.param('version "1.2.3" > version "1.2.4"', id="equal-counts"),
        pytest.param('"2.10.1" > "2.3.3" as version', id="coerced-equal-counts"),
        # Truncating, but in the direction that does not change the answer --
        # the safe half of the table, and the shape most real content uses.
        pytest.param('version "1.2.3" >= version "1.2"', id="left-longer-ge-safe"),
        pytest.param('version "1.2.3" < version "1.2"', id="left-longer-lt-safe"),
        pytest.param('version "1.2" > version "1.2.3"', id="right-longer-gt-safe"),
        pytest.param('version "1.2" <= version "1.2.3"', id="right-longer-le-safe"),
        # The three shapes this repo's own example content uses.
        pytest.param('version of operating system >= "5.1"', id="corpus-os-ge"),
        pytest.param('version of client >= "9.0" as version', id="corpus-client-ge"),
        pytest.param('version of client < "8.0"', id="corpus-client-lt"),
        # Two properties: no literal to anchor a claim about shape.
        pytest.param("version of operating system > version of client", id="two-properties"),
        # Not version-shaped, so not a version-comparison mistake.
        pytest.param('"a.b" > "c.d"', id="dotted-but-not-numeric"),
        pytest.param('"abc" > "abz"', id="plain-strings"),
        pytest.param('"1" > "2"', id="single-components-no-dots"),
        # Not an ordering comparison at all.
        pytest.param('"1.2.3" contains "1.2"', id="contains-is-not-ordering"),
    ],
)
def test_version_comparison_stays_quiet(source: str, env: TypeEnvironment) -> None:
    codes = {d.code for d in check(parse(source), env).diagnostics}
    assert not (codes & {"version-like-string-compare", "version-truncating-compare"}), codes


# ---------------------------------------------------------------------------
# Bare singular world objects
# ---------------------------------------------------------------------------
#
# A world object written singular with no index, where the tables also define an
# *indexed* row returning the same type, is one of many -- and the engine says
# so. Every expectation here was read off a live engine (2026-08-31); the
# transcripts are in `docs/universal_relevance.md`.
#
# The same-return-type condition is what keeps month constants out: `april` has
# an indexed sibling (`april 2026`), but it returns a `date` rather than a
# `month`, so it is a different operation and not a collection index. Confirmed:
# bare `april` answers `April` cleanly.


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("name of filesystem", id="filesystem"),
        pytest.param("name of application", id="application"),
        pytest.param("family name of processor", id="processor"),
        pytest.param("name of cast", id="introspection-cast"),
    ],
)
def test_a_bare_indexable_world_object_is_a_non_unique_risk(
    source: str, env: TypeEnvironment
) -> None:
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert "singular-over-plural-object" in codes, codes


@pytest.mark.parametrize(
    "source",
    [
        # Genuine world singletons: no indexed row at all.
        pytest.param("name of operating system", id="operating-system"),
        pytest.param("computer name", id="computer-name"),
        pytest.param("current date", id="current-date"),
        # An indexed sibling that returns a *different* type is a different
        # operation, not a way of picking one of many.
        pytest.param("april", id="month-constant"),
        pytest.param("december", id="month-constant-december"),
        # Already unambiguous: an index was supplied, or the plural was written.
        pytest.param('name of filesystem "/"', id="indexed"),
        pytest.param("names of filesystems", id="plural"),
    ],
)
def test_an_unambiguous_world_object_is_left_alone(source: str, env: TypeEnvironment) -> None:
    codes = [d.code for d in check(parse(source), env).diagnostics]
    assert "singular-over-plural-object" not in codes, codes


# ---------------------------------------------------------------------------
# The world fallback applies to an implicit context, never an explicit object
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "source",
    [
        # Three world-only names written against a `file`. The engine refuses
        # each one: `E: The operator "<name>" is not defined.`
        pytest.param('action lock state of file "/etc/hosts"', id="action-lock-state"),
        pytest.param('computer name of file "/etc/hosts"', id="computer-name"),
        pytest.param('current date of file "/etc/hosts"', id="current-date"),
        # qna: `number of properties of files of folder "/etc"` -> E: ... not defined.
        pytest.param('number of properties of files of folder "/etc"', id="of-chain"),
        # qna: the same, reached through `it` inside a `whose` -- still explicit.
        pytest.param(
            'number of files whose (exists properties of it) of folder "/etc"',
            id="explicit-it-inside-whose",
        ),
    ],
)
def test_a_property_with_an_explicit_direct_object_does_not_fall_back(
    source: str, env: TypeEnvironment
) -> None:
    """A name the world defines is still not a property *of* the object written.

    The fallback exists for a bare reference inside a `whose`, where the
    enclosing context supplies a subject the name is not a property of. Written
    with an explicit `of`, there is no such excuse -- and the engine agrees, so
    resolving these against the world masks content that cannot run. 1,008
    names resolve as a world property and nowhere else, so the blast radius is
    the whole of that set.
    """
    assert codes_of(source, env) == ["property-not-defined"]


@pytest.mark.parametrize(
    "source",
    [
        # The motivating case for the fallback. qna: A: 58 -- valid relevance.
        pytest.param(
            'number of files whose (exists properties) of folder "/etc"',
            id="bare-reference-in-whose",
        ),
        # qna: A: 58. `types of <file>` is defined, so the qualified lookup
        # answers and the fallback is never reached.
        pytest.param(
            'number of files whose (exists types of it) of folder "/etc"',
            id="resolves-without-the-fallback",
        ),
        # No context at all: the world is the only scope there is.
        pytest.param("properties", id="bare-world-reference"),
    ],
)
def test_an_implicit_filter_context_still_falls_back_to_the_world(
    source: str, env: TypeEnvironment
) -> None:
    """`whose` supplies a subject, not a scope.

    A global name written inside a filter still resolves against the world when
    the item defines nothing by that name, which is ordinary relevance and the
    reason the fallback was added. Narrowing it must not reach this shape.
    """
    assert codes_of(source, env) == []


def test_a_world_only_name_in_a_filter_keeps_the_softer_finding(env: TypeEnvironment) -> None:
    """The docstring's other example must not be promoted to a hard error.

    `operating system` here is the *object* of its `of`, so it is typed in the
    enclosing `whose` frame -- an implicit context. It already reports
    `world-property-not-defined`, the soft finding lint maps to
    `unknown-inspector`, and it must stay on that code rather than becoming
    `property-not-defined`.
    """
    assert codes_of("files whose (name of it = name of operating system)", env) == [
        "world-property-not-defined"
    ]
