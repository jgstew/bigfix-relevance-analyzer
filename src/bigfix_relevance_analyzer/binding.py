"""What each ``it`` in an expression refers to.

``it`` is relevance's closure variable, and resolving it is a **separate pass
over the parsed tree**, not part of parsing -- the same split the BigFix Fixlet
Debugger makes, where ``BreakdownItTracker`` is its own visitor rather than a
parser action. Nothing here touches :mod:`bigfix_relevance_analyzer.parser`.

The binding rule, and the error message that describes it wrongly
------------------------------------------------------------------
The engine's user-visible diagnostic is ``"It" used outside of "whose" clause.``
**That message is wrong**, and following it produces a resolver that disagrees
with the evaluator. ``it`` binds to the nearest enclosing *context-introducing*
construct, and there are two of them:

* ``X whose (P)`` -- inside ``P``, ``it`` is the element of ``X`` being filtered.
* ``A of B`` -- inside ``A``, ``it`` is ``B``.

``of`` really does bind it: ``(it, it) of 5`` evaluates to ``5, 5``, and
``name of it of file "..."`` gives the file's name. ``if/then/else`` introduces
nothing and passes its enclosing context through to all three branches, so
``if true then it else it`` is an error at the top level. The engine's own
internal template is the accurate wording -- see
:data:`bigfix_relevance_analyzer.diagnostics.DIAGNOSTICS`\\ ``["used-without-context"]``.

Evidence for the rule, and for the nesting cases, is recorded in
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_.

Order of the walk matters
-------------------------
For ``A of B`` the object ``B`` is **not** evaluated in its own context: it sees
whatever context encloses the whole ``of``. Only ``A`` sees ``B``. Getting this
backwards silently binds the wrong node in every nested expression, which is why
it is spelled out here rather than left to the traversal.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import assert_never

from bigfix_relevance_analyzer.nodes import (
    Binary,
    Cast,
    Collection,
    Exists,
    If,
    It,
    Node,
    NumberLiteral,
    Of,
    Reference,
    StringLiteral,
    TupleExpr,
    Unary,
    Whose,
)

__all__ = [
    "Binder",
    "ItBinding",
    "resolve_it_bindings",
]


class Binder(enum.Enum):
    """Which construct introduced the context an ``it`` binds to."""

    OF = "of"
    """``A of B``: inside ``A``, ``it`` is ``B``."""

    WHOSE = "whose"
    """``X whose (P)``: inside ``P``, ``it`` is an element of ``X``."""


@dataclass(frozen=True, slots=True)
class ItBinding:
    """One ``it`` in the source, and what it refers to."""

    it: It
    """The ``it`` node itself. Its :attr:`~bigfix_relevance_analyzer.nodes.It.span`
    is where to highlight."""

    context: Node | None
    """The node supplying the context, or ``None`` when there is none.

    ``None`` means the expression is in error: this ``it`` was used without a
    context. It is reported rather than raised, because a resolver that stops at
    the first unbound ``it`` is useless to an editor colorizing as you type.
    """

    binder: Binder | None
    """Which construct bound it, or ``None`` alongside a ``None`` context."""


def resolve_it_bindings(node: Node) -> tuple[ItBinding, ...]:
    """Every ``it`` in the tree, in source order, with what it refers to.

    Returns a tuple rather than a mapping: it is the shape both consumers want
    -- an editor highlighting the selection, and a checker walking the tree in
    order -- and unbound occurrences are simply the entries whose
    :attr:`ItBinding.context` is ``None``, rather than a second return value
    that callers can forget to look at.

    The walk keeps its own stack instead of recursing. Relevance permits
    expression trees 1000 levels deep, past CPython's default recursion limit,
    and this package's discipline is that wild content is never a crash.
    """
    found: list[ItBinding] = []
    # (node, the context it is evaluated in, which construct supplied it)
    stack: list[tuple[Node, Node | None, Binder | None]] = [(node, None, None)]

    while stack:
        current, context, binder = stack.pop()
        match current:
            case It():
                found.append(ItBinding(it=current, context=context, binder=binder))
            case Of(prop=prop, obj=obj):
                # `obj` sees the *enclosing* context, not its own. Pushed last so
                # it is popped last, which keeps `prop` -- the earlier text -- first.
                stack.append((obj, context, binder))
                stack.append((prop, obj, Binder.OF))
            case Whose(collection=collection, predicate=predicate):
                stack.append((predicate, collection, Binder.WHOSE))
                stack.append((collection, context, binder))
            case Reference(index=index):
                if index is not None:
                    stack.append((index, context, binder))
            case Binary(left=left, right=right):
                stack.append((right, context, binder))
                stack.append((left, context, binder))
            case Unary(operand=operand) | Exists(operand=operand) | Cast(operand=operand):
                stack.append((operand, context, binder))
            case If(condition=condition, then_branch=then_branch, else_branch=else_branch):
                # `if` introduces no context of its own; all three branches see
                # whatever encloses the `if`.
                stack.append((else_branch, context, binder))
                stack.append((then_branch, context, binder))
                stack.append((condition, context, binder))
            case TupleExpr(items=items) | Collection(items=items):
                for item in reversed(items):
                    stack.append((item, context, binder))
            case NumberLiteral() | StringLiteral():
                pass
            case _:  # pragma: no cover - exhaustiveness over the Node union
                assert_never(current)

    # The traversal already yields source order; sorting says so rather than
    # leaving it as a property of the push order that a later edit could break.
    found.sort(key=lambda binding: (binding.it.span.start, binding.it.span.end))
    return tuple(found)
