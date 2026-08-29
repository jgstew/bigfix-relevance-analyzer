"""Pin the JSON payloads this package hands to a consumer across a wire.

:meth:`~bigfix_relevance_analyzer.analyzer.RelevanceAnalysis.to_dict` is a
public wire format -- an MCP server or a report file reads it, and neither can
hold the node objects it summarises. That makes its *key set* an API: a rename
breaks a consumer as surely as a renamed function would, and it breaks it
silently, at runtime, in a payload nobody diffs.

So the analysis payload is pinned to a golden file here, and the pin is written
before the payload is refactored to compose the per-class ``to_dict`` methods
the rest of this module tests. Everything about that refactor is meant to be
invisible from outside; this is what makes "meant to be" checkable.

Regenerate deliberately, never reflexively -- a diff here is either an addition
(fine, and the point of ``--diff`` below) or a break (not fine):

    UPDATE_GOLDEN=1 pytest tests/test_serialize.py

The golden file is committed, so a regeneration shows up as a reviewable diff
rather than as a test that quietly started agreeing with itself.
"""

from __future__ import annotations

import enum
import json
import os
from collections.abc import Iterator
from pathlib import Path, PurePath
from typing import Any

import pytest

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.analyzer import analyze, analyze_to_dict
from bigfix_relevance_analyzer.breakdown import interpret_count_results
from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.lint import (
    Finding,
    LintConfig,
    Severity,
    counts,
    lint_analysis,
    lint_paths,
    lint_paths_to_dict,
)

GOLDEN = Path(__file__).parent / "golden" / "analysis_payload.json"
EXAMPLES = Path(__file__).parent / "examples"

# Drawn from `tests/corpus/real_world.rlvcorpus`, so the pinned payloads are
# shapes real content actually produces rather than ones invented to be easy.
# The dialect is forced on the first two: this pins the payload, not the
# classifier, and a classifier change should not be able to rewrite the golden.
CASES: tuple[tuple[str, str, Dialect | None, bool], ...] = (
    (
        "client",
        (
            "windows of operating system AND not exists files "
            '"C:\\Windows\\Temp\\EventLogBackupSecurity.evt"'
        ),
        Dialect.CLIENT,
        False,
    ),
    (
        "session",
        (
            "(id of site of it | 0, id of it | 0, applicable computer count of it | 0) "
            "of fixlets of bes sites whose(id of it is contained by set of (2;78;80))"
        ),
        Dialect.SESSION,
        False,
    ),
    # `--mermaid` is off by default, so the flowchart needs its own case or the
    # `parse.mermaid` key would be pinned by nothing.
    (
        "client_with_mermaid",
        'exists (it as trimmed string) whose(it != "") of values "SearchList" of registries',
        Dialect.CLIENT,
        True,
    ),
    # Unparsable on purpose: the error branches of `lexing` and `parse` carry
    # their own keys, and a payload that only ever pins successes leaves the
    # shape a consumer sees on bad input completely unguarded.
    ("unparsable", "exists files (", None, False),
)


def _payloads() -> dict[str, Any]:
    return {
        name: analyze(text, dialect).to_dict(mermaid=mermaid)
        for name, text, dialect, mermaid in CASES
    }


def test_the_analysis_payload_is_unchanged() -> None:
    """Every key the analysis payload has today, it still has.

    Additions are allowed and expected; this asserts on the recorded keys and
    values, so a new key fails only until the golden is regenerated on purpose.
    """
    payloads = _payloads()
    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.write_text(json.dumps(payloads, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pytest.fail("golden rewritten -- review the diff, then rerun without UPDATE_GOLDEN")

    assert GOLDEN.is_file(), f"missing {GOLDEN}; regenerate with UPDATE_GOLDEN=1"
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    # Compare what a consumer actually receives, not what we handed the
    # encoder: a tuple and a list are the same JSON array but not the same
    # Python object, and it is the array that is the API. `test_no_tuples`
    # below is what holds the pre-encode side to the same shape.
    payloads = json.loads(json.dumps(payloads))
    # Compare case by case: a whole-payload assert prints all four on any
    # failure, which buries the one that actually moved.
    for name in expected:
        assert payloads[name] == expected[name], f"payload for {name!r} changed"
    assert set(payloads) == set(expected), "the set of pinned cases changed"


def test_the_payload_is_json_with_no_custom_encoder() -> None:
    """The actual contract: a consumer can hand this straight to ``json.dumps``.

    A ``to_dict`` that needs ``default=`` is not a wire format -- it is a
    ``repr`` with extra steps, and the failure surfaces in the consumer.
    """
    for name, payload in _payloads().items():
        json.dumps(payload)  # raises TypeError on an enum, a Path, or a set
        assert isinstance(payload, dict), name


def _leaves(value: object, path: str = "") -> Iterator[tuple[str, object]]:
    """Every scalar in a payload, with the dotted path that reaches it."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _leaves(item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _leaves(item, f"{path}[{index}]")
    else:
        yield path, value


def test_the_payload_survives_a_round_trip_unchanged() -> None:
    """``payload == json.loads(json.dumps(payload))``, for every case.

    Stricter than "the encoder accepts it", and the difference is not academic:
    :mod:`json` renders a ``tuple`` as an array quite happily, so a payload can
    encode cleanly and still not equal itself once decoded. A consumer that
    caches a payload, or compares one against a stored copy, sees that as a
    spurious change. Sequences therefore have to be ``list`` before they leave.
    """
    for name, payload in _payloads().items():
        assert payload == json.loads(json.dumps(payload)), name


def test_the_payload_holds_no_python_only_types() -> None:
    """No leaf is a tuple, a set, an enum, or a ``Path``.

    The failure message names the offending path, because "somewhere in this
    900-line payload there is a tuple" is not an actionable test failure.
    """
    for name, payload in _payloads().items():
        for path, leaf in _leaves(payload):
            assert not isinstance(leaf, (tuple, set, frozenset, enum.Enum, PurePath)), (
                f"{name}.{path} is a {type(leaf).__name__}, which JSON has no equivalent for"
            )


# ---------------------------------------------------------------------------
# The standalone result types
# ---------------------------------------------------------------------------
# Every type reachable from a public function needs the same treatment, not
# just the analysis payload: a consumer that returns a lint finding or an
# inspector lookup is on exactly the same wire.


def _samples() -> dict[str, object]:
    """One populated instance of every type that has a ``to_dict``.

    Built from real analysis rather than hand-constructed, so a field that
    stops being populated shows up here instead of silently passing against a
    fixture that was only ever plausible.
    """
    report = analyze('exists files whose (name of it = "x") of folder "/tmp"', Dialect.CLIENT)
    assert report.node is not None and report.check is not None
    broken = analyze("exists files (", Dialect.CLIENT)
    assert broken.parse_error is not None
    site = extract_relevance_from_file(
        Path(__file__).parent
        / "examples"
        / "mixed_context"
        / "task_with_client_and_session_relevance.bes"
    )[0]
    finding = lint_analysis(broken, LintConfig(), path=Path("MyFixlet.bes"), site=site)[0]
    level = report.levels[0]
    return {
        "ParseError": broken.parse_error,
        "RelevanceComplexity": report.complexity,
        "CheckResult": report.check,
        "TypeDiagnostic-bearing CheckResult": analyze('1 + "a"', Dialect.CLIENT).check,
        "Probe": level.probe,
        "Level": level,
        "ProbeOutcome": interpret_count_results(["3"])[0],
        "RelevanceSite": site,
        "Finding": finding,
        "Inspector": inspectors.lookup("files")[0],
        "RelevanceType": next(
            entry for entry in inspectors.relevance_types() if entry.name == "substring"
        ),
        "Diagnostic": DIAGNOSTICS["used-without-context"],
    }


@pytest.mark.parametrize("name", list(_samples()))
def test_every_result_type_serializes_to_plain_json(name: str) -> None:
    """The same contract the analysis payload is held to, per type.

    Encodes with no ``default=``, survives a round trip unchanged, and holds no
    leaf that JSON has no equivalent for. These three together are what "plain
    data" has to mean for something crossing a wire.
    """
    payload = _samples()[name].to_dict()  # type: ignore[attr-defined]
    assert isinstance(payload, dict)
    assert payload == json.loads(json.dumps(payload))
    for path, leaf in _leaves(payload):
        assert not isinstance(leaf, (tuple, set, frozenset, enum.Enum, PurePath)), (
            f"{name}.{path} is a {type(leaf).__name__}"
        )


def test_a_finding_carries_its_own_rendered_line() -> None:
    """``text`` is exactly ``str(finding)``, so no consumer reinvents the format.

    Both CLIs print that line and downstream tooling greps it, which makes it
    an API however much it looks like presentation.
    """
    finding = _samples()["Finding"]
    assert isinstance(finding, Finding)
    assert finding.to_dict()["text"] == str(finding)


def test_a_finding_nests_its_site_rather_than_flattening_it() -> None:
    """A finding's ``site`` is the site's own payload, or ``null``.

    Flattening would collide on ``line`` -- a finding's line is absolute in the
    file, a site's is where the site starts -- and silently lose one of them.
    """
    finding = _samples()["Finding"]
    assert isinstance(finding, Finding)
    payload = finding.to_dict()
    assert payload["site"] == finding.site.to_dict() if finding.site else payload["site"] is None
    assert (
        Finding(code="c", severity=Severity.ERROR, message="m", path=None, line=1).to_dict()["site"]
        is None
    )


def _signature(name: str, signature: str) -> Any:
    """One inspector by exact signature, so a test does not depend on row order.

    ``lookup`` returns every overload of a name; indexing into that is a test
    that breaks when a dump gains a row, which says nothing about the code.
    """
    for entry in inspectors.lookup(name):
        if entry.signature == signature:
            return entry
    raise AssertionError(f"no {signature!r} in the tables")


def test_an_inspector_reports_its_dialects_and_platforms_decoded() -> None:
    """``dialects``/``platforms`` are decoded, so no consumer parses ``sources``.

    Re-deriving them means splitting ``"client:windows"`` on a colon in every
    downstream language, which is exactly the sort of duplicated convention
    this payload exists to remove. Checked on both sides of the split, because
    an empty ``platforms`` under session relevance is a real answer -- platform
    is not an axis there -- and not a lookup that failed.
    """
    client = _signature("files", "files of <folder>").to_dict()
    assert client["dialects"] == ["client"]
    assert client["platforms"] == ["debian", "macos", "rhel", "ubuntu", "windows"]
    assert all(source.startswith("client:") for source in client["sources"])

    session = _signature("bes computers", "bes computers").to_dict()
    assert session["dialects"] == ["session"]
    assert session["platforms"] == []
    assert all(source.startswith("session:") for source in session["sources"])


def test_an_absent_fact_is_null_and_never_omitted() -> None:
    """A key whose value is unknown is present with ``null``.

    ``multivalued`` is the case that matters, and it is a real one rather than a
    hypothetical: some captured rows predate the introspection that reports
    plurality, so ``None`` there means "not captured", which is a different
    claim from ``false``. A consumer can only tell those apart if the key is
    present, so the second assertion is the load-bearing one -- omitting a
    ``None`` would make the distinction unrepresentable.
    """
    unknown = [entry for entry in inspectors.all_inspectors() if entry.multivalued is None]
    assert unknown, "no row leaves plurality unknown, so this convention is untested"
    payload = unknown[0].to_dict()
    assert "multivalued" in payload
    assert payload["multivalued"] is None

    # And it is not merely tolerated on one row: every inspector carries the key.
    assert all("multivalued" in entry.to_dict() for entry in inspectors.all_inspectors())


def test_a_probe_outcome_keeps_null_distinct_from_zero() -> None:
    """``count`` is ``null`` when not evaluable, never ``0``.

    Zero is a real answer -- :attr:`Outcome.EMPTY_OR_ERROR` -- so collapsing
    the two would destroy the only distinction this type carries.
    """
    outcomes = interpret_count_results(["3", "-1", "0"])
    by_outcome = {entry.outcome.value: entry.to_dict() for entry in outcomes}
    assert by_outcome["count"]["count"] == 3
    assert by_outcome["not-evaluable"]["count"] is None
    assert by_outcome["empty-or-error"]["count"] == 0


# ---------------------------------------------------------------------------
# The convenience entry points
# ---------------------------------------------------------------------------


def test_analyze_to_dict_matches_analyze_then_to_dict() -> None:
    """The wrapper is exactly the two-step it replaces, flags included.

    It exists so a server's tool body is one call, not so it can quietly
    diverge -- if these ever differ, the wrapper is a second implementation of
    the payload rather than a shortcut to it.
    """
    text = 'exists files whose (name of it = "x") of folder "/tmp"'
    for mermaid in (False, True):
        assert analyze_to_dict(text, Dialect.CLIENT, mermaid=mermaid) == analyze(
            text, Dialect.CLIENT
        ).to_dict(mermaid=mermaid)


def test_lint_counts_covers_every_severity_that_can_be_reported() -> None:
    """``counts`` has a key per reportable severity, present even at zero.

    ``IGNORE`` is absent by construction: a finding at that severity is dropped
    rather than emitted, so a key for it would always read zero and imply the
    linter had looked and found none.
    """
    findings = lint_analysis(analyze("exists files ("), LintConfig())
    tallies = counts(findings)
    assert set(tallies) == {"error", "warning"}
    assert tallies["error"] >= 1
    assert tallies["warning"] == 0


def test_lint_paths_to_dict_agrees_with_lint_paths() -> None:
    """The envelope's findings are the findings, and ``ok`` follows the errors."""
    paths = [str(EXAMPLES / "mixed_context" / "task_with_client_and_session_relevance.bes")]
    config = LintConfig()
    payload = lint_paths_to_dict(paths, config)
    findings = lint_paths(paths, config)

    assert payload["findings"] == [finding.to_dict() for finding in findings]
    assert payload["counts"] == dict(counts(findings))
    assert payload["ok"] is (payload["counts"]["error"] == 0)
    assert payload == json.loads(json.dumps(payload))


def test_lint_paths_to_dict_is_not_ok_when_something_errors() -> None:
    """``ok`` is the pass/fail verdict both CLIs exit on, computed once here."""
    broken = EXAMPLES.parent / "golden" / "broken.rel"
    broken.write_text("exists files (\n", encoding="utf-8")
    try:
        payload = lint_paths_to_dict([str(broken)], LintConfig())
        assert payload["counts"]["error"] >= 1
        assert payload["ok"] is False
    finally:
        broken.unlink()
