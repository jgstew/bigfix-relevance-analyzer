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
from typing import Final

from bigfix_relevance_analyzer import grammar
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
hostile input, which is exactly what extraction turns up. It also protects the
recursive consumers of the tree it returns, ``to_sexpr`` among them.
"""


class ParseError(ValueError):
    """A syntax error, pointing at the offending position in the source."""

    def __init__(self, message: str, offset: int, line: int, column: int) -> None:
        super().__init__(f"line {line}, column {column}: {message}")
        self.message = message
        self.offset = offset
        self.line = line
        self.column = column


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
    return _Parser(text).parse_statement()


def try_parse(text: str) -> ParseResult:
    """Parse, never raising: any :class:`ParseError` is returned, not thrown.

    Only ParseError is caught -- anything else escaping :func:`parse` is a
    bug in this package and must surface.
    """
    try:
        return ParseResult(node=parse(text), error=None)
    except ParseError as error:
        return ParseResult(node=None, error=error)


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens = list(code_tokens(text))
        self.at = 0
        self.depth = 0

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

        if token.kind is TokenKind.NUMBER:
            self.advance()
            return NumberLiteral(span=_token_span(token), text=token.text)

        if token.kind is TokenKind.STRING:
            self.advance()
            return StringLiteral(span=_token_span(token), text=token.text)

        if token.kind is TokenKind.PUNCT and token.text == "(":
            self.advance()
            inner = self.parse_expression(0)
            closing = self.expect_punct(")", "to close the group opened here")
            return _widen(inner, token, closing)

        if token.kind is TokenKind.PUNCT and token.text == "-":
            self.advance()
            operand = self.parse_expression(grammar.BP_UNARY_MINUS)
            return _unary("-", token, operand)

        if token.kind is TokenKind.WORD:
            if token.normalized == "it":
                self.advance()
                return It(span=_token_span(token))
            if token.normalized == "not":
                self.advance()
                quantifier = self.peek()
                if (
                    quantifier is not None
                    and quantifier.kind is TokenKind.WORD
                    and quantifier.normalized in ("exists", "exist")
                ):
                    self.advance()
                    operand = self.parse_expression(grammar.BP_RELATIONAL)
                    return _exists(negated=True, op_token=token, operand=operand)
                operand = self.parse_expression(grammar.BP_NOT)
                return _unary("not", token, operand)
            if token.normalized in ("exists", "exist"):
                self.advance()
                operand = self.parse_expression(grammar.BP_RELATIONAL)
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
        span = Span(
            start=if_token.offset,
            end=else_branch.span.end,
            line=if_token.line,
            column=if_token.column,
        )
        return If(span=span, condition=condition, then_branch=then_branch, else_branch=else_branch)

    def expect_word(self, word: str, context: str) -> Token:
        token = self.peek()
        if token is None or token.kind is not TokenKind.WORD or token.normalized != word:
            raise self.error_at(token, f"expected '{word}' {context}")
        return self.advance()

    def parse_reference(self) -> Node:
        """A name phrase -- greedy words -- plus its optional index argument."""
        first = self.advance()
        words = [first]
        while not self.phrase_ends_here():
            words.append(self.advance())
        phrase = " ".join(word.normalized for word in words)
        index = self.parse_index()
        end = index.span.end if index is not None else _token_span(words[-1]).end
        span = Span(start=first.offset, end=end, line=first.line, column=first.column)
        return Reference(span=span, phrase=phrase, index=index)

    def parse_index(self) -> Node | None:
        """The single argument a name may take: ``key "foo"``, ``item 0``,
        ``key (name of it)``."""
        token = self.peek()
        if token is None:
            return None
        if token.kind is TokenKind.STRING:
            self.advance()
            return StringLiteral(span=_token_span(token), text=token.text)
        if token.kind is TokenKind.NUMBER:
            self.advance()
            return NumberLiteral(span=_token_span(token), text=token.text)
        if token.kind is TokenKind.WORD and token.normalized == "it":
            self.advance()
            return It(span=_token_span(token))
        if token.kind is TokenKind.PUNCT and token.text == "(":
            self.advance()
            inner = self.parse_expression(0)
            closing = self.expect_punct(")", "to close the argument opened here")
            return _widen(inner, token, closing)
        return None

    def parse_infix(self, left: Node, min_bp: int) -> Node | None:
        """One infix step: extend ``left`` if the next token binds tightly
        enough, else return None to hand control back up."""
        token = self.peek()
        if token is None:
            return None

        if token.kind is TokenKind.PUNCT:
            # `,` and `;` build flat sequence nodes rather than Binary chains:
            # relevance has no nested tuple type (see nodes.py).
            if token.text == "," and min_bp < grammar.BP_COMMA:
                self.advance()
                right = self.parse_expression(grammar.BP_COMMA)
                return _sequence(TupleExpr, left, right)
            if token.text == ";" and min_bp < grammar.BP_SEMICOLON:
                self.advance()
                right = self.parse_expression(grammar.BP_SEMICOLON)
                return _sequence(Collection, left, right)

            op = grammar.PUNCT_INFIX.get(token.text)
            if op is not None and op.lbp > min_bp:
                self.advance()
                right = self.parse_expression(op.lbp - 1 if op.right_assoc else op.lbp)
                if op.canonical == "|":
                    return Bar(span=_join_spans(left.span, right.span), left=left, right=right)
                return _binary(op.canonical, left, right)

        if token.kind is TokenKind.WORD:
            if token.normalized == "of" and min_bp < grammar.BP_OF:
                self.advance()
                obj = self.parse_expression(grammar.BP_OF - 1)  # right-associative
                return _of(left, obj)

            if token.normalized == "whose" and min_bp < grammar.BP_WHOSE:
                self.advance()
                self.expect_punct("(", "after 'whose'")
                predicate = self.parse_expression(0)
                closing = self.expect_punct(")", "to close the whose predicate")
                span = Span(
                    start=left.span.start,
                    end=closing.offset + len(closing.text),
                    line=left.span.line,
                    column=left.span.column,
                )
                return Whose(span=span, collection=left, predicate=predicate)

            if token.normalized == "as" and min_bp < grammar.BP_CAST:
                self.advance()
                target_words: list[Token] = []
                while not self.phrase_ends_here():
                    target_words.append(self.advance())
                if not target_words:
                    raise self.error_at(self.peek(), "expected a type name after 'as'")
                span = Span(
                    start=left.span.start,
                    end=_token_span(target_words[-1]).end,
                    line=left.span.line,
                    column=left.span.column,
                )
                target = " ".join(word.normalized for word in target_words)
                return Cast(span=span, operand=left, target=target)

            matched = self.match_word_infix()
            if matched is not None:
                op, consumed = matched
                if op.lbp > min_bp:
                    self.at += consumed
                    right = self.parse_expression(op.lbp - 1 if op.right_assoc else op.lbp)
                    return _binary(op.canonical, left, right)

        return None

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
        return self.match_word_infix() is not None

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


def _token_span(token: Token) -> Span:
    return Span(
        start=token.offset,
        end=token.offset + len(token.text),
        line=token.line,
        column=token.column,
    )


def _join_spans(start: Span, end: Span) -> Span:
    return Span(start=start.start, end=end.end, line=start.line, column=start.column)


def _widen(node: Node, opening: Token, closing: Token) -> Node:
    """Grow a node's span to cover the parens around it."""
    span = Span(
        start=opening.offset,
        end=closing.offset + len(closing.text),
        line=opening.line,
        column=opening.column,
    )
    return dataclasses.replace(node, span=span)


def _sequence(kind: type[TupleExpr] | type[Collection], left: Node, right: Node) -> Node:
    """Extend or start a flat tuple/collection from one `,` or `;` step."""

    def items_of(node: Node) -> tuple[Node, ...]:
        return node.items if isinstance(node, kind) else (node,)

    return kind(
        span=_join_spans(left.span, right.span),
        items=items_of(left) + items_of(right),
    )


def _of(prop: Node, obj: Node) -> Node:
    """Build ``prop of obj``, specialising the two forms that are not property
    access.

    Both are recognised syntactically, from the phrase and its index alone.
    Neither needs the object's type, which is what keeps this in the parser:
    `number` is not an inspector at all, so `number of x` can only be
    aggregation, and a numeric index can only be a tuple subscript.
    """
    span = _join_spans(prop.span, obj.span)
    if isinstance(prop, Reference):
        if prop.phrase == "number" and prop.index is None:
            return NumberOf(span=span, operand=obj)
        if (
            prop.phrase == "item"
            and isinstance(prop.index, NumberLiteral)
            and prop.index.is_integer_literal
        ):
            return ItemOf(span=span, index=prop.index, operand=obj)
    return Of(span=span, prop=prop, obj=obj)


def _binary(op: str, left: Node, right: Node) -> Node:
    return Binary(span=_join_spans(left.span, right.span), op=op, left=left, right=right)


def _unary(op: str, op_token: Token, operand: Node) -> Node:
    span = _prefix_span(op_token, operand)
    return Unary(span=span, op=op, operand=operand)


def _exists(negated: bool, op_token: Token, operand: Node) -> Node:
    span = _prefix_span(op_token, operand)
    return Exists(span=span, negated=negated, operand=operand)


def _prefix_span(op_token: Token, operand: Node) -> Span:
    return Span(
        start=op_token.offset,
        end=operand.span.end,
        line=op_token.line,
        column=op_token.column,
    )


def _describe_error_token(token: Token) -> str:
    if token.text.startswith('"'):
        return "unterminated string literal"
    if token.text.startswith("/*"):
        return "unterminated comment"
    return f"unexpected character {token.text!r}"
