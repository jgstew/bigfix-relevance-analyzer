"""The structured inspector table: parsing, provenance, and lookup.

Assertions pin specific real rows rather than global counts, so adding a dump
does not break them -- ``tests/test_inspector_data.py`` is what guards the
table against drifting from the dumps.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.inspectors import (
    Inspector,
    InspectorKind,
    _parse_property,
    all_inspectors,
    binary_operators,
    casts,
    inspector_names,
    known_types,
    lookup,
    properties,
    relevance_types,
    sources,
    unary_operators,
)


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
    """A name is usually overloaded across object types."""
    assert len(lookup("key")) > 1
    assert {entry.name for entry in lookup("key")} == {"key"}


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
    """A client-only property has no session enrichment columns."""
    entry = only("current user key", "current user key <logged on user> of <registry>")
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
