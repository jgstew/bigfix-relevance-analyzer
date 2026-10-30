"""Helpers donated by bigfix-relevance-debugger (#213), with their tests.

Everything above "Beyond the moved tests" moved verbatim from the
debugger's ``tests/unit/upstream/test_relevance_analyzer.py`` at
jgstew/bigfix-relevance-debugger@a8c7261. Only two things changed: the import,
and type annotations, which this repo's strict mypy requires of tests. The
debugger deletes its copy once these ship, so the expected values here are the
contract its NiceGUI and iOS apps were built against.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from _corpus import EXAMPLES, corpus_cases, extracted_sites
from _helpers import golden_text

from bigfix_relevance_analyzer import (
    CountSummary,
    Dialect,
    DialectFit,
    Outcome,
    Plurality,
    analyze_relevance,
    client_platforms,
    dialect_fit,
    summarize_count_results,
)
from bigfix_relevance_analyzer.typecheck import CheckResult, RelevanceValue


def platforms_of(text: str) -> tuple[str, ...]:
    return client_platforms(analyze_relevance(text, dialect=Dialect.CLIENT))


def test_platform_specific_expression() -> None:
    assert platforms_of('exists key "HKLM\\\\Software" of registry') == ("windows",)


def test_portable_expression_lists_every_client_platform() -> None:
    assert platforms_of("name of operating system") == (
        "debian",
        "macos",
        "rhel",
        "ubuntu",
        "windows",
    )


def test_session_environments_are_excluded() -> None:
    platforms = platforms_of('exists debianpackage "bash"')

    assert platforms
    assert not any(p.startswith("session:") for p in platforms)


def test_unparsable_expression_has_no_platforms() -> None:
    assert platforms_of("name of (operating system") == ()


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        (["25"], CountSummary("count", 25, 1, 0)),
        (["3", "0", "4"], CountSummary("count", 7, 3, 0)),
        (["0"], CountSummary("empty-or-error", 0, 1, 0)),
        (["-1"], CountSummary("not-evaluable", None, 1, 1)),
        (["-1", "-1"], CountSummary("not-evaluable", None, 2, 2)),
        # Some contexts not evaluable, the rest produced objects.
        (["-1", "5"], CountSummary("count", 5, 2, 1)),
        (["-1", "0"], CountSummary("empty-or-error", 0, 2, 1)),
        ([], CountSummary("no-context", None, 0, 0)),
    ],
)
def test_summarize_count_results(rows: list[str], expected: CountSummary) -> None:
    assert summarize_count_results(rows) == expected


def test_summarize_count_results_rejects_non_count_rows_like_the_analyzer() -> None:
    with pytest.raises(ValueError, match="banana"):
        summarize_count_results(["banana"])


# --- dialect_fit ------------------------------------------------------------------

C, S = Dialect.CLIENT, Dialect.SESSION


@pytest.mark.parametrize(
    ("text", "dialects", "basis"),
    [
        ('names of files of folder "/etc"', {C}, "resolved"),
        ("names of bes computers", {S}, "resolved"),
        # Name-level resolution says "both" (operating system of <bes computer>
        # is a session property); only the client type check accepts it.
        ("name of operating system", {C}, "type-check"),
        ("version of operating system", {C}, "type-check"),
        ("now", {C, S}, "either"),
        ('(1, "a")', {C, S}, "either"),
        ("names of bes computers whose (name of it = computer name)", {C, S}, "mixed"),
        # A typo type-checks in neither: client, as when a typo breaks the parse...
        ("nme of operating system", {C}, "unclear"),
        # ...unless the text itself says which: "bes <word>" is session.
        ("names of bes computerz", {S}, "classified"),
        ("names of (bes computers", {S}, "classified"),
        ("name of (operating system", {C}, "default"),
    ],
)
def test_dialect_fit(text: str, dialects: set[Dialect], basis: str) -> None:
    fit = dialect_fit(text)

    assert isinstance(fit, DialectFit)
    assert fit.dialects == frozenset(dialects)
    assert fit.basis == basis


def test_dialect_fit_names_what_each_side_contributes_when_mixed() -> None:
    fit = dialect_fit("names of bes computers whose (name of it = computer name)")

    assert fit.client_only == ("computer name",)
    assert fit.session_only == ("bes computers",)


def test_dialect_fit_names_session_only_references() -> None:
    assert dialect_fit("names of bes computers").session_only == ("bes computers",)


# --- Beyond the moved tests ---------------------------------------------------------


def value_of(text: str, dialect: Dialect) -> RelevanceValue:
    check = analyze_relevance(text, dialect=dialect).check
    assert check is not None
    return check.value


@pytest.mark.parametrize(
    ("text", "dialect", "expected"),
    [
        ("name of operating system", C, "singular string"),
        ("names of bes computers", S, "plural string"),
        # Types sort, so the spelling does not depend on set order.
        ('(1; "a")', C, "plural integer | string"),
        # An unknown name: neither plurality nor type is known.
        ("nme of operating system", C, "unknown"),
    ],
    ids=repr,
)
def test_describe(text: str, dialect: Dialect, expected: str) -> None:
    assert value_of(text, dialect).describe() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Plurality known, type not: undetermined (None) and ruled out (empty)
        # read the same, since neither has a type name to show.
        (RelevanceValue(None, Plurality.PLURAL), "plural (unknown type)"),
        (RelevanceValue(frozenset(), Plurality.SINGULAR), "singular (unknown type)"),
        (RelevanceValue(None), "unknown"),
        # A type with no known plurality still shows the type.
        (RelevanceValue(frozenset({"string"})), "unknown string"),
    ],
    ids=repr,
)
def test_describe_without_a_type(value: RelevanceValue, expected: str) -> None:
    assert value.describe() == expected


def test_client_platforms_property_sorts_and_drops_session_environments() -> None:
    value = value_of("now", C)

    assert any(p.startswith("session:") for p in value.platforms)
    assert value.client_platforms == ("debian", "macos", "rhel", "ubuntu", "windows")


def test_client_platforms_property_is_empty_for_a_session_only_value() -> None:
    assert value_of("names of bes computers", S).client_platforms == ()


@pytest.mark.parametrize(
    "text",
    ['exists key "HKLM\\\\Software" of registry', "name of operating system", "now"],
)
def test_client_platforms_function_agrees_with_the_property(text: str) -> None:
    analysis = analyze_relevance(text, dialect=C)

    assert analysis.check is not None
    assert client_platforms(analysis) == analysis.check.value.client_platforms


def test_client_platforms_function_is_empty_without_a_check() -> None:
    analysis = analyze_relevance("name of (operating system")

    assert analysis.check is None
    assert client_platforms(analysis) == ()


def test_count_summary_outcomes_are_outcome_values_or_no_context() -> None:
    """``outcome`` is a string so ``"no-context"`` can sit beside the enum's values."""
    rows_per_case = [["25"], ["0"], ["-1"], ["-1", "5"], []]
    outcomes = {summarize_count_results(rows).outcome for rows in rows_per_case}

    assert outcomes == {o.value for o in Outcome} | {CountSummary.NO_CONTEXT}
    assert CountSummary.NO_CONTEXT == "no-context"


def test_summarize_count_results_reads_rows_as_interpret_count_results_does() -> None:
    """Whitespace and any negative are read exactly as the per-row reader reads them."""
    assert summarize_count_results([" 3 ", "-7", "\t0\n"]) == CountSummary("count", 3, 3, 1)


# --- dialect_fit does not change resolved_dialect ----------------------------------
#
# These pin what resolved_dialect and classified_dialect say for the statements
# above, so a change here is visible. Since #141, a client global written bare
# (`name of operating system`) resolves CLIENT, while dialect_fit keeps calling
# it "type-check": the name alone is in both dialects.


@pytest.mark.parametrize(
    ("text", "resolved", "classified"),
    [
        ('names of files of folder "/etc"', C, None),
        ("names of bes computers", S, S),
        ("name of operating system", C, None),  # #141
        ("version of operating system", C, None),  # #141
        ("now", Dialect.BOTH, None),
        ('(1, "a")', Dialect.BOTH, None),
        ("names of bes computers whose (name of it = computer name)", Dialect.UNCERTAIN, S),
        ("nme of operating system", C, None),  # #141: the known name decides
        ("names of bes computerz", Dialect.BOTH, S),
        ("names of (bes computers", None, S),
        ("name of (operating system", None, None),
    ],
    ids=repr,
)
def test_resolved_and_classified_dialects_of_the_dialect_fit_examples(
    text: str, resolved: Dialect | None, classified: Dialect | None
) -> None:
    dialect_fit(text)
    analysis = analyze_relevance(text)

    assert analysis.resolved_dialect is resolved
    assert analysis.classified_dialect is classified


def test_dialect_fit_is_never_empty_and_only_names_client_or_session() -> None:
    texts = ["", "   ", "1 +", "totallymadeupinspectorname", "now", "names of bes computers"]
    for text in texts:
        fit = dialect_fit(text)
        assert fit.dialects
        assert fit.dialects <= {C, S}


# --- dialect_fit over the corpora ---------------------------------------------------
#
# The debugger dispatches on both `dialects` and `basis`, so #141 fixing
# resolved_dialect must not move either for any real statement. Pinned from
# 1.42.0, before that fix: every statement in both corpora, valid or not.

DIALECT_FIT_GOLDEN = Path(__file__).parent / "golden" / "dialect_fit_corpus.json"


def corpus_statements() -> list[tuple[str, str]]:
    """``(id, text)`` for every corpus statement; ids are unique, as in parity.py."""
    rows = [(case.id, case.source) for case in corpus_cases()]
    ordinals: dict[Path, int] = {}
    for path, site in extracted_sites():
        index = ordinals[path] = ordinals.get(path, -1) + 1
        rows.append((f"{path.relative_to(EXAMPLES).as_posix()}#{index}@L{site.line}", site.text))
    return rows


def test_dialect_fit_is_unchanged_over_the_corpora() -> None:
    fits = {}
    for statement_id, text in corpus_statements():
        fit = dialect_fit(text)
        fits[statement_id] = {
            "text": text,
            "dialects": sorted(d.value for d in fit.dialects),
            "basis": fit.basis,
            "client_only": list(fit.client_only),
            "session_only": list(fit.session_only),
        }
    actual = json.dumps(fits, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    assert len(fits) == len(corpus_statements())  # ids are unique
    assert actual == golden_text(DIALECT_FIT_GOLDEN, actual)


@pytest.mark.parametrize(
    ("text", "analyses"),
    [
        # Names say BOTH: one analysis runs both dialects' checks.
        ("name of operating system", 1),
        ("now", 1),
        ('(1, "a")', 1),
        # Names settle it: no type check is asked for.
        ("names of bes computers", 1),
    ],
    ids=repr,
)
def test_dialect_fit_reuses_the_checks_analysis_already_ran(
    monkeypatch: pytest.MonkeyPatch, text: str, analyses: int
) -> None:
    from bigfix_relevance_analyzer import analyzer

    calls = 0
    real = analyzer._analyze

    def counting(
        text: str, dialect: Dialect | None = None, platform: str | None = None, **kwargs: Any
    ) -> tuple[analyzer.RelevanceAnalysis, Mapping[Dialect, CheckResult]]:
        nonlocal calls
        calls += 1
        return real(text, dialect, platform, **kwargs)

    monkeypatch.setattr(analyzer, "_analyze", counting)
    dialect_fit(text)

    assert calls == analyses
