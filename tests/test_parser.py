"""Unit tests for the relevance Pratt parser.

These pin the parser's *contract*: error positions, the `parse` /
`try_parse` split, and span invariants. The grammar itself -- which tree a
given statement produces -- lives in ``tests/corpus/*.rlvcorpus`` and is
exercised by ``test_parser_corpus.py``; a shape pinned there should not be
re-pinned here.
"""

from __future__ import annotations

import pytest

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.nodes import (
    MAX_INTEGER,
    Bar,
    It,
    ItemOf,
    NumberKind,
    NumberLiteral,
    NumberOf,
    Of,
    StringLiteral,
    Unary,
    to_sexpr,
)
from bigfix_relevance_analyzer.parser import (
    MAX_PARSE_DEPTH,
    ParseError,
    parse,
    try_parse,
)

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


# ---------------------------------------------------------------------------
# Nesting depth
# ---------------------------------------------------------------------------

# Every way of nesting an expression. Each builder takes a depth and returns
# source nested exactly that deep -- the point being that all of them route
# through `parse_expression`, so one guard covers the lot.
NESTING = {
    "of": lambda n: "it" + " of x" * n,
    "parens": lambda n: "(" * n + "1" + ")" * n,
    "not": lambda n: "not " * n + "true",
    "unary-minus": lambda n: "-" * n + "1",
    "whose": lambda n: "x whose (" * n + "y" + ")" * n,
    "if": lambda n: "if " * n + "c" + " then t else e" * n,
    "index": lambda n: "key (" * n + "1" + ")" * n,
}


@pytest.mark.parametrize("construct", sorted(NESTING))
def test_nesting_too_deep_is_a_parse_error_not_a_recursion_error(construct: str) -> None:
    """Parsing recurses, so deep enough input exhausts the Python stack.

    Unguarded that surfaces as `RecursionError`, which is not a `ParseError`
    and so escapes `try_parse` -- breaking the one promise that interface
    makes. Content extracted from the wild is regularly truncated or hostile,
    which is exactly how a caller would meet this.
    """
    source = NESTING[construct](MAX_PARSE_DEPTH * 4)
    result = try_parse(source)
    assert not result.ok
    assert result.error is not None
    assert "maximum depth" in result.error.message


@pytest.mark.parametrize("construct", sorted(NESTING))
def test_nesting_just_within_the_limit_still_parses(construct: str) -> None:
    """The guard must not fire early: the limit is a real limit, not a target."""
    parse(NESTING[construct](MAX_PARSE_DEPTH - 1))


def test_the_depth_message_is_the_engines_own_wording() -> None:
    """BigFix has a string for this, so use it rather than inventing one.

    The number is ours -- this parser gives up sooner than the engine does --
    but it is interpolated, so the message stays honest about which limit was
    hit.
    """
    error = try_parse("it" + " of x" * (MAX_PARSE_DEPTH * 2)).error
    assert error is not None
    assert error.message == f"Expression tree is too large (maximum depth {MAX_PARSE_DEPTH})"


def test_the_depth_error_is_positioned_like_any_other() -> None:
    error = try_parse("(" * 500 + "1" + ")" * 500).error
    assert error is not None
    assert error.line == 1
    assert error.column == MAX_PARSE_DEPTH + 1


def test_a_wide_expression_is_not_a_deep_one() -> None:
    """Left-associative chains iterate rather than recurse, and a flat chain of
    `whose` is not nesting either. Neither should be refused."""
    parse("1" + " + 1" * 5000)
    parse("x" + " whose (y)" * 5000)


def test_the_deepest_accepted_tree_survives_its_recursive_consumers() -> None:
    """`to_sexpr` recurses too, so the parser's limit has to leave it room."""
    assert to_sexpr(parse(NESTING["of"](MAX_PARSE_DEPTH - 1))).count("(of ") == MAX_PARSE_DEPTH - 1


# ---------------------------------------------------------------------------
# Numeral classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("0", NumberKind.INTEGER),
        ("42", NumberKind.INTEGER),
        (str(MAX_INTEGER), NumberKind.INTEGER),
        (str(MAX_INTEGER + 1), NumberKind.LARGE_INTEGER),
        ("99999999999999999999999", NumberKind.LARGE_INTEGER),
        ("1.5", NumberKind.NOT_AN_INTEGER),
        ("0.0", NumberKind.NOT_AN_INTEGER),
    ],
)
def test_numerals_are_classified_by_magnitude(source: str, expected: NumberKind) -> None:
    """The engine settles a numeral's type while parsing, with three separate
    node classes. Here it is one node and a derived classification, which keeps
    the literal verbatim and needs no type information either way."""
    node = parse(source)
    assert isinstance(node, NumberLiteral)
    assert node.kind is expected


def test_a_negative_literal_is_a_unary_operator_over_a_positive_one() -> None:
    """So classification never has to consider a sign."""
    node = parse("-1")
    assert isinstance(node, Unary)
    assert isinstance(node.operand, NumberLiteral)
    assert node.operand.kind is NumberKind.INTEGER


def test_classification_does_not_disturb_the_serialized_form() -> None:
    """Deliberate: the corpus stays stable and the literal stays lossless."""
    assert to_sexpr(parse("99999999999999999999999")) == '(num "99999999999999999999999")'


# ---------------------------------------------------------------------------
# The specialised `of` forms
# ---------------------------------------------------------------------------


def test_number_of_is_aggregation() -> None:
    node = parse("number of processors")
    assert isinstance(node, NumberOf)


def test_number_is_not_an_inspector_so_the_specialisation_is_unambiguous() -> None:
    """`number of x` can only be aggregation: the table defines no such
    property, which is what lets the parser decide this without types."""
    assert inspectors.lookup("number") == ()


def test_an_integer_index_makes_a_tuple_subscript() -> None:
    node = parse("item 0 of (1, 2)")
    assert isinstance(node, ItemOf)
    assert node.index.text == "0"


def test_a_string_index_stays_a_property_because_item_really_is_one() -> None:
    """`item <string> of <folder>` is a real inspector, so a string index
    cannot be read as a tuple subscript without knowing the object's type --
    which this parser does not consult. Positive evidence only."""
    assert [entry.signature for entry in inspectors.lookup("item")] != []
    assert isinstance(parse('item "foo" of folder "c"'), Of)


def test_an_indexed_number_is_not_aggregation() -> None:
    assert isinstance(parse('number "x" of y'), Of)


def test_bar_is_its_own_node_not_a_binary_operator() -> None:
    """`|` is error fallback: the right side is used only when the left errors,
    and the engine's binary-operator table has no row for it."""
    node = parse('size of file "c:\\nope" | 42')
    assert isinstance(node, Bar)
    assert not any(
        entry.name == "|" or entry.symbol == "|" for entry in inspectors.binary_operators()
    )


def test_the_specialised_forms_keep_the_span_of_the_whole_expression() -> None:
    for source in ("number of processors", "item 0 of (1, 2)", "1 | 2"):
        node = parse(source)
        assert (node.span.start, node.span.end) == (0, len(source)), source
