# bigfix-relevance-analyzer
A python module for working with BigFix Relevance generically. Extract, Analyze, etc.

It parses client and session relevance, type-checks it, resolves every
inspector against the inspector tables, binds each `it`, scores complexity and
evaluation cost, lints BigFix content (`.bes` files and more), and suggests
safe fixes.

## Ways to use it

| Where | What you get |
| --- | --- |
| [Browser playground](#browser-playground) | Paste relevance into a self-contained [web page](https://www.jgstew.com/files/bigfix-relevance-analyzer-playground.html); nothing to install, nothing sent anywhere |
| [VS Code extension](#vs-code-extension) | Diagnostics, hover and quick fixes [as you type](https://marketplace.visualstudio.com/items?itemName=jgstew.bigfix-relevance-developer) |
| [Command Line `uvx`](#command-line-via-uvx) | Analyse one statement, or lint files, with nothing installed |
| [pre-commit hook](#pre-commit-hook) | Lint the relevance in a BigFix content repo on every commit |
| [Python library](#python-library) | `import` it from PyPI into your own tool |

### Browser playground

[bigfix-relevance-analyzer-playground.html](https://www.jgstew.com/files/bigfix-relevance-analyzer-playground.html)
runs this package in the browser as WebAssembly, so nothing needs installing.
The page is a single self-contained file (the only thing it fetches is its
icon), so the relevance you paste never leaves your browser. It is updated on
each release.

### VS Code extension

Install
[BigFix Relevance Developer](https://marketplace.visualstudio.com/items?itemName=jgstew.bigfix-relevance-developer)
from the Marketplace. It runs this package's [language server](#language-server)
as WebAssembly, so it needs nothing else installed. It also colors relevance and
BigFix ActionScript, including the action scripts and relevance inside `.bes`
files.

### Command line, via `uvx`

Analyse a statement (or every relevance site in a file) and print a report:

```bash
uvx bigfix-relevance-analyzer "(version of client, name of it, version of it) of operating system"
```

Lint files or a directory (the current one by default), exiting non-zero on
errors:

```bash
uvx --from bigfix-relevance-analyzer bigfix-relevance-lint path/to/content
```

See [From the command line](#from-the-command-line) and
[Linting content](#linting-content) for the flags.

### pre-commit hook

The `bes-relevance-lint` hook in
[pre-commit-bigfix](https://github.com/jgstew/pre-commit-bigfix) runs this
package's linter over the `.bes` files in a commit:

```yaml
- repo: https://github.com/jgstew/pre-commit-bigfix
  rev: <tag>
  hooks:
    - id: bes-relevance-lint
```

### Python library

```bash
pip install bigfix-relevance-analyzer
```

```python
from bigfix_relevance_analyzer import analyze_relevance

report = analyze_relevance('exists file "C:\\foo.txt"')
report.parsed, report.check.value.types  # (True, frozenset({'boolean'}))
```

See [Analysing one statement](#analysing-one-statement) and the sections after
it for the API.

## Design notes

As a library it is meant to be depended on by other projects (pre-commit
hooks, `besapi`, MCP servers, the editor and the playground), so:

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
done yet, deliberately: type-directed disambiguation, rebasing the complexity
scorer onto the AST, and error-recovery nodes - the last of these tracked in
[#10](https://github.com/jgstew/bigfix-relevance-analyzer/issues/10) with the
rest of the editor-surface work, since a partial AST has no consumer until
there is an editor to draw it.

The node set follows the engine's own, so that later analysis is a translation
rather than a mapping exercise. Three constructs the engine gives dedicated
nodes are dedicated here too rather than modelled generically - `|` is `Bar`,
not a binary operator, because it is error fallback and has no row in the
operator table; `item 0 of (...)` is `ItemOf`, whose index is 0-based and must
be an integer literal; and `number of x` is `NumberOf`, the sibling of the
`Exists` node that already existed. Numerals carry the engine's magnitude
classification (`NumberKind`) as a derived property rather than as three
separate node classes, which keeps the literal verbatim and the corpus stable.

The engine reads `item <index> of` and `items <index> of` as tuple-index syntax
whatever the object is. So the inspector table's `item <string> of <folder>` is
unreachable: every client target refuses `item "foo" of folder "/etc"` with
`This expression contained a tuple index which was not an integer literal.`
The parser follows suit and raises that error for any index that isn't an
integer literal, parenthesized or not (`item (1) of (1, 2)` is still `2`).

The long-term goal may be to **translate the core to Rust**, exposed as PyO3
wheels for Python consumers and as WebAssembly for editors and browsers. The
Python package already serves pre-commit hooks, `besapi`, MCP servers, and an
editor: the
[VS Code extension](https://marketplace.visualstudio.com/items?itemName=jgstew.bigfix-relevance-developer)
compiles it, with a CPython, into a WebAssembly component. Rust could make that
WebAssembly smaller and faster to start, while one grammar still backs
every consumer without two implementations that drift.

Deliberately not started yet: porting during the grammar-research phase would
slow the part that is actually hard. Keeping the grammar in declarative tables
and the corpus separate from the parser is what makes a later port cheap and
provably equivalent - the same corpus has to pass either way. (A tree-sitter
grammar was also considered and deferred; it fights relevance's
keyword-versus-identifier ambiguity, since relevance has no reserved words and
multi-word inspector names.)

## Analysing one statement

Everything below can be run at once. `analyze_relevance` classifies the dialect,
lexes, parses, type-checks, resolves every name against the inspector tables,
binds each `it`, generates breakdown probes and scores complexity, and returns
the results together as a frozen `RelevanceAnalysis`.

```python
from bigfix_relevance_analyzer import analyze_relevance

report = analyze_relevance(r'exists file "C:\foo.txt" whose (size of it > 100)')

report.dialect  # Dialect.CLIENT  (report.dialect_assumed says if it was a guess)
report.parsed  # True; report.parse_error is None
report.sexpr  # '(exists (whose (ref "file" ...'
report.mermaid  # 'flowchart TD\n    n0{{"exists"}}\n    n1{"whose"}\n...'
report.check.value.types  # frozenset({'boolean'})
report.platforms  # frozenset({'windows', 'macos', 'debian', 'rhel', 'ubuntu'})
report.unknown_references  # () - every name resolved
report.unbound_its  # () - the `it` is bound by the `whose`
report.complexity.score  # 22.0
report.levels  # breakdown probe text, one per measurable level
```

Pass the `dialect` extraction already worked out rather than having it guessed
again from a fragment, and `platform` to narrow client lookups to one platform:
`analyze_relevance(site.text, site.dialect, platform="windows")`.

`classify_relevance_dialect` runs on raw text before parsing and is deliberately
blind to common English words like `file` - too collision-prone in unparsed
prose to trust, per its own docstring. Once the statement has parsed,
`report.resolved_dialect` fills that gap from the other direction: the
intersection, across every resolved `Reference`, of the dialects its table rows
are actually defined in. `files of folder "C:\Windows"` classifies as
`None` (no text marker fires) but resolves as `Dialect.CLIENT`, because `files`
is a client-only inspector - real evidence a text classifier can never use.
`report.dialect_assumed` checks both: false the moment either one, or an
explicit `dialect` argument, settles on one specific dialect.

`report.mermaid` (`nodes.to_mermaid`) renders the same tree as a Mermaid
`flowchart` instead of an S-expression - a real graph built by walking the
parsed structure, not a 1:1 rendering of every node. `to_sexpr` already is
that, in text; a diagram's job is to stay legible instead, so three things
fold without losing information: an `of` chain becomes a chain of
`--"of"-->` edges rather than a box per link (`Of` is right-associative, so
it never branches - except an explicit `(a of b) of c`, which keeps its own
`of` box, since collapsing it would be ambiguous with the un-parenthesized
form); a `Reference`'s literal index folds into its own label (`key 0`,
`firsts "\Sites\"`); an all-literal tuple/collection folds to one box. What
used to be a `ref`/`str`/`num` label prefix is a node shape instead - a
rectangle is a name, a stadium a literal, a hexagon an operator, a rhombus a
branch point (`if`, `whose`). On a real 49-node statement this took the
diagram to 24 boxes. Arrows point the way evaluation actually flows, not the
way the tree nests - an object into the property read off it, a condition
into `if` - so a long chain's true starting point (the innermost object)
lands at the top, with the final result at the bottom; that is what makes
`TD` read top-to-bottom as a flowchart instead of upside down. Following
evaluation is also why an object routes *past* a `whose` to the collection it
filters: `files whose (P) of folders` nests as `Of(Whose(files, P), folders)`,
but nothing about the folders flows into the filter - the folders yield their
files, and only then does `P` reduce them - so it draws as
`folders --of--> files --collection--> whose`, with the reduced set flowing
onward. The CLI embeds it as a fenced ` ```mermaid ` block,
which GitHub, VS Code, and most Markdown viewers render
inline.

Analysis never raises on bad relevance. A statement that does not parse comes
back with `parse_error` set, `parsed` false, and the tree-dependent fields
empty; the dialect, the token stream with its error tokens positioned, and the
complexity metrics - which are counted lexically - are still there. That is the
same conservative contract as `try_parse_relevance`, for the same reason: the
callers this exists for are handed half-written statements constantly.

`report.to_dict()` renders the whole thing as JSON-serializable plain data, for
consumers across a wire.

### From the command line

```bash
python -m bigfix_relevance_analyzer 'exists file "C:\foo.txt" whose (size of it > 100)'
```

Without installing anything, the same report runs through `uvx` under the
package's own name:

```bash
uvx bigfix-relevance-analyzer "(version of client, name of it, version of it) of operating system"
```

There are three output formats:

- **Plain text** (the default) is for a person at a terminal. It starts with a
  verdict (`OK`, `Parses, with warnings`, or `Problems found`) and the
  dialect. Then come aligned rows: the result type, the platforms the
  statement can evaluate on, each inspector and what it returns, what each
  `it` refers to, the parse tree as a one-line S-expression (cut at 100
  characters), and the complexity score. If
  `lint.py`'s rules found anything (a parse error, an unbound `it`, a type
  error, an unknown inspector with "did you mean" suggestions, or complexity /
  evaluation cost past its default ceiling), an `Issues` list follows, with a
  `^` under the position of a parse error. When a fix exists, a
  `Suggested fix` comes next (see [Auto-fix](#auto-fix)). It ends with a
  closing line: `No issues found.` or the error/warning tally. Colour is used
  only on a terminal, and never when `NO_COLOR` is set.
- **`--markdown`** is the same report as Markdown, for pasting into an issue
  or a PR: the statement, a summary table, and the same `Issues` and
  `Suggested fix` sections.
- **`--json`** is for a program, an MCP server or an AI agent (see below).

`--verbose` adds one section per further analysis
(Lexing, Parse tree, Platforms, Inspectors, `it` bindings, Breakdown probes,
Complexity): aligned plain text by default, or with `--markdown`,
GitHub-flavored tables for the tabular sections and fenced code blocks for the
statement source, the S-expression, and each breakdown probe. The S-expression is
always there in verbose mode; the Mermaid flowchart is additionally behind
`--mermaid` (which implies `--verbose`, since the parse tree is the only
place it renders) in both output modes - Markdown and `--json`'s `to_dict()`
(whose own `mermaid` parameter defaults to off the same way) - since it costs
a line per box and per edge and on a real statement outweighs the rest of the
report combined. `--json` always includes everything, verbose or not, plus
the same findings under `"findings"`. `--dialect client|session` forces the
dialect and `--platform windows` narrows the lookups; with no argument the
statement is read from stdin. The exit status is 1 when anything at error
severity was found (a parse failure, a type error, an unbound `it`, ...) and 0
otherwise, the same gate `--check` uses, so a shell check can rely on it. This is the only part of the package
that writes to stdout - importing the library still prints nothing.

When the argument is a path to a file that actually exists, it is run through
`extract_relevance_from_file` first, and every relevance site found is analysed
and reported in turn - each against the dialect extraction already determined
for it, so a `.bes` file's `<Relevance>` and its `<Description>` HTML are each
checked as what they really are, not both guessed at once:

```bash
python -m bigfix_relevance_analyzer MyFixlet.bes
```

Anything that is not a real, existing path - including a typo'd relevance
statement that happens to contain a `/` - is analysed directly as relevance
text; only an actual filesystem hit switches to extraction. `--dialect` still
overrides every site when passed. A file with no relevance in it reports that
and exits 0; the exit status otherwise reflects whether every site parsed.

## Extracting relevance

`extract_relevance_from_file` finds every relevance statement in a file and
reports where each came from and which dialect it is written in:

```python
from bigfix_relevance_analyzer import extract_relevance_from_file

for site in extract_relevance_from_file("MyFixlet.bes"):
    print(f"{site.line}: [{site.dialect.value}] {site.kind} - {site.text}")
```

Each result is a frozen `RelevanceSite` with `kind`, `text`, `line` (1-based,
in the file, where the statement itself starts - below its tag, fence or
`<?Relevance` when a line break comes first), `context` (a short label for
messages), and the dialect fields
described under [Which dialect a statement is in](#which-dialect-a-statement-is-in).

| File type | What is extracted |
| --- | --- |
| `.bes`, `.bes.xml` | `<Relevance>`, `<SuccessCriteria Option="CustomRelevance">`, analysis `<Property>` bodies, `{...}` substitutions in Windows-Shell `<ActionScript>`, and session relevance in `<Description>` HTML |
| `.ojo`, `.besrpt`, `.beswrpt`, `.webreport` | `<?Relevance ?>` substitutions and JavaScript `Relevance(...)` / `EvaluateRelevance(...)` calls |
| `.html`, `.htm` | the same, read as a ClientUI dashboard (see below) |
| `.bsr`, `.rel` | the whole file as one statement |
| `.md` | each fenced code block tagged ```` ```relevance ````, ```` ```client_relevance ````, or ```` ```session_relevance ```` as one statement -- untagged fences and other languages (```` ```python ````, ```` ```bash ````, ...) are skipped |

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

> **Planned for deprecation and removal.** Once
> [#111](https://github.com/jgstew/bigfix-relevance-analyzer/issues/111) lands,
> this adapter will be deprecated and then removed entirely, along with the
> `[lxml]` extra. That issue fixes line numbers shifted by encoded line feeds
> (`&#10;`) inside BES elements, which needs the raw bytes that expat keeps
> and an lxml tree has already discarded. New code should use
> `extract_relevance_from_file` (the expat path) instead.

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
The articles `a`, `an` and `the` (whole words, any case) are trivia too: the
engine skips them wherever they stand, so `"x" as a string` is `"x" as string`.
It never raises - malformed relevance yields error tokens, because content
extracted from the wild is regularly truncated or broken and a scorer still has
to produce a number for it.

It deliberately does **not** bind multi-word inspector names; that needs the
inspector table below and type-directed disambiguation, both of which are parser
work. Keeping this layer table-free makes it total: any input lexes, and the
same input always lexes the same way, regardless of which dumps happen to exist.

## Linting content

`bigfix_relevance_analyzer.lint` turns the analyses above into pre-commit-shaped
verdicts. Every rule but two is always on (the table below lists them all):
parse failures, an `it` with nothing to bind to, any other type-check
diagnostic, an ActionScript `{` that never closes, and a path that could not
be read at all are errors; an inspector no dump defines is a warning. The
other two - complexity
score and evaluation cost - are *also* on by default, at a generous built-in
ceiling (`DEFAULT_MAX_SCORE = 550`, `DEFAULT_MAX_EVALUATION_COST = 50`) chosen
to sit well above ordinary content and catch only the genuinely extreme;
content that legitimately needs to be this complex or this expensive should
raise the ceiling rather than have the rule stay silent about it:

```python
from bigfix_relevance_analyzer import LintConfig, lint_paths

findings = lint_paths(changed_paths, LintConfig())  # built-in ceilings
findings = lint_paths(changed_paths, LintConfig(max_score=800))  # raised for this repo
for finding in findings:
    print(finding)
```

```
MyFixlet.bes:41: error [parse-error] col 18: expected ')'
MyTask.bes:88: error [complexity] score 640 > 550 (whose_clauses=9, max_of_chain=7, tokens=340)
MyDashboard.ojo:12: warning [unknown-inspector] no dump defines `bes computer group`
```

Every rule, its default severity, and what switches it on. This table is
generated from `lint.RULES`, which is also what `bigfix-relevance-lint
--list-rules` prints and what a consumer should join a finding's `code`
against - so a hook, a CI log and an MCP server all explain a finding the
same way instead of each inventing a description:

| Code | Default | Fires when | Ceiling |
| --- | --- | --- | --- |
| `complexity` | error | the complexity score is above the ceiling | `max_score` (default 550) |
| `error-token` | error | the statement contains text that could not be lexed | always on |
| `evaluation-cost` | error | the evaluation cost is above the ceiling | `max_evaluation_cost` (default 50) |
| `file-error` | error | a path given to the linter does not exist, could not be read, or is a file type it does not lint | always on |
| `max-depth-exceeded` | error | a directory tree was deeper than the walk's limit, so it was not fully scanned | always on |
| `parse-error` | error | the statement could not be parsed | always on |
| `type-error` | error | the type checker reported a problem beyond an unbound `it` | always on |
| `singular-required` | error | a plural where the engine requires a single value | always on |
| `site-type-mismatch` | error | the value does not fit the kind of site it was extracted from | always on |
| `unbound-it` | error | `it` is used where there is no context to bind it to | always on |
| `unterminated-substitution` | error | an ActionScript `{` is not closed on its line, so the action fails there | always on |
| `unterminated-processing-instruction` | error | a `<?Relevance` has no closing `?>`, so its relevance was not linted | always on |
| `xml-parse-error` | error | a BES XML file does not parse, so nothing in it was linted | always on |
| `mixed-dialect` | error | inspectors exclusive to client relevance and to session relevance in one statement | always on |
| `non-unique-risk` | warning | a property written singular where more than one value may come back | always on |
| `plural-preferred` | warning | a singular spelling mid-chain, where the plural reads safer | always on |
| `version-truncating-compare` | warning | a version comparison that truncates to the shorter operand's components | always on |
| `version-like-string-compare` | warning | two version-looking strings compared as strings, not as versions | always on |
| `actionscript-keyword` | error | an ActionScript command word used as a relevance name | always on |
| `unknown-inspector` | warning | a name no inspector dump defines | always on |
| `unterminated-code-fence` | warning | a relevance code fence in markdown is never closed, so its relevance was not linted | always on |
| `plural-substitution` | warning | an ordinary ActionScript substitution's value may be more than one value | always on |
| `non-renderable-substitution` | warning | an ordinary ActionScript substitution's value is an opaque object with no text form | always on |

`unterminated-substitution` is the one rule about the ActionScript around the
relevance rather than the relevance itself. The action engine substitutes line
by line, so a `}` on a later line never closes a `{`. Real actions (issue 52,
BES 11.0.6.137) behaved the same inside `createfile until` bodies and outside
them:

| Line | Result | Reported |
| --- | --- | --- |
| `x { name of operating system` | action fails | yes |
| `x {   ` (trailing spaces) | action fails | yes |
| `parameter "p" = "try {"` (the `"` follows the `{`) | action fails | yes |
| `try {`, `} catch {`, `{` alone | written literally | no |

A `//` comment line is not reported, since it never runs, except inside a
heredoc body, where `//` is content. There is no autofix: `}` and `{{` mean
different things, and only the author knows which was meant.

Three more rules come from the same place, extraction, and exist for the same
reason: each is content the extractor could not read relevance out of, which
would otherwise lint clean. `unterminated-processing-instruction` is a
`<?Relevance` with no `?>` after it. A body may span lines, but in a BES
`<Description>` it must close before `</Description>`. `unterminated-code-fence`
is a fence tagged `relevance`, `client_relevance` or `session_relevance` that is
never closed; it's a warning, because CommonMark makes that valid markdown. An
unclosed fence of any other language is not reported. `xml-parse-error` is a
`.bes` file that is not well-formed XML, reported at the line the parser
stopped on.

There is no CLI spelling to disable `complexity`/`evaluation-cost` entirely -
only to raise their ceiling. A caller that wants a rule off altogether passes
`None` for it through the library API: `LintConfig(max_score=None)`.

The same rules are reachable from the command line through the
`bigfix-relevance-lint` console script this package installs, which is what a
pre-commit hook's `entry:` calls. `bigfix-relevance-analyzer --check` (or
`python -m bigfix_relevance_analyzer --check`) is the same command: it hands
every other argument to `bigfix-relevance-lint` unchanged, so it takes all of
the same flags, e.g. `uvx bigfix-relevance-analyzer --check --max-score=800
file1.bes file2.bes`.

```yaml
- repo: https://github.com/jgstew/pre-commit-bigfix
  rev: <tag>
  hooks:
    - id: bes-relevance-lint
```

Without pre-commit, `uvx` fetches and runs the console script without
installing anything:

```bash
uvx --from bigfix-relevance-analyzer bigfix-relevance-lint
```

That walks the current directory with the default rules; every flag below works
the same way after the script name, e.g. `uvx --from bigfix-relevance-analyzer
bigfix-relevance-lint --max-score=800 path/to/content`.

An argument that contains whitespace and is not an existing path is linted as
a relevance statement instead of a file, so a single expression can be checked
directly:

```bash
uvx --from bigfix-relevance-analyzer bigfix-relevance-lint "(version of client, name of it, version of it) of operating system"
```

`bigfix-relevance-lint` adds `--error CODE` / `--warn CODE` / `--ignore CODE`
(each repeatable) to override a rule's default severity per repo, and
`--fail-on-warning` for a repo that wants zero tolerance even for an unknown
inspector name.

`--fix` applies every safe fix in place, in every file type the linter reads
(see [Writing fixes back into files](#writing-fixes-back-into-files)), prints
one line per fix, then the findings left standing:

```text
Fixlet.bes:12: fixed [plural-preferred] setting -> settings
Report.ojo:3: fixed [singular-required] names of bes computers -> unique value of names of bes computers
notes.rel:1: not fixed [plural-preferred] undecodable bytes on line 1
```

It exits `1` whenever it fixed anything, even with nothing left to report:
pre-commit's convention is that a hook which modifies files fails, so the fix
is reviewed and staged rather than committed unread. A second run then passes.
`--json` with `--fix` prints `fix_paths_to_dict()`'s payload. `--fix --diff`
writes nothing: it prints what `--fix` would change as a unified diff per file
on stdout (ready for `patch` or `git apply`), everything else `--fix` would
print on stderr, and exits as `--fix` would - `1` if anything would change.

Called with **no path arguments at all**, either entry point walks the current
directory instead of erroring - `bigfix-relevance-lint` on its own, or
`--check` with nothing after it. This is only for the argument-less case: an
*explicit* path, including `.`, is never expanded - it's taken literally, the
same as any other path, so `bigfix-relevance-lint .` finds nothing rather than
walking (a directory argument is a no-op). A *file* named explicitly whose
suffix no extractor reads is a `file-error`, not a silent pass; the walk skips
such files quietly. The walk skips `.git`, `__pycache__`, `node_modules`, `dist`, `build`,
`venv`, `env`, and any other dot-prefixed directory - a fixed list rather than
`.gitignore`-awareness, since honoring `.gitignore` would mean depending on a
`git` binary and a repository actually being present, and this package stays
zero-dependency and works on a bare checkout of content. It also stops after
`--max-depth` directory levels (6 by default) and reports a
`max-depth-exceeded` error for wherever it stopped, rather than silently
skipping whatever was deeper - a limit this generous being hit at all is worth
a human looking at the tree, not a quiet truncation that would look identical
to a clean, fully-scanned run:

```bash
bigfix-relevance-lint                    # walk .
bigfix-relevance-lint --max-depth=10     # walk ., 10 levels deep
bigfix-relevance-lint .                  # NOT a walk -- one literal path, "."
```

Not a rule at any of the three entry points: `RelevanceAnalysis.missing_platforms`
- a platform absent from the dumps is not proof it's unsupported there, so it
stays a fact to read off the analysis directly rather than a finding this
package asserts an opinion about.

## Language server

`bigfix-relevance-lsp` (or `python -m bigfix_relevance_analyzer.lsp`) is a
language server over stdio, still with no dependencies. It publishes the
linter's findings as diagnostics on open, change and save, using the same
extractors and rules as `bigfix-relevance-lint`, but over the editor's unsaved
buffer. The file type comes from the document URI's suffix. Each diagnostic
covers the text its finding is about - the unterminated
string, the `it` with nothing to bind to, the comparison a type error is in,
each use of an unknown name - counted in UTF-16 code units, with entities,
CDATA and CRLF line endings as the buffer has them. A statement-level finding
(`complexity`, `mixed-dialect`, a substitution's type, ...) and a problem in
the file around the relevance (an unclosed fence) still cover their whole
line, as does any span that cannot be placed for certain.

It also answers hover (`textDocument/hover`) with a few lines of Markdown about
what is under the cursor, inside any statement the linter reads, BES entities
and CDATA included:

- an inspector: the table rows it resolved to here (signature, return type,
  plurality as written, and the client platforms and session contexts that
  define it), or that no table defines it;
- a literal, what an `it` is bound to and by which `of` or `whose`, and the
  construct an operator or keyword belongs to, linked to `docs/reference/`.

Whitespace, comments, articles, parentheses and a statement that does not parse
get no hover.

And it offers each safe fix as a quick fix (`textDocument/codeAction`): one
`quickfix` action per statement with a fixable diagnostic in the requested
range, and a `source.fixAll.bigfix-relevance` action that fixes the whole file,
which an editor can run on save. Nothing about whether a fix is safe is decided
in the editor layer: the buffer's bytes are planned exactly as `--fix` plans a
file (see [Writing fixes back into files](#writing-fixes-back-into-files)), and
each byte edit becomes a range, so a fix inserts only the text it adds and an
action is offered only for a fix `--fix` would write. Code actions are
advertised to a client that accepts `CodeAction` literals, and their edits
carry the document's version when the client supports `documentChanges`.

The protocol logic does no I/O, so it can also run without stdio. A host such
as a WASM runtime inside an editor extension passes each parsed JSON-RPC
message to `Server.handle()` and sends back whatever list it returns:

```python
from bigfix_relevance_analyzer.lsp import Server

server = Server()
for reply in server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}):
    ...  # hand each reply back to the client
```

On a keystroke the server re-judges only the sites that changed. Unchanged
statements keep their cached findings, moved to their current line, so typing
in a 59-site task costs about 2 ms instead of about 50 ms. "Did you mean" leads
are on, as recommended for interactive use. A document over 1 MiB (UTF-8) is
not linted. It gets one informational `document-too-large` diagnostic instead,
because one real 13 MB generated task takes about 19 s. Change the limit with
the `maxDocumentBytes` initialization option.

The protocol layer is a thin adapter. Everything the editor is told (the
diagnostics, the cache, the size guard and their options) comes from
`DocumentLinter`, which has no JSON-RPC in it: `diagnostics(uri, text)`,
`hover(uri, text, (line, character))` and `fixes(uri, text, range=...)` return
plain data in LSP's field names. Moving to a library such as pygls would mean
writing another adapter over it, not porting it.

**[BigFix Relevance Developer](https://marketplace.visualstudio.com/items?itemName=jgstew.bigfix-relevance-developer)**,
on the VS Code Marketplace, runs this server. It compiles the server, with a
CPython, into a WebAssembly component, so nothing needs installing beyond VS
Code. Its source is `tools/vscode-extension/componentize-py/`. Beside it,
`tools/vscode-extension/python-stdio/` is a proof of concept that starts
`bigfix-relevance-lsp` from a local Python instead; see
`tools/vscode-extension/README.md`.

For hover-style questions, `node_at(tree, offset)` returns the innermost node
under a character offset of the parsed statement. `nodes_at` returns the whole
chain from the root down.

## Serving this from an MCP server

This package is meant to be wrapped, and more than one server wraps it. What
follows is the part that exists so those servers do not each invent their own
answer to the same question.

**No server ships here, and there is no `mcp` dependency - not even an optional
one.** `dependencies = []` is the promise this README opens with, and the
pre-commit hooks and `besapi` must not inherit an MCP SDK to get relevance
analysis. There are no tool names, descriptions or JSON schemas here either:
two servers with different transports, auth models and resource URI schemes
need different tool shapes, and a schema baked in here would be either ignored
or in the way. What genuinely has to agree between them is the *value* schema -
the key names in a payload, and the words used to explain a finding - and that
is what is provided.

### Every result type serializes

`RelevanceAnalysis.to_dict()` was always the wire format. Now every type a
public function can hand back has one, with the same conventions: enums become
their `.value`, an unknown fact is `null` and is never omitted (`null` means *no
evidence*, which is not `false`), sets and tuples become sorted lists so a
payload is byte-stable and survives a round trip, and positions are
`line`/`column` (plus `offset` where the source carries one).

```python
from bigfix_relevance_analyzer import analyze_relevance_to_dict, lint_paths_to_dict, LintConfig

analyze_relevance_to_dict('exists files of folder "/tmp"')  # the full analysis
lint_paths_to_dict(changed_paths, LintConfig(max_score=350))
```

`Finding`, `RelevanceSite`, `ParseError`, `RelevanceComplexity`, `CheckResult`,
`Probe`, `Level`, `ProbeOutcome`, `Inspector`, `RelevanceType` and `Diagnostic`
all have `to_dict()`. `Inspector` and `RelevanceType` include the decoded
`dialects` and `platforms` so no consumer parses `"client:windows"` for itself;
`Finding` nests its `site` and carries a `text` key holding the same grep-able
line the CLIs print, and a `spans` list of `{"start", "end", "message"}`: offsets
into the site's text (or the bare statement) for the characters it is about -
empty for a finding about the statement as a whole - and, for an
`unknown-inspector` use, a `message` naming just that name with just its own
"did you mean" leads (`null` on every other rule's spans). `line` keeps its meaning; a span is
relative to the statement, so turning it into a file position is the
consumer's job (`lsp.positions` does it for an editor).

`json.dumps(payload)` works with no `default=`. There is deliberately no
`to_json()`: the encoder is the server's choice.

Three convenience wrappers only, and each earns it - `analyze_relevance_to_dict`
replaces a two-step every caller would write, `lint_paths_to_dict` returns
`{"findings", "counts", "ok"}`, where `ok` is the same pass/fail verdict both
CLIs here exit on, and `fix_paths_to_dict` returns the same envelope over the
findings left after fixing, plus `applied`, `unapplied` and `changed`. There is no `extract_to_dict`, because
`[site.to_dict() for site in sites]` has no shared decision in it.

### Findings explain themselves once

`lint.RULES` maps each code to a `LintRule` with a one-line `summary`, a
`rationale`, its `default_severity`, and whether it is `gated` behind a
threshold. `DEFAULT_SEVERITIES` is derived from it, so the two cannot disagree.

A `Finding` carries only its `code`; serve the catalog once and join on it,
rather than repeating two sentences of prose on every finding. Both CLIs can
print it with the same flag: `bigfix-relevance-analyzer --list-rules` and
`bigfix-relevance-lint --list-rules` (add `--json` or `--markdown` to either).

### Auto-fix

The analyzer works out the fully fixed statement itself, as one final result,
so a hook only has to print it (auto-fix off) or swap it in (auto-fix on):

```python
from bigfix_relevance_analyzer import autofix_relevance

result = autofix_relevance(
    'number of names of files of folder "etc" of folder "private" of folder "/"'
)
result.fixed  # 'number of names of files of folders "etc" of folders "private" of folder "/"'
result.applied  # {'singular-spelling-mid-chain': 2}
result.rounds  # 2
result.unapplied  # {} - fixable diagnostics still standing in `fixed`
```

Two kinds of diagnostic carry a fix today. The checker attaches a `TypeFix`
to each, and the fix layer applies it only when the text in its range really
is what the checker read, case-insensitively and whitespace-normalized.

- `singular-spelling-mid-chain` (`plural-preferred`): the written property
  name becomes its plural spelling (`of  Setting  "x"` becomes
  `of  settings  "x"`). `filtered-singular-spelling` stays unfixable: it fires
  in singular contexts, where the plural would only trade it for a
  `non-unique-risk`.
- `left-operand-not-singular`, `right-operand-not-singular` and
  `argument-not-singular` (`singular-required`): a plural operand where the
  engine requires a singular, which it refuses before evaluating anything. A
  plural aggregate is respelled as its singular
  (`(concatenations ", " of X) | "y"` becomes `(concatenation ", " of X) | "y"`);
  anything else is wrapped whole, parenthesized where needed
  (`pathnames of files "x" | "y"` becomes
  `unique value of pathnames of files "x" | "y"`). A tuple is left alone,
  since the engine defines `unique value of` on none. ActionScript `{...}`
  substitutions are never touched: they join a plural rather than refusing it.

Fixes cascade - pluralizing `folder "etc"` above makes `folder "private"`
fire next - so they are applied in rounds, until nothing more is accepted, the
text stops changing or repeats, or `max_rounds` (16) is reached. Every
candidate is held against the *original* statement: no parse or lex error,
unknown name or checker diagnostic may become more common (with
`guard="errors"`, only the ones whose lint rule defaults to an error count),
and the resolved dialect and the result's types and plurality must not change.
The one exception is a candidate with fewer `singular-required` diagnostics
than the original: its plurality may change, and its types may narrow or gain
`<type> with multiplicity`, the engine's own type for `unique value of`.
A round that fails is retried one edit at a time, keeping the edits that pass.
The result must then also pass a full check that counts fix-carrying
diagnostics and refuses any the edits introduced, so a round limit reached
mid-cascade falls back to the last state that fully passes - often the
original - rather than reporting half a fix.

The same result is on `RelevanceAnalysis.autofix()`, under `"autofix"` in
`to_dict()` (`null` when nothing fixes), and on every fixable lint `Finding`
as `Finding.autofix` - the site's whole result, not the finding's own edit,
because only a rewrite worked out over every fix at once is safe to swap in.
`AutofixResult.to_dict()` names each code's lint rule, and so does each edit
(`TextEdit.rule`):

```json
{"original": "...", "fixed": "...", "changed": true, "rounds": 2,
 "applied": [{"code": "singular-spelling-mid-chain", "rule": "plural-preferred", "count": 2}],
 "unapplied": [],
 "edits": [{"start": 28, "end": 34, "replacement": "folders", "code": "singular-spelling-mid-chain", "rule": "plural-preferred"},
           {"start": 44, "end": 50, "replacement": "folders", "code": "singular-spelling-mid-chain", "rule": "plural-preferred"}]}
```

### Writing fixes back into files

`fix_file()` / `fix_paths()` apply those fixes to the files themselves, and keep
every other byte of each file exactly as written:

```python
from bigfix_relevance_analyzer import LintConfig, fix_paths

result = fix_paths(["Fixlet.bes"], LintConfig())
result.changed  # (PosixPath('Fixlet.bes'),) - files rewritten
result.applied  # one FileFix per site fixed: path, line, site, autofix
result.unapplied  # the same, each with a `reason` it was not applied
result.findings  # lint findings for the files as they now are
```

Every file type the linter reads is fixed this way: BES XML (`.bes`,
`.bes.xml`), whole-file relevance (`.rel`, `.bsr`), markdown fences, and the
HTML family's `<?Relevance ?>` and `Relevance()` calls (`.ojo`, `.besrpt`,
`.beswrpt`, `.html`, ...).

A site's text is decoded and stripped, so it cannot be searched for in its
file. Instead `AutofixResult.edits` gives every edit measured against the
original statement (composed across rounds, so applying them to `original`
gives `fixed`), and each edit is split into the smallest pieces that make it:
a wrap is an insertion of `unique value of ` (and `(`, `)`), a respelling an
insertion of `s` or a one-letter change like `y` -> `ies`. Each piece is
placed at the exact bytes it belongs at - through `RelevanceSite.source_map`
for BES XML, through the site's line and `column` for every other type - and
only writes new text, never a copy of the statement. So `&lt;` stays `&lt;`,
`&quot;` stays `&quot;`, a CDATA section stays CDATA (even one that splits
the statement, as in `sett<![CDATA[ing]]>`), `\"` in a JavaScript string
stays `\"`, and CRLF, CR-only, mixed line endings and a byte order mark stay
as they were. What guards a write:

1. the analyzer's own guard above decided the fix is safe, and no rule it
   applies under is `IGNORE` in the `LintConfig`;
2. every piece writes only names, spaces and parentheses (`[A-Za-z0-9 ()]`),
   which need no escaping anywhere relevance is written, and maps to bytes
   that read back as the text it expects - never part of an entity, never
   across markup, never next to bytes that are not UTF-8;
3. the edited bytes are extracted again *before* anything is written, and
   every site must read back as expected - the fixed text where a fix went,
   the original everywhere else - or nothing in that file is written
   ("re-extract mismatch");
4. the fixed file is linted again with the same `LintConfig`, and no rule may
   report more findings than before ("the fix would add a complexity
   finding"): adding `unique value of` raises a statement's score, and a fix
   must not trade a warning for an error over `max_score`. Only the fix whose
   own statement gained the finding is refused; the others in the file still
   go in;
5. the file must still hold what was planned from when it is written, and is
   read back after writing and restored if it does not hold what was written.

Planning and writing are separate steps, so a caller can check a fix before it
is written - against BES.xsd, say:

```python
from bigfix_relevance_analyzer import LintConfig, plan_fix, write_fix

plan = plan_fix("Fixlet.bes", LintConfig())  # reads the file, writes nothing
plan.changed  # whether any fix applies
plan.original, plan.fixed  # the bytes before and after
plan.findings  # lint findings for `fixed`; `original_findings` for `original`
if plan.changed and my_check(plan.original, plan.fixed):
    result = write_fix(plan)  # a FileFixResult, as fix_file() returns
```

`fix_file()` is `write_fix(plan_fix(...))`. `write_fix()` refuses a file that
changed after it was planned ("file changed since it was planned"), reporting
its fixes and findings as the file now is.

`str` documents and lxml trees have no bytes, so a fix in one cannot be
written back. `source_map` and `column` are left out of a site's equality,
hash and `to_dict()`, so existing outputs do not change. The lower-level
pieces are public too, in `fixfile`: `site_fixes()` (one fix per site, from
findings) and `source_edits(site, autofix, data)` (one fix's pieces as
`ByteEdit`s on the file's bytes `data`, or `Unmapped` with the reason; BES
sites need no `data`). `AutofixResult.applied_rules` tallies the applied codes
by lint rule, so a consumer disabling rules by name need not parse
`to_dict()`.

### Finding an inspector you cannot name

`lookup()` is exact-match: it answers "how do I use `files`". `inspectors.search()`
answers the question a consumer actually arrives with - "what is this called" -
and returns names `lookup()` can then resolve.

```python
from bigfix_relevance_analyzer import inspectors

inspectors.search("registry keys")  # -> keys of <registry key>, via MatchKind.SIGNATURE
inspectors.search("operating system")  # -> operating system, via MatchKind.FUZZY
inspectors.suggest("registry")  # -> ('registry', 'registries', 'x32 registry')
```

Six match tiers, strongest first - `EXACT`, `PREFIX`, `WORDS`, `SIGNATURE`,
`SUBSTRING`, `FUZZY` - and the tier is on every result as `SearchResult.match`.
That is the useful answer rather than a score: `EXACT` means don't say "did you
mean", `FUZZY` means say it out loud, and `SIGNATURE` means "nothing is called
that, but this expression reads it". A float could not express any of those, and
exposing `difflib`'s ratio would make its internals part of this package's API.

Three things worth knowing:

- **`SIGNATURE` is why phrases work.** `registry keys` is nobody's name;
  `keys of <registry key>` is the answer, and only the signature contains both
  words. Without that tier the query gets a fuzzy guess (`difflib` alone answers
  `retry delays`).
- **`search()` knows the engine's spoken operator names, `lookup()` does not.**
  `lookup("mod")` is empty - `mod` lives in `Inspector.written_name`, not in
  `written_forms()` - while `search("mod")` finds the `%` rows with
  `name="%"`, `matched="mod"`. Every result's `name` is one `lookup()` resolves;
  `matched` is what actually hit.
- **`fuzzy=False`** skips the `difflib` pass. Precise tiers are sub-millisecond
  and the fuzzy pass can reach tens, so a caller doing completion rather than
  correction should turn it off - and then every result is a name that exists.

There is no `platform` filter, deliberately, though `dialect` and `kind` are
both there. Absence from the snapshot is never evidence, so filtering on
platform would drop candidates on the strength of a gap in the dumps - and in a
"did you mean", the way to fail is to hide the right answer. `dialect` is
different in kind: the dumps cover both sides, so proposing `bes computers` for
client relevance is positively wrong rather than merely unobserved.

**`SearchResult.to_dict()` never embeds the rows.** `lookup("name")` is 96
overloads and about 43 KB of JSON for one name, so a 25-result search that
inlined them would cost a six-figure token count to answer "did you mean".
Instead it emits identifiers plus at most five signatures, with `overloads`
carrying the true count and `signatures_omitted` accounting for the rest - about
6 KB worst case. **Search hands you an identifier; `lookup` hands you the row.**

Turn `unknown-inspector` warnings into leads with `LintConfig(suggest=True)`:
the message gains `-- did you mean \`registry\`?` and `Finding.suggestions`
carries the same names as structure, so a server is not parsing prose. Off by
default, because unknown names are common in a repo running newer inspectors
than the snapshot - that is the rule's whole rationale - and a few thousand
sites would add real latency to a hook for a warning that blocks nothing.

The loop a model runs: `analyze_relevance_to_dict` -> read `unknown_references`
and `types.diagnostics` -> `suggest()` for a typo or `search()` for a concept ->
`lookup()` on the candidate to see its `operands` and `return_type` -> re-analyze.
The split matters: a model with only `search` re-guesses operand types, and one
with only `lookup` cannot recover from a typo.

Search belongs on a **tool**, not a resource: a resource is addressable by a
stable URI with no arguments, and a free-text query served as one is a tool in a
resource costume whose result is neither listable nor cacheable. `lookup`
legitimately could be a resource template (`inspector://<name>`) - stable,
cacheable, no ranking - but nothing in the library needs to change for a server
to do that. From the command line:

```bash
python -m bigfix_relevance_analyzer --search "registry keys"
```

### Language reference resources

`bigfix_relevance_analyzer.reference` serves four Markdown documents a server
can register as MCP resources: `dialects` (client versus session - serve this
first), `universal-relevance` (what the evaluator does either way), then
`client-relevance` and `session-relevance`.

The two shared documents come first because both are prerequisites for the
dialect references. `universal-relevance` is its own document rather than more
shared syntax prose for two reasons: the dialect references fold the syntax
prose in wholesale, so anything added there is paid for twice and competes with
the generated tables for a context budget, and the material is a different kind
of claim - `syntax` says what parses, `universal-relevance` says what the
evaluator then does with it, confirmed against a live client engine and a live
session engine.

```python
from bigfix_relevance_analyzer import reference

for document in reference.documents():
    register(document.slug, document.title, document.summary, document.read)

reference.client_relevance_reference()  # ~6k tokens
reference.session_relevance_reference(detail=reference.Detail.BRIEF)  # prose only
```

Each is a hybrid, which is the point: the prose is authored (in
`docs/reference/*.md`, embedded into a module by
`tools/generate_reference_prose.py` because the wheel packages `src/` only),
while the tables are generated **at call time** from `grammar.py`,
`inspectors.py`, `COST_RULES` and `DIAGNOSTICS`. So the operator/precedence
table, the type sketch, the per-dialect cost table and the type-checker
vocabulary cannot drift from the snapshot the analyzer itself uses - and there
is no second thing to guard.

`documents()` returns `ReferenceDocument`s carrying `title` and `summary`
because an MCP `list_resources` needs a name and a description for each
resource; a bare `-> str` would make every server invent those. There is no
`uri` field - that namespace is the server's, and `slug` is enough to build one
from.

`Detail.STANDARD` is around 6k tokens, `Detail.BRIEF` around 2.5k, and a test
pins a character ceiling so a generated section cannot grow into a manual. The
full inspector table is not served: 6,000 rows is a search index, not a
reference, so `search()` and `lookup()` are how a consumer answers a question
about one name - see "Finding an inspector you cannot name" above.

Importing the package does **not** import `reference`, and importing
`reference` does not build any document - the prose and table modules are
imported inside function bodies and every renderer is cached. A stdio server
that never serves a document pays nothing, which is checked by a test that runs
in a subprocess.

Try them from the command line:

```bash
python -m bigfix_relevance_analyzer --reference session
```

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

`analyze_relevance` runs this for you and returns the levels; the pieces are
here for a caller that wants them directly.

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
itself produces, as `str.format` templates. `typecheck` emits every type-check
entry in it - a test fails on any that becomes unreachable - so the checker's
output is wording BigFix authors already recognize rather than a second
vocabulary to learn. Imported explicitly, like `inspectors`.

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
like `inspectors`. Every construct is typed: literals, casts, operators,
aggregation, tuples and conditionals, and the `of` chains, `whose` filters and
`it` references that need property resolution.

`of` and `whose` introduce the context `it` refers to, and the object comes
first - in `A of B`, `B` is typed in the enclosing context and only then becomes
the context `A` is typed in. `binding.py` states the same rule for the same
reason, and a test holds the two together. A context does not hide the world: a
global name written inside one still resolves against the world when the context
defines nothing by that name, which is why
`packages ... whose (exists properties whose (...))` types clean.

One mistake produces one finding. A ruled-out value silences the checks it feeds
rather than cascading `<none> as trimmed string` and `<none> != <string>` behind
the property that actually went wrong.

`analyze_relevance` calls this with an environment built from the dialect and
platform it was given; reach for the module directly to control the environment
yourself.

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
