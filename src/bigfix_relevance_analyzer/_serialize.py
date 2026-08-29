"""Shared conventions for the ``to_dict`` methods, and the reasons behind them.

Every result type in this package that a consumer might send across a wire has
a ``to_dict``. They are separate methods rather than one central dispatcher, so
that ``finding.to_dict()`` is reachable from wherever a ``Finding`` already is;
this module holds only the primitives they repeat, and -- more usefully -- the
written-down rules they all follow.

:meth:`~bigfix_relevance_analyzer.analyzer.RelevanceAnalysis.to_dict` set these
by example long before they were stated anywhere:

* **Enums serialize as their** ``.value``, never as the member name. The values
  are the stable, lower-case, hyphenated strings a consumer should show; the
  member names are a Python detail (``Severity.ERROR`` becomes ``"error"``).
* **An absent fact is** ``null``\\ **, and is never omitted.** A consumer reading
  a fixed key set can tell "not applicable" from "not captured"; one reading a
  variable one cannot tell either from "this build is older than that key".
  ``null`` means *no evidence*, which is not the same as ``false`` --
  :attr:`~bigfix_relevance_analyzer.inspectors.Inspector.multivalued` is the
  case where conflating them would actively mislead, since the dumps that
  predate the capture leave it unknown rather than singular.
* **Sets and tuples become sorted lists.** JSON has one sequence type, so a
  ``tuple`` would encode fine and then fail to equal itself after a round trip
  -- which breaks any consumer that caches or diffs a payload. Sorting makes an
  unordered ``frozenset`` render identically run to run; a sequence whose order
  is already meaningful (a list of findings, a signature's operands) keeps it.
* **A position is** ``line`` **and** ``column``\\ **, both 1-based**, plus
  ``offset`` wherever the source of the position carries one. Spans carry
  ``start``/``end`` internally and only their head is reported, because a
  consumer that wants the text can slice it out of ``text`` itself.
* **Lossy by design.** Nodes and tokens do not serialize; they become source
  text, S-expressions, and counts. Anything wanting the tree should hold the
  objects, not the payload.

None of this is exported: these are in-package helpers, and the rules matter to
whoever writes the next ``to_dict``, not to a caller.
"""

from __future__ import annotations

import enum
import os
from collections.abc import Iterable
from pathlib import Path

from bigfix_relevance_analyzer.nodes import Span

__all__: list[str] = []


def _enum(value: enum.Enum | None) -> str | None:
    """One enum member as its ``.value``, passing ``None`` through."""
    return None if value is None else str(value.value)


def _enums(values: Iterable[enum.Enum]) -> list[str]:
    """A set of enum members as a sorted list of their values."""
    return sorted(str(value.value) for value in values)


def _names(names: Iterable[str]) -> list[str]:
    """A set of strings as a sorted list, so the payload is stable run to run."""
    return sorted(names)


def _path(path: Path | None) -> str | None:
    """One filesystem path as a string, passing ``None`` through.

    ``os.fsdecode`` rather than ``str``, so a path that is not valid text in the
    filesystem encoding round-trips through surrogate escapes instead of
    raising here -- a lint run over a repo with one oddly-named file should
    report the file, not die on it.
    """
    return None if path is None else os.fsdecode(path)


def _span(span: Span) -> dict[str, int]:
    """A span's head as ``line`` and ``column``.

    Deliberately not ``start``/``end``: the payload already carries the full
    source text, so a consumer that wants the substring can slice it, and two
    offsets per node across a large tree is real payload weight for something
    almost nothing reads.
    """
    return {"line": span.line, "column": span.column}
