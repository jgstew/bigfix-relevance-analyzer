"""Validate the classifier's marker lists against the real inspector dumps.

The marker lists in :mod:`bigfix_relevance_analyzer.dialect` are hand-curated --
the traps documented there mean the dumps cannot simply be diffed into a word
list. These tests hold the curation to the data: a marker claimed to be
session-only must be absent from all five client platform dumps, and vice versa.

The dumps in ``tests/examples/relevance_properties/`` are the evidence base and
are deliberately test-only reference data, not something the package ships.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from bigfix_relevance_analyzer.dialect import (
    _BES_PHRASE_RE,
    _BES_PREFIX_CLIENT_PHRASES,
    _CLIENT_MARKERS,
    _SESSION_MARKERS,
)

PROPERTIES = Path(__file__).parent / "examples" / "relevance_properties"


def _signatures(path: Path) -> set[str]:
    """The inspector signatures in one dump, normalized for phrase matching.

    Each line is ``<signature>: <return type>``. Placeholder brackets are
    dropped so ``windows of <operating system>`` becomes a plain phrase.
    """
    signatures = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        signature, _, _return_type = line.rpartition(": ")
        signatures.add(signature.replace("<", "").replace(">", "").lower())
    return signatures


def _union(paths: list[Path]) -> set[str]:
    return set().union(*(_signatures(path) for path in paths))


CLIENT_DUMPS = sorted(PROPERTIES.glob("client_relevance_*.txt"))
SESSION_DUMPS = sorted(PROPERTIES.glob("session_relevance_*.txt"))


def test_the_dumps_are_where_the_tests_expect() -> None:
    """Guard against a silent rename turning every check below into a no-op."""
    assert len(CLIENT_DUMPS) == 5
    assert len(SESSION_DUMPS) == 2


def _variants(marker: str) -> set[str]:
    """``marker`` with both grammatical numbers.

    A dump names whichever number the inspector is declared in -- ``statistical
    bin`` but ``current bes servers`` -- while relevance is written in whichever
    number reads naturally, so a marker set carries both and a match on either
    is the same evidence.
    """
    singular = marker[:-3] + "y" if marker.endswith("ies") else marker.removesuffix("s")
    return {marker, singular, f"{singular}s"}


def _present(signatures: set[str], marker: str) -> bool:
    """Whether any signature in ``signatures`` uses ``marker`` as a whole phrase."""
    return any(
        re.compile(rf"\b{re.escape(variant)}\b").search(signature)
        for variant in _variants(marker)
        for signature in signatures
    )


@pytest.mark.parametrize("marker", sorted(_SESSION_MARKERS))
def test_session_markers_appear_only_in_session_relevance(marker: str) -> None:
    assert _present(_union(SESSION_DUMPS), marker), f"{marker!r} is not in any session dump"
    assert not _present(_union(CLIENT_DUMPS), marker), (
        f"{marker!r} is client-valid; it cannot be a session marker"
    )


@pytest.mark.parametrize("marker", sorted(_CLIENT_MARKERS))
def test_client_markers_appear_only_in_client_relevance(marker: str) -> None:
    assert _present(_union(CLIENT_DUMPS), marker), f"{marker!r} is not in any client dump"
    assert not _present(_union(SESSION_DUMPS), marker), (
        f"{marker!r} is session-valid; it cannot be a client marker"
    )


def test_every_client_bes_phrase_is_excepted_from_the_prefix_rule() -> None:
    """The guard that catches `bes license` and `bes product`.

    The ``bes `` prefix is treated as session evidence, so any ``bes <word>``
    phrase a client actually defines has to be listed as an exception or the
    classifier will mistype client relevance using it.
    """
    found = {
        f"bes {match.group(1)}"
        for signature in _union(CLIENT_DUMPS)
        for match in _BES_PHRASE_RE.finditer(signature)
    }
    assert found <= _BES_PREFIX_CLIENT_PHRASES, (
        f"client dumps define {sorted(found - _BES_PREFIX_CLIENT_PHRASES)}, which the "
        "prefix rule would mistype as session evidence"
    )


def test_prefix_exceptions_are_all_really_client_inspectors() -> None:
    """No dead exceptions: each one has to be earning its place."""
    client = _union(CLIENT_DUMPS)
    for phrase in _BES_PREFIX_CLIENT_PHRASES:
        assert _present(client, phrase), f"{phrase!r} is not in any client dump"


def test_the_marker_sets_are_disjoint() -> None:
    assert not _SESSION_MARKERS & _CLIENT_MARKERS
