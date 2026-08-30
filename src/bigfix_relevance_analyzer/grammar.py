"""Declarative grammar tables for BigFix Relevance.

This module is data, not logic: binding powers, operator spellings, and the
words that terminate a name phrase. It exists as a separate file so that a
future port of the parser (the README names Rust) reuses these tables
verbatim and is proven equivalent by the shared parse-tree corpus in
``tests/corpus/``, rather than by re-deriving the grammar.

Relevance has no published BNF and no reserved words; everything here is
reverse-engineered from real content and the platform documentation, and the
corpus is the authority on what these numbers mean. Binding powers are spaced
out so new operators can be slotted in without renumbering.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "CANONICAL_BINARY",
    "GRAMMAR_LEVEL_BINARY",
    "OPERATOR_FIRST_WORDS",
    "PIPE_UNMIXABLE",
    "PUNCT_INFIX",
    "STRUCTURAL_WORDS",
    "WORD_INFIX",
    "WORD_INFIX_TRIE",
    "InfixOp",
    "OperatorForm",
    "WordTrieNode",
]


@dataclass(frozen=True, slots=True)
class InfixOp:
    """One infix operator: its written spelling and left binding power."""

    canonical: str
    """The spelling stored in ``Binary.op`` and written in the corpus."""

    lbp: int
    right_assoc: bool = False

    rbp: int | None = None
    """Minimum binding power for the right operand, when it is not the
    default ``lbp`` rule. The multiplicative class sets this to ``BP_PIPE``:
    the engine never lets `|` nest inside a `*`/`/`/`mod`/`&` right operand
    (`2 * 3 | 5` is a real parse error there, confirmed live), so these
    operators must not capture one either -- the parser then rejects the
    leftover `|` itself (see ``parse_infix``)."""


# Binding powers, loosest first. One source of truth; parser.py never
# hardcodes a number.
#
# `|` sits between the multiplicative class and `as`, not below `or` --
# established against a real evaluator (QnA, 2026-08): `1 | 0 = 0` is False
# (so `(1 | 0) = 0`), `1 | 2 * 3` is 3 (so `(1 | 2) * 3`), `2 + X | 5`
# falls back inside the sum, and `X as string | "z"` casts first. The same
# session pinned `exists` and `not` as taking their operand at this level
# too (`exists 1 + 2` fails on `exists 1`, `not 1 = 1` on `not 1`, while a
# cast still nests inside both) -- which is why there is no BP_NOT: the
# engine gives `not` no looser level of its own.
BP_SEMICOLON = 10
BP_COMMA = 20
BP_OR = 40
BP_AND = 50
BP_RELATIONAL = 60
BP_ADDITIVE = 80
BP_MULTIPLICATIVE = 90
BP_PIPE = 95
BP_CAST = 100
BP_UNARY_MINUS = 105
BP_OF = 110
BP_WHOSE = 120

#: `&` shares the multiplicative level rather than having one of its own.
#: Direct proof is impossible from evaluation alone (every `&`/`+` mixed-type
#: grouping fails at runtime with the same message), but `&` refuses to meet
#: `|` exactly the way `*`, `/` and `mod` do (`"a" & "b" | "c"` is a real
#: parse error) while `+` and `-` happily absorb a fallback -- the signature
#: of one shared product level.
BP_CONCAT = BP_MULTIPLICATIVE

# Infix operators that lex as a single PUNCT token. `>`, `>=` and `!=` are
# sugar the engine canonicalizes away, but they are written in real relevance;
# the spelling is preserved (see nodes.py).
PUNCT_INFIX: dict[str, InfixOp] = {
    "|": InfixOp("|", BP_PIPE),
    "=": InfixOp("=", BP_RELATIONAL),
    "!=": InfixOp("!=", BP_RELATIONAL),
    "<": InfixOp("<", BP_RELATIONAL),
    "<=": InfixOp("<=", BP_RELATIONAL),
    ">": InfixOp(">", BP_RELATIONAL),
    ">=": InfixOp(">=", BP_RELATIONAL),
    "&": InfixOp("&", BP_CONCAT, rbp=BP_PIPE),
    # rbp=BP_PIPE on the multiplicative class: see InfixOp.rbp.
    "+": InfixOp("+", BP_ADDITIVE),
    "-": InfixOp("-", BP_ADDITIVE),
    "*": InfixOp("*", BP_MULTIPLICATIVE, rbp=BP_PIPE),
    "/": InfixOp("/", BP_MULTIPLICATIVE, rbp=BP_PIPE),
}

# Infix operators written as words, keyed by their normalized token sequence.
# Hand-curated: the engine's own introspection canonicalizes most spellings
# away (`is contained by` reports as `contains`, reversed), so this table
# cannot be generated from the inspector dumps.
WORD_INFIX: dict[tuple[str, ...], InfixOp] = {
    ("or",): InfixOp("or", BP_OR),
    ("and",): InfixOp("and", BP_AND),
    ("mod",): InfixOp("mod", BP_MULTIPLICATIVE, rbp=BP_PIPE),
    ("contains",): InfixOp("contains", BP_RELATIONAL),
    ("does", "not", "contain"): InfixOp("does not contain", BP_RELATIONAL),
    ("starts", "with"): InfixOp("starts with", BP_RELATIONAL),
    ("does", "not", "start", "with"): InfixOp("does not start with", BP_RELATIONAL),
    ("ends", "with"): InfixOp("ends with", BP_RELATIONAL),
    ("does", "not", "end", "with"): InfixOp("does not end with", BP_RELATIONAL),
    ("equals",): InfixOp("equals", BP_RELATIONAL),
    ("is",): InfixOp("is", BP_RELATIONAL),
    ("is", "not"): InfixOp("is not", BP_RELATIONAL),
    ("is", "equal", "to"): InfixOp("is equal to", BP_RELATIONAL),
    ("is", "not", "equal", "to"): InfixOp("is not equal to", BP_RELATIONAL),
    ("is", "contained", "by"): InfixOp("is contained by", BP_RELATIONAL),
    ("is", "not", "contained", "by"): InfixOp("is not contained by", BP_RELATIONAL),
    ("is", "greater", "than"): InfixOp("is greater than", BP_RELATIONAL),
    ("is", "greater", "than", "or", "equal", "to"): InfixOp(
        "is greater than or equal to", BP_RELATIONAL
    ),
    ("is", "less", "than"): InfixOp("is less than", BP_RELATIONAL),
    ("is", "less", "than", "or", "equal", "to"): InfixOp("is less than or equal to", BP_RELATIONAL),
}


@dataclass(frozen=True, slots=True)
class WordTrieNode:
    """One state in the max-munch matcher over :data:`WORD_INFIX`.

    The parser walks consecutive words through ``children`` and keeps the
    last state whose ``op`` is set, so `is` alone and `is contained by` both
    resolve in one forward scan with no backtracking.
    """

    op: InfixOp | None
    children: dict[str, WordTrieNode]


def _build_word_trie(table: dict[tuple[str, ...], InfixOp]) -> WordTrieNode:
    ops: dict[tuple[str, ...], InfixOp | None] = {(): None}
    children: dict[tuple[str, ...], dict[str, tuple[str, ...]]] = {(): {}}
    for words, op in table.items():
        for length in range(1, len(words) + 1):
            prefix = words[:length]
            ops.setdefault(prefix, None)
            children.setdefault(prefix, {})
            children[words[: length - 1]][words[length - 1]] = prefix
        ops[words] = op

    def build(prefix: tuple[str, ...]) -> WordTrieNode:
        return WordTrieNode(
            op=ops[prefix],
            children={word: build(child) for word, child in children[prefix].items()},
        )

    return build(())


WORD_INFIX_TRIE: WordTrieNode = _build_word_trie(WORD_INFIX)

# Words that end a name phrase unconditionally, wherever they appear.
# Relevance has no reserved words; this set is a parsing *policy*, and
# tests/test_grammar_tables.py checks it against every written form in the
# inspector snapshot so a platform release that ships a colliding name fails
# loudly.
STRUCTURAL_WORDS: frozenset[str] = frozenset(
    {"of", "whose", "then", "else", "as", "it", "not", "exists", "exist", "if"}
)

# The words a word operator can begin with. NOT terminators in their own right:
# an operator ends a phrase only when the trie matches it in *full*, so `starts`
# is the plural `start` inspector in `starts of ranges` and the `starts with`
# operator only in `starts with "a"`. Treating the first word as a terminator
# made nine real inspector spellings -- `starts`, `date range ends`,
# `stop on idle ends` among them -- impossible to write.
#
# The parser uses this only as a fast path: a word outside it can never begin an
# operator, so the trie walk is skipped. Derived from WORD_INFIX so it cannot
# drift from the trie.
OPERATOR_FIRST_WORDS: frozenset[str] = frozenset(words[0] for words in WORD_INFIX)


# ---------------------------------------------------------------------------
# Canonicalization
# ---------------------------------------------------------------------------
#
# `nodes.py` keeps an operator's written spelling, deliberately, and defers
# canonicalization to a separate pass. This is that pass's table.
#
# The engine defines only twelve binary operators -- `%`, `&`, `*`, `+`, `-`,
# `/`, `<`, `<=`, `=`, `contains`, `ends with`, `starts with`. Every other
# spelling relevance accepts is one of those three transformations away, and
# resolving an operator against the inspector table without applying them finds
# nothing for two thirds of what the parser can emit.


@dataclass(frozen=True, slots=True)
class OperatorForm:
    """How a written operator maps onto one the engine actually defines."""

    operator: str
    """The engine's own name for it, as the binary-operator table spells it."""

    negated: bool = False
    """The written form is the negation of :attr:`operator`."""

    swapped: bool = False
    """The written form takes its operands in the opposite order.

    The engine defines no `>`: `a > b` is `b < a`. Operand types must be
    swapped before looking the overload up, and a diagnostic naming them has to
    swap them back to match what was written.
    """


CANONICAL_BINARY: dict[str, OperatorForm] = {
    # Spelled as themselves.
    "=": OperatorForm("="),
    "<": OperatorForm("<"),
    "<=": OperatorForm("<="),
    "&": OperatorForm("&"),
    "+": OperatorForm("+"),
    "-": OperatorForm("-"),
    "*": OperatorForm("*"),
    "/": OperatorForm("/"),
    "mod": OperatorForm("%"),
    "contains": OperatorForm("contains"),
    "starts with": OperatorForm("starts with"),
    "ends with": OperatorForm("ends with"),
    # Synonyms for equality.
    "is": OperatorForm("="),
    "equals": OperatorForm("="),
    "is equal to": OperatorForm("="),
    # Negations.
    "!=": OperatorForm("=", negated=True),
    "is not": OperatorForm("=", negated=True),
    "is not equal to": OperatorForm("=", negated=True),
    "does not contain": OperatorForm("contains", negated=True),
    "does not start with": OperatorForm("starts with", negated=True),
    "does not end with": OperatorForm("ends with", negated=True),
    "is not contained by": OperatorForm("contains", negated=True, swapped=True),
    # Operand swaps. `>` and `>=` have no rows of their own.
    ">": OperatorForm("<", swapped=True),
    ">=": OperatorForm("<=", swapped=True),
    "is greater than": OperatorForm("<", swapped=True),
    "is greater than or equal to": OperatorForm("<=", swapped=True),
    "is less than": OperatorForm("<"),
    "is less than or equal to": OperatorForm("<="),
    "is contained by": OperatorForm("contains", swapped=True),
}

PIPE_UNMIXABLE: frozenset[str] = frozenset(
    op.canonical for op in (*PUNCT_INFIX.values(), *WORD_INFIX.values()) if op.rbp == BP_PIPE
)
"""The operators whose result the engine refuses as a `|` left operand
without parentheses (`2 * 3 | 5` is a parse error; `(2 * 3) | 5` is not).
Derived from the ``rbp`` markers so the two halves of the rule -- keep `|`
out of these operators' right side, refuse it after their result -- cannot
drift apart."""


GRAMMAR_LEVEL_BINARY: frozenset[str] = frozenset({"and", "or", "|"})
"""Operators with no row in any table, because the grammar defines them.

`and` and `or` take singular booleans and yield one; `|` is error fallback,
choosing its right side only when the left one fails. Their typing rules are
fixed rather than looked up, and the wording for breaking them is already in
:mod:`bigfix_relevance_analyzer.diagnostics`.
"""
