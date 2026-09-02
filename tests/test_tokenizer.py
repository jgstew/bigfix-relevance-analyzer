"""Unit and corpus tests for the relevance tokenizer.

The load-bearing property is **roundtrip**: joining every token's text must
reproduce the input exactly, for valid and invalid input alike. Everything else
here pins a specific lexical decision so it cannot drift silently.
"""

from __future__ import annotations

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.tokenizer import (
    GRAMMAR_WORDS,
    Token,
    TokenKind,
    code_tokens,
    tokenize,
)

WORD = TokenKind.WORD
NUMBER = TokenKind.NUMBER
STRING = TokenKind.STRING
PUNCT = TokenKind.PUNCT
COMMENT = TokenKind.COMMENT
WHITESPACE = TokenKind.WHITESPACE
ERROR = TokenKind.ERROR


def kinds_and_texts(text: str) -> list[tuple[TokenKind, str]]:
    return [(token.kind, token.text) for token in tokenize(text)]


def code(text: str) -> list[tuple[TokenKind, str]]:
    return [(token.kind, token.text) for token in code_tokens(text)]


# ---------------------------------------------------------------------------
# The roundtrip invariant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "exists file",
        'name of it = "abc"',
        "/* unterminated",
        '"unterminated',
        "!",
        "\n\n\t",
        # Non-ASCII is written as escapes throughout this file rather than as
        # literal characters: the `fix-files-to-ascii` pre-commit hook
        # transliterates non-ASCII source characters, which would silently
        # rewrite these into ASCII cases that no longer test anything. The
        # data avoids dictionary-adjacent words for the same reason: the
        # `typos` hook rewrites those too.
        "a\u00e9b",
        '"a\u00e9b"',
    ],
)
def test_roundtrip(text: str) -> None:
    """Joining token texts must reproduce the input, valid or not."""
    assert "".join(token.text for token in tokenize(text)) == text


def test_empty_input_yields_no_tokens() -> None:
    assert list(tokenize("")) == []


# ---------------------------------------------------------------------------
# Token kinds
# ---------------------------------------------------------------------------


def test_words_numbers_and_punctuation() -> None:
    assert code("exists file 42") == [(WORD, "exists"), (WORD, "file"), (NUMBER, "42")]


def test_whitespace_is_trivia_but_still_emitted() -> None:
    assert kinds_and_texts("a b") == [(WORD, "a"), (WHITESPACE, " "), (WORD, "b")]
    assert [token.is_trivia() for token in tokenize("a b")] == [False, True, False]


def test_underscored_words_lex_as_one_word() -> None:
    assert code("binary_string") == [(WORD, "binary_string")]


def test_non_ascii_lexes_as_a_word_not_an_error() -> None:
    """Escapes, not literals -- see the note in `test_roundtrip`."""
    assert code("a\u00e9b") == [(WORD, "a\u00e9b")]
    assert code("\u65e5\u672c") == [(WORD, "\u65e5\u672c")]
    assert code('"a\u00e9b"') == [(STRING, '"a\u00e9b"')]


def test_decimal_point_is_not_part_of_a_number() -> None:
    """Relevance has no decimal-point numeral syntax -- confirmed live on both
    engines, `1.5` draws the identical lexical complaint a stray `#` would.
    `.` lexes as its own ERROR token rather than joining either digit run."""
    assert code("1.5") == [(NUMBER, "1"), (ERROR, "."), (NUMBER, "5")]


def test_hex_looking_text_is_not_a_hex_literal() -> None:
    """Relevance has no hex literals; `0x1F` is a number then a word."""
    assert code("0x1F") == [(NUMBER, "0"), (WORD, "x1F")]


def test_trailing_dot_is_its_own_error_token() -> None:
    """A `.` with no digit after it is still not part of anything else --
    not the number to its left, and not swept into a word."""
    assert code("1.") == [(NUMBER, "1"), (ERROR, ".")]


# ---------------------------------------------------------------------------
# Strings: %xx escapes, no backslashes, no raw quotes inside
# ---------------------------------------------------------------------------


def test_string_literal_includes_its_quotes() -> None:
    assert code('"abc"') == [(STRING, '"abc"')]


def test_percent_escapes_are_inert_to_the_lexer() -> None:
    """`%22` is an escaped quote to the engine but plain text to the lexer."""
    assert code('"a%22b%0ac"') == [(STRING, '"a%22b%0ac"')]


def test_adjacent_string_literals_are_two_tokens() -> None:
    assert code('"a""b"') == [(STRING, '"a"'), (STRING, '"b"')]


def test_backslash_does_not_escape_a_quote() -> None:
    """Relevance has no backslash escapes: the literal ends at the quote."""
    assert code('"a\\" & "b"') == [(STRING, '"a\\"'), (PUNCT, "&"), (STRING, '"b"')]


def test_unterminated_string_takes_the_rest_of_the_input() -> None:
    assert code('exists "abc') == [(WORD, "exists"), (ERROR, '"abc')]


def test_string_may_span_lines() -> None:
    tokens = list(code_tokens('"a\nb" c'))
    assert tokens[0].kind is STRING
    assert tokens[1].line == 2


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


def test_comment_is_trivia() -> None:
    assert kinds_and_texts("/* hi */") == [(COMMENT, "/* hi */")]
    assert code("/* hi */") == []


def test_comments_do_not_nest() -> None:
    """A comment ends at the first `*/`, matching `dialect._NOT_CODE_RE`."""
    assert kinds_and_texts("/* a /* b */ c") == [
        (COMMENT, "/* a /* b */"),
        (WHITESPACE, " "),
        (WORD, "c"),
    ]


def test_unterminated_comment_takes_the_rest_of_the_input() -> None:
    assert code("exists /* abc") == [(WORD, "exists"), (ERROR, "/* abc")]


def test_a_quote_inside_a_comment_opens_nothing() -> None:
    assert kinds_and_texts('/* " */ x') == [
        (COMMENT, '/* " */'),
        (WHITESPACE, " "),
        (WORD, "x"),
    ]


def test_a_comment_opener_inside_a_string_opens_nothing() -> None:
    assert code('"/*" x') == [(STRING, '"/*"'), (WORD, "x")]


def test_slash_alone_is_division_not_a_comment() -> None:
    assert code("4 / 2") == [(NUMBER, "4"), (PUNCT, "/"), (NUMBER, "2")]


# ---------------------------------------------------------------------------
# Punctuation and maximal munch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("operator", ["!=", "<=", ">="])
def test_two_character_operators_win_over_one(operator: str) -> None:
    assert code(f"a {operator} b") == [(WORD, "a"), (PUNCT, operator), (WORD, "b")]


@pytest.mark.parametrize("operator", ["(", ")", ",", ";", "&", "+", "-", "*", "/", "=", "<", ">"])
def test_single_character_punctuation(operator: str) -> None:
    assert code(operator) == [(PUNCT, operator)]


def test_pipe_lexes_as_punctuation() -> None:
    """`|` is the error-fallback operator and appears in real relevance."""
    assert code("a | b") == [(WORD, "a"), (PUNCT, "|"), (WORD, "b")]


def test_lone_bang_is_an_error_token() -> None:
    assert code("a ! b") == [(WORD, "a"), (ERROR, "!"), (WORD, "b")]


def test_error_token_does_not_swallow_the_rest() -> None:
    """Only unterminated strings and comments consume to end of input."""
    assert [token.kind for token in code_tokens("! !")] == [ERROR, ERROR]


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


def test_offsets_line_and_column() -> None:
    tokens = list(code_tokens("ab\n  cd"))
    assert [(t.text, t.offset, t.line, t.column) for t in tokens] == [
        ("ab", 0, 1, 1),
        ("cd", 5, 2, 3),
    ]


def test_line_advances_through_a_multiline_comment() -> None:
    tokens = list(code_tokens("/* a\nb */ x"))
    assert (tokens[0].text, tokens[0].line, tokens[0].column) == ("x", 2, 6)


# ---------------------------------------------------------------------------
# Normalization and grammar words
# ---------------------------------------------------------------------------


def test_words_normalize_to_lowercase() -> None:
    token = next(iter(code_tokens("Exists")))
    assert (token.text, token.normalized) == ("Exists", "exists")


def test_non_words_normalize_to_their_text() -> None:
    token = next(iter(code_tokens('"ABC"')))
    assert token.normalized == '"ABC"'


def test_grammar_words_are_lowercase_and_include_the_structural_keywords() -> None:
    assert {"of", "whose", "it", "and", "or", "not", "exists"} <= GRAMMAR_WORDS
    assert all(word == word.lower() for word in GRAMMAR_WORDS)


def test_token_is_frozen() -> None:
    token = Token(kind=WORD, text="a", offset=0, line=1, column=1)
    with pytest.raises((AttributeError, TypeError)):
        token.text = "b"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# A realistic statement
# ---------------------------------------------------------------------------


def test_a_realistic_statement() -> None:
    statement = 'exists files whose (name of it starts with "bes") of folder "/tmp"'
    assert code(statement) == [
        (WORD, "exists"),
        (WORD, "files"),
        (WORD, "whose"),
        (PUNCT, "("),
        (WORD, "name"),
        (WORD, "of"),
        (WORD, "it"),
        (WORD, "starts"),
        (WORD, "with"),
        (STRING, '"bes"'),
        (PUNCT, ")"),
        (WORD, "of"),
        (WORD, "folder"),
        (STRING, '"/tmp"'),
    ]


# ---------------------------------------------------------------------------
# Corpus: every real relevance string the extractor finds must lex cleanly
# ---------------------------------------------------------------------------


def corpus_sites() -> list[tuple[str, str]]:
    """Every extracted relevance statement in the example corpus."""
    return [
        (f"{path.name}:{site.line}", site.text)
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
    ]


def test_the_corpus_yields_relevance_to_tokenize() -> None:
    assert len(corpus_sites()) > 20


def test_corpus_roundtrips() -> None:
    for label, text in corpus_sites():
        assert "".join(token.text for token in tokenize(text)) == text, label


def test_corpus_has_no_error_tokens() -> None:
    """Known-good relevance must lex without a single error token."""
    offenders = [
        (label, token.text)
        for label, text in corpus_sites()
        for token in tokenize(text)
        if token.kind is ERROR
    ]
    assert offenders == []


def test_tokenizing_the_corpus_is_silent(capsys: pytest.CaptureFixture[str]) -> None:
    """Nothing may reach stdout/stderr: the package must be safe in a stdio server."""
    for _label, text in corpus_sites():
        list(tokenize(text))
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
