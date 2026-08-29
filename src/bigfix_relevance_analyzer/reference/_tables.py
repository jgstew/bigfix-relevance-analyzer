"""The generated half of the language reference: tables rendered from the data.

Every table here is derived, at call time, from the same tables the analyzer
itself uses -- :mod:`~bigfix_relevance_analyzer.grammar` for operators and
precedence, :mod:`~bigfix_relevance_analyzer.inspectors` for vocabulary and
types, :mod:`~bigfix_relevance_analyzer.complexity` for what is expensive, and
:mod:`~bigfix_relevance_analyzer.diagnostics` for what the engine says when
something is wrong.

**Why at call time rather than baked into the generated prose module.** Baking
them would create a second thing that can drift from
``_inspector_data.py``, needing its own guard; deriving them on demand means
regenerating the inspector data refreshes the reference for free, with nothing
to check. The cost is a few milliseconds of table parsing, paid only when a
document is actually read and never at import -- see the lazy-import note in
:mod:`bigfix_relevance_analyzer.reference`.

**What is curated and what is not.** The operator, type, cost and diagnostic
tables are pure derivations: no judgement, nothing to go stale. The starter
vocabulary is the exception -- nothing in the data says which of 4,552
signatures a person should learn first, so :data:`ANCHORS` is a hand-curated
list, held to the shipped tables by ``tests/test_reference.py`` in the same way
``tests/test_dialect_markers.py`` holds :mod:`~bigfix_relevance_analyzer.dialect`'s
marker lists to the dumps. A name that stops resolving fails a test rather than
silently vanishing from the document.
"""

from __future__ import annotations

import functools
from collections.abc import Mapping, Sequence
from typing import Final

from bigfix_relevance_analyzer import grammar, inspectors
from bigfix_relevance_analyzer.complexity import COST_RULES
from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS, Origin
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.inspectors import Inspector, InspectorKind

__all__: list[str] = []

STARTER_LIMIT: Final = 70
"""How many vocabulary entries a starter table may list.

A reference is read by something with a context window. Seventy names is enough
to write real relevance with and short enough to keep the whole document inside
a few thousand tokens; the full table is what
:func:`~bigfix_relevance_analyzer.inspectors.lookup` is for.
"""

TYPE_LIMIT: Final = 40
"""How many type names the type sketch may list, for the same reason."""

#: Vocabulary a starter reference must name however the ranking below scores it.
#: Curated, because breadth and overload count are proxies for usefulness and
#: proxies get the obvious cases wrong: ``operating system`` is one row on one
#: platform and is the first thing anybody writes.
#:
#: Every entry is checked against the shipped tables by a test, so a rename in a
#: future capture fails loudly instead of quietly dropping a row.
ANCHORS: Mapping[Dialect, tuple[str, ...]] = {
    Dialect.CLIENT: (
        "operating system",
        "files",
        "folder",
        "folders",
        "registry",
        "keys",
        "values",
        "processes",
        "services",
        "computer name",
        "ip addresses",
        "version",
        "product version",
        "lines",
        "packages",
        "users",
        "free space",
        "drives",
        "filesystems",
        "windows",
        "mac",
        "unix",
        "linux",
        "now",
        "client",
        "sites",
        "relevant fixlets",
        "names",
        "size",
        "modification time",
        "pathnames",
        "sha1",
        "wmi",
        "running applications",
        "logged on users",
        "environment",
        "system folder",
        "data folders",
        "descendants",
        "ram",
        "architecture",
        "substrings separated by",
    ),
    Dialect.SESSION: (
        "bes computers",
        "bes fixlets",
        "bes sites",
        "bes actions",
        "bes properties",
        "bes users",
        "bes computer groups",
        "bes analyses",
        "bes tasks",
        "bes roles",
        "bes domains",
        "results",
        "values",
        "names",
        "ids",
        "current console user",
        "current bes server",
        "fixlets",
        "sites",
        "properties",
        "computers",
        "relevant fixlets",
        "applicable computer count",
        "subscribed computers",
        "operating system",
        "last report time",
        "unique values",
        "elements",
        "relevance",
        "state",
        "status",
        "firsts",
        "sets",
        "multiplicities",
        "concatenations",
        "substrings",
    ),
}

#: The binding powers, loosest first, with the wording a reference should use.
#: Read off :mod:`~bigfix_relevance_analyzer.grammar`'s own constants rather
#: than restated, so a precedence change cannot leave this table behind.
_PRECEDENCE: Final[tuple[tuple[int, str], ...]] = (
    (grammar.BP_PIPE, "error fallback"),
    (grammar.BP_OR, "or"),
    (grammar.BP_AND, "and"),
    (grammar.BP_RELATIONAL, "comparison"),
    (grammar.BP_CONCAT, "concatenation"),
    (grammar.BP_ADDITIVE, "add / subtract"),
    (grammar.BP_MULTIPLICATIVE, "multiply / divide / mod"),
)


def _escape(text: str) -> str:
    """Make ``text`` safe inside a Markdown table cell.

    ``|`` is a real relevance operator -- error fallback -- and would otherwise
    be read as a column break even inside a code span, which is a GFM quirk
    rather than an oversight here. ``__main__`` escapes it the same way.
    """
    return text.replace("|", "\\|")


def _cell(text: str) -> str:
    return f"`{_escape(text)}`"


def _table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """One GFM table. Empty rows yield an empty string, not a headerless table."""
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


@functools.cache
def operator_table() -> str:
    """Every operator spelling, its precedence, and the operator it really is.

    The most valuable generated table in the reference, because it carries two
    facts that are invisible from examples and that a writer -- or a model --
    routinely gets wrong: relevance accepts many spellings of the same
    operator, and several of them have no definition of their own. ``>`` is not
    an operator: ``a > b`` is ``b < a``. ``is contained by`` is ``contains``
    with its operands swapped. Both matter as soon as a type error names the
    operator, because the engine names the *canonical* one.
    """
    spelling_bp: dict[str, int] = {op.canonical: op.lbp for op in grammar.PUNCT_INFIX.values()}
    spelling_bp.update({op.canonical: op.lbp for op in grammar.WORD_INFIX.values()})

    sections: list[str] = []
    for power, label in _PRECEDENCE:
        spellings = sorted(spelling for spelling, lbp in spelling_bp.items() if lbp == power)
        rows: list[tuple[str, ...]] = []
        for spelling in spellings:
            form = grammar.CANONICAL_BINARY.get(spelling)
            if spelling in grammar.GRAMMAR_LEVEL_BINARY:
                really = "defined by the grammar, not the operator table"
            elif form is None:  # pragma: no cover - every spelling has a form today
                really = "-"
            elif form.operator == spelling and not (form.negated or form.swapped):
                really = "itself"
            else:
                notes = [f"`{form.operator}`"]
                if form.negated:
                    notes.append("negated")
                if form.swapped:
                    notes.append("operands swapped")
                really = ", ".join(notes)
            rows.append((_cell(spelling), really))
        if rows:
            sections.append(f"**{label}** (binding power {power}, looser binds first)\n")
            sections.append(_table(("Written", "Which operator this really is"), rows))
            sections.append("")

    return "\n".join(sections).rstrip()


def _visible(entry: Inspector, dialect: Dialect) -> bool:
    return dialect in entry.dialects


@functools.cache
def _properties_for(dialect: Dialect) -> tuple[Inspector, ...]:
    return tuple(entry for entry in inspectors.properties() if _visible(entry, dialect))


def _rank(name: str, rows: tuple[Inspector, ...], dialect: Dialect) -> tuple[int, int, int, str]:
    """Sort key for a non-anchor name: most broadly useful first.

    Three signals, in order, each a stand-in for "would a person reach for this
    early":

    1. **Source breadth.** A client property present in all five platform dumps
       is portable; one seen on macOS alone is not, and portable relevance is
       what somebody writing their first statement wants.
    2. **Global entry points first.** A property with no direct object is
       something a statement can *start* with. Those are scarce and
       disproportionately useful -- you cannot use ``name of`` until you have
       something to take the name of.
    3. **Overload count.** A name resolving to many rows applies to many types,
       which is what makes it general-purpose.

    Ties break on the name, so a rendered table is byte-identical run to run.
    """
    breadth = max(len(row.sources) for row in rows)
    global_entry = any(not row.operands for row in rows)
    return (-breadth, 0 if global_entry else 1, -len(rows), name)


@functools.cache
def starter_vocabulary(dialect: Dialect) -> str:
    """The vocabulary table for one dialect: anchors first, then ranked fill.

    One row per *name* rather than per signature. A name is what somebody
    writes; the overloads behind it are what
    :func:`~bigfix_relevance_analyzer.inspectors.lookup` is for, and listing all
    of them would spend the whole document's budget on ``file``.
    """
    # Anchors resolve through `lookup`, not through the index below, because a
    # property's `Inspector.name` is its *singular* identifying phrase while an
    # anchor is often written plural -- `names` is curated, the rows say `name`.
    # `lookup` matches either spelling, so going through it is what makes the
    # curated spelling the one that renders.
    chosen: list[tuple[str, tuple[Inspector, ...]]] = []
    shown: set[str] = set()
    for name in ANCHORS[dialect]:
        rows_for_name = tuple(
            entry
            for entry in inspectors.lookup(name, kind=InspectorKind.PROPERTY)
            if _visible(entry, dialect)
        )
        if rows_for_name:
            chosen.append((name, rows_for_name))
            shown.update(entry.signature for entry in rows_for_name)

    by_name: dict[str, tuple[Inspector, ...]] = {}
    for entry in _properties_for(dialect):
        by_name.setdefault(entry.name, ())
        by_name[entry.name] += (entry,)

    # Skip a fill candidate whose rows an anchor already showed: `name` and
    # `names` are one property written two ways, and listing both spends a row
    # on nothing.
    fill = sorted(
        (
            name
            for name, entries in by_name.items()
            if not any(entry.signature in shown for entry in entries)
        ),
        key=lambda name: _rank(name, by_name[name], dialect),
    )
    for name in fill[: max(0, STARTER_LIMIT - len(chosen))]:
        chosen.append((name, by_name[name]))

    rows: list[tuple[str, ...]] = []
    for name, entries in chosen:
        shortest = min(entries, key=lambda entry: (len(entry.signature), entry.signature))
        returns = sorted({entry.return_type for entry in entries})
        rows.append(
            (
                _cell(name),
                _cell(shortest.signature),
                ", ".join(_cell(item) for item in returns[:3])
                + (" ..." if len(returns) > 3 else ""),
            )
        )
    return _table(("Name", "Example signature", "Returns"), rows)


@functools.cache
def type_sketch(dialect: Dialect) -> str:
    """The types this dialect's vocabulary actually uses, with their parents.

    Ranked by how often a property of this dialect takes or returns a type, so
    the sketch describes the types a writer will meet rather than the ones that
    happen to sort first. Plurality lives in the type system itself -- every
    ``X with multiplicity`` is a child of ``X`` -- which is why that rule is
    stated here rather than left to be inferred from the names.
    """
    usage: dict[str, int] = {}
    for entry in _properties_for(dialect):
        for name in (entry.return_type, *entry.operands):
            usage[name] = usage.get(name, 0) + 1

    known = {declared.name: declared for declared in inspectors.relevance_types()}
    ranked = sorted(usage, key=lambda name: (-usage[name], name))[:TYPE_LIMIT]

    rows: list[tuple[str, ...]] = []
    for name in ranked:
        declared = known.get(name)
        parent = declared.parent if declared is not None and declared.parent else "-"
        rows.append(
            (
                _cell(name),
                _cell(parent) if parent != "-" else "-",
                str(usage[name]),
            )
        )
    return _table(("Type", "Parent type", "Uses in this dialect"), rows)


@functools.cache
def expensive_constructs(dialect: Dialect) -> str:
    """What is slow in this dialect, what it costs, and why.

    Straight from :data:`~bigfix_relevance_analyzer.complexity.COST_RULES`,
    filtered to the rules that apply here and ordered by cost. Every rule's
    ``why`` and ``example`` are pinned by tests upstream, so this section cannot
    drift into folklore -- and the per-dialect filter matters: hashing is the
    top tier on a client, which reads whole files, and near-free in session
    relevance, which cannot read a file at all.
    """
    applicable = [rule for rule in COST_RULES if dialect in rule.dialects]
    rows = [
        (
            _cell(rule.label),
            f"{rule.cost_for(dialect):.3g}",
            rule.why,
            _cell(rule.example),
        )
        for rule in sorted(applicable, key=lambda rule: (-rule.cost_for(dialect), rule.label))
    ]
    return _table(("Construct", "Cost", "Why it is slow", "Example"), rows)


@functools.cache
def engine_diagnostics() -> str:
    """What the Fixlet Debugger's type checker says, in its own words.

    Only the :attr:`~bigfix_relevance_analyzer.diagnostics.Origin.TYPE_CHECK`
    entries. The runtime's versions collapse everything into "operator not
    defined", which tells a reader nothing they can act on; the type checker
    names the construct and the types. Quoted verbatim, placeholders and all,
    because the point is that a reader recognises the string they saw in the
    console -- see :mod:`bigfix_relevance_analyzer.diagnostics` on why the
    wording is reproduced as recovered rather than tidied.
    """
    rows = [
        (_cell(entry.code), _escape(entry.template))
        for entry in sorted(DIAGNOSTICS.values(), key=lambda entry: entry.code)
        if entry.origin is Origin.TYPE_CHECK
    ]
    return _table(("Code", "What the type checker prints"), rows)


@functools.cache
def cast_examples(dialect: Dialect) -> str:
    """A sample of the casts this dialect defines, as ``<source> as target``.

    Casts are how relevance changes a value's type and are unusually
    load-bearing -- ``it as string``, ``it as lowercase``, ``it as trimmed
    string`` appear throughout real content -- so a reference that lists
    properties but no casts leaves out half of how statements are actually
    written.
    """
    targets: dict[str, set[str]] = {}
    for entry in inspectors.casts():
        if _visible(entry, dialect):
            targets.setdefault(entry.name, set()).update(entry.operands)
    ranked = sorted(targets, key=lambda name: (-len(targets[name]), name))[:TYPE_LIMIT]
    rows = [
        (_cell(f"it as {name}"), ", ".join(_cell(item) for item in sorted(targets[name])[:3]))
        for name in ranked
    ]
    return _table(("Cast", "Accepts"), rows)


def _kind_counts(dialect: Dialect) -> Mapping[str, int]:
    """How many rows of each category this dialect defines. Used in the preamble."""
    counts: dict[str, int] = {}
    for entry in inspectors.all_inspectors():
        if _visible(entry, dialect):
            counts[entry.kind.value] = counts.get(entry.kind.value, 0) + 1
    return counts


@functools.cache
def coverage_note(dialect: Dialect) -> str:
    """One sentence on how much vocabulary the snapshot holds for this dialect.

    Included so a reader can calibrate: a starter table of seventy names out of
    a few thousand is a starting point, not the language, and the numbers make
    that concrete rather than leaving it as a disclaimer nobody sizes.
    """
    counts = _kind_counts(dialect)
    total = sum(counts.values())
    # `property` pluralizes irregularly and `InspectorKind`'s values are
    # singular, so the label is spelled out rather than suffixed with an "s"
    # that would read as "properties".
    plural = {
        InspectorKind.PROPERTY: "properties",
        InspectorKind.CAST: "casts",
        InspectorKind.BINARY_OPERATOR: "binary operators",
        InspectorKind.UNARY_OPERATOR: "unary operators",
    }
    detail = ", ".join(
        f"{counts[kind.value]} {plural[kind]}" for kind in InspectorKind if counts.get(kind.value)
    )
    return (
        f"The snapshot this reference is generated from defines {total} "
        f"{dialect.value}-relevance signatures ({detail})."
    )
