"""A hand-rolled Pratt parser for BigFix Relevance.

The grammar lives in the declarative tables of
:mod:`bigfix_relevance_analyzer.grammar`; this module is only the Pratt
machinery that applies them. The authority on which tree a statement
produces is the corpus in ``tests/corpus/*.rlvcorpus``.

Two entry points, two policies:

* :func:`parse` raises :class:`ParseError` at the first failure, with a
  position -- for tooling that wants a precise diagnostic.
* :func:`try_parse` never raises -- the conservative "unknown, skip"
  interface for scorers and hooks that must survive broken input.

Non-goals, deliberately: no backtracking, no type-directed disambiguation,
and no error-recovery/partial-AST nodes. Deciding where a name phrase ends
does use *bounded* lookahead -- at most one operator's worth of tokens, in a
single forward pass that never rewinds (see :meth:`_Parser.phrase_ends_here`).
If a future platform ships an inspector name containing a structural word, the
failure mode is a wrong tree or a precise ParseError, never a crash;
``tests/test_grammar_tables.py`` guards that against every written form in the
inspector snapshot -- both spellings of every row, not just the signature's --
so it breaks loudly.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Final

from bigfix_relevance_analyzer import grammar
from bigfix_relevance_analyzer._serialize import _position
from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS
from bigfix_relevance_analyzer.nodes import (
    Bar,
    Binary,
    Cast,
    Collection,
    Exists,
    If,
    It,
    ItemOf,
    Node,
    NumberLiteral,
    NumberOf,
    Of,
    Reference,
    Span,
    StringLiteral,
    TupleExpr,
    Unary,
    Whose,
)
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind, code_tokens

__all__ = [
    "MAX_PARSE_DEPTH",
    "ParseError",
    "ParseResult",
    "parse",
    "try_parse",
]

MAX_PARSE_DEPTH: Final = 200
"""How deeply this parser will nest before giving up.

Parsing is recursive, so an expression nested deeply enough exhausts the Python
stack. Left unguarded that surfaces as ``RecursionError`` -- which escapes
:func:`try_parse`, whose whole contract is that it never raises, and which is
not something a caller handling extracted content can reasonably be asked to
catch. So depth is counted and refused as an ordinary positioned
:class:`ParseError` instead.

The engine has its own limit and it is higher (``MAX_EXPR_DEPTH`` is 1000, see
:mod:`bigfix_relevance_analyzer.diagnostics`), so between this number and that
one there are expressions BigFix accepts and this parser declines to read. That
is the conservative direction -- :func:`try_parse` reports "unknown, skip" --
and it is deliberate: the interpreter runs out of stack around 495 levels, and
a limit set close to that would be a crash waiting on a differently-configured
consumer rather than a limit.

Real content is nowhere near either number. This bound exists for truncated and
hostile input, which is exactly what extraction turns up. It does not bound the
*tree*'s depth -- a long left-associative chain parses at depth 1 -- which is
why every whole-tree pass over the result, ``to_sexpr`` among them, is
iterative.
"""


class ParseError(ValueError):
    """A syntax error, pointing at the offending position in the source."""

    def __init__(self, message: str, offset: int, line: int, column: int) -> None:
        super().__init__(f"line {line}, column {column}: {message}")
        self.message = message
        self.offset = offset
        self.line = line
        self.column = column

    def __reduce__(self) -> tuple[Any, ...]:
        """Rebuild from the four arguments, not from the formatted message.

        `ValueError.__init__` is handed one preformatted string, so `args` is a
        one-tuple -- and pickle reconstructs an exception by calling its class
        with `args`. Without this, unpickling raises `TypeError: missing 3
        required positional arguments` instead of returning the error, which
        breaks anything that fans analysis out to a worker pool, and breaks it
        only for the inputs that failed to parse.
        """
        return (self.__class__, (self.message, self.offset, self.line, self.column))

    def to_dict(self) -> dict[str, Any]:
        """This error as JSON-serializable plain data.

        ``message`` is the bare message, not the ``str(self)`` form that
        prefixes it with the position: the position is already here as its own
        keys, and a consumer rendering both would print it twice.
        """
        return {"message": self.message, **_position(self)}


@dataclass(frozen=True, slots=True)
class ParseResult:
    """What :func:`try_parse` returns: exactly one of node or error is set."""

    node: Node | None
    error: ParseError | None

    @property
    def ok(self) -> bool:
        return self.error is None


def parse(text: str) -> Node:
    """Parse one relevance expression; raise :class:`ParseError` on failure."""
    return _parse_lexed(text, tuple(code_tokens(text)))


def try_parse(text: str) -> ParseResult:
    """Parse, never raising: any :class:`ParseError` is returned, not thrown.

    Only ParseError is caught -- anything else escaping :func:`parse` is a
    bug in this package and must surface.
    """
    return _try_parse_lexed(text, tuple(code_tokens(text)))


def _parse_lexed(text: str, tokens: tuple[Token, ...]) -> Node:
    """:func:`parse`, for a caller that has already lexed the text.

    Takes the code tokens rather than the whole
    :class:`~bigfix_relevance_analyzer.tokenizer._Lexed`, so a caller that only
    wants a tree never pays to build the trivia the parser does not read.
    ``text`` is still needed: an error at end of input is positioned against it.
    """
    return _Parser(text, tokens).parse_statement()


def _try_parse_lexed(text: str, tokens: tuple[Token, ...]) -> ParseResult:
    """:func:`try_parse`, for a caller that has already lexed the text."""
    try:
        return ParseResult(node=_parse_lexed(text, tokens), error=None)
    except ParseError as error:
        return ParseResult(node=None, error=error)


class _Parser:
    def __init__(self, text: str, tokens: tuple[Token, ...]) -> None:
        self.text = text
        self.tokens = tokens
        self.at = 0
        self.depth = 0
        # Nodes that came out of explicit parentheses, by identity. `|` needs
        # this: the engine accepts `(2 * 3) | 5` but refuses `2 * 3 | 5`, and
        # by the time the Bar is built the two lefts are the same tree shape.
        # The dict holds each node too: a bare id() set let a freed node's
        # address go to a later, unparenthesized one, which inherited the mark
        # (issue #57: `name of operating system` W600'd as if `(name)`).
        self.grouped: dict[int, Node] = {}

    # -- token stream -------------------------------------------------------

    def peek(self) -> Token | None:
        """The next token, or None at end of input. ERROR tokens are fatal."""
        if self.at >= len(self.tokens):
            return None
        token = self.tokens[self.at]
        if token.kind is TokenKind.ERROR:
            raise self.error_at(token, _describe_error_token(token))
        return token

    def advance(self) -> Token:
        token = self.peek()
        assert token is not None, "advance past end of input"
        self.at += 1
        return token

    # -- errors -------------------------------------------------------------

    def error_at(self, token: Token | None, message: str) -> ParseError:
        """A ParseError at ``token``, or at end of input when token is None."""
        if token is not None:
            return ParseError(message, token.offset, token.line, token.column)
        offset = len(self.text)
        line = self.text.count("\n") + 1
        column = offset - (self.text.rfind("\n") + 1) + 1
        return ParseError(message, offset, line, column)

    def expect_punct(self, lexeme: str, context: str) -> Token:
        token = self.peek()
        if token is None or token.kind is not TokenKind.PUNCT or token.text != lexeme:
            raise self.error_at(token, f"expected '{lexeme}' {context}")
        return self.advance()

    # -- the Pratt machinery ------------------------------------------------

    def parse_statement(self) -> Node:
        if self.peek() is None:
            raise self.error_at(None, "empty relevance: no expression to parse")
        node = self.parse_expression(0)
        trailing = self.peek()
        if trailing is not None:
            raise self.error_at(
                trailing, f"unexpected {trailing.text!r} after a complete expression"
            )
        return node

    def parse_expression(self, min_bp: int) -> Node:
        """One precedence level. Every nesting construct routes through here --
        parentheses, prefix operators, `of`, `whose`, `if`, and index arguments
        -- so counting depth here counts all of them."""
        self.depth += 1
        try:
            if self.depth > MAX_PARSE_DEPTH:
                raise self.too_deep()
            node = self.parse_prefix()
            while True:
                continued = self.parse_infix(node, min_bp)
                if continued is None:
                    return node
                node = continued
        finally:
            self.depth -= 1

    def too_deep(self) -> ParseError:
        """Refuse a too-deeply-nested expression, in the engine's own wording.

        Read the token directly rather than through `peek`, which raises on an
        ERROR token: at this point the depth is the thing worth reporting, and a
        lexical complaint about whatever happens to sit here would bury it.
        """
        token = self.tokens[self.at] if self.at < len(self.tokens) else None
        message = DIAGNOSTICS["expression-too-deep"].format(max_depth=MAX_PARSE_DEPTH)
        return self.error_at(token, message)

    def parse_prefix(self) -> Node:
        token = self.peek()
        if token is None:
            raise self.error_at(None, "expected an expression, found end of input")

        literal = _literal(token)
        if literal is not None:
            self.advance()
            return literal

        if token.kind is TokenKind.PUNCT and token.text == "(":
            # Inline, not a shared `parse_group` method: a helper would add one
            # stack frame per nesting level, and the index path is already the
            # deepest one per level -- enough to hit `RecursionError` before
            # MAX_PARSE_DEPTH does. Only the post-recursion half is shared.
            self.advance()
            inner = self.parse_expression(0)
            closing = self.expect_punct(")", "to close the group opened here")
            return self.mark_grouped(_widen(inner, token, closing))

        if token.kind is TokenKind.PUNCT and token.text == "-":
            self.advance()
            operand = self.parse_expression(grammar.BP_UNARY_MINUS)
            return _unary("-", token, operand)

        if token.kind is TokenKind.WORD:
            # `exists` and `not` take a tight operand: a cast, `of` or `whose`
            # nests, but nothing looser -- not even `=` or `|`. Confirmed
            # live: `exists 1 + 2` fails on `exists 1`, `not 1 = 1` on
            # `not 1`, `exists X | false` falls back on the exists itself,
            # while `exists 5 as string` and `not 5 as boolean` cast inside.
            if token.normalized == "not":
                self.advance()
                quantifier = self.peek()
                if (
                    quantifier is not None
                    and quantifier.kind is TokenKind.WORD
                    and quantifier.normalized in grammar.EXISTS_WORDS
                ):
                    self.advance()
                    operand = self.parse_expression(grammar.BP_PIPE)
                    return _exists(negated=True, op_token=token, operand=operand)
                operand = self.parse_expression(grammar.BP_PIPE)
                return _unary("not", token, operand)
            if token.normalized in grammar.EXISTS_WORDS:
                self.advance()
                operand = self.parse_expression(grammar.BP_PIPE)
                return _exists(negated=False, op_token=token, operand=operand)
            if token.normalized == "if":
                return self.parse_conditional()
            if not self.phrase_ends_here():
                return self.parse_reference()

        raise self.error_at(token, f"expected an expression, found {token.text!r}")

    def parse_conditional(self) -> Node:
        """``if c then t else e``. The else is mandatory in relevance, and the
        else branch is greedy: it extends as far right as it can."""
        if_token = self.advance()
        condition = self.parse_expression(0)
        self.expect_word("then", "after the condition of 'if'")
        then_branch = self.parse_expression(0)
        self.expect_word("else", "after the then branch of 'if'")
        else_branch = self.parse_expression(0)
        return If(
            span=_join_spans(_token_span(if_token), else_branch.span),
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def expect_word(self, word: str, context: str) -> Token:
        token = self.peek()
        if token is None or token.kind is not TokenKind.WORD or token.normalized != word:
            raise self.error_at(token, f"expected '{word}' {context}")
        return self.advance()

    def parse_reference(self) -> Node:
        """A name phrase -- greedy words -- plus its optional index argument."""
        words = [self.advance(), *self.read_phrase()]
        index = self.parse_index()
        last = index.span if index is not None else _token_span(words[-1])
        span = _join_spans(_token_span(words[0]), last)
        return Reference(span=span, phrase=_phrase(words), index=index)

    def read_phrase(self) -> list[Token]:
        """Consume words up to wherever the current name phrase ends."""
        words: list[Token] = []
        while not self.phrase_ends_here():
            words.append(self.advance())
        return words

    def read_cast_target(self) -> list[Token]:
        """Like :meth:`read_phrase`, but stop at any operator's first word.

        A name phrase absorbs a word that starts an operator without completing
        one (see :meth:`phrase_ends_here`); a cast target does not. Every engine
        target refuses `5 as starts`, `5 as ends`, `5 as does` and `5 as
        contains` as unparsable, while `5 as start` parses and fails only at
        `The operator "start" is not defined.`
        """
        words: list[Token] = []
        while not self.phrase_ends_here():
            token = self.peek()
            assert token is not None
            if token.normalized in grammar.OPERATOR_FIRST_WORDS:
                break
            words.append(self.advance())
        return words

    def mark_grouped(self, grouped: Node) -> Node:
        """Remember ``grouped`` came out of its own parentheses (see :func:`_of`)."""
        self.grouped[id(grouped)] = grouped
        return grouped

    def parse_index(self) -> Node | None:
        """The single argument a name may take: ``key "foo"``, ``item 0``,
        ``key (name of it)``."""
        token = self.peek()
        if token is None:
            return None
        literal = _literal(token)
        if literal is not None:
            self.advance()
            return literal
        if token.kind is TokenKind.PUNCT and token.text == "(":
            # Inline for the frame budget; see the same branch in parse_prefix.
            self.advance()
            inner = self.parse_expression(0)
            closing = self.expect_punct(")", "to close the argument opened here")
            return self.mark_grouped(_widen(inner, token, closing))
        return None

    def parse_infix(self, left: Node, min_bp: int) -> Node | None:
        """One infix step: extend ``left`` if the next token binds tightly
        enough, else return None to hand control back up."""
        token = self.peek()
        if token is None:
            return None

        if token.kind is TokenKind.PUNCT:
            # `,` and `;` build flat sequence nodes rather than Binary chains.
            # A parenthesized tuple is one item of the tuple around it, not
            # spliced into it (see nodes.py).
            if token.text == "," and min_bp < grammar.BP_COMMA:
                self.advance()
                right = self.parse_expression(grammar.BP_COMMA)
                return _sequence(TupleExpr, left, right, nested=self.grouped)
            if token.text == ";" and min_bp < grammar.BP_SEMICOLON:
                self.advance()
                right = self.parse_expression(grammar.BP_SEMICOLON)
                return _sequence(Collection, left, right)

            op = grammar.PUNCT_INFIX.get(token.text)
            if op is not None and op.lbp > min_bp:
                if op.canonical == "|" and self.bare_product(left):
                    assert isinstance(left, Binary)
                    raise self.error_at(
                        token,
                        f"the engine cannot parse '|' after an unparenthesized "
                        f"'{left.op}' expression; parenthesize the left side",
                    )
                if self.chained_comparison(op, left):
                    assert isinstance(left, Binary)
                    raise self.error_at(token, _chained_comparison_message(op, left))
                self.advance()
                right = self.parse_expression(self.right_bp(op))
                if op.canonical == "|":
                    return Bar(span=_join_spans(left.span, right.span), left=left, right=right)
                return _binary(op.canonical, left, right)

        if token.kind is TokenKind.WORD:
            if token.normalized == "of" and min_bp < grammar.BP_OF:
                self.reject_bad_tuple_index(left)
                self.advance()
                obj = self.parse_expression(grammar.BP_OF - 1)  # right-associative
                return _of(left, obj, grouped=id(left) in self.grouped)

            if token.normalized == "whose" and min_bp < grammar.BP_WHOSE:
                self.advance()
                self.expect_punct("(", "after 'whose'")
                predicate = self.parse_expression(0)
                closing = self.expect_punct(")", "to close the whose predicate")
                span = _join_spans(left.span, _token_span(closing))
                return Whose(span=span, collection=left, predicate=predicate)

            if token.normalized == "as" and min_bp < grammar.BP_CAST:
                self.advance()
                target_words = self.read_cast_target()
                if not target_words:
                    raise self.error_at(self.peek(), "expected a type name after 'as'")
                span = _join_spans(left.span, _token_span(target_words[-1]))
                return Cast(span=span, operand=left, target=_phrase(target_words))

            matched = self.match_word_infix()
            if matched is None and token.normalized == "does":
                raise self.incomplete_does(token)
            if matched is not None:
                op, consumed = matched
                if op.lbp > min_bp:
                    if self.chained_comparison(op, left):
                        assert isinstance(left, Binary)
                        raise self.error_at(token, _chained_comparison_message(op, left))
                    self.at += consumed
                    right = self.parse_expression(self.right_bp(op))
                    return _binary(op.canonical, left, right)

        return None

    def reject_bad_tuple_index(self, prop: Node) -> None:
        """Refuse `item <index> of` / `items <index> of` with any index but an
        integer literal, parenthesized or not.

        The engine reads that shape as tuple-index syntax whatever the object
        is -- every client target, Windows included, answers `item "foo" of
        folder "/etc"` and `item (0+1) of (1,2)` with the sentence below -- so
        the inspector table's `item <string> of <folder>` is unreachable.
        `item (1) of (1,2)` answers `2`. A grouped `(item "a") of x` is not this
        shape: parentheses end the bare phrase (see :func:`_of`).
        """
        if (
            not isinstance(prop, Reference)
            or id(prop) in self.grouped
            or prop.phrase not in grammar.TUPLE_INDEX_WORDS
            or prop.index is None
        ):
            return
        index = prop.index
        if isinstance(index, NumberLiteral) and index.is_integer_literal:
            return
        raise ParseError(
            "This expression contained a tuple index which was not an integer literal",
            *self.position_of(index.span.start),
        )

    def position_of(self, offset: int) -> tuple[int, int, int]:
        """``(offset, line, column)`` for a 0-based source offset."""
        line = self.text.count("\n", 0, offset) + 1
        column = offset - (self.text.rfind("\n", 0, offset) + 1) + 1
        return offset, line, column

    def right_bp(self, op: grammar.InfixOp) -> int:
        """The minimum binding power for ``op``'s right operand."""
        if op.rbp is not None:
            return op.rbp
        return op.lbp - 1 if op.right_assoc else op.lbp

    def bare_product(self, node: Node) -> bool:
        """Whether ``node`` is a `*`/`/`/`mod`/`&` result the engine refuses
        to hand to `|` -- confirmed live: `2 * 3 | 5` is a parse error while
        `(2 * 3) | 5` is 6. Parentheses are what make the difference, hence
        the identity check against ``self.grouped``."""
        return (
            isinstance(node, Binary)
            and node.op in grammar.PIPE_UNMIXABLE
            and id(node) not in self.grouped
        )

    def chained_comparison(self, op: grammar.InfixOp, left: Node) -> bool:
        """Whether ``op`` would be a second comparison on an unparenthesized
        first one -- the shape the engine refuses outright (`1 = 1 = true` and
        `1 is 1 is true` are parse errors; `(1 = 1) = true` is True, confirmed
        live). Parentheses are what make the difference, hence the identity
        check against ``self.grouped``, as in ``bare_product``."""
        return (
            op.canonical in grammar.RELATIONAL
            and isinstance(left, Binary)
            and left.op in grammar.RELATIONAL
            and id(left) not in self.grouped
        )

    def phrase_ends_here(self) -> bool:
        """Whether a name phrase must stop at the current token.

        A structural word always stops it. An operator word stops it only when
        the trie matches the operator in *full*: `starts` is the plural `start`
        inspector in `starts of ranges`, and the `starts with` operator only in
        `starts with "a"`. Single-word operators (`and`, `contains`, ...) always
        match, so they stop a phrase exactly as an unconditional terminator
        would.

        Bounded lookahead, never backtracking -- `match_word_infix` walks at
        most one operator's worth of tokens forward and does not move `self.at`.

        The consequence to know about: a trailing word that *could* start an
        operator but does not complete one is absorbed into the phrase, so
        `x ends "a"` reads as the name `x ends` indexed by `"a"` rather than
        failing. That shape already existed for words *inside* an operator
        (`x start with "a"`), and refusing it would refuse the real names
        `date range starts` and `stop on idle ends`.
        """
        token = self.peek()
        if token is None or token.kind is not TokenKind.WORD:
            return True
        if token.normalized in grammar.STRUCTURAL_WORDS:
            return True
        if token.normalized not in grammar.OPERATOR_FIRST_WORDS:
            return False
        if token.normalized == "does" and self.word_ahead(1) == "not":
            # `not` is structural, so no name runs through `does not`: stop
            # here and let parse_infix explain the incomplete operator.
            return True
        return self.match_word_infix() is not None

    def word_ahead(self, ahead: int) -> str | None:
        """The normalized word ``ahead`` tokens on, or None if it is not a word."""
        at = self.at + ahead
        if at >= len(self.tokens) or self.tokens[at].kind is not TokenKind.WORD:
            return None
        return self.tokens[at].normalized

    def incomplete_does(self, does: Token) -> ParseError:
        """Refuse a `does` / `does not` that no operator completes.

        Before the end, `)` or a punctuation operator the engine skips the
        words -- `"a" does not = "a"` is True live, the negation silently
        lost (issue 74) -- so the message says so rather than just "unexpected".
        Before any other word the engine refuses it too ("The operator "does"
        is not defined"), and a near-miss verb gets the spelling it wanted.
        """
        words = 2 if self.word_ahead(1) == "not" else 1
        spelled = "does not" if words == 2 else "does"
        following = self.tokens[self.at + words] if self.at + words < len(self.tokens) else None
        if following is None or (following.kind is TokenKind.PUNCT and following.text != "("):
            return self.error_at(
                does,
                f"'{spelled}' is missing its verb (contain, equal, start with, end with); "
                f"the engine silently ignores a dangling '{spelled}', so this evaluates "
                f"as if it were absent and any negation is lost",
            )
        suggestion = _DOES_NEAR_MISSES.get(self.word_ahead(words) or "")
        if suggestion is not None:
            # A bare `does contain` may have wanted either polarity.
            positive = "" if words == 2 else f"{_DOES_POSITIVE[suggestion]}' or '"
            return self.error_at(
                does,
                f"'{spelled} {following.text}' is not an operator; "
                f"did you mean '{positive}does not {suggestion}'?",
            )
        return self.error_at(
            does,
            f"'{spelled}' must be followed by contain, equal, start with, or end with",
        )

    def match_word_infix(self) -> tuple[grammar.InfixOp, int] | None:
        """Max-munch the word-operator trie at the current position.

        Returns the longest operator that matches and how many tokens it
        spans, without consuming anything.
        """
        state = grammar.WORD_INFIX_TRIE
        best: tuple[grammar.InfixOp, int] | None = None
        ahead = 0
        while self.at + ahead < len(self.tokens):
            token = self.tokens[self.at + ahead]
            if token.kind is not TokenKind.WORD:
                break
            next_state = state.children.get(token.normalized)
            if next_state is None:
                break
            state = next_state
            ahead += 1
            if state.op is not None:
                best = (state.op, ahead)
        return best


# ---------------------------------------------------------------------------
# Node construction helpers
# ---------------------------------------------------------------------------


# The verb a `does` / `does not` was probably reaching for, by the word written.
_DOES_NEAR_MISSES = {
    "contain": "contain",
    "contains": "contain",
    "equal": "equal",
    "equals": "equal",
    "start": "start with",
    "starts": "start with",
    "end": "end with",
    "ends": "end with",
}
_DOES_POSITIVE = {
    "contain": "contains",
    "equal": "equals",
    "start with": "starts with",
    "end with": "ends with",
}


def _token_span(token: Token) -> Span:
    return Span(
        start=token.offset,
        end=token.offset + len(token.text),
        line=token.line,
        column=token.column,
    )


def _join_spans(start: Span, end: Span) -> Span:
    """From the head of ``start`` to the end of ``end``: every compound node's span."""
    return Span(start=start.start, end=end.end, line=start.line, column=start.column)


def _literal(token: Token) -> Node | None:
    """The leaf a single token is on its own -- a number, a string or ``it`` --
    or ``None`` when it is not one."""
    span = _token_span(token)
    if token.kind is TokenKind.NUMBER:
        return NumberLiteral(span=span, text=token.text)
    if token.kind is TokenKind.STRING:
        return StringLiteral(span=span, text=token.text)
    if token.kind is TokenKind.WORD and token.normalized == "it":
        return It(span=span)
    return None


def _phrase(words: list[Token]) -> str:
    """A name or type phrase: its words case-folded, joined by one space."""
    return " ".join(word.normalized for word in words)


def _widen(node: Node, opening: Token, closing: Token) -> Node:
    """Grow a node's span to cover the parens around it."""
    span = _join_spans(_token_span(opening), _token_span(closing))
    return dataclasses.replace(node, span=span)


def _sequence(
    kind: type[TupleExpr] | type[Collection],
    left: Node,
    right: Node,
    *,
    nested: dict[int, Node] | None = None,
) -> Node:
    """Extend or start a flat tuple/collection from one `,` or `;` step.

    ``nested`` holds the nodes that came out of their own parentheses; one of
    those is kept whole as a single item rather than spliced in.
    """

    def items_of(node: Node) -> tuple[Node, ...]:
        if isinstance(node, kind) and (nested is None or id(node) not in nested):
            return node.items
        return (node,)

    return kind(
        span=_join_spans(left.span, right.span),
        items=items_of(left) + items_of(right),
    )


def _of(prop: Node, obj: Node, *, grouped: bool = False) -> Node:
    """Build ``prop of obj``, specialising the two forms that are not property
    access.

    Both are recognised syntactically, from the phrase and its index alone.
    Neither needs the object's type, which is what keeps this in the parser:
    `number` is not an inspector at all, so `number of x` can only be
    aggregation, and a numeric index can only be a tuple subscript.

    ``grouped`` -- ``prop`` came out of its own parentheses -- suppresses both,
    because both read a *bare* phrase and parentheses end that. The names have
    to stand on their own then, and neither does::

        Q: (number) of files of folder "/etc"
        E: The operator "number" is not defined.
        Q: (item 0) of ("a","b")
        E: The operator "item" is not defined.
    """
    span = _join_spans(prop.span, obj.span)
    if isinstance(prop, Reference) and not grouped:
        if prop.phrase == "number" and prop.index is None:
            return NumberOf(span=span, operand=obj)
        if (
            # Either written form subscripts a tuple: `items 1 of (a, b)` is
            # the same indexing said plurally. Any other index never gets here
            # (`reject_bad_tuple_index`): the engine reads `item <x> of` as
            # tuple syntax whatever the object, so the table's `item <string>
            # of <folder>` is unreachable.
            prop.phrase in grammar.TUPLE_INDEX_WORDS
            and isinstance(prop.index, NumberLiteral)
            and prop.index.is_integer_literal
        ):
            return ItemOf(span=span, index=prop.index, operand=obj, plural=prop.phrase == "items")
    return Of(span=span, prop=prop, obj=obj, prop_grouped=grouped)


def _binary(op: str, left: Node, right: Node) -> Node:
    return Binary(span=_join_spans(left.span, right.span), op=op, left=left, right=right)


def _unary(op: str, op_token: Token, operand: Node) -> Node:
    span = _join_spans(_token_span(op_token), operand.span)
    return Unary(span=span, op=op, operand=operand)


def _exists(negated: bool, op_token: Token, operand: Node) -> Node:
    span = _join_spans(_token_span(op_token), operand.span)
    return Exists(span=span, negated=negated, operand=operand)


def _chained_comparison_message(op: grammar.InfixOp, left: Binary) -> str:
    return (
        f"the engine cannot parse '{op.canonical}' after an unparenthesized "
        f"'{left.op}' comparison; parenthesize the left side"
    )


def _describe_error_token(token: Token) -> str:
    if token.text.startswith('"'):
        return "unterminated string literal"
    if token.text.startswith("/*"):
        return "unterminated comment"
    return f"unexpected character {token.text!r}"
