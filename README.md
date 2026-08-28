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
that research is the long pole, and Python is the cheapest place to do it.

The parser now exists: a hand-rolled Pratt parser (`parser.py`) over the
existing tokenizer, producing frozen AST nodes (`nodes.py`) with the operator,
precedence, and keyword data kept in declarative tables (`grammar.py`). The
primary asset is the shared corpus of input to expected S-expression parse
trees in `tests/corpus/*.rlvcorpus` - a port is proven equivalent by making the
same corpus pass. `parse_relevance` raises a positioned `ParseError`;
`try_parse_relevance` never raises, which is the conservative "unknown, skip"
interface for scorers and hooks - including for an expression nested deeper than
`MAX_PARSE_DEPTH`, since parsing recurses and the alternative is a
`RecursionError` escaping an interface whose whole promise is that nothing
escapes it. Every relevance site in the example corpus
currently parses; grammar decisions that have not been spot-checked against a
real evaluator are tagged `[unverified]` in their corpus record titles. Not
done yet, deliberately: type-directed disambiguation, error-recovery nodes,
and rebasing the complexity scorer onto the AST.

The node set follows the engine's own, so that later analysis is a translation
rather than a mapping exercise. Three constructs the engine gives dedicated
nodes are dedicated here too rather than modelled generically - `|` is `Bar`,
not a binary operator, because it is error fallback and has no row in the
operator table; `item 0 of (...)` is `ItemOf`, whose index is 0-based and must
be an integer literal; and `number of x` is `NumberOf`, the sibling of the
`Exists` node that already existed. Numerals carry the engine's magnitude
classification (`NumberKind`) as a derived property rather than as three
separate node classes, which keeps the literal verbatim and the corpus stable.

Recognising `item 0 of (...)` without also swallowing `item "foo" of folder "c"`
is the one place this needs care: `item <string> of <folder>` is a real
inspector, and telling the two apart in general needs the object's type. Only an
integer-literal index is specialised, on the same positive-evidence-only rule
the rest of the package follows.

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

## Scoring complexity

`analyze_relevance_complexity` gives a statement a heuristic score, along with
the individual metrics that produced it, so a pre-commit hook can threshold on
the number and still say *why* something was flagged:

```python
from bigfix_relevance_analyzer import analyze_relevance_complexity

result = analyze_relevance_complexity(
    'exists files whose (name of it starts with "bes") of folder "/tmp"'
)
print(result.score, result.whose_clauses, result.max_of_chain)
```

The score covers two different axes. **Readability** is the token-shaped part:
length, nesting, `of` chains, `whose` filters. **Evaluation cost** is what the
statement does to the client's eval loop, which does not follow from size -
`exists descendants of folder "C:\"` is eight tokens and walks an entire disk on
every evaluation cycle. `costly_inspectors` names the heavy families that were
charged for, so a warning can point at them:

```python
result = analyze_relevance_complexity('exists descendants of folder "C:\\"')
print(result.evaluation_cost, result.costly_inspectors)
# 12.0 ('folder recursion',)
```

Those families are deliberately **not** weighted equally - hashing a file is a
different order of expense from reading a few lines out of one - and neither is
the same family across dialects, when the underlying inspector isn't either.

Cost is also dialect-scoped, per rule rather than per table, and applying to
both dialects does not mean costing the same in both. Session relevance cannot
read a file at all, so `sha1 of <string>` is real work but nowhere near `sha1
of <file>` on a client - the `hashing` rule charges each accordingly. `wmi`
exists only on a Windows client and `results of <bes fixlet>` only on the
server, so neither is charged against the other dialect at all. Pass the
dialect - the extractor already knows it for every site - to get this scoping:

```python
for site in extract_relevance_from_file("MyFixlet.bes"):
    result = analyze_relevance_complexity(site.text, site.dialect)
```

Without a dialect, nothing is excluded. The client-side families come from the
candidate list in `jgstew/besapi`'s `examples/fixlet_add_mime_field.py`; every
inspector name a rule matches on is checked against the QnA dumps by a test, and
so is each rule's declared dialect, so the table stays grounded in what BigFix
actually defines. Two things are not grounded that way and say so: the tiers are
a judgement call rather than a benchmark, and the session-only rules are a seed
rather than a survey - there is no curated equivalent of the besapi list for the
server side yet. `WEIGHT_EVALUATION_COST` turns the whole axis off if a consumer
only cares about readability.

Counting runs over the token stream, never over raw text, so a comment
mentioning `whose` or the word `and` inside a string literal cannot inflate the
score. The metrics are heuristics and the weights are deliberately module-level
constants (`WEIGHT_WHOSE_CLAUSE` and friends) so they can be tuned against
real content without touching the counting.

### The tokenizer

`bigfix_relevance_analyzer.tokenizer` is the lexer the scorer counts against,
and the front end the future parser will sit on. It turns text into a lossless
stream of tokens: joining their texts reproduces the input exactly, whitespace
and comments included, which is what a formatter or auto-fixer would need later.
It never raises - malformed relevance yields error tokens, because content
extracted from the wild is regularly truncated or broken and a scorer still has
to produce a number for it.

It deliberately does **not** bind multi-word inspector names; that needs the
inspector table below and type-directed disambiguation, both of which are parser
work. Keeping this layer table-free makes it total: any input lexes, and the
same input always lexes the same way, regardless of which dumps happen to exist.

## What `it` refers to

This section and the two after it come out of
[jgstew/bigfix-relevance-analyzer#8](https://github.com/jgstew/bigfix-relevance-analyzer/issues/8),
which reverse-engineers how the Fixlet Debugger implements `it` highlighting,
its graphical breakdown mode, and its static type checker. The striking result
is that the first two are **pure AST transforms** - neither needs an evaluator
embedded here, and both are among the cheapest things on that list rather than
the most expensive. That issue is the reference for the behavior described
below, including which claims were executed against a real engine and which
were not.

`resolve_it_bindings` takes a parsed tree and reports, for every `it` in it,
which construct supplies its context - the "click `it`, see its referent"
feature, as a pure AST pass with no evaluator involved.

```python
from bigfix_relevance_analyzer import parse_relevance, resolve_it_bindings

src = "files whose (size of it > 1000)"
for binding in resolve_it_bindings(parse_relevance(src)):
    print(src[binding.it.span.start : binding.it.span.end], "->", binding.binder)
# it -> Binder.WHOSE
```

**BigFix's own error message for this is wrong**, and it is worth stating
plainly because following it produces a resolver that disagrees with the
evaluator. The engine prints `"It" used outside of "whose" clause.`, but `of`
introduces a context too: `(it, it) of 5` evaluates to `5, 5`, and
`name of it of file "..."` gives the file's name. So the rule is that `it` binds
to the nearest enclosing *context-introducing* construct, of which there are
two - `whose (...)`, binding the element being filtered, and `of`, binding the
right-hand operand. `if/then/else` introduces nothing and passes its enclosing
context through, so `if true then it else it` is an error at the top level. The
engine's own internal template says `'$token' used without context`, which is
the accurate wording and the one this package uses.

Order matters in one place worth knowing about: in `A of B`, the object `B` is
*not* evaluated in its own context. Only `A` sees `B`. Getting that backwards
looks right on flat expressions and binds the wrong node on every nested one.

An unbound `it` is reported, not raised - the entry's `context` is `None`. A
resolver that stops at the first bad `it` is no use to an editor colorizing as
you type, which is the same reason `try_parse_relevance` exists.

## Per-level object counts

`breakdown_probes` reproduces the mechanism behind the Fixlet Debugger's
graphical breakdown mode: how many objects each level of an expression produced.
The debugger does not instrument its evaluator - it synthesizes an ordinary
relevance query per level and runs it through the normal engine. That is
something this package can do too, since it is string generation over a tree.

So this is **generation only**: the library emits probe text and the caller
evaluates it, against `qna.exe`, session relevance, the REST `clientquery` API,
or anything else it has. Nothing is added to the dependency list, and the
capability stops being Windows-GUI-only.

```python
from bigfix_relevance_analyzer import breakdown_probes, parse_relevance

src = r'names of files whose (size of it > 1000) of folder "C:\Windows"'
for level in breakdown_probes(src, parse_relevance(src)):
    print(level.label, "->", level.probe.relevance)
```

Hand the rows back to `interpret_count_results`. A probe answers **once per
context object**, not once per level, so the result is reconciled positionally
against the context objects; a length mismatch is an internal error, and is the
condition behind the debugger's own `Result counts do not match result number`.
Three outcomes, and two of them are lossy in ways worth surfacing rather than
hiding:

| Result | `Outcome` | Meaning |
| --- | --- | --- |
| `N > 0` | `COUNT` | the level produced N objects |
| `0` | `EMPTY_OR_ERROR` | evaluated fine and produced nothing - *or* errored in a plural context, which relevance flattens to empty |
| `-1` | `NOT_EVALUABLE` | the level could not be evaluated, e.g. a singular reference to a nonexistent object |

`-1` is also indistinguishable from a legitimately computed `-1`. Both
ambiguities are properties of the probe design rather than something a caller
can resolve, so they are named in the API instead of being reported as a
confident zero.

Levels are found throughout the expression, not only along its outermost `of`
chain - a chain inside a `whose` filter, an operator's operand, an `if` branch
or a tuple item is a level too. One inside a filter is measured against the
collection *before* filtering, which is what `it` means in there: in the example
above, `size of it` is probed against all 25 files rather than the 21 that
survive.

Making that work means rewriting each level's context so it stands on its own,
since a node's source text is written relative to wherever it sits. Where a
sub-expression reaches its context through `it`, that `it` is replaced; where it
is applied to an object below an `of`, it is composed back on. Only the second
of those is a composition, which is why `file "a"` inside a filter stays
`file "a"`.

A `whose` level counts what survived its filter, so the number alone says
nothing about how selective the filter was. Those levels come back paired: a
`Level.unfiltered` probe measures the same collection without its filter, and
comparing the two is what makes selectivity visible. In the example above the
pair answers 21 and 25.

There is one detail that is easy to get wrong and fails loudly when you do: the
measured expression is rewritten against `it` rather than copied from the
source. For the level `files of folder "C:\Windows"` the measured text is
`files of it`, because a property without its direct object is not a valid
expression - splicing the raw text gets you
`The operator "files" is not defined.`

## Diagnostic vocabulary

`bigfix_relevance_analyzer.diagnostics` is a catalog of the messages BigFix
itself produces, as `str.format` templates. Nothing emits them yet; it exists so
that when a checker lands, its output is wording BigFix authors already
recognize rather than a second vocabulary to learn. Imported explicitly, like
`inspectors`.

Two vocabularies are kept, because the same broken expression produces different
messages depending on which part of BigFix sees it. The runtime collapses
everything into "operator not defined"; the debugger's static type checker knows
whether it was a property, a cast or an operator, and names the types. Prefer
the type-checker forms - each entry records which it is.

The `it` message above is catalogued as what the runtime says, wrong rule and
all, next to the accurate `used-without-context`. Where the recovered templates
are inconsistent with each other they are reproduced as recovered, with the
inconsistency noted, rather than tidied up.

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

## Type checking

`bigfix_relevance_analyzer.typecheck` types an expression against the inspector
table and reports findings in BigFix's own wording. It is imported explicitly,
like `inspectors`. This is the first slice: literals, casts, operators,
aggregation, tuples and conditionals are typed; `of` chains and `whose` filters
still need property resolution and come back as unknown.

```python
from bigfix_relevance_analyzer import Dialect
from bigfix_relevance_analyzer.typecheck import TypeEnvironment, check, resolve_property

env = TypeEnvironment.create(Dialect.CLIENT)
print(check(parse_relevance('1 + "a"'), env).diagnostics[0].message)
# the operator '+' is not defined for the types '<integer> + <string>'
```

A value's type is a **set**, because inspectors are overloaded and because the
same name resolves differently per platform. Later inspectors narrow it:

```python
drives = resolve_property("drives", None, env)
# {drive, filesystem, volume} on all five platforms
resolve_property("block size", drives.types, env)
# {integer} on debian, rhel, ubuntu - `block size` exists on none of the others
```

So "where can this run?" falls out of typing rather than needing to be declared.
Pass a `platform` to `TypeEnvironment` if you know it; leaving it out keeps every
platform in play and lets the narrowing report the answer.

`types` distinguishes `None` from the empty set deliberately. `None` means the
table said nothing, which - as everywhere in this package - is grounds for a
warning at most, never proof. Empty means every candidate was ruled out.

### Platform coverage is reported, not enforced

A single statement routinely targets several platforms at once, guarding
platform-specific inspectors behind `if`/`then`/`else` so the wrong platform
never evaluates the branch that would fail on it. The statement is correct; each
branch is correct only somewhere. The example corpus has a fixlet whose `then`
branch is Debian/Ubuntu-only and whose `else` branch is RHEL-only.

So platform sets **intersect along a chain** and **union across alternatives** -
`if` branches, and the two sides of `|`. An empty platform set is never an error
by itself: findings live on the type axis and have to hold on every platform.
Treating platforms as a constraint instead would report valid, shipped relevance
as broken, which is the worst thing this package could do.

The engine agrees. Its own checker carries `at most one branch of an
if-statement may have type errors` - deliberate tolerance for exactly this
idiom, and `check` implements it: one failing branch is survivable, two is not.

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
