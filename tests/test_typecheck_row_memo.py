"""The memoized row lookups answer exactly what the inline filters they replace did.

#199: ``combine_cast``, ``combine_unary`` and ``combine_binary`` used to refilter
a name's table rows -- visibility, then operand acceptance -- on every node, so
``as string`` re-walked ~50 rows each time it was written. The answer depends
only on the name, the operand types and the environment's ``(dialect,
platform)``, so it is now computed once per key and kept in a bounded cache.

The reference implementations below are the comprehensions those methods ran
before, verbatim. Each memo is swept over every name in its table, a spread of
operand types, and several environments -- environment-major, with the cache
left warm between environments, so an entry computed for one dialect or
platform that leaked into another would fail here: 49 of the 101 cast names
have different visible rows in client and session.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable

import pytest

from bigfix_relevance_analyzer import inspectors, typecheck
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.typecheck import UNTYPED, TypeEnvironment, _accepts

Inspector = inspectors.Inspector
Kind = inspectors.InspectorKind

ENVIRONMENTS = (
    TypeEnvironment.create(Dialect.CLIENT),
    TypeEnvironment.create(Dialect.CLIENT, "windows"),
    TypeEnvironment.create(Dialect.CLIENT, "macos"),
    TypeEnvironment.create(Dialect.SESSION),
    TypeEnvironment.create(Dialect.SESSION, "session:console"),
)

# Types no row declares, plus the untyped `nothing`, which every row accepts.
_EXTRA_TYPES = ("integer", "string", "boolean", "version", UNTYPED, "no such type")


def _names(kind: Kind) -> list[str]:
    return sorted(
        {
            entry.name
            for rows in inspectors._by_name().values()
            for entry in rows
            if entry.kind is kind
        }
    )


def _operand_types(rows: Iterable[Inspector]) -> list[str]:
    return sorted({operand for entry in rows for operand in entry.operands} | set(_EXTRA_TYPES))


def _legacy_visible(entries: tuple[Inspector, ...], env: TypeEnvironment) -> list[Inspector]:
    return [entry for entry in entries if env.visible(entry)]


def _legacy_cast(target: str, types: frozenset[str], env: TypeEnvironment) -> list[Inspector]:
    return [
        entry
        for entry in _legacy_visible(inspectors.lookup(target, kind=Kind.CAST), env)
        if entry.name == target
        and any(_accepts(source, candidate) for candidate in types for source in entry.operands)
    ]


def _legacy_unary(operator: str, types: frozenset[str], env: TypeEnvironment) -> list[Inspector]:
    return [
        entry
        for entry in _legacy_visible(inspectors.lookup(operator, kind=Kind.UNARY_OPERATOR), env)
        if any(_accepts(o, t) for t in types for o in entry.operands)
    ]


def _legacy_binary(
    operator: str, lhs: frozenset[str], rhs: frozenset[str], env: TypeEnvironment
) -> list[Inspector]:
    return [
        entry
        for entry in _legacy_visible(inspectors.lookup(operator, kind=Kind.BINARY_OPERATOR), env)
        if len(entry.operands) == 2
        and any(_accepts(entry.operands[0], t) for t in lhs or frozenset())
        and any(_accepts(entry.operands[1], t) for t in rhs or frozenset())
    ]


@pytest.fixture(autouse=True)
def _cold_caches() -> None:
    for memo in (typecheck._cast_rows, typecheck._unary_rows, typecheck._binary_rows):
        memo.cache_clear()


def test_cast_rows_match_the_inline_filter() -> None:
    for env in ENVIRONMENTS:
        for target in _names(Kind.CAST):
            types = _operand_types(inspectors.lookup(target, kind=Kind.CAST))
            for subject in [frozenset({t}) for t in types] + [frozenset(types[:2]), frozenset()]:
                want = _legacy_cast(target, subject, env)
                assert list(typecheck._cast_rows(target, subject, env)) == want, (
                    target,
                    subject,
                    env,
                )


def test_unary_rows_match_the_inline_filter() -> None:
    for env in ENVIRONMENTS:
        for operator in _names(Kind.UNARY_OPERATOR):
            types = _operand_types(inspectors.lookup(operator, kind=Kind.UNARY_OPERATOR))
            for subject in [frozenset({t}) for t in types] + [frozenset(types)]:
                want = _legacy_unary(operator, subject, env)
                assert list(typecheck._unary_rows(operator, subject, env)) == want


def test_binary_rows_match_the_inline_filter() -> None:
    for env in ENVIRONMENTS:
        for operator in _names(Kind.BINARY_OPERATOR):
            types = _operand_types(inspectors.lookup(operator, kind=Kind.BINARY_OPERATOR))
            partners = ("string", "integer", "version", UNTYPED)
            for left, right in itertools.chain(
                ((t, p) for t in types for p in partners), ((p, t) for t in types for p in partners)
            ):
                lhs, rhs = frozenset({left}), frozenset({right})
                want = _legacy_binary(operator, lhs, rhs, env)
                assert list(typecheck._binary_rows(operator, lhs, rhs, env)) == want


def test_the_environment_is_part_of_the_key() -> None:
    """Same name and types, different dialect: different rows, both right.

    ``file as string`` is client-only: session relevance has no ``file``."""
    client, session = (
        TypeEnvironment.create(Dialect.CLIENT),
        TypeEnvironment.create(Dialect.SESSION),
    )
    types = frozenset({"file"})
    from_client = typecheck._cast_rows("string", types, client)
    from_session = typecheck._cast_rows("string", types, session)
    assert list(from_client) == _legacy_cast("string", types, client)
    assert list(from_session) == _legacy_cast("string", types, session)
    assert from_client
    assert not from_session


_SAMPLE_ARGUMENTS: dict[str, tuple[object, ...]] = {
    "_cast_rows": ("string", frozenset({"integer"})),
    "_unary_rows": ("-", frozenset({"integer"})),
    "_binary_rows": ("=", frozenset({"string"}), frozenset({"string"})),
}


@pytest.mark.parametrize("name", sorted(_SAMPLE_ARGUMENTS))
def test_the_memo_is_bounded_and_hands_out_tuples(name: str) -> None:
    """Bounded: operand type sets come from untrusted relevance, and a language
    server lives long. Tuples: a cached list shared between callers is one
    ``append`` away from corrupting every later answer."""
    memo = getattr(typecheck, name)
    assert memo.cache_info().maxsize is not None
    rows = memo(*_SAMPLE_ARGUMENTS[name], TypeEnvironment.create(Dialect.CLIENT))
    assert isinstance(rows, tuple)
    assert rows


def _every_name() -> list[str]:
    return sorted(inspectors._by_name())


def test_visible_lookup_matches_the_inline_filter() -> None:
    """What ``analyze`` reports as a reference's visible rows (#199 item 5):
    every row of any kind the name has, filtered by the environment alone."""
    typecheck._visible_lookup.cache_clear()
    for env in ENVIRONMENTS:
        for name in [*_every_name(), "no such inspector", "NAME"]:
            want = _legacy_visible(inspectors.lookup(name), env)
            assert list(typecheck._visible_lookup(name, env)) == want, (name, env)


def test_visible_lookup_is_bounded_and_hands_out_tuples() -> None:
    assert typecheck._visible_lookup.cache_info().maxsize is not None
    rows = typecheck._visible_lookup("name", TypeEnvironment.create(Dialect.SESSION))
    assert isinstance(rows, tuple)
    assert rows


def _legacy_matched(
    name: str, subject: frozenset[str] | None, env: TypeEnvironment, indexed: bool | None
) -> list[Inspector] | None:
    rows = typecheck._visible_rows(name, env, indexed)
    if not rows:
        return None
    if subject is None:
        return [entry for entry in rows if not entry.operands]
    return [
        entry
        for entry in rows
        if any(_accepts(operand, candidate) for candidate in subject for operand in entry.operands)
    ]


def _legacy_resolve(
    name: str, subject: frozenset[str] | None, env: TypeEnvironment, indexed: bool | None
) -> typecheck.RelevanceValue:
    matched = _legacy_matched(name, subject, env, indexed)
    if matched is None:
        return typecheck.RelevanceValue(types=None, platforms=env.universe)
    return typecheck.RelevanceValue(
        types=frozenset(entry.return_type for entry in matched),
        plurality=typecheck._written_plurality(name, matched),
        platforms=env.platforms_of(matched),
    )


def _property_cases() -> list[tuple[str, frozenset[str] | None]]:
    """Every 7th property name, written both bare and against the types its
    rows take, plus names in both spellings and one the tables lack."""
    names = [*_names(Kind.PROPERTY)[::7], "names", "files", "no such property"]
    cases: list[tuple[str, frozenset[str] | None]] = []
    for name in names:
        rows = inspectors.lookup(name, kind=Kind.PROPERTY)
        cases.append((name, None))
        cases.append((name, frozenset(_operand_types(rows)[:3])))
    return cases


def test_property_matches_and_resolutions_match_the_inline_computation() -> None:
    typecheck._matched_rows.cache_clear()
    typecheck._property_reading.cache_clear()
    for env in ENVIRONMENTS:
        for name, subject in _property_cases():
            for indexed in (None, True, False):
                matched = typecheck._matched_rows(name, subject, env, indexed=indexed)
                want = _legacy_matched(name, subject, env, indexed)
                assert (None if matched is None else list(matched)) == want, (name, subject, env)
                resolved = typecheck.resolve_property(name, subject, env, indexed=indexed)
                assert resolved == _legacy_resolve(name, subject, env, indexed)


def test_resolution_reads_the_platform_universe_of_the_environment_it_was_given() -> None:
    """``TypeEnvironment`` hashes on ``(dialect, platform)`` only, so the
    cached half must not carry the universe: an environment with a narrower
    one still gets its own, however warm the cache is."""
    full = TypeEnvironment.create(Dialect.CLIENT)
    narrow = TypeEnvironment(dialect=Dialect.CLIENT, _all_platforms=frozenset({"windows"}))
    for name in ("no such property", "name"):
        assert typecheck.resolve_property(name, None, full) == _legacy_resolve(
            name, None, full, None
        )
        assert typecheck.resolve_property(name, None, narrow) == _legacy_resolve(
            name, None, narrow, None
        )
    assert typecheck.resolve_property("no such property", None, narrow).platforms == {"windows"}


@pytest.mark.parametrize("name", ["_matched_rows", "_property_reading"])
def test_the_property_memos_are_bounded(name: str) -> None:
    assert getattr(typecheck, name).cache_info().maxsize is not None


def test_matched_rows_hands_out_tuples() -> None:
    rows = typecheck._matched_rows("name", frozenset({"file"}), ENVIRONMENTS[0])
    assert isinstance(rows, tuple)
    assert rows
