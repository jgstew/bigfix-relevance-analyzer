"""Guards on the declarative grammar tables.

The parser decides where a name phrase ends using ``PHRASE_TERMINATORS``
alone -- never the inspector snapshot -- so these tests make the underlying
assumption loud: no known inspector name contains a terminator word. If a
future dump regeneration breaks that, the right response is a parser design
discussion, not a silent misparse.
"""

from __future__ import annotations

from bigfix_relevance_analyzer.grammar import (
    CANONICAL_BINARY,
    GRAMMAR_LEVEL_BINARY,
    PHRASE_TERMINATORS,
    PUNCT_INFIX,
    WORD_INFIX,
    WORD_INFIX_TRIE,
)
from bigfix_relevance_analyzer.inspectors import binary_operators, inspector_names
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


def test_every_operator_the_parser_emits_can_be_resolved() -> None:
    """Written spelling is not what the engine's table is keyed on.

    `nodes.py` keeps the spelling deliberately and defers canonicalization to a
    later pass. Until that pass existed, two thirds of what the parser can emit
    resolved to nothing: the engine defines only twelve binary operators, and
    everything else is a synonym, a negation or an operand swap of one of them.
    """
    emitted = {op.canonical for op in PUNCT_INFIX.values()} | {
        op.canonical for op in WORD_INFIX.values()
    }
    unresolvable = sorted(
        spelling
        for spelling in emitted
        if spelling not in CANONICAL_BINARY and spelling not in GRAMMAR_LEVEL_BINARY
    )
    assert unresolvable == []


def test_every_canonical_target_is_a_name_the_table_defines() -> None:
    """Canonicalizing onto a name the engine does not define would be worse than
    not canonicalizing at all -- it would look resolved and find nothing."""
    defined = {entry.name for entry in binary_operators()}
    unbacked = sorted(
        f"{spelling} -> {form.operator}"
        for spelling, form in CANONICAL_BINARY.items()
        if form.operator not in defined
    )
    assert unbacked == []


def test_the_grammar_level_operators_really_have_no_rows() -> None:
    """`and`, `or` and `|` are defined by the grammar, not the operator table.
    If a dump ever gains rows for them, they should stop being special-cased."""
    named = {entry.name for entry in binary_operators()} | {
        entry.written_name for entry in binary_operators() if entry.written_name
    }
    assert not (GRAMMAR_LEVEL_BINARY & named)
