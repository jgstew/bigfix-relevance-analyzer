"""The hot enums hash by identity, and nothing that hashing promises has moved.

``enum.Enum.__hash__`` is ``hash(self._name_)``: a Python frame on every set or
dict probe. #199 profiled ~9 M of them linting one 12 MB file, mostly
``TypeEnvironment.visible`` asking ``dialect in entry.dialects`` and
``Token.is_trivia`` asking ``kind in _TRIVIA``. Enum members are singletons and
``Enum`` compares by identity, so :meth:`object.__hash__` agrees with equality
and costs no frame. These tests pin both halves: that the fast hash is in place,
and that every property a caller relies on still holds with it.
"""

from __future__ import annotations

import copy
import enum
import pickle

import pytest

from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.inspectors import InspectorKind, WrittenForm
from bigfix_relevance_analyzer.tokenizer import TokenKind
from bigfix_relevance_analyzer.typecheck import Plurality

HOT_ENUMS: tuple[type[enum.Enum], ...] = (
    Dialect,
    InspectorKind,
    Plurality,
    TokenKind,
    WrittenForm,
)


@pytest.mark.parametrize("cls", HOT_ENUMS, ids=lambda cls: cls.__name__)
def test_hot_enums_hash_by_identity(cls: type[enum.Enum]) -> None:
    assert cls.__hash__ is object.__hash__


@pytest.mark.parametrize("cls", HOT_ENUMS, ids=lambda cls: cls.__name__)
def test_the_class_docstring_survives(cls: type[enum.Enum]) -> None:
    """The assignment goes *after* the docstring: before it, the docstring
    stops being the first statement and ``__doc__`` silently becomes the
    generic Enum one."""
    assert cls.__doc__
    assert "An enumeration" not in cls.__doc__


@pytest.mark.parametrize("cls", HOT_ENUMS, ids=lambda cls: cls.__name__)
def test_the_hash_is_not_a_member(cls: type[enum.Enum]) -> None:
    assert "__hash__" not in cls.__members__
    assert all(isinstance(member.value, str) for member in cls)


@pytest.mark.parametrize("cls", HOT_ENUMS, ids=lambda cls: cls.__name__)
def test_hashing_agrees_with_equality(cls: type[enum.Enum]) -> None:
    members = list(cls)
    index = {member: position for position, member in enumerate(members)}
    for position, member in enumerate(members):
        assert hash(member) == hash(cls(member.value)) == hash(cls[member.name])
        assert index[member] == position
        assert member in frozenset(members)
        # The members a copy or an unpickle hands back are the same objects,
        # so they still find their own dict entries.
        assert copy.deepcopy(member) is member
        assert pickle.loads(pickle.dumps(member)) is member
        assert index[pickle.loads(pickle.dumps(member))] == position
    assert len({hash(member) for member in members}) == len(members)
