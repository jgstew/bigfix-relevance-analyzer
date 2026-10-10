"""Where the cursor is, and what fits there: a :class:`CompletionContext`.

The context is the seam between *finding* where the cursor is and *ranking*
what fits. Ranking (:mod:`~bigfix_relevance_analyzer.completion.rank`) reads
only the context, so a second way of finding one -- an error-recovering parser
(#96 item 3) -- plugs in beside :func:`scan_context` without touching ranking.
That is why the context carries *types* (``expected_types``,
``subject_types``) and not only a consumer phrase: a comparison operand or a
cast target has types and no phrase.

The scan
--------
:func:`scan_context` reads the tokens before the cursor and never parses the
statement, so a half-written one costs nothing to recover from. It knows three
places, measured on real content in #127:

``after-of``
    ``files of |``. The words before ``of`` are the *consumer*, and what fits is
    a producer of what it takes. Read back over an index (``key "x" of``), any
    ``whose (...)`` filters (``files whose (...) of``), and to the start of the
    name phrase, which ends where the parser's would: at a structural word, or
    at a word operator the trie matches in full (``substrings separated by``
    stays whole, ``x contains y of`` is cut after ``contains``). A
    parenthesized consumer (``(preceding text of it) of``) is the head of the
    group, parsed on its own: a complete expression, so no recovery.

``whose-it``
    Wherever a new expression starts inside ``whose (`` (see below): what
    fits is a property of the filtered collection's type, written ``X of it``.

``statement-start``
    Nothing before the cursor, or an opening ``(``, a tuple's ``,``, a
    collection's ``;``, ``and``, ``or``, ``exists``, ``not``, ``if``, ``then``
    or ``else``.

Anywhere else -- a cast target, an operator's operand -- there is no context
yet, and nothing inside a string, a comment, or an unlexable token. The scan is
built from the parser's own tables (:data:`~bigfix_relevance_analyzer.grammar.STRUCTURAL_WORDS`,
:data:`~bigfix_relevance_analyzer.grammar.WORD_INFIX_TRIE`), and
``tests/test_completion_context.py`` holds it to the parser on every ``of`` in
both corpora.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Final, Literal

from bigfix_relevance_analyzer import grammar, inspectors
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.inspectors import InspectorKind
from bigfix_relevance_analyzer.nodes import ItemOf, Node, Of, Reference, Whose
from bigfix_relevance_analyzer.parser import try_parse
from bigfix_relevance_analyzer.tokenizer import Token, TokenKind, _normalize_phrase, tokenize

__all__ = [
    "CompletionContext",
    "ContextKind",
    "canonical",
    "expected_types",
    "head",
    "scan_context",
    "singular",
    "subject_types",
    "written_plural",
]

ContextKind = Literal["after-of", "whose-it", "statement-start"]


@dataclass(frozen=True, slots=True)
class CompletionContext:
    """Where the cursor is, and what a candidate must be to fit there."""

    kind: ContextKind

    replace: tuple[int, int]
    """Offsets into the site's text of the partial word being typed (empty when none)."""

    partial: str
    """What is being typed, whitespace collapsed: what candidates are filtered
    by. One word (``fold``), or a multi-word name so far (``bes c``), which ends
    in a space when one was typed after it (``bes ``)."""

    dialect: Dialect | None
    """The site's dialect when definite, else ``None``: offer both, ranked."""

    consumer: str | None = None
    """after-of: the canonical name of the inspector the candidate is the object
    of (``file`` for ``files of``). whose-it: the filtered collection's. An
    unknown name is kept as written; ``None`` when there is no name at all."""

    consumer_indexed: bool = False
    """Whether the consumer has an index: ``value "x" of`` (after-of),
    ``action "x" whose (`` (whose-it)."""

    outer: str | None = None
    """after-of: what consumes the consumer (``version`` in ``version of name of |``)."""

    expected_types: frozenset[str] | None = None
    """What a candidate must return (reverse lookup). after-of: the consumer's
    object types. ``None`` when not known, which ranks by the corpus alone."""

    subject_types: frozenset[str] | None = None
    """What a candidate must apply to (forward lookup). whose-it: the filtered
    collection's types."""

    source: Literal["scan", "recovery"] = "scan"
    """Which producer found this context."""


_OPENING_WORDS: Final = frozenset({"and", "or", "exists", "exist", "not", "if", "then", "else"})
"""Words after which a new expression starts. At the top level what fits is
anything; inside ``whose (`` it is ``X of it`` for the filtered collection
(``whose (exists line whose (...) of it)``)."""

_OPENING_PUNCTUATION: Final = frozenset({"(", ",", ";"})
"""Punctuation after which a new expression starts: a group, or the next item
of a tuple or a collection."""


def canonical(phrase: str) -> str | None:
    """The singular name a property phrase canonicalizes to, or ``None`` when
    no property can be written as it: ``folders`` and ``folder`` are ``folder``,
    ``unique values`` is ``unique value``.

    A phrase that is some row's own singular stays itself, even when it is
    another row's plural too: ``windows`` (of an operating system) stays
    ``windows`` rather than becoming the plural of ``window`` (of a route).
    """
    normalized = _normalize_phrase(phrase)
    rows = inspectors.lookup(normalized, kind=InspectorKind.PROPERTY)
    if not rows:
        return None
    singulars = [singular(row) for row in rows]
    if normalized in singulars:
        return normalized
    for row, written in zip(rows, singulars, strict=True):
        if row.plural_name is not None and row.plural_name.lower() == normalized:
            return written
    return singulars[0]


def singular(row: inspectors.Inspector) -> str:
    """A row's singular written form: the name it canonicalizes to."""
    return (row.singular_name or row.name).lower()


def written_plural(phrase: str) -> bool:
    """Whether ``phrase`` is written plural: some row's plural and no row's
    singular (``windows`` is neither, being an operating system's own name)."""
    normalized = _normalize_phrase(phrase)
    rows = inspectors.lookup(normalized, kind=InspectorKind.PROPERTY)
    plural = any(
        row.plural_name is not None and row.plural_name.lower() == normalized for row in rows
    )
    return plural and not any(singular(row) == normalized for row in rows)


def expected_types(name: str, *, indexed: bool) -> frozenset[str] | None:
    """What a producer for the consumer ``name`` must return (after-of): its
    object types, narrowed by whether it has an index when that leaves any.
    ``None`` when ``name`` is no known property."""
    if canonical(name) is None:
        return None
    return inspectors.object_types(name, indexed=indexed) or inspectors.object_types(name)


def subject_types(name: str, *, indexed: bool) -> frozenset[str] | None:
    """What a collection named ``name`` is (whose-it): its rows' return types,
    narrowed by the index as :func:`expected_types` is. ``None`` when ``name``
    is no known property."""
    if canonical(name) is None:
        return None
    rows = inspectors.lookup(name, kind=InspectorKind.PROPERTY)
    narrowed = [row for row in rows if (row.index_type is not None) is indexed]
    return frozenset(row.return_type for row in narrowed or rows)


def head(node: Node) -> Reference | None:
    """The inspector phrase an expression starts from, read leftward through
    ``of``, ``whose`` and ``item ... of``: ``names`` in ``names of files
    whose (...) of folder "x"``. ``None`` for anything else (``it``, a cast, a
    literal, a tuple)."""
    while True:
        if isinstance(node, Reference):
            return node
        if isinstance(node, Of):
            node = node.prop
        elif isinstance(node, Whose):
            node = node.collection
        elif isinstance(node, ItemOf):
            node = node.operand
        else:
            return None


def scan_context(
    text: str, offset: int, after_space: bool, dialect: Dialect | None
) -> CompletionContext | None:
    """The context of a cursor at ``offset`` in a site's ``text``, from the
    tokens before it, or ``None`` where nothing is offered.

    ``after_space`` says that whitespace the site's text does not hold lies
    between ``offset`` and the cursor: the cursor is past the end of a site
    whose text was stripped (see
    :meth:`~bigfix_relevance_analyzer.lsp.positions.DocumentIndex.site_cursor`).
    """
    tokens = list(tokenize(text[:offset]))
    if tokens and tokens[-1].kind is TokenKind.ERROR:
        # Inside an unterminated string or comment, or after a stray character.
        return None
    last = tokens[-1] if tokens else None
    typing = (
        last
        if last is not None
        and last.kind in (TokenKind.WORD, TokenKind.ARTICLE)
        and not after_space
        and last.offset + len(last.text) == offset
        else None
    )
    code = [token for token in tokens if not token.is_trivia()]
    if typing is not None and typing.kind is TokenKind.WORD:
        code.pop()
    replace = (offset, offset)
    partial = ""
    if typing is not None:
        # An article being typed is the start of a word too (`a` for `application`).
        replace = (typing.offset, offset)
        partial = typing.text
    # A multi-word name being typed (`names of bes c`) is one partial: the
    # name phrase the cursor ends, back to where the parser's would start --
    # after the anchor, or after the last complete word operator (`true and
    # va` is typing `va`). A structural word being typed extends nothing; an
    # article does when it follows a name word, as the `a` of `active action`.
    extends = typing is None or _is_name_word(typing) or typing.kind is TokenKind.ARTICLE
    if extends and code and _is_name_word(code[-1]):
        words = [*code, typing] if typing is not None else code
        _, start = _Scan(text, words).phrase_ending_at(len(words) - 1)
        if start < len(code):
            first = code[start]
            partial = " ".join(text[first.offset : offset].split()) + ("" if typing else " ")
            replace = (first.offset, offset)
            del code[start:]
    return _Scan(text, code).context(replace, partial, dialect)


@dataclass(slots=True)
class _Consumer:
    """A consumer read back from the tokens: its name, whether it has an index,
    and where it starts (the index of its first token)."""

    name: str | None
    indexed: bool
    start: int


class _Scan:
    """The backward scan over the code tokens before the cursor."""

    def __init__(self, text: str, code: list[Token]) -> None:
        self.text = text
        self.code = code

    def context(
        self, replace: tuple[int, int], partial: str, dialect: Dialect | None
    ) -> CompletionContext | None:
        code = self.code
        make = functools.partial(
            CompletionContext, replace=replace, partial=partial, dialect=dialect
        )
        if code and _is_word(code[-1], "of"):
            consumer = self.consumer_before(len(code) - 2)
            if consumer is None:
                return make(kind="after-of")
            outer = None
            if consumer.start >= 1 and _is_word(code[consumer.start - 1], "of"):
                found = self.consumer_before(consumer.start - 2)
                outer = found.name if found is not None else None
            return make(
                kind="after-of",
                consumer=consumer.name,
                consumer_indexed=consumer.indexed,
                outer=outer,
                expected_types=(
                    None
                    if consumer.name is None
                    else expected_types(consumer.name, indexed=consumer.indexed)
                ),
            )
        opens = not code or _opens_expression(code[-1])
        whose = self.open_whose()
        if whose is not None and opens:
            collection = self.consumer_before(whose - 2)
            if collection is None or collection.name is None:
                return make(kind="whose-it")
            return make(
                kind="whose-it",
                consumer=collection.name,
                consumer_indexed=collection.indexed,
                subject_types=subject_types(collection.name, indexed=collection.indexed),
            )
        if opens:
            return make(kind="statement-start")
        return None

    def open_whose(self) -> int | None:
        """The index of the ``(`` of the innermost unclosed ``whose (`` the
        cursor is inside, or ``None``."""
        unclosed: list[int] = []
        for at, token in enumerate(self.code):
            if _is_punct(token, "("):
                unclosed.append(at)
            elif _is_punct(token, ")") and unclosed:
                unclosed.pop()
        for at in reversed(unclosed):
            if at >= 1 and _is_word(self.code[at - 1], "whose"):
                return at
        return None

    def consumer_before(self, end: int) -> _Consumer | None:
        """The consumer whose last token is ``code[end]``: a name phrase with
        any index and ``whose`` filters after it, or a parenthesized group.
        ``None`` when nothing there can be one."""
        code = self.code
        # `whose (...)` filters bind to the consumer: `files whose (...) of`.
        while end >= 0 and _is_punct(code[end], ")"):
            opener = self.opener_of(end)
            if opener is None or opener < 1 or not _is_word(code[opener - 1], "whose"):
                break
            end = opener - 2
        if end < 0:
            return None
        token = code[end]
        indexed = False
        if token.kind in (TokenKind.STRING, TokenKind.NUMBER):
            indexed, end = True, end - 1
        elif _is_punct(token, ")"):
            opener = self.opener_of(end)
            if opener is None:
                return None
            if opener >= 1 and _is_name_word(code[opener - 1]):
                # An index: `key (name of it) of`.
                indexed, end = True, opener - 1
            else:
                return self.grouped(opener, end)
        if end < 0 or not _is_name_word(code[end]):
            # `"abc" of` or `it of`: nothing names a consumer, and a literal
            # with no name before it is no index.
            return _Consumer(None, False, end + 1)
        words, start = self.phrase_ending_at(end)
        return _Consumer(_known_suffix(words), indexed, start)

    def grouped(self, opener: int, closer: int) -> _Consumer:
        """A parenthesized consumer, ``(folders it) of``: the head of the group,
        parsed on its own. It is a complete expression, so this is no recovery;
        one that does not parse names no consumer."""
        inner = self.text[self.code[opener].offset + 1 : self.code[closer].offset]
        result = try_parse(inner)
        found = head(result.node) if result.node is not None else None
        if found is None:
            return _Consumer(None, False, opener)
        return _Consumer(canonical(found.phrase) or found.phrase, found.index is not None, opener)

    def opener_of(self, closer: int) -> int | None:
        """The index of the ``(`` matching the ``)`` at ``closer``."""
        depth = 0
        for at in range(closer, -1, -1):
            if _is_punct(self.code[at], ")"):
                depth += 1
            elif _is_punct(self.code[at], "("):
                depth -= 1
                if depth == 0:
                    return at
        return None

    def phrase_ending_at(self, end: int) -> tuple[list[str], int]:
        """The words of the name phrase ending at ``code[end]``, and the index
        of its first token: where the parser's phrase would have started."""
        code = self.code
        first = end
        while first > 0 and _is_name_word(code[first - 1]):
            first -= 1
        run = [token.normalized for token in code[first : end + 1]]
        before = code[first - 1] if first > 0 else None
        start = 0
        state: grammar.WordTrieNode | None = None
        if before is not None and _is_word(before, "not") and first >= 2:
            # `does not contain names of`: the run may finish an operator that
            # `not` (structural, so outside the run) is the middle of.
            opening = grammar.WORD_INFIX_TRIE.children.get(code[first - 2].normalized)
            state = opening.children.get("not") if opening is not None else None
        if state is not None:
            start = _operator_end(run, 0, state) or 0
        # The first word of a phrase in prefix position is a name whatever it
        # is (`starts of ranges`); after an operand it may start an operator.
        first_is_name = before is None or not _ends_operand(before) or start > 0
        at = start
        while at < len(run):
            if not (at == start and first_is_name) and run[at] in grammar.OPERATOR_FIRST_WORDS:
                matched = _operator_end(run, at, grammar.WORD_INFIX_TRIE)
                if matched is not None:
                    start = at = matched
                    first_is_name = True
                    continue
            at += 1
        return run[start:], first + start


def _operator_end(words: list[str], at: int, state: grammar.WordTrieNode) -> int | None:
    """Where the longest word operator starting at ``words[at]`` (from trie
    ``state``) ends, or ``None`` if none completes: the parser's max munch."""
    best = None
    for position in range(at, len(words)):
        child = state.children.get(words[position])
        if child is None:
            break
        state = child
        if state.op is not None:
            best = position + 1
    return best


def _known_suffix(words: list[str]) -> str | None:
    """The canonical name of the longest trailing run of ``words`` a property
    can be written as, else the whole phrase as written (an unknown name)."""
    if not words:
        return None
    for start in range(len(words)):
        name = canonical(" ".join(words[start:]))
        if name is not None:
            return name
    return " ".join(words)


def _opens_expression(token: Token) -> bool:
    """Whether a new expression starts after ``token``."""
    if token.kind is TokenKind.PUNCT:
        return token.text in _OPENING_PUNCTUATION
    return token.kind is TokenKind.WORD and token.normalized in _OPENING_WORDS


def _is_word(token: Token, word: str) -> bool:
    return token.kind is TokenKind.WORD and token.normalized == word


def _is_punct(token: Token, lexeme: str) -> bool:
    return token.kind is TokenKind.PUNCT and token.text == lexeme


def _is_name_word(token: Token) -> bool:
    """Whether ``token`` can be part of a name phrase: a word, not a structural one."""
    return token.kind is TokenKind.WORD and token.normalized not in grammar.STRUCTURAL_WORDS


def _ends_operand(token: Token) -> bool:
    """Whether an operand can end at ``token``, so a word after it is in infix
    position: a literal, ``it`` or a closing parenthesis."""
    return (
        token.kind in (TokenKind.STRING, TokenKind.NUMBER)
        or _is_word(token, "it")
        or _is_punct(token, ")")
    )
