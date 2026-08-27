"""A lexer for BigFix Relevance: text in, a lossless stream of tokens out.

This is the front end of the future relevance parser, and the layer
:mod:`bigfix_relevance_analyzer.complexity` counts against so that metrics come
from real tokens rather than regexes over raw text.

What this module deliberately does not do
-----------------------------------------
It does **not** resolve multi-word inspector names. ``names of processes`` comes
out as three ``WORD`` tokens, not one name; deciding where a name begins and
ends is the parser's job, using the tables in
:mod:`bigfix_relevance_analyzer.inspectors`.

That split matters. Relevance has no reserved words, so ``of``, ``whose`` and
``and`` are ordinary words that also appear *inside* inspector names -- there is
a real inspector called ``day of month``. Binding those phrases needs the name
table, and the name table is a snapshot: it covers the platforms and versions
someone happened to dump, so a tokenizer keyed on it would lex the same text
differently as dumps are added, and would lex relevance for an unsampled
platform wrong. Worse, longest-match is not even the right answer -- whether
``day of month of now`` groups as ``(day of month) of now`` depends on operand
types, which is type-directed disambiguation and squarely parser work. Keeping
this layer table-free makes it total: any input lexes, and the same input always
lexes the same way.

Guarantees
----------
**Roundtrip.** ``"".join(t.text for t in tokenize(s)) == s`` for every input,
valid or not. Whitespace and comments are emitted as trivia tokens rather than
skipped, which is what makes a future formatter or auto-fixer possible.

**No exceptions.** Malformed input yields :attr:`TokenKind.ERROR` tokens instead
of raising. This library runs over relevance extracted from real content, which
is regularly truncated or broken; a scorer must still produce a number for it.
A parser is free to treat any ``ERROR`` token as fatal -- that is a policy
decision for the layer that has one.

Relationship to :mod:`bigfix_relevance_analyzer.dialect`
--------------------------------------------------------
``dialect._strip_non_code`` makes the same lexical judgements about string
literals and ``/* */`` comments, in one cheap regex pass. The duplication is
deliberate: dialect classification runs on every extracted site and only needs
to blank out non-code, so paying for a full token stream there would be waste.
The two must agree, though -- if ``/* */`` ever turns out to nest, or a new
escape form appears, both change together.
"""

from __future__ import annotations

import enum
import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass

__all__ = [
    "GRAMMAR_WORDS",
    "PUNCTUATION",
    "Token",
    "TokenKind",
    "code_tokens",
    "tokenize",
]

logger = logging.getLogger(__name__)


class TokenKind(enum.Enum):
    """What a token is, lexically -- never what it means."""

    WORD = "word"
    """A bare word: part of an inspector name, a grammar word, a type name."""

    NUMBER = "number"
    """A numeric literal, integer or decimal."""

    STRING = "string"
    """A double-quoted literal, quotes included."""

    PUNCT = "punct"
    """An operator or separator; see :data:`PUNCTUATION`."""

    COMMENT = "comment"
    """A ``/* */`` comment. Trivia."""

    WHITESPACE = "whitespace"
    """A run of whitespace. Trivia."""

    ERROR = "error"
    """Text no rule accepts: a stray character, or an unterminated construct."""


@dataclass(frozen=True, slots=True)
class Token:
    """One lexeme, carrying enough position to point a diagnostic at it."""

    kind: TokenKind
    text: str
    """The verbatim slice of the input, so the stream can be rejoined."""

    offset: int
    """0-based character offset of the token's first character."""

    line: int
    """1-based line of the token's first character."""

    column: int
    """1-based column of the token's first character."""

    @property
    def normalized(self) -> str:
        """Case-folded text for words; the text itself for everything else.

        Relevance is case-insensitive in its grammar but not inside string
        literals, so only :attr:`TokenKind.WORD` folds.
        """
        return self.text.lower() if self.kind is TokenKind.WORD else self.text

    def is_trivia(self) -> bool:
        """Whether this token carries no meaning: whitespace or a comment."""
        return self.kind is TokenKind.COMMENT or self.kind is TokenKind.WHITESPACE


# ---------------------------------------------------------------------------
# Lexical tables
# ---------------------------------------------------------------------------

# Longest first, so `!=` is never lexed as `!` followed by `=`.
#
# `%` is absent on purpose: the modulo operator is spelled `mod` in source and
# only reported as `%` by the engine's own introspection, so a `%` outside a
# string literal is not something relevance writes. `|` is the error-fallback
# operator. `>`, `>=` and `!=` are sugar the engine canonicalizes away, but they
# are written in real relevance and so must lex.
PUNCTUATION: tuple[str, ...] = (
    "!=",
    "<=",
    ">=",
    "(",
    ")",
    ",",
    ";",
    "|",
    "&",
    "+",
    "-",
    "*",
    "/",
    "=",
    "<",
    ">",
)

# Words that carry grammatical structure. This is a *heuristic* set for
# consumers that want to tell scaffolding from names -- it is not a keyword
# list, because relevance has none: every word here is also legal inside an
# inspector name, and `day of month` proves it.
GRAMMAR_WORDS: frozenset[str] = frozenset(
    {
        "and",
        "as",
        "else",
        "exist",
        "exists",
        "if",
        "it",
        "item",
        "items",
        "mod",
        "not",
        "of",
        "or",
        "then",
        "whose",
    }
)

# Characters that can never appear in a word: whitespace, the string delimiter,
# every punctuation character, and `!`, which only ever participates in `!=`.
_NOT_WORD_CHARS = frozenset('"!') | {char for lexeme in PUNCTUATION for char in lexeme}

_WHITESPACE_RE = re.compile(r"\s+")
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
# The complement approach: a word is any run of characters nothing else claims,
# so underscores, dots and non-ASCII letters stay inside one token instead of
# fragmenting into errors.
_WORD_RE = re.compile(rf"[^\s{re.escape(''.join(sorted(_NOT_WORD_CHARS)))}]+")


def _scan(text: str, at: int) -> tuple[TokenKind, int]:
    """Lex one token starting at ``at``; return its kind and end offset.

    Always advances: the final fallback consumes a single character as an
    error, so the caller's loop cannot stall.
    """
    char = text[at]

    if char.isspace():
        return TokenKind.WHITESPACE, _WHITESPACE_RE.match(text, at).end()  # type: ignore[union-attr]

    if text.startswith("/*", at):
        # Non-nesting, matching `dialect._NOT_CODE_RE`: the comment ends at the
        # first `*/`, and a `"` inside it opens nothing.
        end = text.find("*/", at + 2)
        return (TokenKind.COMMENT, end + 2) if end != -1 else (TokenKind.ERROR, len(text))

    if char == '"':
        # A literal cannot contain a raw quote -- one is written `%22` inside
        # the string rather than backslashed -- so pairing quotes off left to
        # right is exact, and a backslash escapes nothing.
        end = text.find('"', at + 1)
        return (TokenKind.STRING, end + 1) if end != -1 else (TokenKind.ERROR, len(text))

    if char.isdigit():
        return TokenKind.NUMBER, _NUMBER_RE.match(text, at).end()  # type: ignore[union-attr]

    for lexeme in PUNCTUATION:
        if text.startswith(lexeme, at):
            return TokenKind.PUNCT, at + len(lexeme)

    if word := _WORD_RE.match(text, at):
        return TokenKind.WORD, word.end()

    return TokenKind.ERROR, at + 1


def tokenize(text: str) -> Iterator[Token]:
    """Lex ``text``, yielding every token including whitespace and comments.

    Never raises: anything unlexable becomes a :attr:`TokenKind.ERROR` token.
    An unterminated string or comment takes the rest of the input with it, since
    none of what follows is code that would evaluate.
    """
    at = 0
    line = 1
    line_start = 0
    length = len(text)

    while at < length:
        kind, end = _scan(text, at)
        lexeme = text[at:end]
        yield Token(kind=kind, text=lexeme, offset=at, line=line, column=at - line_start + 1)

        if kind is TokenKind.ERROR:
            logger.debug("unlexable input at offset %d: %r", at, lexeme[:40])

        newlines = lexeme.count("\n")
        if newlines:
            line += newlines
            line_start = at + lexeme.rindex("\n") + 1
        at = end


def code_tokens(text: str) -> Iterator[Token]:
    """Lex ``text``, yielding only tokens that carry meaning.

    Trivia is dropped; error tokens are kept, because a consumer that ignores
    them silently would report on relevance it never actually read.
    """
    return (token for token in tokenize(text) if not token.is_trivia())
