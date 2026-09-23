"""Guards on the development-time performance tools in ``tools/perf``.

These tools are not shipped and not imported by the package, so nothing else
would notice them rotting. The tests here are deliberately few: that the parity
gate reuses this suite's corpus readers rather than growing a second one, that
it really does fail when the two arms disagree, and that every arm is exercised.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from test_examples import corpus_files
from test_parser_corpus import corpus_cases

sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "perf"))

import parity


def test_the_parity_gate_reuses_this_suites_corpus_readers() -> None:
    """One corpus, one reader.

    A second reader would drift from this one silently -- and the record format
    is load-bearing enough that ``test_parser_corpus`` documents it in its
    module docstring. Asserting the imported objects are the same function is
    the cheapest way to keep that true.
    """
    # Through ``__dict__`` rather than attribute access: mypy's strict mode
    # disables implicit re-export, so ``parity.corpus_cases`` is an error even
    # though the name is genuinely bound there. The name binding is exactly
    # what this test is about, so read it directly.
    assert parity.__dict__["corpus_cases"] is corpus_cases
    assert parity.__dict__["corpus_files"] is corpus_files


def test_every_statement_in_the_repository_is_checked() -> None:
    """Both sources are covered, and the malformed records are not dropped."""
    ids = [case_id for case_id, _ in parity.statements()]
    assert len(ids) == len(set(ids)), "statement ids must be unique to be reportable"
    assert len(ids) >= len(corpus_cases())
    sources = [text for _, text in parity.statements()]
    assert any("unterminated" in text or text.count('"') % 2 for text in sources), (
        "the corpus' malformed records must reach the gate -- they are the ones "
        "an optimisation is most likely to break"
    )


@pytest.mark.parametrize("arm", sorted(parity.ARMS))
def test_an_arm_compared_with_itself_is_always_identical(arm: str) -> None:
    """The self-test. A failure here means the gate itself is broken.

    It also exercises each arm's own internal assertions over the whole corpus
    -- the tokenize arm's roundtrip check in particular, which no cross-arm
    comparison could catch because both arms would share the bug.
    """
    checked, failures = parity.check(parity.ARMS[arm], parity.ARMS[arm])
    assert failures == []
    assert checked > 0


def test_the_gate_fails_and_names_the_first_differing_case() -> None:
    """The property that matters: a difference is caught, located and printed."""
    baseline = parity.ARMS["parse"]

    def candidate(text: str) -> str:
        return baseline(text) + " DIFFERENT"

    checked, failures = parity.check(baseline, candidate)
    assert len(failures) == checked > 0
    assert "source:" in failures[0] and "baseline:" in failures[0]


def test_an_empty_candidate_registry_runs_the_self_test_and_passes() -> None:
    """``CANDIDATES`` is empty on main; that is a pass, not an error."""
    assert parity.CANDIDATES == {}
    assert parity.main(["--arm", "parse"]) == 0
