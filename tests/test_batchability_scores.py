"""The batchability classifier's measured accuracy, pinned (#225).

``tools/batchability/scores.md`` is :func:`score.report` over the committed
corpus and qna outcomes. Regenerating it here means any change that moves a
verdict on those 545 statements shows up as a diff to review, rather than
silently changing the precision the module docstring quotes.
"""

from __future__ import annotations

import json

from _helpers import REPO_ROOT, golden_text, load_tool

TOOL = REPO_ROOT / "tools" / "batchability"
score = load_tool(TOOL / "score.py", "batchability_score")


def _rows(name: str) -> list[dict[str, str]]:
    return [json.loads(line) for line in (TOOL / name).read_text(encoding="utf-8").splitlines()]


def _all_hosts(scores: str, predictor: str) -> tuple[int, int]:
    """(predicted safe, actually one) on the ``all`` / ``all hosts`` row."""
    for line in scores.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[:3] == [predictor, "all", "all hosts"]:
            return int(cells[3]), int(cells[4])
    raise AssertionError(f"no all-hosts row for {predictor!r}")


def test_the_scores_are_what_the_committed_outcomes_give() -> None:
    actual = score.report(_rows("corpus.jsonl"), _rows("outcomes.jsonl"))

    assert actual == golden_text(TOOL / "scores.md", actual)


def test_a_safe_verdict_with_the_platform_is_right_at_least_96_percent_of_the_time() -> None:
    """The figure the module docstring and the PR quote. A floor, not the
    exact count, so the message says what broke when the golden also moves."""
    scores = (TOOL / "scores.md").read_text(encoding="utf-8")
    safe, one = _all_hosts(scores, "classifier (platform known)")

    assert (safe, one) == (872, 846)
    assert one / safe >= 0.96


def test_the_outcomes_carry_no_host_names_or_paths() -> None:
    """Stripped on the way in: what ran where is a public label and a platform."""
    text = (TOOL / "outcomes.jsonl").read_text(encoding="utf-8")
    rows = _rows("outcomes.jsonl")

    assert {row["platform"] for row in rows} == {"macos", "rhel", "ubuntu", "windows"}
    assert set().union(*(row.keys() for row in rows)) <= {
        "id",
        "host",
        "platform",
        "qna",
        "outcome",
        "error",
    }
    for marker in ("/Users/", "/home/", "C:\\\\Users", ".local", "/sys/", "/dev/"):
        assert marker not in text, marker


def test_every_outcome_names_a_corpus_statement() -> None:
    ids = {row["id"] for row in _rows("corpus.jsonl")}
    outcomes = _rows("outcomes.jsonl")

    assert len(ids) == 545
    assert {row["id"] for row in outcomes} == ids
    assert len(outcomes) == 4 * len(ids)
