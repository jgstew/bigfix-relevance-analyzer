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

import enum
from dataclasses import dataclass
from typing import Final

__all__ = [
    "MAX_INTEGER",
    "Bar",
    "Binary",
    "Cast",
    "Collection",
    "Exists",
    "If",
    "It",
    "ItemOf",
    "Node",
    "NumberKind",
    "NumberLiteral",
    "NumberOf",
    "Of",
    "Reference",
    "Span",
    "StringLiteral",
    "TupleExpr",
    "Unary",
    "Whose",
    "to_sexpr",
]

MAX_INTEGER: Final = 2**63 - 1
"""Largest value the engine's ``integer`` type holds, above which a literal is a
``large integer``.

[INFER] Read off the type table, where ``integer`` reports ``size`` 8 bytes and
``large integer`` reports 24 -- so the boundary is a signed 64-bit one. It has
not been confirmed against a running engine, and there is a known loose end: the
engine also defines ``uinteger`` at 8 bytes, so an unsigned literal's real
ceiling may be ``2**64 - 1``. A literal between the two is classified
:attr:`NumberKind.LARGE_INTEGER` here and might be a ``uinteger`` there.
"""


class NumberKind(enum.Enum):
    """How the engine classifies a numeral, by magnitude, at parse time.

    The engine has three separate node classes for numerals rather than one --
    ``IntegerExpression``, ``LargeIntegerExpression`` and ``NoIntegerExpression``
    -- so a numeral's type is settled while parsing, not during evaluation.

    This package keeps one :class:`NumberLiteral` holding verbatim text and
    derives the classification from it. That was a deliberate choice: the tree
    stays lossless and the S-expression corpus stays stable, and nothing is
    gained by splitting a node whose only difference is a fact about its own
    text. The classification is still available without any type information,
    which is what "at parse time" was really buying.
    """

    INTEGER = "integer"
    """Whole, and within :data:`MAX_INTEGER`."""

    LARGE_INTEGER = "large integer"
    """Whole, but beyond :data:`MAX_INTEGER`."""

    NOT_AN_INTEGER = "not an integer"
    """Not whole -- a decimal literal, which the engine types as
    ``floating point``. Named ``NoInteger`` in the engine."""


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

    @property
    def kind(self) -> NumberKind:
        """How the engine would classify this numeral. See :class:`NumberKind`.

        Derived from :attr:`text` rather than stored, so the node stays exactly
        what was written. Literals are never negative here -- ``-1`` parses as
        :class:`Unary` over ``1`` -- so the sign plays no part.
        """
        if not self.text.isdigit():
            return NumberKind.NOT_AN_INTEGER
        if int(self.text) > MAX_INTEGER:
            return NumberKind.LARGE_INTEGER
        return NumberKind.INTEGER

    @property
    def is_integer_literal(self) -> bool:
        """Whether this is a whole number, of any magnitude.

        The distinction a tuple index turns on: the engine requires an integer
        literal there, and complains separately about one that is merely too big.
        """
        return self.kind is not NumberKind.NOT_AN_INTEGER


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
class ItemOf:
    """``item N of tuple`` -- indexing a tuple, which is not a property access.

    The index is **0-based**, must be an integer literal, and is bounds-checked
    against the tuple's arity while type checking rather than at evaluation.
    None of those rules have anywhere to attach on a generic
    :class:`Reference` plus :class:`Of`, which is why this is its own node.

    Only an integer-literal index produces this node. ``item`` is also a real
    property -- ``item <string> of <folder>`` yields a filesystem object -- and
    telling that apart from a tuple index needs the direct object's type, which
    this parser deliberately does not consult. So a string index stays a
    :class:`Reference`, on the package's usual rule of drawing only positive
    conclusions.
    """

    span: Span
    index: NumberLiteral
    operand: Node


@dataclass(frozen=True, slots=True)
class NumberOf:
    """``number of x`` -- aggregation, the sibling of :class:`Exists`.

    The engine unifies the two into a single ``AggregateExpression``: counting
    and testing for existence are one concept with two spellings. ``exists`` was
    already a node here and this was not, which left aggregation only half
    visible to anything walking the tree.
    """

    span: Span
    operand: Node


@dataclass(frozen=True, slots=True)
class Bar:
    """``left | right`` -- error fallback, not an ordinary operator.

    The right side is evaluated only when the left one *errors*:
    ``size of file "C:\\nope.txt" | 42`` is ``42``, while ``1 | 2`` is ``1``.
    Typing is still enforced across it (``"a" | 42`` is an error), but no row
    for ``|`` exists in the engine's binary-operator table, so anything
    resolving operators by lookup will not find it. Cost and evaluation-order
    analysis need to know the right side is conditional, too.
    """

    span: Span
    left: Node
    right: Node


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
    | ItemOf
    | NumberOf
    | Bar
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
        case ItemOf(index=index, operand=operand):
            return f"(item-of {to_sexpr(index)} {to_sexpr(operand)})"
        case NumberOf(operand=operand):
            return f"(number-of {to_sexpr(operand)})"
        case Bar(left=left, right=right):
            return f"(bar {to_sexpr(left)} {to_sexpr(right)})"
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
