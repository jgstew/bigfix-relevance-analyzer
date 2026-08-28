"""Guards on the declarative grammar tables.

The parser decides where a name phrase ends from these tables alone -- never
the inspector snapshot -- so these tests make the underlying assumption loud:
no known inspector spelling collides with a word that unconditionally ends a
phrase. If a future dump regeneration breaks that, the right response is a
parser design discussion, not a silent misparse.
"""

from __future__ import annotations

from bigfix_relevance_analyzer.grammar import (
    CANONICAL_BINARY,
    GRAMMAR_LEVEL_BINARY,
    OPERATOR_FIRST_WORDS,
    PUNCT_INFIX,
    STRUCTURAL_WORDS,
    WORD_INFIX,
    WORD_INFIX_TRIE,
)
from bigfix_relevance_analyzer.inspectors import all_inspectors, binary_operators, written_forms
from bigfix_relevance_analyzer.tokenizer import PUNCTUATION

# ---------------------------------------------------------------------------
# The load-bearing assumption: names and grammar words do not collide
# ---------------------------------------------------------------------------


def test_no_inspector_written_form_contains_a_structural_word() -> None:
    """A structural word inside a name would cut the phrase short mid-name.

    Every *written form* has to be checked, not just the signature's. A
    property's signature records one spelling, but relevance is written with
    either -- `name of <file>` and `names of <folder>` are one row -- and the
    plural is the half the signature usually drops. Checking `inspector_names()`
    alone tested 2900 of the 5389 forms the parser actually meets, and missed
    that `starts`, `date range ends` and seven others were unparsable as names.

    The dumps list the word operators themselves (`contains`, `starts with`,
    ...) as names; those are exempt, because the parser treating them as
    operators *is* the correct reading.
    """
    operator_spellings = {op.canonical for op in WORD_INFIX.values()}
    offenders = sorted(
        {
            form
            for entry in all_inspectors()
            for form in written_forms(entry)
            if form not in operator_spellings and STRUCTURAL_WORDS & set(form.split())
        }
    )
    assert offenders == []


def test_operator_words_do_not_unconditionally_terminate_a_phrase() -> None:
    """An operator ends a phrase only on a *complete* trie match, so a name may
    contain -- or be -- an operator's first word.

    In practice that only frees the first words that begin no single-word
    operator: `contains` or `and` matches the moment it is seen, so it still
    always terminates. `does`, `ends` and `starts` are the ones that gain a
    reading as a name, and nine real inspector spellings depend on it.
    """
    always_complete = {words[0] for words in WORD_INFIX if len(words) == 1}
    conditional = OPERATOR_FIRST_WORDS - always_complete
    assert conditional == {"does", "ends", "starts"}

    # The operators themselves are inspector rows too (`starts with`); they are
    # exempt for the same reason as in the guard above.
    operator_spellings = {op.canonical for op in WORD_INFIX.values()}
    rescued = sorted(
        {
            form
            for entry in all_inspectors()
            for form in written_forms(entry)
            if form not in operator_spellings and conditional & set(form.split())
        }
    )
    assert rescued == [
        "allow demand starts",
        "date range ends",
        "date range starts",
        "ends",
        "starts",
        "stop at duration ends",
        "stop on idle ends",
        "time range ends",
        "time range starts",
    ]


def test_interior_operator_words_are_not_structural() -> None:
    """Words like `by`, `to` and `with` appear inside real names
    (`substrings separated by`), so they must stay free for use inside names;
    the trie handles them as part of an operator."""
    first_words = {words[0] for words in WORD_INFIX}
    interior_words = {word for words in WORD_INFIX for word in words[1:]}
    # `not` and `or` are operators/structural words in their own right; every
    # other interior word must stay free for use inside names.
    assert (interior_words - first_words - {"not", "or"}) & STRUCTURAL_WORDS == set()


def test_structural_words_and_operator_first_words_are_disjoint() -> None:
    """The two sets answer different questions and share no word. Moving `is`
    or `contains` into the structural set would make it an unconditional
    terminator again and silently re-break the plural names above."""
    assert not (STRUCTURAL_WORDS & OPERATOR_FIRST_WORDS)


# ---------------------------------------------------------------------------
# Table well-formedness
# ---------------------------------------------------------------------------


def test_operator_first_words_is_derived_from_word_infix() -> None:
    """The parser's fast path skips the trie for any word not in this set, so a
    drift here would make an operator silently stop terminating phrases."""
    assert {words[0] for words in WORD_INFIX} == OPERATOR_FIRST_WORDS


def test_every_operator_first_word_resolves_through_the_trie() -> None:
    for word in OPERATOR_FIRST_WORDS:
        assert word in WORD_INFIX_TRIE.children


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
