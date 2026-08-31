"""Tests for the servable language references.

Two different things need holding down here, and they fail in different ways.

The **authored prose** cannot be checked for truth by a test -- but it can be
checked for the things that make a reference actively harmful: drifting from the
Markdown it is generated from, growing into a manual that will not fit in the
context it is loaded into, or silently losing a section.

The **generated tables** can be checked against their sources, and are: an
anchor that stops resolving, a cost rule that stops appearing, or an extraction
context nobody documented all fail here rather than quietly leaving a gap in a
document a model is being asked to trust.

The curated-then-verified pattern for :data:`ANCHORS` is the same one
:mod:`test_dialect_markers` uses for the dialect classifier's marker lists,
except stronger: it checks against the shipped tables rather than the
test-only dumps, so it holds for an installed wheel too.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from bigfix_relevance_analyzer import reference
from bigfix_relevance_analyzer.complexity import COST_RULES
from bigfix_relevance_analyzer.dialect import Dialect
from bigfix_relevance_analyzer.extract import SiteKind
from bigfix_relevance_analyzer.inspectors import lookup
from bigfix_relevance_analyzer.reference import Detail, _tables

REPO_ROOT = Path(__file__).parent.parent
DOCS = REPO_ROOT / "docs" / "reference"

#: A runaway guard with headroom, not a target. The documents sit around 23k
#: (12.3k brief) today; a table that started dumping its whole source would
#: blow straight past this, while adding a handful of rows will not.
STANDARD_LIMIT = 28_000
BRIEF_LIMIT = 13_000

DIALECTS = (Dialect.CLIENT, Dialect.SESSION)


# ---------------------------------------------------------------------------
# The documents as a set
# ---------------------------------------------------------------------------


def test_the_four_documents_are_discoverable_and_distinct() -> None:
    """``documents()`` is the registry a server enumerates instead of hardcoding names."""
    listed = reference.documents()
    slugs = [document.slug for document in listed]
    assert slugs == [
        "dialects",
        "universal-relevance",
        "client-relevance",
        "session-relevance",
    ]
    assert len(set(slugs)) == len(slugs)
    assert [document.dialect for document in listed] == [
        None,
        None,
        Dialect.CLIENT,
        Dialect.SESSION,
    ]


def test_the_explainer_is_listed_first() -> None:
    """Listing order is offer order, and the dialect distinction comes first.

    A consumer registering documents in listing order should end up offering
    the prerequisite before the two that assume it.
    """
    assert reference.documents()[0].slug == "dialects"


def test_every_document_carries_the_metadata_a_resource_listing_needs() -> None:
    """A title and a one-sentence summary, so no server has to invent them."""
    for document in reference.documents():
        assert document.title and "\n" not in document.title
        assert len(document.title) <= 80, document.slug
        assert document.summary.endswith(".") and len(document.summary) > 40, document.slug
        assert re.fullmatch(r"[a-z][a-z-]*[a-z]", document.slug), document.slug


@pytest.mark.parametrize("slug", [document.slug for document in reference.documents()])
def test_every_document_is_markdown_within_its_budget(slug: str) -> None:
    """Non-empty, headed, balanced fences, and small enough to actually load.

    The budget is the mechanism that keeps these references rather than
    manuals: they are read by something with a context window, and a document
    that no longer fits is not a smaller problem than a document that is wrong.
    """
    document = reference.get_document(slug)
    for detail, limit in ((Detail.STANDARD, STANDARD_LIMIT), (Detail.BRIEF, BRIEF_LIMIT)):
        text = document.read(detail=detail)
        assert text.startswith("# "), (slug, detail)
        assert text.endswith("\n"), (slug, detail)
        assert len(text) <= limit, (
            f"{slug} at {detail.value} is {len(text)} chars, over the {limit} budget"
        )
        assert text.count("```") % 2 == 0, f"{slug} at {detail.value} has an unclosed fence"


def test_brief_drops_the_tables_and_keeps_the_prose() -> None:
    """``BRIEF`` is the prose alone -- that is the whole distinction from ``STANDARD``."""
    for dialect in DIALECTS:
        document = reference.get_document(f"{dialect.value}-relevance")
        brief = document.read(detail=Detail.BRIEF)
        standard = document.read(detail=Detail.STANDARD)
        assert len(brief) < len(standard)
        assert "# Generated tables" not in brief
        assert "# Generated tables" in standard
        # The prose is not merely a prefix of `standard` by accident; it is the
        # same text, so anything in brief must appear in standard.
        assert brief.rstrip() in standard


# ---------------------------------------------------------------------------
# Lookup and error behaviour
# ---------------------------------------------------------------------------


def test_markdown_accepts_a_slug_or_a_dialect() -> None:
    """The registry and the two named front doors return the same bytes."""
    assert reference.markdown("client-relevance") == reference.client_relevance_reference()
    assert reference.markdown(Dialect.CLIENT) == reference.client_relevance_reference()
    assert reference.markdown("session-relevance") == reference.session_relevance_reference()
    assert reference.markdown(Dialect.SESSION) == reference.session_relevance_reference()


def test_an_unknown_slug_names_the_ones_that_exist() -> None:
    """A consumer hitting this has a typo or a stale name; say what is valid."""
    with pytest.raises(KeyError) as caught:
        reference.get_document("client")
    message = str(caught.value)
    for document in reference.documents():
        assert document.slug in message


@pytest.mark.parametrize("dialect", [Dialect.BOTH, Dialect.UNCERTAIN])
def test_an_indefinite_dialect_is_refused_rather_than_guessed(dialect: Dialect) -> None:
    """``BOTH`` and ``UNCERTAIN`` are verdicts about a statement, not documents.

    Falling back to the explainer would answer a question the caller did not
    ask, and would do it silently.
    """
    with pytest.raises(ValueError, match="no reference document"):
        reference.markdown(dialect)


def test_a_document_serializes_to_plain_json() -> None:
    """``to_dict`` carries the text and the listing metadata together."""
    payload = reference.get_document("dialects").to_dict()
    assert payload == json.loads(json.dumps(payload))
    assert payload["mime_type"] == reference.MIME_TYPE
    assert payload["detail"] == Detail.STANDARD.value
    assert payload["text"] == reference.get_document("dialects").read()
    assert payload["dialect"] is None


# ---------------------------------------------------------------------------
# The generated tables, against their sources
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("dialect", DIALECTS)
def test_every_anchor_resolves_in_the_shipped_tables(dialect: Dialect) -> None:
    """Curated vocabulary, verified against the data -- the point of the pattern.

    An anchor is a hand-picked name, so nothing but a test stops it rotting. A
    future capture that renames or drops one should fail here loudly, not
    silently ship a reference that recommends a name no engine defines. Checked
    against ``inspectors`` rather than the dumps, so this holds for an installed
    wheel too.
    """
    for name in _tables.ANCHORS[dialect]:
        rows = lookup(name)
        assert rows, f"{name!r} is an anchor but resolves to nothing"
        assert any(dialect in row.dialects for row in rows), (
            f"{name!r} is a {dialect.value} anchor but no row defines it there"
        )


@pytest.mark.parametrize("dialect", DIALECTS)
def test_every_anchor_reaches_the_rendered_vocabulary(dialect: Dialect) -> None:
    """An anchor that resolves but gets ranked out would be curation with no effect."""
    rendered = _tables.starter_vocabulary(dialect)
    for name in _tables.ANCHORS[dialect]:
        assert f"| `{name}` |" in rendered, f"{name!r} was curated in but not rendered"


@pytest.mark.parametrize("dialect", DIALECTS)
def test_the_vocabulary_table_respects_its_limit(dialect: Dialect) -> None:
    """Anchors plus ranked fill, capped -- header and separator excluded."""
    rows = len(_tables.starter_vocabulary(dialect).splitlines()) - 2
    assert rows == _tables.STARTER_LIMIT


@pytest.mark.parametrize("dialect", DIALECTS)
def test_every_applicable_cost_rule_appears_in_that_dialect(dialect: Dialect) -> None:
    """The cost section is complete for the dialect, and filtered to it.

    The filter is load-bearing rather than cosmetic: hashing is the top tier on
    a client, which reads whole files, and near-free in session relevance, which
    cannot read a file at all. A document that showed the client cost to a
    session author would be worse than showing nothing.
    """
    rendered = _tables.expensive_constructs(dialect)
    for rule in COST_RULES:
        if dialect in rule.dialects:
            assert f"| `{rule.label}` |" in rendered, rule.label
        else:
            assert f"| `{rule.label}` |" not in rendered, rule.label


@pytest.mark.parametrize("dialect", DIALECTS)
def test_the_cost_shown_is_this_dialects_cost(dialect: Dialect) -> None:
    """Not merely present -- present with the right number."""
    rendered = _tables.expensive_constructs(dialect)
    for rule in COST_RULES:
        if dialect not in rule.dialects:
            continue
        row = next(line for line in rendered.splitlines() if f"| `{rule.label}` |" in line)
        assert f"| {rule.cost_for(dialect):.3g} |" in row, rule.label


def test_the_operator_table_covers_every_spelling_the_parser_accepts() -> None:
    """Every operator a statement can contain is explained, canonical form included.

    An operator missing here is an operator a reader cannot look up, and the
    canonicalization is exactly what they would come looking for -- the engine
    reports errors against `<`, never against `>`.
    """
    from bigfix_relevance_analyzer import grammar

    rendered = _tables.operator_table()
    spellings = {op.canonical for op in grammar.PUNCT_INFIX.values()} | {
        op.canonical for op in grammar.WORD_INFIX.values()
    }
    for spelling in spellings:
        assert f"| `{spelling.replace('|', chr(92) + '|')}` |" in rendered, spelling

    # The two facts this table exists to carry.
    assert "operands swapped" in rendered
    assert "defined by the grammar, not the operator table" in rendered


def test_the_type_checker_vocabulary_is_quoted_not_paraphrased() -> None:
    """The engine's own strings, so a reader recognises what they saw."""
    from bigfix_relevance_analyzer.diagnostics import DIAGNOSTICS, Origin

    rendered = _tables.engine_diagnostics()
    type_check = [entry for entry in DIAGNOSTICS.values() if entry.origin is Origin.TYPE_CHECK]
    assert type_check
    for entry in type_check:
        assert f"| `{entry.code}` |" in rendered, entry.code
    # Runtime wording is deliberately excluded: it collapses everything into
    # "operator not defined", which a reader cannot act on.
    runtime = [entry for entry in DIAGNOSTICS.values() if entry.origin is Origin.RUNTIME]
    for entry in runtime:
        assert f"| `{entry.code}` |" not in rendered, entry.code


def test_every_extraction_context_is_documented_somewhere() -> None:
    """A new place relevance can be found must be described in the references.

    ``SiteKind`` is extraction-shaped, so the documents describe the authoring
    surfaces in their own words rather than listing the literals -- but a new
    kind still has to be written up, and this is what makes that non-optional.
    The mapping is spelled out here rather than inferred, so adding a kind means
    a deliberate choice about where it belongs.
    """
    described = "\n".join(document.read() for document in reference.documents()).lower()
    phrases: dict[str, tuple[str, ...]] = {
        "relevance": ("<relevance>",),
        "success-criteria": ("<successcriteria>",),
        "analysis-property": ("analysis properties", "analysis property"),
        "actionscript-substitution": ("actionscript",),
        "relevance-pi": ("<?relevance ?>",),
        "javascript-call": ("evaluaterelevance",),
        "plain-text": (".rel", ".bsr"),
        "markdown-codeblock": ("markdown",),
    }
    kinds = set(SiteKind.__args__)  # type: ignore[attr-defined]
    assert set(phrases) == kinds, "a SiteKind was added or removed without updating this map"
    for kind, options in phrases.items():
        assert any(phrase in described for phrase in options), (
            f"no reference document mentions the {kind!r} authoring surface"
        )


# ---------------------------------------------------------------------------
# The prose, and how it reaches the wheel
# ---------------------------------------------------------------------------


def test_the_generated_prose_matches_the_docs() -> None:
    """The embedded module and ``docs/reference/*.md`` agree.

    Same generate-and-guard arrangement as the inspector data: the Markdown is
    the reviewable copy, the module is only how it reaches the wheel, and a
    hand-edit to either is caught here rather than shipping a reference that
    disagrees with its own source.
    """
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "generate_reference_prose.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_every_authored_document_is_actually_embedded() -> None:
    """A Markdown file nobody embedded is prose that never reaches a consumer."""
    from bigfix_relevance_analyzer.reference import _prose

    on_disk = {path.stem.upper() for path in DOCS.glob("*.md")}
    assert on_disk == set(_prose.NAMES) == set(_prose.DOCUMENTS)
    assert on_disk, "docs/reference/ has no Markdown at all"


def test_the_universal_prose_states_the_version_comparison_traps() -> None:
    """A guard on the two version traps, both confirmed on live client and session engines.

    These are the highest-consequence facts in the language: each produces a
    *wrong answer* rather than an error, so nothing downstream notices. A
    consumer's model that has not been told will write the broken form, because
    the broken form is what every other language it has seen would accept.

    The expansive source, with the engine transcripts, is
    ``docs/universal_relevance.md``.
    """
    from bigfix_relevance_analyzer.reference import _prose

    universal = _prose.UNIVERSAL_RELEVANCE
    assert "pad of" in universal, "the fix for truncating comparison is missing"
    assert "truncate" in universal.lower(), "the truncation rule is missing"
    assert "as version" in universal, "the one-sided coercion rule is missing"
    assert "left to right" in universal, "the short-circuit direction is missing"


def test_the_universal_prose_states_the_whose_scoping_rule() -> None:
    """A bare name inside `whose` is a world reference, not a property of the item.

    Guarded because it is the kind of rule a model fills in from analogy with
    other languages -- `whose` binds `it`, so surely everything inside is scoped
    to `it` -- and gets exactly backwards. Both halves were confirmed on a live
    client engine and a live session engine: `files whose (exists properties)`
    answers, and `files whose (exists properties of it)` is refused.

    Its practical value is the error-reading advice: an `is not defined` inside a
    `whose` is as often a spurious `of it` as it is a misspelling.
    """
    from bigfix_relevance_analyzer.reference import _prose

    universal = _prose.UNIVERSAL_RELEVANCE
    # Phrases distinctive to this rule's section, checked to survive nothing
    # else: bare "world", "whose" and "of it" all occur elsewhere in the
    # document, so asserting on those would be a guard that cannot fail.
    assert "is a world reference" in universal, "the world-reference rule is missing"
    assert "resolves against the **world**" in universal, "the resolution rule is missing"
    assert "properties of it" in universal, "the refused `of it` example is missing"
    assert "Dropping `of it`" in universal, "the error-reading advice is missing"


def test_the_syntax_prose_states_the_rules_that_are_easiest_to_get_wrong() -> None:
    """A guard on the few facts a model reliably invents wrongly if unstated.

    Each of these was verified against this package's own implementation rather
    than recalled: the escaping rule from the tokenizer, the ``it`` binding rule
    from the binder, and the flattening rule from the breakdown probes. If the
    prose ever loses one, a consumer's model goes back to guessing it.
    """
    from bigfix_relevance_analyzer.reference import _prose

    syntax = _prose.SYNTAX
    assert "%22" in syntax, "the raw-quote rule is missing"
    assert "backslash escapes nothing" in syntax, "the backslash rule is missing"
    assert "`of` binds `it`" in syntax, "the it-binding rule is missing"
    assert "0-based" in syntax, "the item index base is missing"
    assert "no reserved words" in syntax.lower(), "the no-keywords rule is missing"
    assert "error fallback" in syntax, "the `|` semantics are missing"


# ---------------------------------------------------------------------------
# Import cost
# ---------------------------------------------------------------------------


def test_importing_the_package_does_not_build_a_reference() -> None:
    """Neither the package nor this module assembles any prose at import.

    Run in a subprocess because import order elsewhere in this suite would mask
    a regression -- by the time this test runs in-process, everything is already
    imported. The promise being protected is the one in the package docstring:
    cheap and safe to import inside a stdio MCP server.
    """
    script = (
        "import sys\n"
        "import bigfix_relevance_analyzer\n"
        "assert 'bigfix_relevance_analyzer.reference' not in sys.modules, 'package imports it'\n"
        "from bigfix_relevance_analyzer import reference\n"
        "assert 'bigfix_relevance_analyzer.reference._prose' not in sys.modules, 'prose eager'\n"
        "assert 'bigfix_relevance_analyzer.reference._tables' not in sys.modules, 'tables eager'\n"
        "reference.markdown('client-relevance')\n"
        "assert 'bigfix_relevance_analyzer.reference._prose' in sys.modules\n"
        "assert 'bigfix_relevance_analyzer.reference._tables' in sys.modules\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "ok"


# ---------------------------------------------------------------------------
# The CLI surfaces
# ---------------------------------------------------------------------------


def test_the_cli_prints_a_reference(capsys: pytest.CaptureFixture[str]) -> None:
    """``--reference`` takes the dialect names the other flags use, not slugs.

    A caller already knows `client`/`session` from ``--dialect``; making them
    learn ``client-relevance`` for this one flag would be gratuitous.
    """
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--reference", "client"]) == 0
    assert capsys.readouterr().out == reference.client_relevance_reference()

    assert main(["--reference", "dialects"]) == 0
    assert capsys.readouterr().out == reference.get_document("dialects").read()

    assert main(["--reference", "universal"]) == 0
    assert capsys.readouterr().out == reference.get_document("universal-relevance").read()


def test_the_cli_reference_honours_brief_and_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--reference", "session", "--brief"]) == 0
    assert capsys.readouterr().out == reference.session_relevance_reference(detail=Detail.BRIEF)

    assert main(["--reference", "session", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == reference.get_document("session-relevance").to_dict()


def test_asking_for_a_reference_never_analyses_anything(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A question about the language exits 0 even beside an unparsable statement.

    ``--reference`` and ``--rules`` are answered before the positional argument
    is looked at, so a script probing the tool's capabilities cannot be made to
    fail by whatever happened to be on the command line.
    """
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--reference", "client", "exists files ("]) == 0
    assert capsys.readouterr().out.startswith("# Client relevance")

    assert main(["--rules", "exists files ("]) == 0
    assert "unbound-it" in capsys.readouterr().out


def test_the_cli_searches_the_inspector_tables(capsys: pytest.CaptureFixture[str]) -> None:
    """``--search`` makes the capability discoverable and the docs runnable."""
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--search", "registry keys"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# Inspector search: registry keys")
    assert "`keys of <registry key>`" in out
    assert "signature" in out


def test_the_cli_search_narrows_by_dialect(capsys: pytest.CaptureFixture[str]) -> None:
    """Suggesting a session inspector to a client-relevance author is worse than silence."""
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--search", "bes computers", "--dialect", "session"]) == 0
    assert "bes computers" in capsys.readouterr().out

    assert main(["--search", "bes computers", "--dialect", "client"]) == 0
    assert "`bes computers`" not in capsys.readouterr().out


def test_the_cli_search_reports_nothing_found_without_failing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An empty result is an answer, not an error -- exit stays 0.

    A script asking "is there anything called this" reads the output; making it
    read the exit status instead would conflate "no match" with "the tool
    broke".
    """
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--search", "xyzzy"]) == 0
    assert "Nothing matched." in capsys.readouterr().out


def test_the_cli_search_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    """The shape a server would hand a model, straight from the CLI."""
    from bigfix_relevance_analyzer import inspectors
    from bigfix_relevance_analyzer.__main__ import main

    assert main(["--search", "sha", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["query"] == "sha"
    assert payload["results"] == [result.to_dict() for result in inspectors.search("sha")]
