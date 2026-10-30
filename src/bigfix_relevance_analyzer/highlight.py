"""Parse-aware syntax highlighting: what each piece of a statement *is*.

:func:`highlight` takes a statement and returns :class:`HighlightSpan`\\ s, one
per meaningful token, for an editor to colour: a native text view with no
TextMate engine, or the language server's semantic tokens
(:mod:`bigfix_relevance_analyzer.lsp.server`).

Why the parse tree, not a word list
-----------------------------------
Relevance has no reserved words. ``starts`` is the plural ``start`` inspector
in ``starts of ranges`` and the first half of an operator in ``starts with
"a"``; ``it as lowercase`` casts to a type named like any inspector. A
regex-based grammar -- the generated TextMate one included -- cannot tell
these apart, so names are coloured here from what the parser built:

* a word inside a :class:`~bigfix_relevance_analyzer.nodes.Reference`, before
  its index, is a :attr:`~HighlightKind.PROPERTY`;
* the words after a :class:`~bigfix_relevance_analyzer.nodes.Cast`'s operand
  are ``as`` (a keyword) and then the :attr:`~HighlightKind.TYPE`;
* the words between a :class:`~bigfix_relevance_analyzer.nodes.Binary`'s
  operands are its :attr:`~HighlightKind.OPERATOR` -- all of ``does not
  contain``, ``not`` included;
* ``it``, and the words heading a ``number of`` or an ``item N of``, are
  keywords, as is every remaining structural word (``of``, ``whose``, ``if``,
  ``exists``...).

Text that does not parse -- the normal state of a buffer being typed --
degrades to the same judgement made from the tokens alone, so a keystroke
that breaks the parse does not recolor what came before it: a *complete* word
operator (the parser's own trie, so ``starts`` alone stays a name) is an
operator; ``number`` before ``of`` and ``item`` before a number are keywords;
the words after ``as``, up to the next grammar word, are a type; any other
structural word is a keyword, and any other word a name. Literals, comments
and lexical errors never need the tree.

One tree walk, not a lookup per token
-------------------------------------
:func:`~bigfix_relevance_analyzer.nodes.node_at` walks down from the root, so
asking it once per token is quadratic on a deep tree, and a long ``or`` chain
is as deep as it is long. Instead one walk collects the regions above, which
never overlap (each lies inside its node's span and outside all its
children's), and one merge pass over the sorted regions and the token stream
classifies everything. The text is lexed once for both the parser and the
merge.

Offsets are characters, like :class:`~bigfix_relevance_analyzer.nodes.Span`'s.
Converting them to an editor's units (UTF-16 for LSP) is the caller's job.
"""

from __future__ import annotations

import enum
from collections.abc import Sequence
from dataclasses import dataclass

from bigfix_relevance_analyzer import nodes
from bigfix_relevance_analyzer.grammar import STRUCTURAL_WORDS, TUPLE_INDEX_WORDS, WORD_INFIX_TRIE
from bigfix_relevance_analyzer.parser import _try_parse_lexed
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind, _lex

__all__ = ["HighlightKind", "HighlightSpan", "highlight"]


class HighlightKind(enum.StrEnum):
    """What a highlighted span is. A ``str``, so it serializes as its value."""

    KEYWORD = "keyword"
    """Grammar: ``of``, ``whose``, ``it``, ``as``, ``if``/``then``/``else``,
    ``exists``, a prefix ``not``, and the ``number``/``item`` heading an
    aggregate or a tuple index."""

    OPERATOR = "operator"
    """An infix or prefix operator, word or symbol: ``starts with``, ``and``,
    ``mod``, ``=``, ``-``, ``|``."""

    PROPERTY = "property"
    """A word of an inspector or property name: ``operating system``."""

    TYPE = "type"
    """The target of a cast: ``lowercase`` in ``it as lowercase``."""

    STRING = "string"
    NUMBER = "number"
    COMMENT = "comment"

    PUNCTUATION = "punctuation"
    """``(``, ``)``, ``,`` and ``;``."""

    ERROR = "error"
    """Text that does not lex: a stray character, or an unterminated string or
    comment (which takes the rest of the statement with it)."""


@dataclass(frozen=True, slots=True)
class HighlightSpan:
    """One token's worth of colour."""

    start: int
    """0-based character offset, inclusive."""

    end: int
    """0-based character offset, exclusive."""

    kind: HighlightKind


_LITERALS = {
    TokenKind.STRING: HighlightKind.STRING,
    TokenKind.NUMBER: HighlightKind.NUMBER,
    TokenKind.COMMENT: HighlightKind.COMMENT,
    TokenKind.ERROR: HighlightKind.ERROR,
}

_PUNCTUATION = frozenset({"(", ")", ",", ";"})
"""The punctuation that separates rather than operates. Every other
:data:`~bigfix_relevance_analyzer.tokenizer.PUNCTUATION` lexeme is an operator."""

_Region = tuple[int, int, HighlightKind]


def highlight(text: str) -> list[HighlightSpan]:
    """Every meaningful token of ``text``, classified, in source order.

    One span per token: whitespace and articles (``a``/``an``/``the``, which the
    engine skips) get none; everything else, comments and errors included,
    gets exactly one, over exactly its text. Never raises: text that does not
    parse is classified from its tokens alone (see the module docstring).
    """
    lexed = _lex(text)
    parsed = _try_parse_lexed(text, lexed.code)
    if parsed.node is not None:
        return _classify(lexed.tokens, _regions(parsed.node))
    return _classify(lexed.tokens, _token_regions(lexed.code))


def _regions(root: nodes.Node) -> list[_Region]:
    """The parts of the text the tree says something about, sorted; disjoint."""
    regions: list[_Region] = []
    for node in nodes.walk(root):
        match node:
            case nodes.Reference(span=span, index=index):
                end = span.end if index is None else index.span.start
                regions.append((span.start, end, HighlightKind.PROPERTY))
            case nodes.It(span=span):
                regions.append((span.start, span.end, HighlightKind.KEYWORD))
            case nodes.Cast(span=span, operand=operand):
                # `as` and the target; `_classify` gives the `as` its own kind.
                regions.append((operand.span.end, span.end, HighlightKind.TYPE))
            case nodes.Binary(left=left, right=right):
                regions.append((left.span.end, right.span.start, HighlightKind.OPERATOR))
            case nodes.NumberOf(span=span, operand=head) | nodes.ItemOf(span=span, index=head):
                regions.append((span.start, head.span.start, HighlightKind.KEYWORD))
    regions.sort()
    return regions


def _token_regions(code: Sequence[Token]) -> list[_Region]:
    """For text that does not parse: the regions the tree would have given,
    judged from the tokens, so a keystroke that breaks the parse does not
    recolor the words before it.

    * A complete word operator, matched longest-first against the parser's own
      trie, as the parser would. A word that only *begins* one stays a name, so
      ``starts of`` keeps ``starts`` an inspector even here.
    * ``number`` before ``of``, and ``item``/``items`` before a number: the
      aggregate and the tuple index, as the parser reads them.
    * ``as`` and the words after it, up to the next structural word or
      operator: a cast and its type.
    """
    regions: list[_Region] = []
    at = 0
    while at < len(code):
        token = code[at]
        word = token.normalized if token.kind is TokenKind.WORD else None
        following = code[at + 1] if at + 1 < len(code) else None
        if (matched := _operator_length(code, at)) > 0:
            regions.append((token.offset, _end(code[at + matched - 1]), HighlightKind.OPERATOR))
            at += matched
        elif (word == "number" and following is not None and following.normalized == "of") or (
            word in TUPLE_INDEX_WORDS
            and following is not None
            and following.kind is TokenKind.NUMBER
        ):
            regions.append((token.offset, _end(token), HighlightKind.KEYWORD))
            at += 1
        elif word == "as":
            last = at
            while (
                last + 1 < len(code)
                and code[last + 1].kind is TokenKind.WORD
                and code[last + 1].normalized not in STRUCTURAL_WORDS
                and _operator_length(code, last + 1) == 0
            ):
                last += 1
            regions.append((token.offset, _end(code[last]), HighlightKind.TYPE))
            at = last + 1
        else:
            at += 1
    return regions


def _operator_length(code: Sequence[Token], at: int) -> int:
    """How many words of ``code`` from ``at`` make the longest complete word
    operator there, by the parser's trie; 0 for none."""
    state = WORD_INFIX_TRIE
    matched = 0
    ahead = 0
    while at + ahead < len(code) and code[at + ahead].kind is TokenKind.WORD:
        next_state = state.children.get(code[at + ahead].normalized)
        if next_state is None:
            break
        state = next_state
        ahead += 1
        if state.op is not None:
            matched = ahead
    return matched


def _end(token: Token) -> int:
    return token.offset + len(token.text)


def _classify(tokens: Sequence[Token], regions: Sequence[_Region]) -> list[HighlightSpan]:
    """Merge the token stream with the sorted, disjoint ``regions``."""
    spans: list[HighlightSpan] = []
    current = 0
    # The region a word was last seen in: a cast region's first word is `as`.
    worded = -1
    for token in tokens:
        kind = token.kind
        if kind is TokenKind.WHITESPACE or kind is TokenKind.ARTICLE:
            continue
        start = token.offset
        end = start + len(token.text)
        found = _LITERALS.get(kind)
        if found is None and kind is TokenKind.PUNCT:
            found = (
                HighlightKind.PUNCTUATION if token.text in _PUNCTUATION else HighlightKind.OPERATOR
            )
        if found is None:
            # A word: the region it falls in, if any, decides.
            while current < len(regions) and regions[current][1] <= start:
                current += 1
            if current < len(regions) and regions[current][0] <= start:
                found = regions[current][2]
                if found is HighlightKind.TYPE and worded != current:
                    found = HighlightKind.KEYWORD  # the `as`
                worded = current
            elif token.normalized in STRUCTURAL_WORDS:
                found = HighlightKind.KEYWORD
            else:
                found = HighlightKind.PROPERTY
        spans.append(HighlightSpan(start, end, found))
    return spans
