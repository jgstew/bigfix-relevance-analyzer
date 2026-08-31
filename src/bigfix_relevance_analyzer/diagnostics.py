"""The wording BigFix itself uses when relevance is wrong.

This is a **catalog**: :mod:`~bigfix_relevance_analyzer.typecheck` emits the
``TYPE_CHECK``-origin entries here as :class:`~bigfix_relevance_analyzer.typecheck.TypeDiagnostic`
(and :mod:`~bigfix_relevance_analyzer.lint` turns most of those into ``type-error``
findings); the ``LEXICAL``, ``PARSE``, and ``RUNTIME`` entries remain unemitted
reference material for now. Either way, its output is the wording BigFix
authors already recognize from the console and the Fixlet Debugger, rather
than a second vocabulary they have to learn.

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

Some messages are wrong and are kept anyway
--------------------------------------------
``"It" used outside of "whose" clause.`` is what the runtime prints, and it
describes a narrower rule than the engine implements -- ``of`` binds ``it`` too
(see :mod:`bigfix_relevance_analyzer.binding`). It is catalogued as the runtime
string it is; ``used-without-context`` is the accurate one and is what a checker
in this package should emit.

``tuple-index-unreasonable`` is the same pattern for a second case:
``item <large integer> of (...)`` prints the identical ``"...was not an
integer literal."`` as a genuinely non-literal index, even though the token
*is* an integer literal, just too big to index a tuple with (confirmed live
against qna 11.0.6.137). Rather than quote the misleading runtime string
outright or silently replace it, its template leads with that confirmed
sentence verbatim and appends the accurate detail after a colon -- the same
treatment given to ``operand-types-incompatible``'s runtime-message base
(``"Incompatible types: ..."``), for the same reason: the built-in message
alone is not enough to act on.

Provenance and licensing
------------------------
These strings were recovered from ``FixletDebugger.exe`` 11.0.6.137's string
tables and confirmed against ``qna.exe``; the work is recorded in
`issue #8 <https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_. They
are behavioral findings about a proprietary HCL binary, gathered so an
independent open-source analyzer can interoperate with it. No code was copied.
Matching HCL's exact wording is the entire point here, because users recognize
it -- which is also why the templates are reproduced as recovered rather than
tidied up. See :data:`DIAGNOSTICS` for where that asymmetry shows.

One entry, ``integer-constant-too-large``, is not from that binary-string
recovery at all -- it was found by probing the live evaluator (see
:data:`bigfix_relevance_analyzer.nodes.MAX_LARGE_INTEGER`), and has not been
cross-checked against ``FixletDebugger.exe``'s string tables the way the rest
of this catalog was.
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
        "max_value",
        "name",
        "of_keyword",
        "phrase",
        "plural_phrase",
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
    _entry(
        "singular-over-plural-object",
        # The runtime's, not the type checker's: writing the singular form is
        # legal and types cleanly, and the engine only objects once the object
        # turns out not to hold exactly one value -- `name of files of folders
        # "/"` answers with a name *and* an error.
        #
        # Alone in this catalog, the wording here is entirely this package's
        # own: every other `Origin.RUNTIME` entry quotes what the evaluator
        # prints, and the two that apply -- `non-unique-object` and
        # `nonexistent-object` -- are carried verbatim on their own entries
        # below. Quoting one of them *here* would state as fact something that
        # has not happened and may never: this is a risk, reported statically,
        # about an evaluation nobody has run. The origin still says runtime,
        # because that is what would raise it, and `CheckResult.ok` reads the
        # origin to keep a risk from failing a type check.
        Origin.RUNTIME,
        "'{phrase}' is written singular over an object that may be plural; "
        "a singular context errors at evaluation if it is",
    ),
    _entry(
        "singular-of-multivalued-property",
        # The sibling of `singular-over-plural-object`, and this package's own
        # wording for the same reason given there: it is a risk reported
        # statically about an evaluation nobody has run. Here the object is
        # singular and the *property* is the hazard -- the tables record it as
        # multivalued, so the singular form raises `Singular expression refers
        # to non-unique object.` whenever more than one value exists. The
        # origin says runtime because that is what would raise it, which also
        # keeps `CheckResult.ok` from failing a type check over a risk.
        Origin.RUNTIME,
        "'{phrase}' can hold several values; a singular context errors at "
        "evaluation when it does -- the plural '{plural_phrase}' is preferred",
    ),
    _entry(
        "singular-of-filtered-collection",
        # The `whose`-filtered sibling of `singular-of-multivalued-property`,
        # split out because it is *not* retracted where a singular is
        # required. The generous reading behind `accept_collapse` -- that the
        # singular context is what forces the singular spelling, and the
        # author had no way to write anything else -- does not hold once a
        # filter is involved: `exists values whose (name of it contains "X"
        # and it as string contains "Y") of <key>` says the same thing and
        # cannot collapse. And what the collapse costs is not an error the
        # author would see. Confirmed live in qna, filtering 49 folders that
        # 47 satisfy:
        #
        #     Q: number of folders whose (exists file whose
        #          (name of it contains "e") of it) of folder "<d>"
        #     A: 47
        #     Q: number of folders whose (name of file whose
        #          (name of it contains "e") of it contains "z") of folder "<d>"
        #     A: 0
        #
        # Every element raised `Singular expression refers to non-unique
        # object.` inside the filter and was dropped, silently: the answer is
        # wrong, not absent. The origin still says runtime -- it is a risk
        # about an evaluation nobody has run, as on the two entries above.
        Origin.RUNTIME,
        "'{phrase} whose (...)' asserts the filter matches exactly one; a singular "
        "context errors at evaluation when more than one does -- filter the plural "
        "'{plural_phrase}' instead",
    ),
    _entry(
        "filtered-singular-spelling",
        # The shape, where the *non-unique* hazard above cannot fire: an index
        # means `pathname of file "x.bes" whose (...) of folder "c:\\"` never
        # matches twice. The chain may even be singular throughout -- nothing
        # need collapse -- but the filter sits on a singular spelling in the
        # middle of it rather than at the end, which is the habit the two
        # entries above are the consequence of -- and the empty case is a
        # hazard of its own, since a filter that matches nothing has nothing
        # to be singular about. Confirmed in qna::
        #
        #     Q: (file "README.md" whose (size of it > 99999999) of folder "<d>") as string
        #     E: Singular expression refers to nonexistent object.
        #     Q: number of (files "README.md" whose (size of it > 99999999) of folder "<d>")
        #     A: 0
        #
        # The maintainer's rule, and the reason this is worth saying out loud:
        # stay plural for as long as possible and collapse once, at the end,
        # with `unique value of` where a singular is actually required.
        Origin.RUNTIME,
        "'{phrase} whose (...)' writes a filter on a singular spelling and "
        "errors when the filter matches nothing; prefer "
        "'{plural_phrase} whose (...)' and, where a singular is required, "
        "'unique value of' at the end of the chain",
    ),
    # Operators and casts.
    _entry(
        "operand-types-incompatible",
        Origin.TYPE_CHECK,
        # `|` has no operator-table row of its own, so there is no recovered
        # string from the type checker to quote for it. What *is* confirmed
        # is the runtime's terse `incompatible-types` ("Incompatible types."),
        # which this leads with verbatim; the clause after the colon is this
        # package's own addition, naming both types, because the runtime
        # message alone doesn't say what was actually mismatched.
        "Incompatible types: the types in '<{left_type}> {token} <{right_type}>' "
        "are not compatible",
    ),
    _entry(
        "binary-operator-not-defined",
        Origin.TYPE_CHECK,
        "the operator '{token}' is not defined for the types "
        "'<{left_type}> {token} <{right_type}>'",
    ),
    # Version comparison. Both are advisories with the runtime origin, for the
    # same reason `singular-over-plural-object` has it: the statement type-checks
    # and the engine answers it. What is wrong is the *answer*, so nothing here
    # may fail a type check. Confirmed on a live client engine and a live session
    # engine (2026-08-30); `docs/universal_relevance.md` carries the transcripts.
    _entry(
        "version-like-string-compare",
        Origin.RUNTIME,
        "'{token}' compares these as strings, not versions -- "
        "'2.10.1' sorts below '2.3.3'; add 'as version' to one side",
    ),
    _entry(
        "version-truncating-compare",
        Origin.RUNTIME,
        "'{token}' compares only as many components as the shorter version has, "
        "so 'version \"1.2.3\"' equals 'version \"1.2\"' -- use 'pad of' on both sides",
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
    # A second instance of the pattern below: the runtime's own message here
    # is confirmed but wrong. `item <large integer> of (...)` prints the exact
    # same "...was not an integer literal." as a genuinely non-literal index
    # (confirmed live against qna 11.0.6.137, up to `MAX_LARGE_INTEGER`) --
    # even though the token *is* an integer literal, just too big to index
    # with. The template leads with that confirmed sentence verbatim, then
    # adds the accurate clause the runtime string omits.
    _entry(
        "tuple-index-unreasonable",
        Origin.TYPE_CHECK,
        "This expression contained a tuple index which was not an integer "
        "literal: the tuple index '{token}' is too big (it's quite unreasonably "
        "large)",
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
    # The world-scope sibling, in this catalog's own words rather than the
    # engine's. The engine would print the `property-not-defined` text here
    # too, but this case is a weaker claim: the dumps know the name, just
    # never without a direct object, and the dumps do not cover every
    # evaluation context -- proxy agent inspectors define top-level names
    # (`devices`) that collide with captured operand-taking ones (`device of
    # <grub file location>`). `lint` maps this to `unknown-inspector`, so the
    # message is phrased like that rule's, not like an engine error.
    _entry(
        "world-property-not-defined",
        Origin.TYPE_CHECK,
        "no dump defines the property '{phrase}{index}' without a direct object",
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
    # Confirmed live against qna 11.0.6.137, not (yet) cross-checked against
    # FixletDebugger.exe's string tables the way the rest of this catalog was
    # (see the module docstring's Provenance section) -- unlike those, this one
    # was found by probing the running evaluator, not read off the binary.
    # Fires for any numeral past `MAX_LARGE_INTEGER`, in any context: a bare
    # literal, arithmetic, and a tuple index all fail identically.
    _entry(
        "integer-constant-too-large",
        Origin.RUNTIME,
        "An integer constant was too large: '{token}' exceeds "
        "{max_value}, the largest value the engine can parse a numeral into",
    ),
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
