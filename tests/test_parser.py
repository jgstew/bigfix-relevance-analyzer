"""Unit tests for the relevance Pratt parser.

These pin the parser's *contract*: error positions, the `parse` /
`try_parse` split, and span invariants. The grammar itself -- which tree a
given statement produces -- lives in ``tests/corpus/*.rlvcorpus`` and is
exercised by ``test_parser_corpus.py``; a shape pinned there should not be
re-pinned here.
"""

from __future__ import annotations

import pytest

from bigfix_relevance_analyzer.nodes import It, NumberLiteral, StringLiteral, to_sexpr
from bigfix_relevance_analyzer.parser import ParseError, parse, try_parse

# ---------------------------------------------------------------------------
# Literals and the trivial operands
# ---------------------------------------------------------------------------


def test_a_number_parses_to_a_number_literal_with_verbatim_text() -> None:
    node = parse("42")
    assert isinstance(node, NumberLiteral)
    assert node.text == "42"


def test_a_decimal_number_keeps_its_text_undamaged() -> None:
    node = parse("1.5")
    assert isinstance(node, NumberLiteral)
    assert node.text == "1.5"


def test_a_string_literal_keeps_its_quotes_and_escapes() -> None:
    node = parse('"a%22b"')
    assert isinstance(node, StringLiteral)
    assert node.text == '"a%22b"'


def test_it_parses_to_the_it_node_case_insensitively() -> None:
    assert isinstance(parse("it"), It)
    assert isinstance(parse("It"), It)
    assert isinstance(parse("IT"), It)


# ---------------------------------------------------------------------------
# Spans
# ---------------------------------------------------------------------------


def test_a_literal_span_covers_exactly_its_token() -> None:
    node = parse("42")
    assert (node.span.start, node.span.end) == (0, 2)
    assert (node.span.line, node.span.column) == (1, 1)


def test_parentheses_widen_the_span_of_the_inner_node() -> None:
    """The root span must cover the whole statement, grouping included."""
    node = parse("( 42 )")
    assert isinstance(node, NumberLiteral)
    assert (node.span.start, node.span.end) == (0, 6)


def test_leading_whitespace_is_not_part_of_any_span() -> None:
    node = parse("  42")
    assert (node.span.start, node.span.end) == (2, 4)
    assert node.span.column == 3


# ---------------------------------------------------------------------------
# Errors: every failure is a ParseError pointing at a position
# ---------------------------------------------------------------------------


def test_blank_input_is_a_parse_error() -> None:
    with pytest.raises(ParseError, match="empty"):
        parse("")
    with pytest.raises(ParseError, match="empty"):
        parse("   ")


def test_a_comment_alone_is_still_empty_input() -> None:
    with pytest.raises(ParseError, match="empty"):
        parse("/* nothing here */")


def test_an_unterminated_string_reports_its_position() -> None:
    with pytest.raises(ParseError, match="unterminated string") as info:
        parse('("abc')
    assert info.value.offset == 1
    assert info.value.line == 1
    assert info.value.column == 2


def test_an_unterminated_comment_reports_its_position() -> None:
    with pytest.raises(ParseError, match="unterminated comment"):
        parse("1 /* abc")


def test_trailing_input_after_a_complete_expression_is_an_error() -> None:
    with pytest.raises(ParseError, match="unexpected") as info:
        parse("1 2")
    assert info.value.offset == 2


def test_an_unclosed_paren_is_an_error() -> None:
    with pytest.raises(ParseError, match=r"\)"):
        parse("(1")


def test_empty_parens_are_an_error() -> None:
    with pytest.raises(ParseError, match="expected"):
        parse("()")


def test_a_lone_operator_is_an_error() -> None:
    with pytest.raises(ParseError, match="expected"):
        parse("+")


def test_parse_error_str_names_line_and_column() -> None:
    with pytest.raises(ParseError) as info:
        parse("(\n(1")
    message = str(info.value)
    assert "line 2" in message
    assert "column" in message


def test_parse_error_is_a_value_error() -> None:
    """Downstream code that catches ValueError keeps working."""
    with pytest.raises(ValueError, match="empty"):
        parse("")


# ---------------------------------------------------------------------------
# try_parse: the conservative interface
# ---------------------------------------------------------------------------


def test_try_parse_wraps_a_success() -> None:
    result = try_parse("42")
    assert result.ok
    assert result.error is None
    assert isinstance(result.node, NumberLiteral)


def test_try_parse_wraps_a_failure_instead_of_raising() -> None:
    result = try_parse("(1")
    assert not result.ok
    assert result.node is None
    assert isinstance(result.error, ParseError)


# ---------------------------------------------------------------------------
# S-expression serialization basics
# ---------------------------------------------------------------------------


def test_to_sexpr_of_literals() -> None:
    assert to_sexpr(parse("42")) == '(num "42")'
    assert to_sexpr(parse('"a"')) == '(str "a")'
    assert to_sexpr(parse("it")) == "it"


def test_to_sexpr_escapes_quotes_and_backslashes_in_strings() -> None:
    assert to_sexpr(parse('"C:\\x"')) == '(str "C:\\\\x")'
    assert to_sexpr(parse('"a%22b"')) == '(str "a%22b")'
