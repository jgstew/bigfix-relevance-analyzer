"""Hold the diagnostic catalog to the strings it was recovered from.

The catalog's whole value is that the wording is BigFix's, so these tests are
mostly about wording: a typo here is not a cosmetic defect, it is the feature
failing silently. See `issue #8
<https://github.com/jgstew/bigfix-relevance-analyzer/issues/8>`_ for provenance.
"""

from __future__ import annotations

import string

import pytest

from bigfix_relevance_analyzer.diagnostics import (
    DIAGNOSTICS,
    FIELDS,
    PROPERTY_DIRECT_OBJECT_FRAGMENT,
    PROPERTY_INDEX_FRAGMENT,
    Diagnostic,
    Origin,
)


@pytest.mark.parametrize("code", sorted(DIAGNOSTICS))
def test_every_entry_is_keyed_by_its_own_code(code: str) -> None:
    assert DIAGNOSTICS[code].code == code


def test_codes_are_unique() -> None:
    """`dict` would silently drop a duplicate, so count the source entries."""
    codes = [entry.code for entry in DIAGNOSTICS.values()]
    assert len(codes) == len(set(codes))


@pytest.mark.parametrize("code", sorted(DIAGNOSTICS))
def test_every_template_uses_only_documented_fields(code: str) -> None:
    unknown = DIAGNOSTICS[code].fields - FIELDS
    assert not unknown, f"{code} uses undocumented fields {sorted(unknown)}"


@pytest.mark.parametrize("code", sorted(DIAGNOSTICS))
def test_every_template_renders(code: str) -> None:
    """Catches an unbalanced brace or a malformed field, which `format` hides
    until the moment something actually tries to report an error."""
    entry = DIAGNOSTICS[code]
    rendered = entry.format(**{field: f"<{field}>" for field in entry.fields})
    assert "{" not in rendered and "}" not in rendered


def test_every_documented_field_is_used_by_something() -> None:
    """FIELDS is documentation; an entry that drifts out of it should show.

    The two property fragments count as templates too -- `name` is theirs, and
    appears in no catalog entry directly.
    """
    used = {field for entry in DIAGNOSTICS.values() for field in entry.fields}
    used |= {
        name
        for fragment in (PROPERTY_INDEX_FRAGMENT, PROPERTY_DIRECT_OBJECT_FRAGMENT)
        for _text, name, _spec, _conv in string.Formatter().parse(fragment)
        if name
    }
    assert used == set(FIELDS)


def test_the_catalog_is_read_only() -> None:
    with pytest.raises(TypeError):
        DIAGNOSTICS["used-without-context"] = Diagnostic(  # type: ignore[index]
            code="x", origin=Origin.RUNTIME, template="x"
        )


def test_the_context_message_is_the_accurate_one_not_the_shipped_one() -> None:
    """The engine prints a rule narrower than the one it implements.

    `of` binds `it` as well as `whose`, so the runtime string is wrong. Both are
    catalogued -- one as what the runtime says, one as what is true -- and a
    checker in this package emits the type-checker wording.
    """
    accurate = DIAGNOSTICS["used-without-context"]
    assert accurate.origin is Origin.TYPE_CHECK
    assert accurate.format(token="it") == "'it' used without context"

    shipped = DIAGNOSTICS["runtime-it-without-context"]
    assert shipped.origin is Origin.RUNTIME
    assert shipped.template == '"It" used outside of "whose" clause.'


def test_the_two_operator_vocabularies_say_different_things() -> None:
    """The runtime collapses property, cast and operator into one message; the
    type checker names the types. This is the reason to prefer the latter."""
    assert (
        DIAGNOSTICS["runtime-operator-not-defined"].format(token="plus")
        == 'The operator "plus" is not defined.'
    )
    assert (
        DIAGNOSTICS["binary-operator-not-defined"].format(
            token="plus", left_type="integer", right_type="string"
        )
        == "the operator 'plus' is not defined for the types '<integer> plus <string>'"
    )


def test_the_whose_and_if_templates_keep_their_recovered_asymmetry() -> None:
    """[INFER] `whose` says `boolean` with no plurality slot; `if` says
    `singular boolean` with one. The string table really differs, and the
    difference was never isolated behaviorally -- so it is preserved, not tidied.
    """
    whose = DIAGNOSTICS["whose-filter-not-boolean"]
    condition = DIAGNOSTICS["if-condition-not-singular-boolean"]
    assert whose.fields == {"type"}
    assert condition.fields == {"plurality", "type"}
    assert "singular boolean" in condition.template
    assert "singular boolean" not in whose.template


def test_tuple_index_messages_cover_both_too_big_cases() -> None:
    assert DIAGNOSTICS["tuple-index-out-of-range"].format(token="5", total=3) == (
        "the tuple index '5' is too big (there are 3 items in the tuple)"
    )
    assert "unreasonably large" in DIAGNOSTICS["tuple-index-unreasonable"].template


def test_the_property_template_composes_from_its_fragments() -> None:
    """`{index}` and `{direct_object}` are rendered by sub-templates, and are
    empty when the property has neither."""
    entry = DIAGNOSTICS["property-not-defined"]
    assert (
        entry.format(
            phrase="bogusproperty",
            index=PROPERTY_INDEX_FRAGMENT.format(name="string"),
            direct_object=PROPERTY_DIRECT_OBJECT_FRAGMENT.format(name="file"),
        )
        == "the property 'bogusproperty <string> of <file>' is not defined"
    )
    assert entry.format(phrase="bogusproperty", index="", direct_object="") == (
        "the property 'bogusproperty' is not defined"
    )


def test_if_branch_error_tolerance_is_recorded_as_a_rule() -> None:
    """One bad branch is survivable, two is fatal -- a checker must not fail
    fast on the first branch that does not type."""
    assert DIAGNOSTICS["both-if-branches-have-type-errors"].template == (
        "at most one branch of an if-statement may have type errors"
    )


def test_every_origin_is_represented() -> None:
    assert {entry.origin for entry in DIAGNOSTICS.values()} == set(Origin)
