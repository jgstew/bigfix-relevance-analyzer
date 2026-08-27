"""How hard a relevance statement is to read, as a heuristic score.

The point is not to measure relevance precisely -- it is to give a pre-commit
hook something to threshold on, so that a statement which has grown into a
nested pile of ``whose`` filters gets flagged for a human to look at. A
:class:`RelevanceComplexity` carries the individual metrics alongside the score
so a warning can say *why* something scored high, not just that it did.

Counting happens over the token stream from
:mod:`bigfix_relevance_analyzer.tokenizer`, never over raw text. That is what
keeps a comment mentioning ``whose``, or the word ``and`` inside a string
literal, from inflating the score: only text that will actually evaluate counts,
the same discipline :mod:`bigfix_relevance_analyzer.dialect` applies.

What the metrics are not
------------------------
They are heuristics, and the tokenizer deliberately does not bind multi-word
inspector names (see its docstring), so the counts are position-blind: the
``of`` in the inspector name ``day of month`` counts as an ``of``, and a name
containing ``and`` counts as a boolean operator. For a *scorer* that is fine --
a statement using such names really is denser to read -- but nothing here should
be mistaken for a parse.

The weights are provisional. They are module-level constants so they can be
tuned against a real corpus without touching the counting, and no test pins an
absolute score, only orderings.
"""

from __future__ import annotations

from dataclasses import dataclass

from bigfix_relevance_analyzer.tokenizer import GRAMMAR_WORDS, TokenKind, code_tokens

__all__ = [
    "RelevanceComplexity",
    "analyze",
    "score",
]

# ---------------------------------------------------------------------------
# Weights. Provisional -- see the module docstring.
# ---------------------------------------------------------------------------

WEIGHT_TOKEN = 1.0
"""Baseline: longer statements are harder, all else equal."""

WEIGHT_PAREN_DEPTH = 3.0
"""Nesting depth, the single strongest readability signal."""

WEIGHT_BOOLEAN_OPERATOR = 2.0
WEIGHT_OF = 1.0
WEIGHT_MAX_OF_CHAIN = 2.0
"""A long unbroken `of` chain costs more than the same `of`s spread out."""

WEIGHT_WHOSE_CLAUSE = 5.0
"""A `whose` filter introduces a second scope with its own `it`."""

WEIGHT_ITERATION_KEYWORD = 1.0
WEIGHT_SEMICOLON_CLAUSE = 2.0
WEIGHT_STRING_LITERAL = 0.5
WEIGHT_UNIQUE_IDENTIFIER = 1.0
"""Distinct names to hold in your head, as opposed to repeated ones."""

WEIGHT_ERROR_TOKEN = 5.0
"""Unlexable text: the statement is broken, which is worth surfacing."""

# Words treated as boolean operators when they appear as bare words.
_BOOLEAN_WORDS = frozenset({"and", "or", "not"})

# Words that name the implicit iteration subject.
_ITERATION_WORDS = frozenset({"it", "item", "items"})

# Words that introduce a filter clause.
_WHOSE_WORDS = frozenset({"whose", "whoses"})

# Punctuation that ends an `of` chain: a chain cannot cross a clause boundary.
_CHAIN_BREAKERS = frozenset({"(", ")", ";", ","})


@dataclass(frozen=True, slots=True)
class RelevanceComplexity:
    """Per-metric counts for one relevance statement, plus a weighted score."""

    token_count: int = 0
    """Tokens that carry meaning: whitespace and comments excluded."""

    max_paren_depth: int = 0
    boolean_operators: int = 0
    """Bare ``and`` / ``or`` / ``not`` words."""

    of_count: int = 0
    """Every ``of``, however it groups."""

    max_of_chain: int = 0
    """The most ``of``s in one clause, chains being broken by ``()``, ``;``, ``,``."""

    whose_clauses: int = 0
    iteration_keywords: int = 0
    """References to the implicit subject: ``it``, ``item``, ``items``."""

    semicolon_clauses: int = 0
    """Number of ``;``-separated clauses, or 0 when there is no ``;`` at all."""

    string_literals: int = 0
    unique_identifiers: int = 0
    """Distinct words that are not grammar words, compared case-insensitively."""

    error_tokens: int = 0
    """Text the tokenizer could not lex. Non-zero means the statement is broken."""

    @property
    def score(self) -> float:
        """The weighted sum of every metric. Higher is harder to read."""
        return (
            WEIGHT_TOKEN * self.token_count
            + WEIGHT_PAREN_DEPTH * self.max_paren_depth
            + WEIGHT_BOOLEAN_OPERATOR * self.boolean_operators
            + WEIGHT_OF * self.of_count
            + WEIGHT_MAX_OF_CHAIN * self.max_of_chain
            + WEIGHT_WHOSE_CLAUSE * self.whose_clauses
            + WEIGHT_ITERATION_KEYWORD * self.iteration_keywords
            + WEIGHT_SEMICOLON_CLAUSE * self.semicolon_clauses
            + WEIGHT_STRING_LITERAL * self.string_literals
            + WEIGHT_UNIQUE_IDENTIFIER * self.unique_identifiers
            + WEIGHT_ERROR_TOKEN * self.error_tokens
        )


def analyze(text: str) -> RelevanceComplexity:
    """Count every complexity metric for ``text`` in one pass.

    Never raises. Malformed relevance is scored like anything else, with the
    unlexable part reported as :attr:`RelevanceComplexity.error_tokens`.
    """
    token_count = 0
    depth = 0
    max_depth = 0
    booleans = 0
    ofs = 0
    of_chain = 0
    max_of_chain = 0
    whoses = 0
    iterations = 0
    semicolons = 0
    strings = 0
    errors = 0
    identifiers: set[str] = set()

    for token in code_tokens(text):
        token_count += 1
        word = token.normalized

        if token.kind is TokenKind.WORD:
            if word == "of":
                ofs += 1
                of_chain += 1
                max_of_chain = max(max_of_chain, of_chain)
                continue
            if word in _BOOLEAN_WORDS:
                booleans += 1
            elif word in _WHOSE_WORDS:
                whoses += 1
            elif word in _ITERATION_WORDS:
                iterations += 1
            if word not in GRAMMAR_WORDS:
                identifiers.add(word)
        elif token.kind is TokenKind.STRING:
            strings += 1
        elif token.kind is TokenKind.ERROR:
            errors += 1
        elif token.kind is TokenKind.PUNCT:
            if word == "(":
                depth += 1
                max_depth = max(max_depth, depth)
            elif word == ")":
                # Clamped: unbalanced relevance must not push depth negative and
                # then hide real nesting that follows.
                depth = max(0, depth - 1)
            elif word == ";":
                semicolons += 1
            if word in _CHAIN_BREAKERS:
                of_chain = 0

    return RelevanceComplexity(
        token_count=token_count,
        max_paren_depth=max_depth,
        boolean_operators=booleans,
        of_count=ofs,
        max_of_chain=max_of_chain,
        whose_clauses=whoses,
        iteration_keywords=iterations,
        semicolon_clauses=semicolons + 1 if semicolons else 0,
        string_literals=strings,
        unique_identifiers=len(identifiers),
        error_tokens=errors,
    )


def score(text: str) -> float:
    """The complexity score for ``text``. Shorthand for ``analyze(text).score``."""
    return analyze(text).score
