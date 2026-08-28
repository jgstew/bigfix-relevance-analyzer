"""The type model, the narrowing, and the checker slice.

Everything here derives from the inspector dumps -- a snapshot of one build --
and nothing in this suite runs a relevance engine. That is exactly why the
checker is built to stay quiet: a name it cannot find yields `None`, and `None`
never becomes an error. Findings drawn from the issue #8 investigation are
tagged where they have not been confirmed against a real evaluator.
"""

from __future__ import annotations

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.dialect import Dialect
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


def test_no_example_site_is_reported_broken(env: TypeEnvironment) -> None:
    """The false-positive guard, over every real statement in the corpus.

    The corpus contains 12 `if` statements whose branches differ in platform
    support; an intersecting model would flag them. Nothing here may report a
    finding on shipped content.
    """
    offenders = [
        (path.name, site.line, diagnostic.code, diagnostic.message)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
        for diagnostic in check(parsed.node, env).diagnostics
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
        pytest.param('"a" | 42', "incompatible-types", id="bar-still-type-checked"),
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


@pytest.mark.parametrize(
    "source", ["name of it", "files whose (size of it > 1)", "processors", 'file "x"']
)
def test_constructs_awaiting_property_resolution_stay_silent(
    source: str, env: TypeEnvironment
) -> None:
    """`None` propagates without ever becoming a finding."""
    result = check(parse(source), env)
    assert result.value.types is None
    assert result.diagnostics == ()


def test_unknown_operands_do_not_produce_findings(env: TypeEnvironment) -> None:
    """Half-known is not enough to complain about."""
    assert check(parse('name of it + "a"'), env).diagnostics == ()


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
