"""AST nodes for BigFix Relevance, plus their S-expression serialization.

Nodes are pure data: frozen dataclasses with no behavior, so that the tree
shape -- not any Python method -- is the contract a future port (the README
names Rust) has to reproduce. ``to_sexpr`` is a module-level function for
the same reason.

Every node carries a :class:`Span` over the source text. Spans are excluded
from S-expressions so the parse-tree corpus stays stable under reformatting
of the input.

Design decisions pinned here
----------------------------
* Literals keep their **verbatim text**: no float conversion, no ``%22``
  decoding, quotes included on :class:`StringLiteral`. The S-expression form
  strips a string's delimiting quotes for readability, nothing more.
* Operators keep their **written spelling**: ``a is b`` is ``Binary("is")``,
  not a canonicalized ``=``. Canonicalization is a later, separate pass.
* Tuples (``,``) and collections (``;``) are **flattened**: relevance has no
  nested tuple type, ``((a, b), c)`` and ``(a, b, c)`` are the same value.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Binary",
    "Cast",
    "Collection",
    "Exists",
    "If",
    "It",
    "Node",
    "NumberLiteral",
    "Of",
    "Reference",
    "Span",
    "StringLiteral",
    "TupleExpr",
    "Unary",
    "Whose",
    "to_sexpr",
]


@dataclass(frozen=True, slots=True)
class Span:
    """Where a node's text sits in the source."""

    start: int
    """0-based character offset, inclusive."""

    end: int
    """0-based character offset, exclusive."""

    line: int
    """1-based line of the first character."""

    column: int
    """1-based column of the first character."""


@dataclass(frozen=True, slots=True)
class NumberLiteral:
    """A numeric literal, kept verbatim: ``42``, ``1.5``."""

    span: Span
    text: str


@dataclass(frozen=True, slots=True)
class StringLiteral:
    """A string literal, quotes included and ``%xx`` escapes untouched."""

    span: Span
    text: str

    @property
    def content(self) -> str:
        """The text between the quotes, still with ``%xx`` escapes intact."""
        return self.text[1:-1]


@dataclass(frozen=True, slots=True)
class It:
    """The closure variable ``it``."""

    span: Span


@dataclass(frozen=True, slots=True)
class Reference:
    """A property or object name, with its optional single index argument.

    ``phrase`` is the case-folded, single-space-joined name -- ``operating
    system``, ``key``, ``substrings separated by``. ``index`` is the argument
    written between the name and any ``of``: the string in ``key "foo"``,
    the number in ``item 0``, the parenthesized expression in
    ``file (pathname of it)``.
    """

    span: Span
    phrase: str
    index: Node | None = None


@dataclass(frozen=True, slots=True)
class Of:
    """``prop of obj``. Right-associative: ``a of b of c`` is ``a of (b of c)``."""

    span: Span
    prop: Node
    obj: Node


@dataclass(frozen=True, slots=True)
class Binary:
    """Any infix operator, in its written spelling: ``+``, ``and``, ``is
    contained by``, ``|``, ``!=``."""

    span: Span
    op: str
    left: Node
    right: Node


@dataclass(frozen=True, slots=True)
class Unary:
    """A prefix operator: ``-`` or ``not``."""

    span: Span
    op: str
    operand: Node


@dataclass(frozen=True, slots=True)
class Exists:
    """``exists x`` or ``not exists x`` (and the singular ``exist``)."""

    span: Span
    negated: bool
    operand: Node


@dataclass(frozen=True, slots=True)
class Whose:
    """``collection whose (predicate)``."""

    span: Span
    collection: Node
    predicate: Node


@dataclass(frozen=True, slots=True)
class Cast:
    """``operand as target``. Chains left: ``it as string as lowercase`` is
    ``Cast(Cast(it, "string"), "lowercase")``."""

    span: Span
    operand: Node
    target: str


@dataclass(frozen=True, slots=True)
class If:
    """``if condition then then_branch else else_branch``. An expression;
    relevance requires the ``else``."""

    span: Span
    condition: Node
    then_branch: Node
    else_branch: Node


@dataclass(frozen=True, slots=True)
class TupleExpr:
    """A ``,`` tuple, flattened: always two or more items."""

    span: Span
    items: tuple[Node, ...]


@dataclass(frozen=True, slots=True)
class Collection:
    """A ``;`` collection, flattened: always two or more items."""

    span: Span
    items: tuple[Node, ...]


Node = (
    NumberLiteral
    | StringLiteral
    | It
    | Reference
    | Of
    | Binary
    | Unary
    | Exists
    | Whose
    | Cast
    | If
    | TupleExpr
    | Collection
)


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_sexpr(node: Node) -> str:
    """Serialize a tree to the S-expression form the corpus is written in."""
    match node:
        case NumberLiteral(text=text):
            return f"(num {_quote(text)})"
        case StringLiteral():
            return f"(str {_quote(node.content)})"
        case It():
            return "it"
        case Reference(phrase=phrase, index=None):
            return f"(ref {_quote(phrase)})"
        case Reference(phrase=phrase, index=index):
            assert index is not None
            return f"(ref {_quote(phrase)} {to_sexpr(index)})"
        case Of(prop=prop, obj=obj):
            return f"(of {to_sexpr(prop)} {to_sexpr(obj)})"
        case Binary(op=op, left=left, right=right):
            return f"(bin {_quote(op)} {to_sexpr(left)} {to_sexpr(right)})"
        case Unary(op=op, operand=operand):
            return f"(un {_quote(op)} {to_sexpr(operand)})"
        case Exists(negated=negated, operand=operand):
            head = "not-exists" if negated else "exists"
            return f"({head} {to_sexpr(operand)})"
        case Whose(collection=collection, predicate=predicate):
            return f"(whose {to_sexpr(collection)} {to_sexpr(predicate)})"
        case Cast(operand=operand, target=target):
            return f"(cast {to_sexpr(operand)} {_quote(target)})"
        case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
            return f"(if {to_sexpr(condition)} {to_sexpr(then_branch)} {to_sexpr(else_branch)})"
        case TupleExpr(items=items):
            return f"(tuple {' '.join(to_sexpr(item) for item in items)})"
        case Collection(items=items):
            return f"(coll {' '.join(to_sexpr(item) for item in items)})"
