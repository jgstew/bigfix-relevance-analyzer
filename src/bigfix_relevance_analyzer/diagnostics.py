"""The wording BigFix itself uses when relevance is wrong.

This is a **catalog, not a checker**. Nothing in this package emits these yet.
It exists so that when something does, its output is the wording BigFix authors
already recognize from the console and the Fixlet Debugger, rather than a second
vocabulary they have to learn.

Two vocabularies, and which to prefer
-------------------------------------
The same broken expression produces different messages depending on which part
of BigFix sees it. The runtime collapses everything into "operator not defined";
the debugger's static type checker knows whether it was a property, a cast or an
operator, and names the types involved:

===============================  ==========================================================
``1 + "a"`` at runtime           ``The operator "plus" is not defined.``
``1 + "a"`` type-checked         ``the operator 'plus' is not defined for the types
                                 '<integer> plus <string>'``
===============================  ==========================================================

Prefer :attr:`Origin.TYPE_CHECK` where both exist. Both are kept, and each entry
says which it is, because a tool reporting what an *engine* said should quote the
engine.

One message is wrong and is kept anyway
---------------------------------------
``"It" used outside of "whose" clause.`` is what the runtime prints, and it
describes a narrower rule than the engine implements -- ``of`` binds ``it`` too
(see :mod:`bigfix_relevance_analyzer.binding`). It is catalogued as the runtime
string it is; ``used-without-context`` is the accurate one and is what a checker
in this package should emit.

Provenance and licensing
------------------------
These strings were recovered from ``FixletDebugger.exe`` 11.0.6.137's string
tables and confirmed against ``qna.exe``; the work is recorded in
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_. They
are behavioral findings about a proprietary HCL binary, gathered so an
independent open-source analyzer can interoperate with it. No code was copied.
Matching HCL's exact wording is the entire point here, because users recognize
it -- which is also why the templates are reproduced as recovered rather than
tidied up. See :data:`DIAGNOSTICS` for the one place that asymmetry shows.
"""

from __future__ import annotations

import enum
import string
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

from bigfix_relevance_analyzer._serialize import _names

__all__ = [
    "DIAGNOSTICS",
    "FIELDS",
    "MAX_EXPR_DEPTH",
    "MAX_TRIGGER_DEPTH",
    "PROPERTY_DIRECT_OBJECT_FRAGMENT",
    "PROPERTY_INDEX_FRAGMENT",
    "Diagnostic",
    "Origin",
]

MAX_EXPR_DEPTH: Final = 1000
"""The engine's own limit on expression-tree depth."""

MAX_TRIGGER_DEPTH: Final = 1000
"""The engine's own limit on trigger depth."""

PROPERTY_INDEX_FRAGMENT: Final = " <{name}>"
"""Renders the ``{index}`` slot of ``property-not-defined``."""

PROPERTY_DIRECT_OBJECT_FRAGMENT: Final = " of <{name}>"
"""Renders the ``{direct_object}`` slot of ``property-not-defined``."""

FIELDS: Final = frozenset(
    {
        "argument_type",
        "cast_name",
        "direct_object",
        "if_false_type",
        "if_true_type",
        "index",
        "item_keyword",
        "left_type",
        "max_depth",
        "name",
        "of_keyword",
        "phrase",
        "plurality",
        "right_type",
        "source_type",
        "token",
        "total",
        "type",
    }
)
"""Every placeholder name any template uses. A test holds the catalog to it."""


class Origin(enum.Enum):
    """Which part of BigFix produces a message, and so how precise it is."""

    LEXICAL = "lexical"
    """The tokenizer, before anything is parsed."""

    PARSE = "parse"
    """The parser."""

    TYPE_CHECK = "type-check"
    """The Fixlet Debugger's static type checker: templated, and names types."""

    RUNTIME = "runtime"
    """What the evaluator actually prints. Terser, and collapses distinctions."""


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One message, as a :meth:`str.format` template."""

    code: str
    """Stable identifier, and this entry's key in :data:`DIAGNOSTICS`."""

    origin: Origin
    template: str
    """The message. Recovered ``$token`` placeholders are rendered as
    ``{token}``-style fields; the surrounding wording is untouched."""

    @property
    def fields(self) -> frozenset[str]:
        """The placeholder names this template expects."""
        return frozenset(
            name for _text, name, _spec, _conv in string.Formatter().parse(self.template) if name
        )

    def format(self, **fields: object) -> str:
        """Render the message."""
        return self.template.format(**fields)

    def to_dict(self) -> dict[str, Any]:
        """This entry as JSON-serializable plain data.

        The unrendered ``template`` and its ``fields``, not a formatted
        message: this is a catalog entry, and what a consumer serving the
        catalog needs is the shape of the message plus the names it expects.
        Rendering needs values only the caller has.
        """
        return {
            "code": self.code,
            "origin": self.origin.value,
            "template": self.template,
            "fields": _names(self.fields),
        }


def _entry(code: str, origin: Origin, template: str) -> tuple[str, Diagnostic]:
    return code, Diagnostic(code=code, origin=origin, template=template)


_TYPE_CHECK: Final = [
    # Singularity.
    _entry(
        "left-operand-not-singular",
        Origin.TYPE_CHECK,
        "the left operand of '{token}' must be singular",
    ),
    _entry(
        "right-operand-not-singular",
        Origin.TYPE_CHECK,
        "the right operand of '{token}' must be singular",
    ),
    _entry(
        "argument-not-singular", Origin.TYPE_CHECK, "the argument of '{token}' must be singular"
    ),
    # Operators and casts.
    _entry(
        "operand-types-incompatible",
        Origin.TYPE_CHECK,
        "the types in '<{left_type}> {token} <{right_type}>' are not compatible",
    ),
    _entry(
        "binary-operator-not-defined",
        Origin.TYPE_CHECK,
        "the operator '{token}' is not defined for the types "
        "'<{left_type}> {token} <{right_type}>'",
    ),
    _entry(
        "unary-operator-not-defined",
        Origin.TYPE_CHECK,
        "the operator '{token}' is not defined for the type '{token} <{argument_type}>'",
    ),
    _entry(
        "cast-not-defined",
        Origin.TYPE_CHECK,
        "the cast '<{source_type}> {token} {cast_name}' is not defined",
    ),
    # Conditionals.
    _entry(
        "if-condition-not-singular-boolean",
        Origin.TYPE_CHECK,
        "if-condition's must have type 'singular boolean' (it has type '{plurality} {type}' now)",
    ),
    # Deliberate error tolerance: one bad branch is survivable, two is fatal.
    # A checker must not fail fast on the first branch that does not type.
    _entry(
        "both-if-branches-have-type-errors",
        Origin.TYPE_CHECK,
        "at most one branch of an if-statement may have type errors",
    ),
    _entry(
        "if-branch-types-incompatible",
        Origin.TYPE_CHECK,
        "the types in 'then <{if_true_type}> else <{if_false_type}>' are not compatible",
    ),
    # Boolean contexts.
    _entry(
        "left-operand-not-boolean",
        Origin.TYPE_CHECK,
        "the left operand of '{token}' must have type 'singular boolean' "
        "(it has type '{plurality} {type}' now)",
    ),
    _entry(
        "right-operand-not-boolean",
        Origin.TYPE_CHECK,
        "the right operand of '{token}' must have type 'singular boolean' "
        "(it has type '{plurality} {type}' now)",
    ),
    _entry(
        "argument-not-boolean",
        Origin.TYPE_CHECK,
        "the argument to '{token}' must have type 'singular boolean' "
        "(it has type '{plurality} {type}' now)",
    ),
    # Reproduced as recovered, asymmetry included: this one says `boolean` where
    # the if-condition above says `singular boolean`, and it has no {plurality}
    # slot. The difference is real in the string table, but the investigation
    # could not isolate it behaviorally -- a comparison operator imposes its own
    # singularity rule first -- so it is tagged [INFER] there. Do not "fix" it.
    _entry(
        "whose-filter-not-boolean",
        Origin.TYPE_CHECK,
        "a whose filter must have type 'boolean' (it has type '{type}' now)",
    ),
    # Tuples. Indices are 0-based and bounds-checked at compile time.
    _entry(
        "tuple-index-not-literal",
        Origin.TYPE_CHECK,
        "the tuple index '{token}' is not an integer literal",
    ),
    _entry(
        "argument-not-a-tuple",
        Origin.TYPE_CHECK,
        "the argument to '{item_keyword} {of_keyword}' is not a tuple",
    ),
    _entry(
        "tuple-index-out-of-range",
        Origin.TYPE_CHECK,
        "the tuple index '{token}' is too big (there are {total} items in the tuple)",
    ),
    _entry(
        "tuple-index-unreasonable",
        Origin.TYPE_CHECK,
        "the tuple index '{token}' is too big (it's quite unreasonably large)",
    ),
    # Context. This is the accurate counterpart to the runtime's misleading
    # "It used outside of whose clause" -- `of` introduces a context too.
    _entry("used-without-context", Origin.TYPE_CHECK, "'{token}' used without context"),
    # Properties. {index} and {direct_object} are rendered by the two fragment
    # templates above, and are empty strings when the property has neither.
    _entry(
        "property-not-defined",
        Origin.TYPE_CHECK,
        "the property '{phrase}{index}{direct_object}' is not defined",
    ),
]

_LEXICAL: Final = [
    _entry("very-long-word", Origin.LEXICAL, "This expression has a very long word."),
    _entry("very-long-phrase", Origin.LEXICAL, "This expression has a very long phrase."),
    _entry("very-long-string", Origin.LEXICAL, "This expression has a very long string."),
    _entry(
        "unterminated-string", Origin.LEXICAL, "A string constant had no ending quotation mark."
    ),
    _entry("bad-percent-sequence", Origin.LEXICAL, "A string constant had an improper %-sequence."),
    _entry("integer-too-large", Origin.LEXICAL, "An integer constant was too large."),
    _entry("strange-punctuation", Origin.LEXICAL, "This expression has strange punctuation."),
    _entry(
        "illegal-character",
        Origin.LEXICAL,
        "This expression contained a character which is not allowed.",
    ),
    _entry("unterminated-comment", Origin.LEXICAL, "A comment was not terminated."),
]

_PARSE: Final = [
    _entry("could-not-parse", Origin.PARSE, "This expression could not be parsed."),
    _entry("unexpected-end", Origin.PARSE, "Unexpected end of expression."),
    _entry(
        "not-understood",
        Origin.PARSE,
        "The expression could not be understood: for an unknown reason.",
    ),
    _entry(
        "runtime-tuple-index-not-literal",
        Origin.PARSE,
        "This expression contained a tuple index which was not an integer literal.",
    ),
    _entry(
        "runtime-tuple-index-out-of-range",
        Origin.PARSE,
        "The tuple index {token} is out of range.",
    ),
]

_RUNTIME: Final = [
    _entry(
        "runtime-operator-not-defined", Origin.RUNTIME, 'The operator "{token}" is not defined.'
    ),
    _entry("singular-required", Origin.RUNTIME, "A singular expression is required."),
    _entry("boolean-required", Origin.RUNTIME, "A boolean expression is required."),
    # Misleading: `of` binds `it` as well. Prefer `used-without-context`.
    _entry(
        "runtime-it-without-context",
        Origin.RUNTIME,
        '"It" used outside of "whose" clause.',
    ),
    _entry(
        "nonexistent-object",
        Origin.RUNTIME,
        "Singular expression refers to nonexistent object.",
    ),
    _entry(
        "non-unique-object",
        Origin.RUNTIME,
        "Singular expression refers to non-unique object.",
    ),
    _entry("conversion-failed", Origin.RUNTIME, "Could not convert value to required type."),
    _entry("incompatible-types", Origin.RUNTIME, "Incompatible types."),
    _entry(
        "conversion-wrong-type",
        Origin.RUNTIME,
        'The conversion "as {token}" does not produce the required type.',
    ),
    _entry(
        "not-evaluable-here",
        Origin.RUNTIME,
        "Cannot evaluate expression now or in this context.",
    ),
    _entry("blacklisted-inspector", Origin.RUNTIME, "The inspector '{token}' is blacklisted."),
    _entry(
        "expression-too-deep",
        Origin.RUNTIME,
        "Expression tree is too large (maximum depth {max_depth})",
    ),
]

DIAGNOSTICS: Final[MappingProxyType[str, Diagnostic]] = MappingProxyType(
    dict(_TYPE_CHECK + _LEXICAL + _PARSE + _RUNTIME)
)
"""Every catalogued message, keyed by :attr:`Diagnostic.code`."""
