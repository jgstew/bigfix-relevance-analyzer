"""Tests for :mod:`bigfix_relevance_analyzer.completion.context`: where the
cursor is, read back from the text before it (#127).

Relevance flows right to left and is typed left to right: in ``files of |`` the
text to the left is the *consumer*, and completion suggests a producer of what
it takes. The scan finds that consumer from tokens alone, with no parse of the
half-written statement. The parser-agreement test at the end pins it to the
grammar, so the two cannot drift apart.
"""

from __future__ import annotations

import pytest
from _corpus import corpus_cases, parsed_corpus_sites

from bigfix_relevance_analyzer.completion.context import (
    CompletionContext,
    canonical,
    expected_types,
    head,
    scan_context,
    singular,
    subject_types,
    written_plural,
)
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.nodes import Node, NumberOf, Of, children, walk
from bigfix_relevance_analyzer.parser import try_parse


def at_end(prefix: str, dialect: Dialect | None = None) -> CompletionContext | None:
    """The context for a cursor at the end of ``prefix``, as an editor gives it:
    site text is stripped, so trailing whitespace becomes ``after_space``."""
    text = prefix.rstrip()
    return scan_context(text, len(text), text != prefix, dialect)


def after_of(prefix: str) -> CompletionContext:
    found = at_end(prefix)
    assert found is not None, prefix
    assert found.kind == "after-of", found
    return found


# ---------------------------------------------------------------------------
# after `X of`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("prefix", "consumer", "indexed"),
    [
        ("files of ", "file", False),
        ("exists files of ", "file", False),
        ('key "x" of ', "key", True),
        ("item 3 of ", "item", True),
        ('value "x" of keys "y" of ', "key", True),
        ('files whose (name of it = "a") of ', "file", False),
        ('values "x" whose (it as string contains "a") of ', "value", True),
        ("files whose (exists it) whose (true) of ", "file", False),
        ("key (name of it) of ", "key", True),
        ("(folders it) of ", "folder", True),
        ('(preceding text of first " MB" of it) of ', "preceding text", False),
        ('substrings separated by ";" of ', "substring separated by", True),
        ("the files of ", "file", False),
        ("exists files of /* a comment */ ", "file", False),
        ("NAMES OF ", "name", False),
        ("it contains files of ", "file", False),
        ('"a" starts with files of ', "file", False),
        ("x = 1 and files of ", "file", False),
        ("starts of ", "start", False),
        ("number of ", "number", False),
    ],
)
def test_the_consumer_is_read_back_from_the_text(
    prefix: str, consumer: str | None, indexed: bool | None
) -> None:
    found = at_end(prefix)
    if consumer is None:
        assert found is None or found.kind != "after-of"
        return
    assert found is not None, prefix
    assert found.kind == "after-of"
    assert (found.consumer, found.consumer_indexed) == (consumer, indexed)


def test_an_operator_cuts_the_phrase_only_where_it_is_complete() -> None:
    # `starts` alone is the plural of `start`; `starts with` is the operator.
    assert after_of("starts of ").consumer == "start"
    assert after_of('"a" starts with names of ').consumer == "name"
    # `x contains y of`: the phrase is `y`, not `x contains y`.
    assert after_of('"a" contains names of ').consumer == "name"


def test_an_operator_word_after_an_operand_is_an_operator() -> None:
    # After `it` the next word is in infix position, so `contains` cuts.
    assert after_of("it contains names of ").consumer == "name"


def test_the_outer_consumer() -> None:
    found = after_of("version of names of ")
    assert (found.consumer, found.outer) == ("name", "version")
    assert after_of("names of ").outer is None
    assert after_of('value "a" of keys "b" of ').outer == "value"


def test_an_unknown_consumer_keeps_its_phrase_and_has_no_types() -> None:
    found = after_of("totally bogus of ")
    assert found.consumer == "totally bogus"
    assert found.expected_types is None


def test_a_known_suffix_of_an_unknown_phrase_is_the_consumer() -> None:
    assert after_of("bogus files of ").consumer == "file"


def test_the_expected_types_are_the_consumers_object_types() -> None:
    assert after_of("files of ").expected_types == frozenset({"folder", "service"})
    assert after_of('file "x" of ').expected_types == frozenset({"folder", "encoding"})


def test_a_grouped_consumer_that_does_not_parse_has_none() -> None:
    found = after_of("(files of) of ")
    assert found.consumer is None
    assert found.expected_types is None


# ---------------------------------------------------------------------------
# The partial word and the replace range
# ---------------------------------------------------------------------------


def test_a_partial_word_is_what_gets_replaced() -> None:
    found = after_of("files of fold")
    assert found.partial == "fold"
    assert found.replace == (len("files of "), len("files of fold"))
    assert found.consumer == "file"


def test_no_partial_word_after_a_space() -> None:
    found = after_of("files of ")
    assert found.partial == ""
    assert found.replace == (len("files of"), len("files of"))
    # A space after a word keeps it typed: a longer name may follow (`bes `
    # for `bes computers`), so the phrase is the partial, space included.
    found = after_of("files of fold ")
    assert (found.partial, found.replace) == ("fold ", (len("files of "), len("files of fold")))


def test_an_article_being_typed_is_a_partial_word() -> None:
    found = after_of("files of a")
    assert found.partial == "a"
    assert found.replace == (len("files of "), len("files of a"))


def test_the_cursor_mid_statement() -> None:
    text = 'exists files of folders "x"'
    found = scan_context(text, len("exists files of "), False, None)
    assert found is not None
    assert (found.kind, found.consumer, found.partial) == ("after-of", "file", "")
    found = scan_context(text, len("exists files of fol"), False, None)
    assert found is not None
    assert found.partial == "fol"
    assert found.replace == (len("exists files of "), len("exists files of fol"))


def test_the_cursor_right_after_of_is_no_context() -> None:
    """``files of|`` is still typing ``of``: inserting a producer there would
    glue it on (``files offolders``)."""
    assert at_end("files of") is None


@pytest.mark.parametrize(
    "prefix",
    [
        '"abc of ',
        'files of "fold',
        "files of /* fold",
        "files of /* fold ",
        'exists file "x',
        "files of .",
    ],
)
def test_no_context_inside_a_string_a_comment_or_an_error(prefix: str) -> None:
    text = prefix  # an unterminated string or comment takes the space with it
    assert scan_context(text, len(text), False, None) is None


def test_the_dialect_is_carried_through() -> None:
    assert at_end("files of ", Dialect.CLIENT).dialect is Dialect.CLIENT  # type: ignore[union-attr]
    assert at_end("files of ").dialect is None  # type: ignore[union-attr]


def test_the_source_is_the_scan() -> None:
    assert after_of("files of ").source == "scan"


# ---------------------------------------------------------------------------
# inside `whose (`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("prefix", "collection"),
    [
        ("files whose (", "file"),
        ("exists files whose (", "file"),
        ('files whose (name of it = "a" and ', "file"),
        ('files whose (name of it = "a" or ', "file"),
        ("files whose (not ", "file"),
        ("files whose ((", "file"),
        ('files of folder "x" whose (', "folder"),
        ("bes computers whose (", "bes computer"),
        ("files whose (na", "file"),
    ],
)
def test_inside_whose(prefix: str, collection: str) -> None:
    found = at_end(prefix)
    assert found is not None, prefix
    assert found.kind == "whose-it"
    assert found.consumer == collection


def test_inside_whose_the_subject_types_are_the_collections() -> None:
    found = at_end("files whose (")
    assert found is not None
    assert found.subject_types == frozenset({"file"})
    found = at_end("bes computers whose (")
    assert found is not None
    assert found.subject_types == frozenset({"bes computer"})


def test_after_a_closed_whose_is_not_inside_it() -> None:
    found = at_end('files whose (name of it = "a") and ')
    assert found is not None
    assert found.kind == "statement-start"


def test_after_of_inside_whose_is_after_of() -> None:
    found = at_end("files whose (name of ")
    assert found is not None
    assert (found.kind, found.consumer) == ("after-of", "name")


def test_a_partial_word_inside_whose() -> None:
    found = at_end("files whose (na")
    assert found is not None
    assert found.partial == "na"
    assert found.replace == (len("files whose ("), len("files whose (na"))


# ---------------------------------------------------------------------------
# statement start
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "va",
        "exists ",
        "exist ",
        "not ",
        "not exists ",
        "(",
        "true and ",
        "true or ",
        "if ",
        "if true then ",
        "if true then 1 else ",
        "true and va",
    ],
)
def test_statement_start(prefix: str) -> None:
    found = scan_context(prefix.rstrip(), len(prefix.rstrip()), prefix != prefix.rstrip(), None)
    assert found is not None, prefix
    assert found.kind == "statement-start"
    assert found.consumer is None


def test_a_multi_word_name_being_typed_is_one_partial() -> None:
    found = after_of("names of bes c")
    assert (found.consumer, found.partial) == ("name", "bes c")
    assert found.replace == (len("names of "), len("names of bes c"))


def test_a_multi_word_partial_keeps_its_trailing_space() -> None:
    found = after_of("names of bes ")
    assert found.partial == "bes "
    # The replace range is the site's text; the space past it is the editor's.
    assert found.replace == (len("names of "), len("names of bes"))


def test_a_multi_word_partial_collapses_whitespace() -> None:
    assert after_of("names of bes   c").partial == "bes c"


def test_a_multi_word_partial_at_the_start_and_inside_whose() -> None:
    found = at_end("exists bes c")
    assert found is not None
    assert (found.kind, found.partial) == ("statement-start", "bes c")
    found = at_end("files whose (modification t")
    assert found is not None
    assert (found.kind, found.partial) == ("whose-it", "modification t")


@pytest.mark.parametrize("prefix", ["files of x contains", "files of x and", "files of x is "])
def test_a_complete_operator_ends_the_partial(prefix: str) -> None:
    """After an operator the cursor is in its operand: no context in v1."""
    assert at_end(prefix) is None


def test_a_structural_word_being_typed_is_not_extended() -> None:
    assert at_end("exists files of") is None


@pytest.mark.parametrize("prefix", ["files as ", "1 + ", "name of it = ", '"a" ', "it "])
def test_no_context_elsewhere(prefix: str) -> None:
    """A cast target, an operator operand and the like wait for recovery."""
    assert at_end(prefix) is None


# ---------------------------------------------------------------------------
# head and canonical
# ---------------------------------------------------------------------------


def _parsed(text: str) -> Node:
    result = try_parse(text)
    assert result.node is not None, result.error
    return result.node


def test_head_follows_of_whose_and_item() -> None:
    found = head(_parsed('names of files whose (true) of folder "x"'))
    assert found is not None and found.phrase == "names"
    found = head(_parsed('files whose (true) of folder "x"'))
    assert found is not None and found.phrase == "files"
    found = head(_parsed('item 0 of names of folders "x"'))
    assert found is not None and found.phrase == "names"
    assert head(_parsed("it")) is None
    assert head(_parsed('"a" as lowercase')) is None


def test_canonical_names() -> None:
    assert canonical("folders") == "folder"
    assert canonical("FILES") == "file"
    assert canonical("windows") == "windows"  # its own row, not `window`'s plural
    assert canonical("unique values") == "unique value"
    assert canonical("Substrings Separated By") == "substring separated by"
    assert canonical("totally bogus") is None


# ---------------------------------------------------------------------------
# Agreement with the parser
# ---------------------------------------------------------------------------
#
# For every `X of Y` the parser builds in both corpora, the scan of the text up
# to `Y` must find the parser's consumer, index flag and outer consumer.

# The scan's known misses, each with the reason. Empty is the goal: anything
# listed here is a shape a recovering parser should win (#96 item 3).
KNOWN_DISAGREEMENTS: dict[str, str] = {}


def _statements() -> list[str]:
    texts = {case.source for case in corpus_cases()}
    texts.update(site.text for _, site, _ in parsed_corpus_sites())
    return sorted(texts)


def _expected(node: Of, parent: Node | None) -> tuple[str | None, bool, str | None]:
    found = head(node.prop)
    assert found is not None
    consumer = canonical(found.phrase) or found.phrase
    outer = None
    if isinstance(parent, NumberOf):
        # `number of files of`: aggregation, not a property, but the same seat
        # for completion -- and the generator mines it as one.
        outer = "number"
    elif isinstance(parent, Of) and parent.obj is node:
        outer_head = head(parent.prop)
        if outer_head is not None:
            outer = canonical(outer_head.phrase) or outer_head.phrase
    return consumer, found.index is not None, outer


def _parents(root: Node) -> dict[int, Node]:
    return {id(child): node for node in walk(root) for child in children(node)}


def test_the_scan_agrees_with_the_parser_on_every_of() -> None:
    checked = 0
    disagreements: list[str] = []
    for text in _statements():
        result = try_parse(text)
        if result.node is None:
            continue
        parents = _parents(result.node)
        for node in walk(result.node):
            if not isinstance(node, Of) or head(node.prop) is None:
                continue
            checked += 1
            prefix = text[: node.obj.span.start]
            expected = _expected(node, parents.get(id(node)))
            found = scan_context(text, node.obj.span.start, False, None)
            got = (
                None
                if found is None or found.kind != "after-of"
                else (found.consumer, found.consumer_indexed, found.outer)
            )
            if got != expected and prefix not in KNOWN_DISAGREEMENTS:
                disagreements.append(f"{prefix!r}: expected {expected}, got {got}")
    assert not disagreements, "\n".join(disagreements[:40]) + f"\n({len(disagreements)} in all)"
    # 465 when this landed (2026-10-10); a corpus that shrank would prove less.
    assert checked >= 450, checked


# ---------------------------------------------------------------------------
# PR #129 review
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prefix",
    [
        "files whose (exists ",
        "files whose (exist ",
        "files whose (not exists ",
        "files whose (if ",
        "files whose (if true then ",
        "files whose (if true then true else ",
        "files whose (exists na",
    ],
)
def test_inside_whose_after_exists_or_a_conditional_is_whose_it(prefix: str) -> None:
    """`whose (exists line whose (...) of it)` is a common predicate: the
    filtered collection still decides what fits (review finding 2)."""
    found = at_end(prefix)
    assert found is not None, prefix
    assert (found.kind, found.consumer) == ("whose-it", "file")


@pytest.mark.parametrize("article", ["a", "an", "the", "A"])
def test_an_article_as_a_later_word_of_a_name_extends_the_partial(article: str) -> None:
    """Typing the `a` of `active action` must not close the list (finding 3)."""
    found = at_end(f"exists active {article}")
    assert found is not None
    assert (found.kind, found.partial) == ("statement-start", f"active {article}")
    assert found.replace == (len("exists "), len(f"exists active {article}"))


def test_a_lone_article_is_still_a_one_word_partial() -> None:
    found = after_of("files of an")
    assert (found.partial, found.replace) == ("an", (len("files of "), len("files of an")))


@pytest.mark.parametrize("separator", [",", ";"])
def test_a_tuple_or_collection_separator_starts_an_expression(separator: str) -> None:
    """Every element after the first gets suggestions too (finding 9)."""
    found = at_end(f"(name of operating system{separator} ")
    assert found is not None
    assert found.kind == "statement-start"
    found = at_end(f"files whose (exists (name of it{separator} ")
    assert found is not None
    assert (found.kind, found.consumer) == ("whose-it", "file")


def test_the_type_helpers_are_the_scans() -> None:
    """The generator's evaluation builds contexts with these, so it measures
    what the editor sees (finding 7)."""
    assert expected_types("file", indexed=False) == after_of("files of ").expected_types
    assert expected_types("file", indexed=True) == after_of('file "x" of ').expected_types
    assert expected_types("totally bogus", indexed=False) is None
    # An indexed collection narrows to its indexed rows' types.
    indexed = at_end('action "x" whose (')
    plain = at_end("actions whose (")
    assert indexed is not None and plain is not None
    assert indexed.subject_types == subject_types("action", indexed=True)
    assert plain.subject_types == subject_types("action", indexed=False)
    assert indexed.subject_types != plain.subject_types
    assert indexed.consumer_indexed and not plain.consumer_indexed


def test_singular_is_shared() -> None:
    from bigfix_relevance_analyzer import inspectors

    (row,) = [r for r in inspectors.lookup("files") if r.signature == "files of <folder>"]
    assert singular(row) == "file"
    assert written_plural("files") and not written_plural("file")
    assert not written_plural("windows")  # `window`'s plural, and its own row's singular


@pytest.mark.parametrize(
    "prefix",
    [
        "names of files of (",
        "names of files of ((",
        "names of files of ( ",
        "names of files of (fold",
    ],
)
def test_an_object_opened_in_parentheses_keeps_its_consumer(prefix: str) -> None:
    """`X of (Y ...)`: the group is still X's object (second review, finding 1)."""
    found = at_end(prefix)
    assert found is not None
    assert (found.kind, found.consumer, found.outer) == ("after-of", "file", "name")


def test_after_of_parenthesized_inside_whose_is_still_after_of() -> None:
    found = at_end("files whose (name of (")
    assert found is not None
    assert (found.kind, found.consumer) == ("after-of", "name")


def test_an_index_group_is_not_an_object() -> None:
    """`key (` opens an index, not an object: no consumer reaches inside it."""
    found = at_end("key (")
    assert found is not None
    assert found.kind == "statement-start"


def test_a_written_plural_keeps_every_reading() -> None:
    """`attributes` is the plural of `attribute` (on an xml dom node) and the
    singular of a dmi row; both readings resolve, so both types fit."""
    assert {"xml dom node", "dmi memory_device"} <= (
        expected_types("attributes", indexed=False) or set()
    )
