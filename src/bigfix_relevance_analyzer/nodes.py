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
from collections.abc import Callable, Generator, Iterator
from dataclasses import dataclass
from itertools import count
from typing import Any, Final, NamedTuple, TypeVar, assert_never

__all__ = [
    "MAX_INTEGER",
    "MAX_LARGE_INTEGER",
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
    "children",
    "to_mermaid",
    "to_sexpr",
    "tree_depth",
    "walk",
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

MAX_LARGE_INTEGER: Final = 2**128 - 1
"""Largest value the engine can parse a numeral into at all, above which a
literal is rejected outright rather than typed.

Confirmed live against qna 11.0.6.137: ``item 340282366920938463463374607431768211455
of (1,2,3)`` types and evaluates the literal (as a ``large integer``, in every
context, not only as a tuple index); ``item 340282366920938463463374607431768211456
of (1,2,3)`` -- one more -- fails to parse at all, with ``An integer constant was
too large.``, regardless of where the literal appears (a bare literal or
arithmetic fail identically). The boundary is exactly ``2**128 - 1``, i.e.
unsigned 128-bit range; see :attr:`NumberKind.CONSTANT_TOO_LARGE`.
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
    """Whole, but beyond :data:`MAX_INTEGER`. Still a real, usable literal of
    this type everywhere -- confirmed live, it evaluates fine as a bare value
    or in arithmetic. The one place it is refused is as a tuple index, and even
    there the engine's own message is identical to :attr:`NOT_AN_INTEGER`'s
    (``"...was not an integer literal."``); it does not, contrary to an earlier
    assumption here, complain separately about a literal that is merely too big
    to index with."""

    CONSTANT_TOO_LARGE = "constant too large"
    """Beyond :data:`MAX_LARGE_INTEGER`: the engine cannot parse this numeral
    into any type at all, in any context -- confirmed live, a bare literal this
    large fails the same way a tuple index does. Its own message, ``"An integer
    constant was too large."``, is genuinely distinct from both
    :attr:`LARGE_INTEGER` and :attr:`NOT_AN_INTEGER`."""

    NOT_AN_INTEGER = "not an integer"
    """Named ``NoInteger`` in the engine, and real as a *value* type --
    ``floating point`` is what a cast like ``"1.5" as floating point`` or
    ``1/2 as floating point`` produces. It is not reachable here, though:
    confirmed live on both engines, relevance has no decimal-point numeral
    syntax at all -- ``1.5``, ``1.``, ``.5`` and ``1 . 3`` are all a lexical
    error (`` "This expression contained a character which is not allowed."
    ``), not a numeral this package's own tokenizer would ever hand a
    :class:`NumberLiteral` -- see ``tokenizer._NOT_WORD_CHARS``. Kept for the
    :class:`NumberKind` enumeration's own completeness against the engine's
    three numeral node classes; :meth:`NumberLiteral.kind` only reaches it
    through the defensive ``not text.isdigit()`` branch, which no tokenized
    input can trigger any more."""


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
    """A numeric literal, kept verbatim: ``42``, ``99999999999999999999``.

    Always a run of digits -- the tokenizer has no decimal-point numeral
    syntax, so ``text`` can never contain ``.``; see :attr:`NumberKind.
    NOT_AN_INTEGER`."""

    span: Span
    text: str

    @property
    def kind(self) -> NumberKind:
        """How the engine would classify this numeral. See :class:`NumberKind`.

        Derived from :attr:`text` rather than stored, so the node stays exactly
        what was written. Literals are never negative here -- ``-1`` parses as
        :class:`Unary` over ``1`` -- so the sign plays no part.
        """
        if not self.text.isdigit():  # defensive: not reachable via the tokenizer/parser
            return NumberKind.NOT_AN_INTEGER
        value = int(self.text)
        if value > MAX_LARGE_INTEGER:
            return NumberKind.CONSTANT_TOO_LARGE
        if value > MAX_INTEGER:
            return NumberKind.LARGE_INTEGER
        return NumberKind.INTEGER

    @property
    def is_integer_literal(self) -> bool:
        """Whether this is written as a whole number, of any magnitude.

        The distinction a tuple index turns on: the parser needs to tell a
        tuple subscript from the real `item <string> of <folder>` property by
        the index's written form alone (see :func:`parser._of`), before any
        magnitude check runs. A numeral too large even to parse is still
        written as a whole number, so it counts here too -- the checker is
        what tells :attr:`~NumberKind.LARGE_INTEGER` and
        :attr:`~NumberKind.CONSTANT_TOO_LARGE` apart from there, since each has
        its own, distinct, confirmed message.
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
    prop_grouped: bool = False
    """Whether ``prop`` was written inside its own parentheses.

    Semantic, not cosmetic. Parentheses make ``prop`` a standalone expression
    evaluated with ``it`` bound to ``obj``, so ``obj`` stops being a direct
    object and the name must resolve against the world::

        Q: computer name of file "/etc/hosts"
        E: The operator "computer name" is not defined.
        Q: (computer name) of file "/etc/hosts"
        A: Laptop (796)

    Deliberately absent from :func:`to_sexpr`: the parse-tree corpus pins the
    grammar's shape, and this is a fact *about* a shape the corpus already
    distinguishes by where its parens fall.
    """


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
    plural: bool = False
    """Whether it was written ``items N of``.

    The two spellings index the same position; only the plurality of the
    answer differs, and the engine settles that from the spelling alone --
    the tuple being singular does not make ``items`` singular::

        Q: (item 1 of ("a","b")) | "x"
        A: b
        Q: (items 1 of ("a","b")) | "x"
        E: A singular expression is required.
    """


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


def children(node: Node) -> tuple[Node, ...]:
    """The direct child nodes of ``node``, in source order.

    An explicit ``match`` rather than reflection over dataclass fields, so the
    node classes stay pure data and adding one is a type error here until it
    is handled.
    """
    match node:
        case NumberLiteral() | StringLiteral() | It():
            return ()
        case Reference(index=index):
            return () if index is None else (index,)
        case Of(prop=prop, obj=obj):
            return (prop, obj)
        case ItemOf(index=index, operand=operand):
            return (index, operand)
        case NumberOf(operand=operand) | Unary(operand=operand) | Exists(operand=operand):
            return (operand,)
        case Cast(operand=operand):
            return (operand,)
        case Bar(left=left, right=right) | Binary(left=left, right=right):
            return (left, right)
        case Whose(collection=collection, predicate=predicate):
            return (collection, predicate)
        case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
            return (condition, then_branch, else_branch)
        case TupleExpr(items=items) | Collection(items=items):
            return items
        case _:
            assert_never(node)


def walk(node: Node) -> Iterator[Node]:
    """Every node in the tree, pre-order: parents before children, siblings in
    source order.

    Iterative, as every whole-tree pass here is: a left-associative chain such
    as a long ``or`` parses within the parser's nesting limit yet builds a tree
    far deeper than CPython's recursion limit, and wild content must never be a
    crash.
    """
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(children(current)))


def tree_depth(node: Node) -> int:
    """The height of the tree, iteratively; a lone leaf is 1."""
    deepest = 0
    stack: list[tuple[Node, int]] = [(node, 1)]
    while stack:
        current, level = stack.pop()
        deepest = max(deepest, level)
        stack.extend((child, level + 1) for child in children(current))
    return deepest


_R = TypeVar("_R")


def _fold(root: Node, step: Callable[[Node], Generator[Node, _R, _R]]) -> _R:
    """Run a recursive fold over the tree without recursing.

    ``step`` is written as if it recursed: a generator that yields each
    child it needs, is sent that child's result back, and returns its
    own. This drives those generators from an explicit stack, so the fold keeps
    the readable recursive shape -- and the exact order its side effects happen
    in -- while surviving trees deeper than the recursion limit. See
    :func:`walk` for why that depth is reachable.
    """
    stack = [step(root)]
    # None primes a freshly pushed generator; otherwise it is the result of the
    # child the top generator is waiting on.
    sent: Any = None
    while True:
        try:
            child = stack[-1].send(sent)
        except StopIteration as done:
            stack.pop()
            value: _R = done.value
            if not stack:
                return value
            sent = value
        else:
            stack.append(step(child))
            sent = None


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _sexpr_step(node: Node) -> Generator[Node, str, str]:
    """One node of :func:`to_sexpr`, as a :func:`_fold` step."""
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
            return f"(ref {_quote(phrase)} {(yield index)})"
        case Of(prop=prop, obj=obj):
            return f"(of {(yield prop)} {(yield obj)})"
        case ItemOf(index=index, operand=operand, plural=plural):
            head = "items-of" if plural else "item-of"
            return f"({head} {(yield index)} {(yield operand)})"
        case NumberOf(operand=operand):
            return f"(number-of {(yield operand)})"
        case Bar(left=left, right=right):
            return f"(bar {(yield left)} {(yield right)})"
        case Binary(op=op, left=left, right=right):
            return f"(bin {_quote(op)} {(yield left)} {(yield right)})"
        case Unary(op=op, operand=operand):
            return f"(un {_quote(op)} {(yield operand)})"
        case Exists(negated=negated, operand=operand):
            head = "not-exists" if negated else "exists"
            return f"({head} {(yield operand)})"
        case Whose(collection=collection, predicate=predicate):
            return f"(whose {(yield collection)} {(yield predicate)})"
        case Cast(operand=operand, target=target):
            return f"(cast {(yield operand)} {_quote(target)})"
        case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
            return f"(if {(yield condition)} {(yield then_branch)} {(yield else_branch)})"
        case TupleExpr(items=items) | Collection(items=items):
            head = "tuple" if isinstance(node, TupleExpr) else "coll"
            parts = []
            for item in items:  # not a comprehension: `yield` is not allowed in one
                parts.append((yield item))
            return f"({head} {' '.join(parts)})"
        case _:
            assert_never(node)


def to_sexpr(node: Node) -> str:
    """Serialize a tree to the S-expression form the corpus is written in."""
    return _fold(node, _sexpr_step)


def _mermaid_escape(text: str) -> str:
    """Make ``text`` safe inside a Mermaid node label: ``id["text"]``.

    Collapses embedded whitespace first -- a string literal's raw content can
    contain a newline, which would otherwise split one node's definition
    across lines -- then escapes the characters Mermaid's own label syntax
    treats specially, using Mermaid's ``#<decimal>;`` numeric-character-
    reference convention (``#34;`` for ``"``), not HTML's ``&name;`` one.

    That distinction is not cosmetic. This same escaped text ends up in two
    different places: a plain-text ` ```mermaid ` fence (the CLI's Markdown
    output), and inside a real ``<pre class="mermaid">`` element in an HTML
    page (an Artifact). A browser HTML-decodes ``&quot;`` back into a literal
    ``"`` *before* Mermaid ever reads the element's text -- so HTML-style
    escaping silently corrupts the diagram the moment it is embedded in HTML,
    even though the same text is fine in a plain fence. ``#34;`` contains no
    ``&``, so no HTML parser touches it either way, and Mermaid decodes it
    identically in both contexts. Confirmed against a real Mermaid render,
    not just inferred from the spec.
    """
    collapsed = " ".join(text.split())
    return (
        collapsed.replace("&", "#38;")
        .replace('"', "#34;")
        .replace("<", "#60;")
        .replace(">", "#62;")
    )


_MERMAID_SHAPES: dict[str, tuple[str, str]] = {
    # Shape carries what a ``ref``/``str``/``num`` label prefix used to: which
    # kind of thing a box is, at a glance, without spending label text on it.
    "rectangle": ('["', '"]'),  # a name: Reference
    "stadium": ('(["', '"])'),  # a literal value: NumberLiteral, StringLiteral
    "rounded": ('("', '")'),  # the closure variable: It
    "hexagon": ('{{"', '"}}'),  # an operator/transform: Binary, Unary, Bar,
    # Cast, Exists, NumberOf, ItemOf, and an explicit (non-collapsed) Of
    "rhombus": ('{"', '"}'),  # a branch point: If, Whose
    "subroutine": ('[["', '"]]'),  # a fixed group: TupleExpr, Collection
}


class _Rendered(NamedTuple):
    """One rendered sub-expression: what flows out of it, and what flows in.

    Two ids rather than one, because for a filtered collection they differ.
    ``files whose (P) of folders`` nests as ``Of(Whose(files, P), folders)``,
    since ``whose`` binds tighter than ``of`` -- but that nesting is not the
    evaluation order. What actually happens is: the folders yield their
    files, *then* ``P`` reduces them. So the incoming object has to reach
    ``files``, not the ``whose`` that wraps it, while the value flowing
    onward is the filtered result at the ``whose``.
    """

    result: str
    """The node id this expression's value flows out of."""

    sink: str
    """The node id an incoming ``of`` object should flow into.

    The same as :attr:`result` for everything except :class:`Whose`, which
    passes it through to whatever it filters -- recursively, so a chained
    ``x whose (a) whose (b)`` still routes an object all the way to ``x``.
    """


def _plain(node_id: str) -> _Rendered:
    """A node an incoming object attaches to directly: everything but ``whose``."""
    return _Rendered(result=node_id, sink=node_id)


def _literal_text(node: Node) -> str | None:
    """The label for ``node`` if it is a literal, else ``None``.

    A number renders bare; a string keeps quotes, so ``key 0`` and ``key
    "0"`` -- a real distinction in relevance -- still read differently once
    folded into a single box. Shared by both the literal-index fold on
    :class:`Reference` and the all-literal fold on :class:`TupleExpr` /
    :class:`Collection`, so the two stay rendered the same way.
    """
    match node:
        case NumberLiteral(text=text):
            return text
        case StringLiteral():
            return f'"{node.content}"'
        case _:
            return None


def to_mermaid(node: Node) -> str:
    """Render a tree as a Mermaid ``flowchart`` -- a real graph, not prose.

    Walks the actual parsed tree and emits one line per node and edge from
    that structure, the same way :func:`to_sexpr` does -- nothing here is
    approximated or hand-drawn. Node ids are a plain sequential counter
    (``n0``, ``n1``, ...) assigned during one fixed depth-first walk, the
    same field order :func:`to_sexpr` uses; a side effect of that -- not the
    point of it -- is that the same tree always renders identically.

    Unlike :func:`to_sexpr`, this is not a 1:1 rendering of every node --
    that reads as scaffolding once a chain gets long, and the point of a
    *diagram* is to be legible, not exhaustively faithful; :func:`to_sexpr`
    already is that, in text. Three things fold, none of them losing
    information:

    * An ``Of`` chain is linear, because ``Of`` is right-associative -- ``a
      of b of c`` is ``a of (b of c)``, never a branch -- so it draws as
      ``a -- "of" --> b -- "of" --> c`` instead of three ``of`` boxes plus
      three leaves. The one case that is *not* this shape, an explicitly
      parenthesized ``(a of b) of c``, keeps its own ``of`` box, since
      collapsing it would hang two ``of`` edges off ``a`` and read as the
      chain it is not.
    * A :class:`Reference`'s index folds into its own label when the index
      is a literal (``key 0``, ``firsts "\\Sites\\"``) -- a name and a
      constant read as one term. A non-literal index (``file (pathname of
      it)``) keeps its separate box; that genuinely is a sub-expression.
    * A :class:`TupleExpr` / :class:`Collection` whose members are all
      literals folds to one box listing them, instead of one box per member
      of what is really a single value (a set of extensions, a list of
      paths).

    What used to be a label prefix (``ref``, ``str``, ``num``) is now a node
    shape instead, so a folded label still reads like source: a rectangle is
    a name, a stadium a literal, a hexagon an operator or transform, a
    rhombus a branch point (``if``, ``whose``), a subroutine box a fixed
    group. No truncation and no size limit otherwise -- a large tree still
    makes a large diagram, just a smaller one than before.

    Laid out top-down (``TD``), and arrows point the way evaluation actually
    flows, not the way the tree nests. ``Of``'s object has to resolve before
    its property can be read off it -- relevance itself reads right-to-left,
    the same right-associativity above -- so an edge is drawn from the
    operand *to* the thing that consumes it (object into property, condition
    into ``if``, items into a tuple), never the reverse. The practical
    consequence: a long chain's ultimate starting point -- the innermost
    object, e.g. a bare path at the end of a long ``of`` chain -- lands at
    the *top* of the diagram, with the final result at the bottom, which is
    what makes ``TD`` read as a flowchart rather than upside down. (``TD``
    itself is still the right call over a left/right layout for the reason
    given above: a deep tree stays legible top-down in a way it would not
    running off the side.)

    Following evaluation rather than nesting is also why an object routes
    *past* a ``whose`` to the collection it filters. ``files whose (P) of
    folders`` nests as ``Of(Whose(files, P), folders)``, but nothing about
    the folders flows into the filter: the folders yield their files, and
    only then does ``P`` reduce them. So the diagram draws ``folders --of-->
    files --collection--> whose``, and it is the ``whose`` -- the reduced
    set -- that flows onward. See :class:`_Rendered`.
    """
    lines = ["flowchart TD"]
    counter = count()

    def emit(label: str, shape: str = "rectangle") -> str:
        node_id = f"n{next(counter)}"
        opening, closing = _MERMAID_SHAPES[shape]
        lines.append(f"    {node_id}{opening}{_mermaid_escape(label)}{closing}")
        return node_id

    def edge(consumer: str, operand: str, label: str | None = None) -> None:
        # Drawn operand -> consumer, not consumer -> operand: the arrow is
        # evaluation flow (what feeds what), which runs opposite the tree's
        # own parent/child direction. See the flow-direction paragraph above.
        arrow = f'-- "{_mermaid_escape(label)}" -->' if label else "-->"
        lines.append(f"    {operand} {arrow} {consumer}")

    def literal_group(items: tuple[Node, ...]) -> str | None:
        """The folded label for an all-literal tuple/collection, else None."""
        texts = [_literal_text(item) for item in items]
        if any(text is None for text in texts):
            return None
        return "; ".join(text for text in texts if text is not None)

    def step(node: Node) -> Generator[Node, _Rendered, _Rendered]:
        # A _fold step: `(yield child)` renders `child` and hands back its
        # _Rendered, in exactly the order a recursive walk would.
        match node:
            case NumberLiteral() | StringLiteral():
                text = _literal_text(node)
                assert text is not None
                return _plain(emit(text, "stadium"))
            case It():
                return _plain(emit("it", "rounded"))
            case Reference(phrase=phrase, index=None):
                return _plain(emit(phrase))
            case Reference(phrase=phrase, index=index):
                assert index is not None
                literal = _literal_text(index)
                if literal is not None:
                    return _plain(emit(f"{phrase} {literal}"))
                me = emit(phrase)
                edge(me, (yield index).result, "index")
                return _plain(me)
            case Of(prop=prop, obj=obj) if isinstance(prop, Of):
                # An explicit (a of b) of c: collapsing would hang two `of`
                # edges off `a`, which is the shape of `a of b of c` instead.
                me = emit("of", "hexagon")
                edge(me, (yield prop).result, "prop")
                edge(me, (yield obj).result, "obj")
                return _plain(me)
            case Of(prop=prop, obj=obj):
                # The object flows into the property's *sink*, which is the
                # property itself unless a `whose` wraps it -- see _Rendered.
                rendered_prop = yield prop
                rendered_obj = yield obj
                edge(rendered_prop.sink, rendered_obj.result, "of")
                return _Rendered(result=rendered_prop.result, sink=rendered_obj.sink)
            case ItemOf(index=index, operand=operand, plural=plural):
                me = emit("items of" if plural else "item of", "hexagon")
                edge(me, (yield index).result, "index")
                edge(me, (yield operand).result, "of")
                return _plain(me)
            case Bar(left=left, right=right) | Binary(left=left, right=right):
                me = emit(node.op if isinstance(node, Binary) else "|", "hexagon")
                edge(me, (yield left).result)
                edge(me, (yield right).result)
                return _plain(me)
            case NumberOf(operand=operand) | Unary(operand=operand) | Exists(operand=operand):
                match node:
                    case NumberOf():
                        label = "number of"
                    case Unary(op=op):
                        label = op
                    case Exists(negated=negated):
                        label = "not exists" if negated else "exists"
                me = emit(label, "hexagon")
                edge(me, (yield operand).result)
                return _plain(me)
            case Whose(collection=collection, predicate=predicate):
                # The filtered collection flows *through* here: an object
                # arriving from an enclosing `of` belongs to what is being
                # filtered, so this passes that collection's sink onward.
                me = emit("whose", "rhombus")
                rendered_collection = yield collection
                edge(me, rendered_collection.result, "collection")
                edge(me, (yield predicate).result, "predicate")
                return _Rendered(result=me, sink=rendered_collection.sink)
            case Cast(operand=operand, target=target):
                me = emit(f"as {target}", "hexagon")
                edge(me, (yield operand).result)
                return _plain(me)
            case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
                me = emit("if", "rhombus")
                edge(me, (yield condition).result, "condition")
                edge(me, (yield then_branch).result, "then")
                edge(me, (yield else_branch).result, "else")
                return _plain(me)
            case TupleExpr(items=items) | Collection(items=items):
                group = literal_group(items)
                if group is not None:
                    return _plain(emit(group, "subroutine"))
                me = emit("tuple" if isinstance(node, TupleExpr) else ";", "subroutine")
                for item in items:
                    edge(me, (yield item).result)
                return _plain(me)
            case _:
                assert_never(node)

    _fold(node, step)
    return "\n".join(lines)
