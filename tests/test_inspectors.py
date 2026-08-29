"""The structured inspector table: parsing, provenance, and lookup.

Assertions pin specific real rows rather than global counts, so adding a dump
does not break them -- ``tests/test_inspector_data.py`` is what guards the
table against drifting from the dumps.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable, Sequence

import pytest
from test_examples import corpus_files

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import extract_relevance_from_file
from bigfix_relevance_analyzer.inspectors import (
    SIGNATURE_SAMPLE,
    Inspector,
    InspectorKind,
    MatchKind,
    WrittenForm,
    _parse_property,
    all_inspectors,
    ancestors,
    binary_operators,
    casts,
    inspector_names,
    known_types,
    lookup,
    properties,
    relevance_types,
    search,
    sources,
    suggest,
    unary_operators,
    written_form_of,
)
from bigfix_relevance_analyzer.nodes import Reference
from bigfix_relevance_analyzer.parser import try_parse


def only(name: str, signature: str) -> Inspector:
    """The single inspector named ``name`` whose signature is ``signature``."""
    found = [entry for entry in lookup(name) if entry.signature == signature]
    assert len(found) == 1, f"expected exactly one {signature!r}, got {len(found)}"
    return found[0]


# --------------------------------------------------------------------------
# Tables load and are non-trivial
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "table",
    [properties, casts, binary_operators, unary_operators, relevance_types],
)
def test_every_table_is_populated(table: Callable[[], Sequence[object]]) -> None:
    assert len(table()) > 0


def test_tables_are_cached_not_reparsed() -> None:
    assert properties() is properties()
    assert all_inspectors() is all_inspectors()


def test_every_source_is_dialect_qualified() -> None:
    for label in sources():
        assert label.startswith(("client:", "session:")), label


# --------------------------------------------------------------------------
# Property signature parsing
# --------------------------------------------------------------------------


def test_a_global_property_has_no_operands() -> None:
    """`bes computers` takes no object -- it is the root of a session query."""
    entry = only("bes computers", "bes computers")
    assert entry.kind is InspectorKind.PROPERTY
    assert entry.operands == ()
    assert entry.index_type is None
    assert entry.return_type == "bes computer"


def test_a_property_with_a_direct_object() -> None:
    entry = only("windows", "windows of <operating system>")
    assert entry.operands == ("operating system",)
    assert entry.index_type is None
    assert entry.return_type == "boolean"


def test_a_property_with_an_index_argument_and_an_object() -> None:
    entry = only("key", "key <string> of <registry>")
    assert entry.name == "key"
    assert entry.index_type == "string"
    assert entry.operands == ("registry",)
    assert entry.return_type == "registry key"


def test_an_index_argument_is_not_always_a_string() -> None:
    entry = only("current user key", "current user key <logged on user> of <registry>")
    assert entry.index_type == "logged on user"
    assert entry.operands == ("registry",)


def test_a_property_can_have_an_index_argument_and_no_object() -> None:
    entry = only("drives", "drives <string>")
    assert entry.index_type == "string"
    assert entry.operands == ()


def test_a_name_containing_of_is_not_split_at_the_wrong_of() -> None:
    """No sampled dump has such a name, but the grammar permits one.

    The trailing `of <object>` group is anchored, so backtracking has to settle
    this rather than greedily taking the first `of` as the object separator.
    """
    entry = _parse_property(frozenset({"client:windows"}), "day of month of <date>: integer")
    assert entry.name == "day of month"
    assert entry.operands == ("date",)
    assert entry.return_type == "integer"


def test_tuple_types_are_preserved_verbatim() -> None:
    """Relevance has anonymous tuple types the `types` inspector never lists."""
    entry = only("attr lists", "attr lists of <( string, string )>")
    assert entry.operands == ("( string, string )",)
    assert entry.operands[0] not in known_types()


# --------------------------------------------------------------------------
# Casts and operators
# --------------------------------------------------------------------------


def test_a_cast_records_its_source_type_and_target_name() -> None:
    entry = only("trimmed string", "<string> as trimmed string")
    assert entry.kind is InspectorKind.CAST
    assert entry.operands == ("string",)
    assert entry.return_type == "string"


def test_a_word_shaped_binary_operator() -> None:
    entry = only("starts with", "<string> starts with <string>")
    assert entry.kind is InspectorKind.BINARY_OPERATOR
    assert entry.operands == ("string", "string")
    assert entry.return_type == "boolean"


def test_a_symbol_shaped_binary_operator() -> None:
    entry = only("&", "<string> & <string>")
    assert entry.kind is InspectorKind.BINARY_OPERATOR
    assert entry.operands == ("string", "string")
    assert entry.return_type == "string"


def test_a_parameterized_return_type_is_preserved_verbatim() -> None:
    """`timed( time range, integer )` is a real return type, not a signature."""
    entry = only("*", "<integer> * <time range>")
    assert entry.return_type == "timed( time range, integer )"


def test_the_only_sampled_unary_operator_is_negation() -> None:
    assert {entry.name for entry in unary_operators()} == {"-"}
    entry = only("-", "- <integer>")
    assert entry.kind is InspectorKind.UNARY_OPERATOR
    assert entry.operands == ("integer",)


# --------------------------------------------------------------------------
# Provenance: dialects and platforms
# --------------------------------------------------------------------------


def test_a_session_only_property_reports_only_the_session_dialect() -> None:
    entry = only("bes computers", "bes computers")
    assert entry.dialects == frozenset({Dialect.SESSION})
    assert entry.platforms == frozenset()


def test_a_cross_platform_client_property_lists_every_platform() -> None:
    entry = only("windows", "windows of <operating system>")
    assert entry.dialects == frozenset({Dialect.CLIENT})
    assert entry.platforms == frozenset({"windows", "macos", "ubuntu", "debian", "rhel"})


def test_a_windows_only_property_lists_only_windows() -> None:
    entry = only("key", "key <string> of <registry>")
    assert entry.platforms == frozenset({"windows"})


def test_a_property_shared_by_both_dialects_reports_both() -> None:
    entry = only("key", "key <string> of <json value>")
    assert entry.dialects == frozenset({Dialect.CLIENT, Dialect.SESSION})


def test_the_same_signature_can_return_different_types_per_platform() -> None:
    """`drives` is a drive on Windows, a filesystem on Linux, a volume on macOS.

    Stored as separate rows rather than collapsed, so a type-aware consumer can
    still tell which platform gives which answer.
    """
    by_return = {
        entry.return_type: entry.platforms
        for entry in lookup("drives")
        if entry.signature == "drives"
    }
    assert by_return["drive"] == frozenset({"windows"})
    assert by_return["volume"] == frozenset({"macos"})
    assert by_return["filesystem"] == frozenset({"debian", "rhel", "ubuntu"})


# --------------------------------------------------------------------------
# Lookup
# --------------------------------------------------------------------------


def test_lookup_is_case_insensitive_and_ignores_surrounding_space() -> None:
    assert lookup("BES Computers") == lookup("bes computers") == lookup("  bes computers  ")


def test_lookup_returns_every_overload_of_a_name() -> None:
    """A name is usually overloaded across object types.

    Rows come back under every spelling the engine reports, so `key` also finds
    the ones whose signature reads `keys`: `key <string> of <json value>` and
    `keys of <json value>` are the same property, singular and plural, and both
    are written in real relevance. Use `written_form_of` to tell which was used.
    """
    assert len(lookup("key")) > 1
    assert {entry.name for entry in lookup("key")} == {"key", "keys"}
    assert all(
        "key" in (entry.singular_name, entry.plural_name, entry.name) for entry in lookup("key")
    )


def test_lookup_can_filter_by_kind() -> None:
    assert lookup("starts with", kind=InspectorKind.PROPERTY) == ()
    assert len(lookup("starts with", kind=InspectorKind.BINARY_OPERATOR)) > 0


def test_lookup_of_an_unknown_name_is_empty_not_an_error() -> None:
    """Absence means "not in this snapshot", never "invalid"."""
    assert lookup("wnidows of oprating system") == ()


# --------------------------------------------------------------------------
# Name and type universes
# --------------------------------------------------------------------------


def test_inspector_names_includes_multi_word_names() -> None:
    """The set a tokenizer needs to find where a multi-word name ends."""
    names = inspector_names()
    assert "bes computers" in names
    assert "current user key" in names
    assert "starts with" in names


def test_known_types_covers_the_common_scalars() -> None:
    types = known_types()
    for name in ("string", "boolean", "integer", "time", "bes computer", "registry key"):
        assert name in types


def test_every_inspector_name_is_non_empty_and_stripped() -> None:
    for entry in all_inspectors():
        assert entry.name == entry.name.strip() != ""


# --------------------------------------------------------------------------
# Enrichment: singular/plural/usual name and multivalued, from the session
# REST API's own introspection of the `property` type (see
# tests/examples/relevance_inspectors/session_relevance_properties_rest_api.txt).
# Older dumps carry none of this, so every field is optional.
# --------------------------------------------------------------------------


def test_a_multivalued_property_records_its_plural_and_usual_names() -> None:
    entry = only("keys", "keys of <json value>")
    assert entry.singular_name == "key"
    assert entry.plural_name == "keys"
    assert entry.usual_name == "keys"
    assert entry.multivalued is True


def test_a_single_valued_property_is_not_multivalued() -> None:
    entry = only("key", "key <string> of <json value>")
    assert entry.singular_name == "key"
    assert entry.plural_name == "keys"
    assert entry.usual_name == "key"
    assert entry.multivalued is False


def test_enrichment_is_absent_for_a_dump_that_never_carried_it() -> None:
    """A property found only on a surface whose dump was never enriched has
    no enrichment columns. Every client platform's dump is enriched now (see
    the relevance_inspectors README's "Regenerating" section), so this needs
    a property found only in the still-bare console/Web Reports session
    dumps."""
    entry = only("active directory path", "active directory path of <bes computer>")
    assert entry.sources == frozenset({"session:console", "session:web_reports"})
    assert entry.singular_name is None
    assert entry.plural_name is None
    assert entry.usual_name is None
    assert entry.multivalued is None


def test_a_binary_operator_records_its_written_name_and_symbol() -> None:
    entry = only("%", "<integer> % <integer>")
    assert entry.written_name == "mod"
    assert entry.symbol == "%"


def test_a_unary_operator_records_its_written_name_and_symbol() -> None:
    entry = only("-", "- <integer>")
    assert entry.written_name == "minus"
    assert entry.symbol == "-"


def test_a_type_with_a_parent_records_the_subtyping_relationship() -> None:
    types = {t.name: t for t in relevance_types()}
    assert types["substring"].parent == "string"
    assert types["string"].parent is None


def test_a_type_records_its_internal_size_when_known() -> None:
    types = {t.name: t for t in relevance_types()}
    assert types["integer"].size == 8
    assert types["boolean"].size == 1


def test_lookup_finds_both_written_forms() -> None:
    """A signature records one spelling; relevance is written with either.

    `names of <folder>` and `name of <file>` are the same rows read plural and
    singular, and indexing only the signature's form loses whichever one it did
    not happen to record.
    """
    assert lookup("names")
    assert lookup("name")
    entry = lookup("names")[0]
    assert written_form_of(entry, "names") is WrittenForm.PLURAL
    assert written_form_of(entry, entry.singular_name or "") is WrittenForm.SINGULAR


def test_every_reference_in_the_example_corpus_resolves() -> None:
    """Before both forms were indexed, 14% of real references found nothing --
    all of them real inspectors, keyed under a spelling `lookup` never saw."""
    unresolved = {
        node.phrase
        for path in corpus_files()
        for site in extract_relevance_from_file(path)
        if (parsed := try_parse(site.text)).ok and parsed.node is not None
        for node in _walk(parsed.node)
        if isinstance(node, Reference) and not lookup(node.phrase)
    }
    assert unresolved == set()


def test_ancestors_walks_to_the_root() -> None:
    """Resolution depends on this: a property is declared on the base type."""
    assert ancestors("client") == ("client", "application", "file", "filesystem object")
    assert ancestors("string") == ("string",)


def test_ancestors_of_an_unknown_type_is_just_itself() -> None:
    """Absence from the snapshot is never treated as a finding."""
    assert ancestors("no such type") == ("no such type",)


def _walk(node: object) -> list[object]:
    found: list[object] = []
    stack = [node]
    while stack:
        current = stack.pop()
        found.append(current)
        for name in getattr(current, "__slots__", ()):
            if name == "span":
                continue
            child = getattr(current, name, None)
            if isinstance(child, tuple):
                stack.extend(x for x in child if hasattr(x, "span"))
            elif hasattr(child, "span"):
                stack.append(child)
    return found


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------
# `lookup` is exact-match only, which answers "how do I use `files`" but not
# "what is this called". These tests pin the two failure modes that shaped the
# design: a result set that is one-per-overload rather than one-per-name (so a
# limit of 25 returns between 1 and 25 actual answers), and a matcher that
# confidently returns nonsense.


def test_search_finds_an_exact_name_first() -> None:
    """A query that *is* a written form ranks above everything else.

    Unconditionally, and that is the whole ranking rule: tiers are strict, so
    no number of weaker matches can displace an exact one.
    """
    results = search("bes computer")
    assert results
    assert results[0].name == "bes computer"
    assert results[0].match is MatchKind.EXACT
    assert results[0].matched == "bes computer"
    assert len(results[0].inspectors) == 2


def test_search_returns_one_result_per_name_not_per_overload() -> None:
    """The constraint that fixes the return type.

    ``lookup("name")`` is 96 rows and ``lookup("=")`` is 153, so a result per
    *row* would spend a whole 25-slot limit restating one answer -- an early
    prototype returned ``files`` six times for ``"flies"``. Results are
    therefore one per matched text, carrying their rows behind them.
    """
    for query in ("flies", "name", "size"):
        results = search(query)
        names = [result.name for result in results]
        assert len(names) == len(set(names)), f"{query!r} returned a duplicated name"

    # And the rows are still all there, just grouped rather than repeated.
    grouped = next(result for result in search("flies") if result.name == "files")
    assert grouped.inspectors == lookup("files")


def test_search_result_names_are_always_resolvable() -> None:
    """``lookup(result.name)`` is never empty, for any tier.

    This is why ``name`` and ``matched`` are two fields rather than one: a
    consumer follows up on ``name`` to get the rows, while ``matched`` says what
    actually hit -- a plural spelling, a signature, or a spoken operator name.
    A result whose ``name`` did not resolve would be a dead end.
    """
    queries = ("bes computer", "sha", "registry keys", "oprating system", "flies", "mod")
    seen: set[MatchKind] = set()
    for query in queries:
        for result in search(query):
            assert lookup(result.name), f"{result.name!r} from {query!r} does not resolve"
            seen.add(result.match)
    assert len(seen) > 1, "these queries should exercise more than one tier"


def test_search_prefers_a_prefix_over_substring_noise() -> None:
    """``sha`` finds the hashes, not the longest name containing those letters.

    A plain substring scan puts ``media type shared access host lan`` above
    ``sha1``, because "sha" really is inside it. The prefix tier is what fixes
    that, and this pins it.
    """
    results = search("sha", limit=5)
    names = [result.name for result in results]
    assert "sha1" in names
    assert all(result.match is MatchKind.PREFIX for result in results), names
    assert not any("media type" in name for name in names)


def test_search_matches_a_relationship_through_the_signature() -> None:
    """``registry keys`` is nothing's name, and ``keys of <registry key>`` is the answer.

    The query describes a name applied to an object type, which is how somebody
    naturally asks. Only the signature holds both words, so without this tier
    the query either returns nothing useful or -- worse -- a fuzzy guess:
    :mod:`difflib` alone answers ``retry delays``.
    """
    results = search("registry keys")
    assert results
    assert results[0].matched == "keys of <registry key>"
    assert results[0].match is MatchKind.SIGNATURE
    assert results[0].name == "keys"

    # `retry delays` is still reachable, as a fuzzy fill further down -- the
    # claim is not that it disappears but that it no longer wins, which is what
    # a stricter tier buys. Ranking it below the signature hit is the fix.
    names = [result.name for result in results]
    assert names.index("keys") < names.index("retry delays")


def test_search_matches_other_relationship_queries() -> None:
    """The same tier, on the two other phrasings it was designed against."""
    assert "size of <file>" in [result.matched for result in search("file size")[:2]]
    assert search("bes fixlet name")[0].matched == "name of <bes fixlet>"


def test_search_ranks_a_name_above_a_signature() -> None:
    """Names outrank signatures unconditionally -- and that is a judgement.

    ``folder files`` puts the WORDS hits (``program files folder``) above
    ``files of <folder>``, because a name is what you actually write. Asserted
    as "in the top five" rather than "first" on purpose: pinning first place
    would state more confidence in the ordering than the design has, and would
    break on a tie the data could shift at any time.
    """
    assert "files of <folder>" in [result.matched for result in search("folder files")[:5]]


def test_search_recovers_from_a_typo() -> None:
    """The fuzzy tier, and the reason it is last rather than first.

    The query is spelled ``oprating`` on purpose, and specifically *that*
    misspelling: ``_typos.toml`` and ``.codespellrc`` allowlist it, so the
    spell-check hooks leave it alone. A freshly invented typo here gets
    silently corrected on commit, which leaves the test passing while no longer
    testing anything.
    """
    results = search("oprating system")
    assert results[0].name == "operating system"
    assert results[0].match is MatchKind.FUZZY


def test_a_fuzzy_match_prefers_the_queries_first_letter() -> None:
    """``flies`` means ``files``, not ``lines``.

    Both differ from the query by one transposition, and raw
    :meth:`difflib.SequenceMatcher.ratio` puts ``lines`` first. Preferring a
    candidate that starts with the query's own first character is the measured
    fix, and it is scoped to the fuzzy tier for the reason given in
    :func:`~bigfix_relevance_analyzer.inspectors.search`.
    """
    names = [result.name for result in search("flies")]
    assert "files" in names and "lines" in names
    assert names.index("files") < names.index("lines")


def test_search_finds_a_spoken_operator_name() -> None:
    """``mod`` finds the ``%`` rows, which :func:`lookup` alone cannot.

    The engine records its own spoken words for the operators -- ``mod``,
    ``plus``, ``times`` -- in :attr:`Inspector.written_name`, and
    :func:`written_forms` does not carry them, so ``lookup("mod")`` is empty
    even though ``mod`` is how modulo is written in real relevance. Search
    carries the wider pool; ``lookup`` is deliberately untouched.
    """
    assert lookup("mod") == ()

    results = search("mod")
    assert results
    assert results[0].matched == "mod"
    assert results[0].name == "%", "a result's name must be one lookup() resolves"
    assert lookup(results[0].name)
    assert all(entry.written_name == "mod" for entry in results[0].inspectors)


def test_search_returns_nothing_for_nonsense() -> None:
    """The most important test here: a suggester that always suggests is useless.

    If a future ranking tweak lowers the cutoff far enough to answer this, it
    has stopped being a suggester and started being a random name generator.
    """
    assert search("xyzzy") == ()
    assert search("qqqqqqqqqqqq") == ()


def test_search_normalizes_case_and_inner_whitespace() -> None:
    """Pasted text is the normal input, so it has to be the same question.

    Stronger normalization than :func:`lookup`'s, which stays literal because it
    answers about an exact name.
    """
    assert search("Registry  Keys") == search("registry keys")
    assert search("  BES Computer ") == search("bes computer")


def test_search_declines_a_blank_query_rather_than_returning_everything() -> None:
    """An empty query is not a request for the whole table."""
    for query in ("", "   ", "\n\t"):
        assert search(query) == ()
    assert search("file", limit=0) == ()
    assert search("file", limit=-1) == ()


def test_search_filters_by_dialect_in_both_directions() -> None:
    """A dialect that does not define a name must not have it proposed.

    Unlike platform, this is positive evidence: the dumps cover both sides, so
    ``bes computer`` really is absent from client relevance rather than merely
    uncaptured. Suggesting it to somebody writing a fixlet's ``<Relevance>``
    would be actively wrong.
    """
    client_only = search("registry", dialect=Dialect.CLIENT)
    assert client_only[0].name == "registry"
    assert client_only[0].match is MatchKind.EXACT
    assert "registry" not in [result.name for result in search("registry", dialect=Dialect.SESSION)]

    session_only = search("bes computer", dialect=Dialect.SESSION)
    assert session_only[0].name == "bes computer"
    assert "bes computer" not in [
        result.name for result in search("bes computer", dialect=Dialect.CLIENT)
    ]


def test_search_filters_by_kind() -> None:
    """``kind`` narrows to one introspection category, rows and all."""
    for result in search("string", kind=InspectorKind.CAST):
        assert result.kinds == {InspectorKind.CAST}
        assert all(entry.kind is InspectorKind.CAST for entry in result.inspectors)


def test_search_filters_before_it_limits() -> None:
    """A filtered-out row must not consume a slot.

    If the limit were applied first, a narrow search could come back empty
    while perfectly good answers existed just past the cut -- the failure is
    silent and looks identical to "nothing matches".
    """
    narrow = search("registry", dialect=Dialect.CLIENT, limit=3)
    assert narrow, "filtering before limiting should still find client registry rows"
    assert len(narrow) <= 3
    assert all(Dialect.CLIENT in result.dialects for result in narrow)


def test_search_respects_its_limit() -> None:
    for size in (1, 3, 10):
        assert len(search("file", limit=size)) <= size


def test_search_is_deterministic_and_stable_under_a_larger_limit() -> None:
    """The sort is a total order, so ordering never depends on dict iteration.

    The second assertion is the strong form and comes for free from that: a
    smaller limit is a prefix of a larger one. It would fail the moment two
    results could compare equal.
    """
    first = [(r.name, r.match, r.matched) for r in search("file")]
    second = [(r.name, r.match, r.matched) for r in search("file")]
    assert first == second

    ten = [(r.name, r.matched) for r in search("file", limit=10)]
    twenty_five = [(r.name, r.matched) for r in search("file", limit=25)]
    assert len(ten) == 10
    assert ten == twenty_five[:10]


def test_fuzzy_can_be_switched_off() -> None:
    """``fuzzy=False`` returns only forms that really exist.

    The switch is about cost and honesty rather than tuning: a caller doing
    completion wants no invented near-misses, and the precise tiers are the
    cheap ones.
    """
    assert search("oprating system", fuzzy=False) == ()

    precise = search("file", fuzzy=False)
    assert precise
    for result in precise:
        assert result.match is not MatchKind.FUZZY
        assert lookup(result.name), f"{result.name!r} does not exist"


def test_suggest_offers_leads_without_echoing_the_input() -> None:
    """A "did you mean" that repeats the unknown name back reads as a contradiction.

    It can genuinely happen: a name can be a real written form that the
    *dialect* in question does not define, so the name both is and is not
    known, and returning it would be useless either way.
    """
    assert "operating system" in suggest("oprating system")
    assert "registry" not in suggest("registry")
    assert len(suggest("file", limit=2)) <= 2
    assert suggest("xyzzy") == ()


def test_a_search_result_serializes_to_plain_json() -> None:
    """The same conventions the rest of the package's payloads follow."""
    payload = search("keys")[0].to_dict()
    assert payload == json.loads(json.dumps(payload))
    assert set(payload) == {
        "name",
        "match",
        "matched",
        "kinds",
        "dialects",
        "return_types",
        "overloads",
        "signatures",
        "signatures_omitted",
    }
    assert payload["match"] in {kind.value for kind in MatchKind}
    assert payload["kinds"] == sorted(payload["kinds"])


def test_a_serialized_result_samples_signatures_but_never_miscounts_them() -> None:
    """``overloads`` is the truth even when ``signatures`` is capped.

    The cap is what keeps a search payload affordable; ``signatures_omitted`` is
    what stops the cap from being a silent truncation that reads like a
    complete answer.
    """
    result = next(r for r in search("name") if r.name == "name")
    payload = result.to_dict()

    assert payload["overloads"] == len(result.inspectors)
    assert payload["overloads"] > SIGNATURE_SAMPLE
    assert len(payload["signatures"]) == SIGNATURE_SAMPLE
    assert payload["signatures_omitted"] == len(result.signatures) - SIGNATURE_SAMPLE

    # And nothing is dropped when there is nothing to drop.
    small = next(r for r in search("bes computer") if r.name == "bes computer").to_dict()
    assert small["signatures_omitted"] == 0
    assert len(small["signatures"]) == small["overloads"]


def test_a_search_payload_stays_affordable_for_a_model() -> None:
    """A full 25-result payload must not approach the cost of the rows themselves.

    The guard that stops somebody 'simplifying' ``to_dict`` by embedding
    :meth:`Inspector.to_dict`: ``lookup("name")`` alone is ~43,000 bytes, so a
    search that inlined rows would cost a six-figure token count to answer
    "did you mean". Search hands back an identifier; :func:`lookup` hands back
    the row.
    """
    worst = json.dumps([result.to_dict() for result in search("name", limit=25)])
    assert len(worst) < 40_000, f"search payload has grown to {len(worst)} bytes"

    rows = json.dumps([entry.to_dict() for entry in lookup("name")])
    assert len(worst) < len(rows), "a 25-result search must cost less than one name's rows"


def test_the_search_index_is_not_built_at_import() -> None:
    """Nothing new happens at import, proven in a subprocess.

    A subprocess is mandatory rather than stylistic: by the time an in-process
    version of this ran, the rest of this module would have warmed every cache,
    so it would pass forever regardless of the truth. ``inspectors`` is imported
    by the package root, so the trick used for ``reference`` -- asserting a
    module is absent from :data:`sys.modules` -- is unavailable here; the caches
    are the observable thing instead.
    """
    script = (
        "import bigfix_relevance_analyzer\n"
        "from bigfix_relevance_analyzer import inspectors\n"
        "assert inspectors.all_inspectors.cache_info().currsize == 0, 'tables parsed'\n"
        "assert inspectors._search_index.cache_info().currsize == 0, 'index built'\n"
        "inspectors.search('sha')\n"
        "assert inspectors._search_index.cache_info().currsize == 1, 'index not cached'\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "ok"
