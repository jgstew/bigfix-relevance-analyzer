# bigfix-relevance-analyzer
A python module for working with BigFix Relevance generically. Extract, Analyze, etc.

This is a library first: it is meant to be depended on by other projects
(pre-commit hooks, `besapi`, MCP servers) rather than run directly.

- **No dependencies outside the standard library.** (Not "pure Python" - the
  stdlib XML modules are backed by `pyexpat`, which is C - but it ships with
  CPython and PyPy, so there are no wheels to build and no platform matrix.)
- **It logs, it never prints.** Diagnostics go to the `bigfix_relevance_analyzer`
  logger, which gets a `NullHandler` and nothing else; the library never calls
  `basicConfig` or touches your handlers or levels. Nothing is written to stdout,
  so it is safe to import inside a stdio MCP server, where stray output would
  corrupt the JSON-RPC stream.

## Origin

This project starts from
[jgstew/pre-commit-bigfix#13](https://github.com/jgstew/pre-commit-bigfix/issues/13),
which is the design document for the package: why relevance analysis belongs in
a standalone library rather than inside the pre-commit hooks that consume it,
what the first milestone covers (a relevance extractor and a heuristic
complexity scorer), and the reasoning behind the naming, the dependency
choices, and the roadmap. That issue and its comments are the reference for
decisions made here; read it before making a structural change.

## Roadmap: Python now, possibly Rust later

The short-term goal is **pure Python** - it keeps iteration fast while the hard
part is still unsolved. Relevance has no published grammar, so a real parser
means reverse-engineering one from the console, the docs, and real content;
that research is the long pole, and Python is the cheapest place to do it. The
plan of record is a hand-rolled Pratt parser with the operator, precedence, and
keyword data kept in declarative tables, plus a shared corpus of input to
expected parse trees as the primary asset.

The long-term goal may be to **translate the core to Rust**, exposed as PyO3
wheels for Python consumers and as WebAssembly for a VS Code extension. That is
the honest end-state for "one implementation, every consumer": today a Python
package can serve pre-commit hooks, `besapi`, and MCP servers, but it cannot
serve an editor. Rust would let the same grammar back both without maintaining
two implementations that drift.

Deliberately not started yet: porting during the grammar-research phase would
slow the part that is actually hard. Keeping the grammar in declarative tables
and the corpus separate from the parser is what makes a later port cheap and
provably equivalent - the same corpus has to pass either way. (A tree-sitter
grammar was also considered and deferred; it fights relevance's
keyword-versus-identifier ambiguity, since relevance has no reserved words and
multi-word inspector names.)

## Extracting relevance

`extract_relevance_from_file` finds every relevance statement in a file and
reports where each came from and which dialect it is written in:

```python
from bigfix_relevance_analyzer import extract_relevance_from_file

for site in extract_relevance_from_file("MyFixlet.bes"):
    print(f"{site.line}: [{site.dialect.value}] {site.kind} - {site.text}")
```

Each result is a frozen `RelevanceSite` with `kind`, `text`, `line` (1-based,
in the file), `context` (a short label for messages), and the dialect fields
described under [Which dialect a statement is in](#which-dialect-a-statement-is-in).

| File type | What is extracted |
| --- | --- |
| `.bes`, `.bes.xml` | `<Relevance>`, `<SuccessCriteria Option="CustomRelevance">`, analysis `<Property>` bodies, `{...}` substitutions in Windows-Shell `<ActionScript>`, and session relevance in `<Description>` HTML |
| `.ojo`, `.besrpt`, `.beswrpt`, `.webreport` | `<?Relevance ?>` substitutions and JavaScript `Relevance(...)` / `EvaluateRelevance(...)` calls |
| `.html`, `.htm` | the same, read as a ClientUI dashboard (see below) |
| `.bsr`, `.rel` | the whole file as one statement |
| `.md` | each fenced code block as one statement |

Lower-level entry points (`extract_relevance_from_bes_xml`,
`extract_relevance_from_html_text`, `extract_relevance_from_actionscript`,
`extract_relevance_from_markdown`) take content directly, for callers that
already have it in hand.

### Which dialect a statement is in

`Dialect` is `CLIENT`, `SESSION`, `UNCERTAIN` or `BOTH`. Two independent
opinions decide it, and every `RelevanceSite` keeps both rather than collapsing
them:

| Field | Meaning |
| --- | --- |
| `context_dialect` | What the mechanism said: which element, of which kind of file. `UNCERTAIN` when the mechanism settles nothing. |
| `content_dialect` | What `classify_relevance_dialect` made of the inspectors used in the statement. `None` means it had no opinion. |
| `dialect` | The resolved verdict: definite context wins, otherwise content, otherwise `UNCERTAIN`. |
| `dialect_conflict` | True when context and content each reached a definite, *different* dialect. |

Definite context wins because it is a fact about which engine will evaluate the
statement, not an inference. Content fills in the gaps, and a conflict between
the two is surfaced rather than resolved away - session inspectors in a fixlet's
`<Relevance>` is relevance in the wrong place, and it fails on every endpoint
that evaluates it. Conflicts are logged at `WARNING`.

The classifier only ever uses *positive* evidence: an inspector it does not
recognize contributes nothing. New BigFix versions add inspectors to both
dialects, so an unfamiliar name is never grounds for typing a statement by
elimination or for calling it invalid.

One context case is worth knowing about: relevance in HTML or JavaScript is
almost always session relevance, but **ClientUI dashboards** are HTML rendered
by the BES Client on the endpoint and hold *client* relevance, using the
identical `<?Relevance ?>` syntax. What separates them is the mechanism - a
ClientUI cannot evaluate relevance from JavaScript at all. So a static
substitution in a `.html` file is read as client relevance, a JavaScript
relevance call is always session relevance, and in a file doing both the
mechanism settles nothing for its substitutions, leaving their dialect to the
content classifier.

### Optional lxml adapter

Extraction uses stdlib expat by default. Projects that already parse BES XML
with lxml can hand over their existing tree instead of having it parsed twice:

```bash
pip install 'bigfix-relevance-analyzer[lxml]'
```

```python
from bigfix_relevance_analyzer.extract import extract_relevance_from_lxml_tree

sites = extract_relevance_from_lxml_tree(my_tree)
```

Both paths report identical line numbers, including for a start tag whose
attributes span several lines - a test pins this across the whole example
corpus, since an off-by-one there would shift every reported line in a file.

## The inspector table

`bigfix_relevance_analyzer.inspectors` is the structured table of what relevance
actually defines - properties, casts, binary and unary operators, and the type
universe - parsed from the dumps in `tests/examples/relevance_inspectors/`.

This is a **parser prerequisite, not a parser dependent**. Relevance has no
reserved words and multi-word inspector names, so nothing about the text of
`logged on users of bes computers` says where one name ends and the next begins;
resolving that needs a name table, which is what this is.

```python
from bigfix_relevance_analyzer import inspectors

for entry in inspectors.lookup("drives"):
    print(entry.signature, "->", entry.return_type, sorted(entry.platforms))
# drives -> drive ['windows']
# drives -> filesystem ['debian', 'rhel', 'ubuntu']
# drives -> volume ['macos']
```

Each row keeps the **sources** that defined it, so `dialects` and `platforms`
are derived rather than baked in. That is what makes the example above possible:
`drives` genuinely returns a different type per platform family, and collapsing
rows into one "client" verdict would have destroyed that. It is imported
explicitly rather than from the package root, since most callers only extract.

The table is a **snapshot, not a specification**. New BigFix versions add
inspectors, and the dumps only cover what someone captured - so absence is
grounds for a warning at most, never proof that a name is invalid. Only positive
evidence should be drawn from it, the same discipline the dialect classifier
applies.

`src/bigfix_relevance_analyzer/_inspector_data.py` is generated; the dumps are
the source of truth. Regenerate after adding or editing one:

```bash
python tools/generate_inspector_data.py
```

A pre-commit hook and `tests/test_inspector_data.py` both fail if the two have
drifted. Dump filenames carry their own provenance as
`{dialect}_relevance_{category}[_{context}].txt`, so a newly captured dump is
picked up with no code change.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and packaging
(build backend: hatchling), with a `src/` layout.

```bash
uv sync                    # create .venv and install project + dev dependencies
uv run pytest              # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy                # type-check
```

Set up the git hooks once (the extra hook types let `uv-sync` re-create `.venv` after a pull or
branch switch, and let the pre-push checks below actually run):

```bash
uv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type post-checkout --hook-type post-merge
```

A few slower checks (`pytest`, `uv lock --check`, `uv build --wheel`) are deferred to `git push`
rather than every commit, via `stages: [pre-push, manual]`. Run them by hand with:

```bash
uv run pre-commit run --all-files --hook-stage pre-push
```

The rest of the manual-only hooks (release/build checks, `uv audit`, pyproject and GitHub Actions
schema validation) don't run automatically at all - CI invokes them with `--hook-stage manual`,
which also picks up the `pre-push` ones above:

```bash
uv run pre-commit run --all-files --hook-stage manual
```

### Dependency freshness delay

`pyproject.toml` sets `[tool.uv] exclude-newer = "7 days"`, so `uv lock`/`uv sync`/`uv add` only
consider package versions that were published at least 7 days ago. This is a rolling window (not a
fixed date), giving newly published releases a week to be pulled before this project can depend on
them. To deliberately bypass this - for example to pull in an urgent security fix - run:

```bash
uv lock --exclude-newer=false
```
