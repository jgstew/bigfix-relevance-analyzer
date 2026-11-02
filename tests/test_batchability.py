"""The batchability classifier (#225): can a statement share one tuple query?

One case per rule, ported from bigfix-remote-client-relevance's
``tools/batchability/test_batchability.py`` (client 1.13.0, its #78), where
every expectation was also measured with qna 11.0.7: the comment on a case
says what qna did. What the rules score over a 545-statement corpus on four
hosts is pinned separately, in :mod:`test_batchability_scores`.
"""

from __future__ import annotations

import pytest

from bigfix_relevance_analyzer import (
    BATCH_RULES,
    RULES,
    Batchability,
    BatchabilityKind,
    BatchReason,
    Plurality,
    analyze_relevance,
    batchability,
)

SAFE = BatchabilityKind.SAFE
ERROR_RISK = BatchabilityKind.ERROR_RISK
UNKNOWN = BatchabilityKind.UNKNOWN
PLURAL_RISK = BatchabilityKind.PLURAL_RISK
SPLIT_RISK = BatchabilityKind.SPLIT_RISK


def rules(text: str, platform: str | None = None) -> set[str]:
    return {reason.rule for reason in batchability(text, platform=platform).reasons}


@pytest.mark.parametrize(
    "text",
    [
        "true",
        "42",
        "name of operating system",  # world objects every endpoint has
        "version of client",
        'version of client >= "9"',
        "computer name as lowercase",
        'exists file "/nonexistent"',  # False: exists absorbs the outermost step
        'not exists file "/nonexistent"',
        'number of files "/nonexistent"',  # 0
        "exists (1;2) whose (it > 5)",  # False
        "number of (1;2) whose (it > 5)",  # 0
        'size of file "/nonexistent" | 0',  # 0: `|` answers for its left side
        'concatenation of ("a";"b")',  # aggregates that answer "" or 0 when empty
        "sum of (1;2) whose (it > 5)",
        "exists maximum of (1;2) whose (it > 5)",  # False
        # The analyzer's runtime risks are absorbed by the guard here.
        'exists key "HKLM\\SOFTWARE" of native registry',
        "exists wmi",
    ],
)
def test_safe(text: str) -> None:
    verdict = batchability(text)

    assert verdict.kind is SAFE, verdict.reasons
    assert verdict.safe
    assert verdict.plurality is Plurality.SINGULAR


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        # Singular expression refers to nonexistent object.
        ('size of file "/nonexistent"', "singular-lookup"),
        ('value of variable "BFRCR_MISSING" of environment', "singular-lookup"),
        ('value of setting "bfrcr_missing" of client', "singular-lookup"),
        ('line 1 of file "/etc/hosts"', "singular-lookup"),
        # exists absorbs only the outermost step; these error beneath it.
        ('exists (size of file "/nonexistent")', "singular-lookup"),
        ('exists files of folder "/nonexistent"', "singular-lookup"),
        ('number of lines of file "/nonexistent"', "singular-lookup"),
        ('exists (folder "/a" | folder "/b")', "singular-lookup"),
        # A property an existing object may lack.
        ('version of file "/x"', "singular-property"),
        # Errors on an empty operand.
        ("maximum of (1;2) whose (it > 5)", "aggregate-of-plural"),
        ("unique value of (1;2) whose (it > 5)", "aggregate-of-plural"),
        # Refused before it runs.
        ('1 + "a"', "type-error"),
        ("name of", "parse-error"),
        # Plural spelling answers empty where the singular errors.
        ('names of files of folder "/nonexistent"', "singular-lookup"),
        # The checker's own runtime risk, outside any guard.
        ("name of wmi", "runtime-risk"),
    ],
)
def test_error_risk(text: str, rule: str) -> None:
    verdict = batchability(text)

    assert verdict.kind is ERROR_RISK
    assert rule in rules(text)


def test_an_inspector_the_platform_lacks_is_an_error_risk_even_after_false_and() -> None:
    """qna: `false and exists wmi` -> The operator "wmi" is not defined."""
    for text in ("exists wmi", "false and exists wmi"):
        verdict = batchability(text, platform="rhel")
        assert verdict.kind is ERROR_RISK, text
        assert "not-on-platform" in rules(text, platform="rhel")


def test_an_untaken_if_branch_may_use_an_inspector_the_platform_lacks() -> None:
    """qna on Linux: `if false then exists wmi else false` -> False."""
    text = 'if windows of operating system then exists wmi "root/cimv2" else false'

    assert batchability(text, platform="rhel").safe


def test_without_a_platform_no_inspector_is_ruled_out() -> None:
    assert batchability("exists wmi").safe


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        ('names of files of folders "/tmp"', "plural-result"),
        ("(1;2;3)", "plural-result"),
        # Singular, but the filter can leave nothing: qna errors or answers empty.
        ("(it) whose (it > 5) of 2", "whose-may-be-empty"),
    ],
)
def test_plural_risk(text: str, rule: str) -> None:
    assert batchability(text).kind is PLURAL_RISK
    assert rule in rules(text)


@pytest.mark.parametrize(
    "text",
    [
        "now",  # Sat, 31 Oct 2026 23:25:11 -0400
        '(1, "a")',  # a tuple inside a tuple is wrapped: ( 1, a )
        '"a, b"',
        '"(a)"',
        '"x" & "%2c y"',  # the escape is a comma too
        'if true then "a,b" else "c"',
    ],
)
def test_split_risk(text: str) -> None:
    verdict = batchability(text)

    assert verdict.kind is SPLIT_RISK, verdict.reasons
    assert "comma-in-display" in rules(text)


def test_an_unknown_inspector_is_unknown() -> None:
    verdict = batchability("bfrcr nonexistent inspector")

    assert verdict.kind is UNKNOWN
    assert "unknown-reference" in rules("bfrcr nonexistent inspector")


def test_the_worst_kind_wins() -> None:
    """Plural and erroring: the error is what decides."""
    assert batchability('names of files of folder "/nonexistent"').kind is ERROR_RISK


def test_reasons_point_at_the_node() -> None:
    text = 'size of file "/nonexistent"'

    (lookup,) = (r for r in batchability(text).reasons if r.rule == "singular-lookup")

    assert lookup.span is not None
    assert text[lookup.span.start : lookup.span.end] == 'file "/nonexistent"'
    assert lookup.kind is ERROR_RISK


def test_to_dict() -> None:
    payload = batchability('size of file "/nonexistent"').to_dict()

    assert payload["kind"] == "error-risk"
    assert payload["plurality"] == "singular"
    assert {"rule", "kind", "start", "end", "detail"} <= set(payload["reasons"][0])


# ---------------------------------------------------------------------------
# The analyzer's own surface, beyond the ported rule tests
# ---------------------------------------------------------------------------


def test_kinds_are_kebab_case_like_every_other_value_the_analyzer_serializes() -> None:
    assert [kind.value for kind in BatchabilityKind] == [
        "safe",
        "error-risk",
        "unknown",
        "plural-risk",
        "split-risk",
    ]


def test_a_safe_verdict_serializes_with_no_reasons() -> None:
    assert batchability("true").to_dict() == {
        "kind": "safe",
        "plurality": "singular",
        "reasons": [],
    }


def test_a_reason_serializes_its_span_as_flat_offsets_like_a_lint_span() -> None:
    lookup = BatchReason("singular-lookup", analyze_relevance('file "x"').node.span, "file")  # type: ignore[union-attr]
    whole = BatchReason("parse-error", None, "no parse")

    assert lookup.to_dict() == {
        "rule": "singular-lookup",
        "kind": "error-risk",
        "start": 0,
        "end": 8,
        "detail": "file",
    }
    assert (whole.to_dict()["start"], whole.to_dict()["end"]) == (None, None)


def test_the_rule_table_is_read_only_and_never_says_safe() -> None:
    """Exported at the root like `COST_RULES`, under its own name: the root's
    `RULES` is lint's (the two share `parse-error`, meaning the same thing).
    Read-only, as `RULES` and `DIAGNOSTICS` are, since every
    `BatchReason.kind` reads it."""
    assert BatchabilityKind.SAFE not in set(BATCH_RULES.values())
    assert BATCH_RULES.keys() != RULES.keys()
    with pytest.raises(TypeError):
        BATCH_RULES["comma-in-display"] = SAFE  # type: ignore[index]


def test_an_unknown_platform_is_refused_rather_than_ruling_out_every_inspector() -> None:
    """A misspelt platform would make every inspector look missing, and every
    statement an error risk, without a word: refuse it instead."""
    with pytest.raises(ValueError, match="mac os x"):
        batchability("true", platform="mac os x")


@pytest.mark.parametrize("platform", ["windows", "macos", "rhel", "ubuntu", "debian"])
def test_every_client_platform_is_accepted(platform: str) -> None:
    assert batchability("true", platform=platform).safe


@pytest.mark.parametrize(
    "text", ["number of bes computers", "exists bes computers", "names of bes computers"]
)
@pytest.mark.parametrize("platform", [None, "windows"])
def test_a_session_inspector_is_an_error_risk_with_or_without_a_platform(
    text: str, platform: str | None
) -> None:
    """Read as client relevance always: a ClientQuery tuple only ever carries
    client relevance, where a session inspector is not defined. The name is
    known, so it is no `unknown-reference`, and under `number of` / `exists`
    the plurality is fine: before this rule, those two came back safe."""
    verdict = batchability(text, platform=platform)

    assert verdict.kind is ERROR_RISK
    assert "not-client-relevance" in rules(text, platform)
    assert "not-on-platform" not in rules(text, platform)


@pytest.mark.parametrize(
    "text",
    [
        # qna: E: The operator "bes computers" is not defined. -- no condition
        # makes a session inspector defined, so a branch is no escape.
        "if true then number of bes computers else 0",
        "if windows of operating system then exists bes computers else false",
        "exists bes computers | false",
        "exists true whose (exists bes computers)",
    ],
)
def test_a_session_inspector_is_flagged_inside_a_branch_or_a_guard(text: str) -> None:
    assert "not-client-relevance" in rules(text)
    assert batchability(text).kind is ERROR_RISK


@pytest.mark.parametrize(
    "text",
    ["exists current date", "now", "current date", "exists true"],
)
def test_a_name_both_dialects_have_is_not_session_only(text: str) -> None:
    assert "not-client-relevance" not in rules(text)


@pytest.mark.parametrize(
    "text",
    # qna: E: The operator "size" is not defined. -- a property only, bare,
    # under `exists` / `number of` or not.
    ["exists size", "number of names", "exists versions", "size"],
)
def test_a_property_with_no_object_is_an_error_risk(text: str) -> None:
    assert "property-without-object" in rules(text)
    assert batchability(text).kind is ERROR_RISK


def test_a_platform_inspector_in_a_branch_taken_is_still_missed() -> None:
    """A known gap, pinned so changing it is a decision: the branch exemption
    is what lets `if windows of operating system then <windows inspector>`
    through, and statically a taken branch looks the same. qna on macOS:
    `if true then exists wmi else false` errors."""
    assert batchability("if true then exists wmi else false", platform="macos").safe


@pytest.mark.parametrize("text", ["", "   ", "1\u00b2", "(" * 2000, '"unterminated'])
def test_never_raises_for_bad_relevance(text: str) -> None:
    verdict = batchability(text)

    assert isinstance(verdict, Batchability)
    assert not verdict.safe


def test_a_deep_or_chain_is_walked_without_recursion() -> None:
    text = " or ".join(["true"] * 3000)

    assert batchability(text).safe
