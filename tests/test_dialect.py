"""Content-based dialect classification: what it types, and what it must not."""

from __future__ import annotations

import pytest

from bigfix_relevance_analyzer.dialect import Dialect, classify_relevance_dialect, is_definite


@pytest.mark.parametrize(
    "text",
    [
        "number of bes computers",
        "names of bes fixlets whose(relevant flag of it)",
        "elements of statistical bin",
        "in web reports context",
        "name of current console user",
        "(webui enabled) of current bes server",
        "number of statistic ranges of it",
    ],
)
def test_session_inspectors_type_a_statement_as_session(text: str) -> None:
    assert classify_relevance_dialect(text) is Dialect.SESSION


@pytest.mark.parametrize(
    "text",
    [
        "windows of operating system",
        (
            'unique values of strings "product-name" of dictionaries of service planes'
            " of iokit registries"
        ),
        "names of logged on users",
        "locked of action lock state",
        "number of filesystems whose(free space of it < 1024)",
        'exists key "HKLM\\Software\\Foo" of native registry',
    ],
)
def test_client_inspectors_type_a_statement_as_client(text: str) -> None:
    assert classify_relevance_dialect(text) is Dialect.CLIENT


@pytest.mark.parametrize(
    ("text", "why"),
    [
        ("", "nothing to go on"),
        ('version of client >= "11.0"', "shared inspectors only"),
        ('exists file "/etc/passwd"', "shared inspectors only"),
        # Trap 1: ClientUI dashboards use these in *client* relevance.
        ("number of relevant fixlets of sites", "ClientUI trap"),
        ("ids of relevant offer actions of sites", "ClientUI trap"),
        ('headers "Subject" of it of relevant fixlets of sites', "ClientUI trap"),
        ("ids of it of offer actions of sites", "ClientUI trap"),
        # Trap 2: the introspection meta-layer is identical in both dialects.
        ("names of types", "introspection meta-layer"),
        ("number of properties", "introspection meta-layer"),
        ('names of casts of type "string"', "introspection meta-layer"),
        ("number of binary operators", "introspection meta-layer"),
        # Trap 3: macOS clients define the projection/rate family.
        ("rate of linear projection of it", "macOS-only client inspectors"),
        ("extrapolation (now) of exponential projection of it", "macOS-only client inspectors"),
        # `bes license` and `bes product` are client inspectors too.
        ("number of bes licenses", "bes-prefix exception"),
        ("names of products of bes license", "bes-prefix exception"),
    ],
)
def test_ambiguous_statements_get_no_opinion(text: str, why: str) -> None:
    """``None`` is "no opinion", and every trap must produce it."""
    assert classify_relevance_dialect(text) is None, why


@pytest.mark.parametrize(
    "text",
    [
        'exists (it) whose (it as string contains "bes computers")',
        'name of it = "number of bes computers"',
        # An unterminated literal discards the rest rather than scanning it.
        'name of it = "bes computers',
    ],
)
def test_inspector_names_inside_string_literals_do_not_type_a_statement(text: str) -> None:
    assert classify_relevance_dialect(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "/* number of bes computers */ now",
        "now /* number of bes computers */",
        "/* count the\n   bes computers */ now",
        # A `"` inside a comment opens no literal, so the comment still closes.
        '/* say "hi" to bes computers */ now',
        # An unterminated comment discards the rest rather than scanning it.
        "now /* number of bes computers",
    ],
)
def test_inspector_names_inside_comments_do_not_type_a_statement(text: str) -> None:
    """Only text that evaluates can say what dialect a statement is in."""
    assert classify_relevance_dialect(text) is None


def test_a_comment_does_not_fabricate_a_contradiction() -> None:
    """A session name in a comment must not turn client relevance into UNCERTAIN."""
    text = "/* faster than counting bes computers */ windows of operating system"
    assert classify_relevance_dialect(text) is Dialect.CLIENT


def test_a_comment_marker_does_not_hide_a_real_one() -> None:
    """Stripping a comment must not swallow the code around it."""
    assert classify_relevance_dialect("number /* a comment */ of bes computers") is Dialect.SESSION


def test_a_comment_opener_inside_a_string_literal_is_just_text() -> None:
    """The literal wins when it opens first, so its `/*` starts no comment."""
    assert classify_relevance_dialect('windows of operating system AND it = "/*"') is Dialect.CLIENT


def test_a_marker_from_each_dialect_is_a_recorded_uncertain() -> None:
    """Both dialects' inspectors in one statement: it cannot be valid as either."""
    assert (
        classify_relevance_dialect("names of logged on users of bes computers") is Dialect.UNCERTAIN
    )


def test_markers_match_on_word_boundaries() -> None:
    """A marker embedded in a longer identifier is not a match."""
    assert classify_relevance_dialect("value of regapproval of it") is None
    assert classify_relevance_dialect("number of besuit of it") is None


def test_matching_ignores_case_and_extra_whitespace() -> None:
    assert classify_relevance_dialect("Number  of\n  BES\tComputers") is Dialect.SESSION


def test_classifier_never_claims_both() -> None:
    """Proving a statement valid in both dialects needs the future parser."""
    for text in ("number of bes computers", "windows of operating system", "names of types"):
        assert classify_relevance_dialect(text) is not Dialect.BOTH


@pytest.mark.parametrize(
    ("dialect", "expected"),
    [
        (Dialect.CLIENT, True),
        (Dialect.SESSION, True),
        (Dialect.UNCERTAIN, False),
        (Dialect.BOTH, False),
        (None, False),
    ],
)
def test_is_definite(dialect: Dialect | None, expected: bool) -> None:
    assert is_definite(dialect) is expected
