"""Guards on the declarative grammar tables.

The parser decides where a name phrase ends using ``PHRASE_TERMINATORS``
alone -- never the inspector snapshot -- so these tests make the underlying
assumption loud: no known inspector name contains a terminator word. If a
future dump regeneration breaks that, the right response is a parser design
discussion, not a silent misparse.
"""

from __future__ import annotations

from bigfix_relevance_analyzer.grammar import (
    PHRASE_TERMINATORS,
    PUNCT_INFIX,
    WORD_INFIX,
    WORD_INFIX_TRIE,
)
from bigfix_relevance_analyzer.inspectors import inspector_names
from bigfix_relevance_analyzer.tokenizer import PUNCTUATION

# ---------------------------------------------------------------------------
# The load-bearing assumption: names and grammar words do not collide
# ---------------------------------------------------------------------------


def test_no_inspector_name_contains_a_phrase_terminator_word() -> None:
    """A terminator inside a name would cut the phrase short mid-name.

    The inspector dumps list the word operators themselves (`contains`,
    `starts with`, ...) as names; those are exempt, because the parser
    treating them as operators *is* the correct reading.
    """
    operator_spellings = {op.canonical for op in WORD_INFIX.values()}
    offenders = [
        name
        for name in inspector_names()
        if name.lower() not in operator_spellings and PHRASE_TERMINATORS & set(name.lower().split())
    ]
    assert offenders == []


def test_interior_operator_words_are_not_phrase_terminators() -> None:
    """Words like `by`, `to` and `with` appear inside real names
    (`substrings separated by`), so only an operator's *first* word may
    terminate a phrase; the trie handles the rest of the operator."""
    first_words = {words[0] for words in WORD_INFIX}
    interior_words = {word for words in WORD_INFIX for word in words[1:]}
    # `not` and `or` are operators/structural words in their own right; every
    # other interior word must stay free for use inside names.
    assert (interior_words - first_words - {"not", "or"}) & PHRASE_TERMINATORS == set()


# ---------------------------------------------------------------------------
# Table well-formedness
# ---------------------------------------------------------------------------


def test_phrase_terminators_cover_every_word_operator_start() -> None:
    assert {words[0] for words in WORD_INFIX} <= PHRASE_TERMINATORS


def test_word_operator_spellings_are_normalized() -> None:
    for words in WORD_INFIX:
        assert words, "empty word-operator key"
        for word in words:
            assert word == word.lower().strip()
        assert WORD_INFIX[words].canonical == " ".join(words)


def test_punct_operators_are_a_subset_of_what_the_lexer_emits() -> None:
    assert set(PUNCT_INFIX) <= set(PUNCTUATION)
    for lexeme, op in PUNCT_INFIX.items():
        assert op.canonical == lexeme


def test_operator_spellings_are_unique() -> None:
    spellings = [op.canonical for op in PUNCT_INFIX.values()]
    spellings += [op.canonical for op in WORD_INFIX.values()]
    assert len(spellings) == len(set(spellings))


def test_the_trie_resolves_every_operator_to_itself() -> None:
    for words, op in WORD_INFIX.items():
        state = WORD_INFIX_TRIE
        for word in words:
            state = state.children[word]
        assert state.op is op
