"""What the cursor is on, as a few lines of Markdown, with no protocol in it.

:func:`describe` takes a statement's
:class:`~bigfix_relevance_analyzer.analyzer.RelevanceAnalysis` and an offset
into its text, and says what is there: an inspector with the table rows it
resolved to (signature, return type, plurality, where it is defined), a
literal, what an ``it`` is bound to, or the construct a keyword or operator
belongs to. Nothing is looked up again: the rows are the analysis's own
:attr:`~bigfix_relevance_analyzer.analyzer.ReferenceReport.resolved`, the
narrowed answer the checker already worked out, so a hover can never disagree
with a diagnostic.

There is no hover, rather than a vague one, on whitespace, comments, articles
and grouping parentheses, and anywhere in a statement that does not parse: a
wrong tree is worse than none (issue 96, item 3).

Mapping the editor's position to the offset, and the answer's span back to a
range, is :class:`~bigfix_relevance_analyzer.lsp.positions.DocumentIndex`'s;
the per-document plumbing is
:meth:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter.hover`.
"""

from __future__ import annotations

import itertools
from typing import Final, NamedTuple

from bigfix_relevance_analyzer import inspectors
from bigfix_relevance_analyzer.analyzer import ReferenceReport, RelevanceAnalysis
from bigfix_relevance_analyzer.binding import Binder
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.lint import TextSpan
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
    NumberKind,
    NumberLiteral,
    NumberOf,
    Of,
    Reference,
    StringLiteral,
    TupleExpr,
    Unary,
    Whose,
    node_at,
    nodes_at,
)
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind

DOCS_URL: Final = "https://github.com/jgstew/bigfix-relevance-analyzer/blob/main/docs/reference/"
"""Where hover links point: the reference pages, on the default branch.

Not a release tag. An unreleased build -- or one whose version falls back to
``0.0.0`` -- would link to a tag that does not exist, which is a 404. On
``main`` the worst a later heading rename can do is open the right page at its
top, and a test holds every linked anchor to a heading in this checkout's
``docs/reference/``, so a rename cannot go unnoticed."""

MAX_ROWS: Final = 8
"""Inspector rows listed before the rest are summarized as a count."""

MAX_QUOTED: Final = 60
"""Characters of source quoted (a literal, what ``it`` is) before eliding."""

_SYNTAX: Final = DOCS_URL + "syntax.md"
_OF_LINK: Final = f"[`of` chains]({_SYNTAX}#of-chains-read-right-to-left)"
_WHOSE_LINK: Final = f"[`whose` and `it`]({_SYNTAX}#whose-filters-and-it-refers-to-the-context)"
_CAST_LINK: Final = f"[Casts]({_SYNTAX}#casts-convert-with-as)"
_BAR_LINK: Final = f"[Error fallback]({_SYNTAX}#-is-error-fallback-not-or)"
_STRING_LINK: Final = f"[String literals]({_SYNTAX}#string-literals)"
_TUPLE_LINK: Final = f"[Tuples and collections]({_SYNTAX}#tuples-and-collections)"
_OPERATOR_LINK: Final = f"[Operator spellings]({_SYNTAX}#operator-spellings-collapse)"
_ABSORB_LINK: Final = (
    f"[Errors are values]({DOCS_URL}universal_relevance.md"
    "#errors-are-values-and-some-constructs-absorb-them)"
)
_GUARD_LINK: Final = (
    f"[Only `if` guards]({DOCS_URL}client_relevance.md"
    "#only-if-guards-a-platform-specific-inspector)"
)
_DIALECT_LINKS: Final = {
    Dialect.CLIENT: f"[Client relevance]({DOCS_URL}client_relevance.md)",
    Dialect.SESSION: f"[Session relevance]({DOCS_URL}session_relevance.md)",
}

_NO_HOVER_TOKENS: Final = frozenset({TokenKind.WHITESPACE, TokenKind.COMMENT, TokenKind.ARTICLE})


class Hover(NamedTuple):
    """What to show, and the text of the statement it is about."""

    markdown: str
    span: TextSpan


def describe(analysis: RelevanceAnalysis, offset: int) -> Hover | None:
    """The hover for ``offset`` in ``analysis.text``, or ``None`` if there is none."""
    root = analysis.node
    if root is None:
        return None
    token = _token_at(analysis.tokens, offset)
    if token is None or token.kind in _NO_HOVER_TOKENS:
        return None
    if token.kind is TokenKind.PUNCT and token.text in ("(", ")"):
        return None
    node = node_at(root, offset)
    if node is None:
        return None
    words = _keywords(analysis.tokens, node)
    spelled = " ".join(word.text for word in words) if words else None
    markdown = _markdown(analysis, node, spelled or token.text)
    if markdown is None:
        return None
    if isinstance(node, (Reference, StringLiteral, NumberLiteral, It)):
        span = _ungrouped(analysis.tokens, node)
    elif words:
        span = TextSpan(words[0].offset, _end(words[-1]))
    else:
        # A construct spans its operands; what the cursor is on is its keyword.
        span = TextSpan(token.offset, _end(token))
    return Hover(markdown, span)


def _token_at(tokens: tuple[Token, ...], offset: int) -> Token | None:
    for token in tokens:
        if token.offset <= offset < _end(token):
            return token
    return None


def _end(token: Token) -> int:
    return token.offset + len(token.text)


def _significant(tokens: tuple[Token, ...], start: int, end: int) -> list[Token]:
    """The tokens in ``[start, end)`` that are not trivia or a parenthesis."""
    return [
        token
        for token in tokens
        if start <= token.offset
        and _end(token) <= end
        and token.kind not in _NO_HOVER_TOKENS
        and token.text not in ("(", ")")
    ]


def _keywords(tokens: tuple[Token, ...], node: Node) -> list[Token]:
    """The words a construct is spelled with, as written, when they are one run
    between its operands: ``IS NOT EQUAL TO``, ``NOT EXISTS``, ``as integer``,
    ``item 0 of``. Empty for anything else, which highlights the one token
    under the cursor -- ``if`` ... ``then`` ... ``else`` are three places.

    Read from the tokens because a node keeps its operator normalized
    (``and`` for ``AND``), and the author's spelling is the one to show."""
    match node:
        case Binary(left=left, right=right):
            return _significant(tokens, left.span.end, right.span.start)
        case (
            Unary(operand=operand)
            | Exists(operand=operand)
            | NumberOf(operand=operand)
            | ItemOf(operand=operand)
        ):
            return _significant(tokens, node.span.start, operand.span.start)
        case Cast(operand=operand):
            return _significant(tokens, operand.span.end, node.span.end)
    return []


def _ungrouped(tokens: tuple[Token, ...], node: Node) -> TextSpan:
    """A leaf's span without the grouping parentheses the parser folds into it.

    ``exists (1)`` gives the ``1`` the span ``(1)``. Pairs come off only from
    both ends at once, so an index's own parentheses -- ``file ("x")`` -- stay.
    """
    inside = [
        token
        for token in tokens
        if node.span.start <= token.offset
        and _end(token) <= node.span.end
        and token.kind not in _NO_HOVER_TOKENS
    ]
    while len(inside) > 2 and inside[0].text == "(" and inside[-1].text == ")":
        inside = inside[1:-1]
    if not inside:
        return TextSpan(node.span.start, node.span.end)
    return TextSpan(inside[0].offset, _end(inside[-1]))


def _markdown(analysis: RelevanceAnalysis, node: Node, spelled: str) -> str | None:
    """``spelled`` is what the author wrote: the construct's words (see
    :func:`_keywords`), else the token under the cursor. Every title shows the
    author's spelling, so two hovers in one document never disagree on it."""
    match node:
        case Reference():
            return _reference(analysis, node)
        case StringLiteral(text=text):
            return _lines(f"{_code(_elide(text))} - **string** literal", _STRING_LINK)
        case NumberLiteral():
            return _number(node)
        case It():
            return _it(analysis, node, spelled)
        case Of():
            return _lines(
                f"**{_code(spelled)}** - property access: the left side is a property of the "
                "right side",
                _OF_LINK,
            )
        case Whose():
            return _lines(
                f"**{_code(spelled)}** - filter: keeps the values on its left for which the "
                "condition in parentheses is true, with `it` as each value",
                _WHOSE_LINK,
            )
        case Cast(target=target):
            written = _code(spelled)
            return _lines(f"**{written}** - cast to `{target}`", _CAST_LINK)
        case Bar():
            return _lines(
                f"**{_code(spelled)}** - error fallback: the right side is evaluated only when "
                "the left side errors",
                _BAR_LINK,
            )
        case Binary():
            return _lines(f"**{_code(spelled)}** - binary operator", _OPERATOR_LINK)
        case Unary():
            return _lines(f"**{_code(spelled)}** - unary operator", _OPERATOR_LINK)
        case Exists(negated=negated):
            written = _code(spelled)
            meaning = "no value" if negated else "at least one value"
            return _lines(f"**{written}** - true when its operand has {meaning}", _ABSORB_LINK)
        case NumberOf():
            return _lines(f"**{_code(spelled)}** - how many values its operand has", _ABSORB_LINK)
        case ItemOf(index=index):
            return _lines(
                f"**{_code(spelled)}** - tuple element {index.text}, counting from 0", _TUPLE_LINK
            )
        case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
            # Three keywords in three places, each in the author's spelling.
            tokens = analysis.tokens
            keywords = [
                _significant(tokens, start, end)
                for start, end in (
                    (node.span.start, condition.span.start),
                    (condition.span.end, then_branch.span.start),
                    (then_branch.span.end, else_branch.span.start),
                )
            ]
            spelled_if, spelled_then, spelled_else = (
                words[0].text if words else default
                for words, default in zip(keywords, ("if", "then", "else"), strict=True)
            )
            return _lines(
                f"**{_code(spelled_if)} ... {_code(spelled_then)} ... {_code(spelled_else)}** "
                "- conditional expression",
                _GUARD_LINK,
            )
        case TupleExpr(items=items):
            return _lines(f"**{_code(spelled)}** - tuple of {len(items)} items", _TUPLE_LINK)
        case Collection(items=items):
            return _lines(
                f"**{_code(spelled)}** - collection of {len(items)} expressions", _TUPLE_LINK
            )
    return None


def _reference(analysis: RelevanceAnalysis, node: Reference) -> str:
    report = next((r for r in analysis.references if r.reference is node), None)
    title = f"**{_code(_written_name(analysis, node))}**"
    if report is None or not report.known:
        return f"{title} - not defined in any inspector table this analyzer knows"
    rows = report.resolved
    if len(rows) == 1 and (report.narrowed or report.visible):
        what = "inspector"
    elif report.narrowed:
        what = f"inspector, {len(rows)} overloads here"
    elif report.visible:
        what = f"inspector, one of {len(rows)} definitions"
    else:
        what = _not_visible(analysis, report)
    listed = [f"- {_row(row, node.phrase)}" for row in rows[:MAX_ROWS]]
    if len(rows) > MAX_ROWS:
        listed.append(f"- ... and {len(rows) - MAX_ROWS} more")
    return _lines(f"{title} - {what}", "\n".join(listed), _DIALECT_LINKS.get(analysis.dialect))


def _written_name(analysis: RelevanceAnalysis, node: Reference) -> str:
    """The name as the author wrote it -- its words, without an index argument,
    joined by one space -- rather than the case-folded :attr:`Reference.phrase`."""
    stop = node.index.span.start if node.index is not None else node.span.end
    words = [
        token.text
        for token in analysis.tokens
        if token.kind is TokenKind.WORD and node.span.start <= token.offset < stop
    ]
    return " ".join(words) or node.phrase


def _not_visible(analysis: RelevanceAnalysis, report: ReferenceReport) -> str:
    """Why a name some table defines resolves to nothing here.

    :attr:`~bigfix_relevance_analyzer.analyzer.ReferenceReport.visible` is
    empty for two reasons: the name is the other dialect's, or the platform
    selected rules out every row of this one. Naming the dialect is only true
    for the first, and only when the analysis settled on one.
    """
    dialect = analysis.dialect
    platform = analysis.environment.platform
    if platform is not None and any(dialect in row.dialects for row in report.matches):
        return f"defined, but not on {platform}"
    if dialect in _DIALECT_LINKS:
        return f"defined, but not in {dialect.value} relevance"
    return "defined, but not visible here"


def _row(row: inspectors.Inspector, phrase: str) -> str:
    """One table row: signature, what it returns, and where it is defined."""
    # The plurality of the expression, which is the spelling's -- not the row's
    # usual form (`keys` over `key <string> of <registry>` is plural). Only a
    # row that records no matching spelling falls back to its own fact.
    written = inspectors.written_form_of(row, phrase)
    if written is not inspectors.WrittenForm.UNKNOWN:
        plurality = f", {written.value}"
    elif row.multivalued is not None:
        plurality = ", plural" if row.multivalued else ", singular"
    else:
        plurality = ""
    where = []
    if row.platforms:
        where.append("client: " + ", ".join(sorted(row.platforms)))
    session = sorted(
        context.removeprefix("session:")
        for context in row.contexts
        if context.startswith("session:")
    )
    if session:
        where.append("session: " + ", ".join(session))
    defined = f" - {'; '.join(where)}" if where else ""
    return f"{_code(row.signature)} -> {_code(row.return_type)}{plurality}{defined}"


def _number(node: NumberLiteral) -> str:
    kind = node.kind
    if kind is NumberKind.INTEGER:
        return f"{_code(node.text)} - **integer** literal"
    return f"{_code(_elide(node.text))} - **{kind.value}** literal"


def _it(analysis: RelevanceAnalysis, node: It, spelled: str) -> str:
    title = f"**{_code(spelled)}**"
    binding = next((b for b in analysis.it_bindings if b.it is node), None)
    if binding is None or binding.context is None or binding.binder is None:
        if _is_an_object(analysis, node):
            return _lines(
                f"{title} - nothing binds it here: it is on the right of an `of`, as the "
                "object, and only the left side of an `of` or a `whose` condition binds `it`",
                _WHOSE_LINK,
            )
        return _lines(
            f"{title} - nothing binds it here: there is no `of` or `whose` around it",
            _WHOSE_LINK,
        )
    context = analysis.text[binding.context.span.start : binding.context.span.end]
    quoted = _code(_elide(" ".join(context.split())))
    if binding.binder is Binder.WHOSE:
        return _lines(f"{title} - each value of {quoted}, bound by `whose`", _WHOSE_LINK)
    return _lines(f"{title} - {quoted}, bound by `of`", _WHOSE_LINK)


def _is_an_object(analysis: RelevanceAnalysis, node: It) -> bool:
    """Whether ``node`` sits in the object (right side) of some ``of``."""
    assert analysis.node is not None
    chain = nodes_at(analysis.node, node.span.start)
    return any(
        isinstance(parent, Of) and child is parent.obj
        for parent, child in itertools.pairwise(chain)
    )


def _lines(*parts: str | None) -> str:
    return "\n\n".join(part for part in parts if part)


def _elide(text: str) -> str:
    return text if len(text) <= MAX_QUOTED else text[: MAX_QUOTED - 3] + "..."


def _code(text: str) -> str:
    """``text`` as one Markdown code span, whatever backticks it holds."""
    longest = run = 0
    for char in text:
        run = run + 1 if char == "`" else 0
        longest = max(longest, run)
    fence = "`" * (longest + 1)
    if longest:
        return f"{fence} {text} {fence}"
    return f"{fence}{text}{fence}"
