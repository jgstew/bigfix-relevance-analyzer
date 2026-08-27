# Relevance inspectors

Raw dumps of the inspectors (built-in properties/operators) that BigFix
relevance exposes, one per line, in several evaluation contexts. This is
reference data for the analyzer's inspector/operator tables, not parsed by any
test yet - `corpus_files()` in `tests/test_examples.py` deliberately skips this
directory, since these are inspector-name dumps rather than documents with
embedded relevance to extract. See the parent
[`tests/examples/README.md`](../README.md) for the client relevance vs. session
relevance distinction these files are organized around.

## Files: properties

The `properties` inspector category, captured per platform/context (see
"Introspection meta-layer" below for the other categories - casts, operators,
types).

Client relevance, one file per *distinct* dump. Every platform in a "covers"
row produced byte-identical output, same order, so they are not stored
separately:

| File | Signatures | Covers |
| --- | --- | --- |
| `client_relevance_properties_windows.txt` | 2883 | `windows-latest`, `windows-2025` |
| `client_relevance_properties_macos.txt` | 2345 | `macos-latest` (macOS 26, arm64) |
| `client_relevance_properties_ubuntu.txt` | 2124 | Ubuntu latest, 24.04, 22.04, 20.04 |
| `client_relevance_properties_rhel.txt` | 2088 | AlmaLinux, Amazon Linux 2023, Oracle Linux 9, Rocky Linux 9 |
| `client_relevance_properties_debian.txt` | 2073 | Debian latest, Debian 11 |

Session relevance:

| File | Signatures | Context |
| --- | --- | --- |
| `session_relevance_properties_web_reports.txt` | 1644 | A **Web Reports** session |
| `session_relevance_properties_console.txt` | 1644 | A **console** session |

The two session dumps are byte-identical: the console and Web Reports expose the
same inspector surface, so "session relevance" below means either.

Counts are lines; the three Linux files each contain 3 duplicate lines
(`device file <symlink>`, `fifo file <symlink>`, `socket file <symlink>`), kept
because these are verbatim captures. Deduplicated they are 2121 / 2085 / 2070.

## Introspection meta-layer: casts, operators, types

`properties` is one of several introspection categories BigFix exposes over
itself; `casts`, `binary operators`, `unary operators` and `types` are the
others, and none of the files above capture them. That is why things like
`as trimmed string`, `as lowercase`, `contains`, `starts with` and `-` (unary
minus) read as unrecognized words against the `properties`-only vocabulary --
they are casts and operators, not properties, and were never in scope for
those dumps.

Session-side, all from the REST API via `bigfix_query_session_relevance` (see
Provenance below):

| File | Signatures | Query |
| --- | --- | --- |
| `session_relevance_casts_rest_api.txt` | 171 | `(it as string) of casts` |
| `session_relevance_binary_operators_rest_api.txt` | 442 | `(it as string) of binary operators` |
| `session_relevance_unary_operators_rest_api.txt` | 7 | `(it as string) of unary operators` |
| `session_relevance_types_rest_api.txt` | 166 | `(it as string) of types` |

Client-side, captured on Windows and now macOS:

| File | Signatures | Query |
| --- | --- | --- |
| `client_relevance_casts_windows.txt` | 230 | `(it as string) of casts` |
| `client_relevance_binary_operators_windows.txt` | 374 | `(it as string) of binary operators` |
| `client_relevance_unary_operators_windows.txt` | 6 | `(it as string) of unary operators` |
| `client_relevance_types_windows.txt` | 309 | `(it as string) of types` |
| `client_relevance_casts_macos.txt` | 188 | `(it as string) of casts` |
| `client_relevance_binary_operators_macos.txt` | 345 | `(it as string) of binary operators` |
| `client_relevance_unary_operators_macos.txt` | 7 | `(it as string) of unary operators` |
| `client_relevance_types_macos.txt` | 244 | `(it as string) of types` |

Casts and operators are in the same `signature: type` format as the property
dumps. `types` is not: a type's `as string` form is just its own name, so that
file is a flat list of type names, one per line, no `: type` suffix -- and the
REST API capture's first line is a genuine empty string, part of the capture
rather than a formatting accident (this project has no theory for which type
that is; see it as unresolved rather than guess). The macOS `types` dump has
the same leading empty line, captured directly via `sudo QnA` on the BES
Agent -- not just a REST API/Windows quirk.

**Trap 2 is now an evidence-backed finding, not an assumption.** Every one of
these five categories -- `properties`, `casts`, `binary operators`, `unary
operators`, `types` -- has at least one client dump and one session dump, and
`bigfix_relevance_analyzer.inspectors` resolves every one of them to
`dialects={client, session}`: the Windows and macOS clients genuinely define
the same introspection meta-layer the session engine does. The remaining gap
is platform breadth, not dialect: **Ubuntu, Debian and RHEL have no
casts/operators/types dumps yet** -- only `properties` was captured on all
five platforms. Someone with Fixlet Debugger, `sudo QnA` (macOS/Linux), or
console client-relevance access to those platforms can capture them the same
way the original `client_relevance_properties_*.txt` files were made -- run
the four queries above per platform. `tools/generate_inspector_data.py` (see
"Filenames are the provenance" below) picks up a new dump with no code
change.

## Filenames are the provenance

Every dump's name is `{dialect}_relevance_{category}[_{context}].txt`:

- `dialect` is `client` or `session`.
- `category` is one of the five introspection categories above --
  `properties`, `casts`, `binary_operators`, `unary_operators`, `types`.
- `context` names the platform or session surface (`windows`, `console`,
  `rest_api`, ...). Omit it when only one capture exists for that dialect and
  category -- that is why the four REST API files above carry a context
  segment but nothing forces every file to.

`tools/generate_inspector_data.py` parses this to build
`bigfix_relevance_analyzer._inspector_data`, and its tests
(`tests/test_inspector_data.py`) fail on a filename that does not parse. Adding
a dump is exactly: name it correctly, drop it in this folder, run
`python tools/generate_inspector_data.py`, commit both.

## What `properties` shares between the two dialects

Computed from the `properties` files in this folder -- the only category
captured across all five client platforms, so it is the one with cross-platform
counts worth stating. See "Trap 2" above for what the other four categories
show instead (both dialects, Windows-only breadth so far).

| Set | Count |
| --- | --- |
| Client union (all five platforms) | 3701 |
| Cross-platform client core (present on all five) | 1715 |
| Session (Web Reports) | 1644 |
| Shared between client union and session | 828 |
| Client-only | 2873 |
| Session-only | 816 |
| Distinct signatures overall | 4517 |

Client relevance and session relevance are genuinely different dialects (see
the parent README) - only 828 of 4517 signatures are valid in both. Do not
assume an inspector present in one file is valid in the other.

### Platform-specific surface

Signatures unique to one platform, measured against the union of the other
four:

| Platform | Unique | Character of the unique set |
| --- | --- | --- |
| windows | 949 | registry, WMI, COM, Active Directory, security accounts |
| macos | 448 | `osxvalue`/`dictionary`/`array` plists, `applications`, macOS folder domains, **and the statistics/projection layer** (see the warning below) |
| rhel | 65 | `rpm`, `package`, `capability`, `rpm package version record`, `runlevels of <service>` |
| ubuntu | 0 | - |
| debian | 0 | - |

Ubuntu and Debian contribute no signatures of their own, but they are not
identical to each other: Ubuntu has 51 that Debian lacks (`cidr subnet`, perl
regexes, `display name of <operating system>`). Both are subsets of the
union, so neither is redundant as a *platform* record.

> [!WARNING]
> **macOS defines inspectors that look like Web Reports statistics.** The
> macOS client is the only client here that exposes `rate`,
> `linear projection` and `exponential projection` - 11 signatures such as
> `rate of <linear projection>`, `correlation coefficient of <linear
> projection>` and `extrapolation <time> of <exponential projection>`.
> Against the Windows dump alone those look session-only. They are not, and
> using any of them as a session marker is a false positive on macOS. This is
> why session-only is 816 here and not the 827 a Windows-only comparison
> gives. See `classify_relevance_dialect` in
> `src/bigfix_relevance_analyzer/dialect.py`.

Of the 816 session-only signatures, 753 (92%) mention a `bes *` server object.
The remaining 63 are Web Reports statistics types (`statistical bin`,
`statistic range`, `historical computer count`, `fixlet count pair`) and
context probes (`in console context`, `in web reports context`,
`webui enabled`, `pending license update`, `datastore inspector`,
`shared variable`, `private variable`, `mime field`).

## Still not exhaustive

- **No session relevance from other contexts.** The console and Web Reports are
  captured and agree exactly, but the Fixlet Debugger's QnA view, the WebUI, and
  the REST API may each expose a different set. This is the largest remaining
  gap, and it is on the side that dialect detection depends on: it is why the
  classifier's client marker list is short and conservative.
- **No AIX, Solaris, or HP-UX.** The Unix inspectors those add are unknown
  here, and by the macOS precedent above, an unsampled platform can move a
  signature out of the session-only set.
- **One client version per platform.** Inspector availability changes between
  BigFix client releases; each file is a single point in time.
- Every file reflects one deployment/runner, not the union of everything the
  dialect can do.

## Format

One inspector per line:

```
<property signature>: <return type>
```

- `<property signature>` is the inspector as you would write it in relevance,
  with placeholders in angle brackets for its argument/direct-object types,
  e.g. `key <string> of <registry>` (a real line from the Windows dump; the
  index argument is not always a `<string>` - see `current user key <logged on
  user> of <registry>`). A bare placeholder type like `<string>` or `<html>` is
  itself the name of a first-class relevance type, not markup for "any string".
- `<return type>` is the name of the type the inspector evaluates to, e.g.
  `boolean`, `string`, `registry key`. This is BigFix's own string
  representation of a property (`(it as string) of properties` produces this
  exact `signature: type` text - see Regenerating below), not a paraphrase
  assembled by this project.
- Lines are in the order the introspection returned them (grouping is by
  internal definition, not alphabetical - note line 2 sorts before line 1 in
  every file).
- No header, footer, or blank lines; every line in every file is a
  `signature: type` entry with no exceptions.

## Provenance

The five client files come from the `run_qna` workflow in
[`jgstew/tools`](https://github.com/jgstew/tools), which runs QnA across a
matrix of runners and containers -
[run 33090097829](https://github.com/jgstew/tools/actions/runs/33090097829).

Take the text from the **raw job logs**, not the workflow's step summary: the
summary renders as Markdown, which mangles the `<string>` / `<html>`
placeholders. The `A: ` answer lines in the logs carry the exact text (the
container jobs prefix them `Q: A: `):

```bash
gh run view --repo jgstew/tools --job <JOB_ID> --log | sed -E 's/^[^\t]*\t[^\t]*\t//' | sed -E 's/^[0-9-]{10}T[0-9:.]+Z //; s/^Q: //' | grep '^A: ' | sed 's/^A: //'
```

`client_relevance_properties_windows.txt` predates this and was captured by hand; the
extraction above reproduces it byte-for-byte from the `windows-latest` job,
which is how the pipeline was validated.

The four `*_rest_api.txt` session meta-layer files (`session_relevance_casts_rest_api.txt`,
`session_relevance_binary_operators_rest_api.txt`,
`session_relevance_unary_operators_rest_api.txt`,
`session_relevance_types_rest_api.txt`) were captured directly through the
BigFix SaaS MCP server's `bigfix_query_session_relevance` tool against a live
session, one query per file: `(it as string) of casts`, and the same shape for
`binary operators`, `unary operators` and `types`. The query is identical
across all four; only `types`' result differs in shape, since a type's
`as string` form is its own name rather than a `signature: return-type` pair.

The four `*_windows.txt` client meta-layer files
(`client_relevance_casts_windows.txt`,
`client_relevance_binary_operators_windows.txt`,
`client_relevance_unary_operators_windows.txt`,
`client_relevance_types_windows.txt`) were captured the same way as
`client_relevance_properties_windows.txt` above.

The four `*_macos.txt` client meta-layer files
(`client_relevance_casts_macos.txt`,
`client_relevance_binary_operators_macos.txt`,
`client_relevance_unary_operators_macos.txt`,
`client_relevance_types_macos.txt`) were captured directly on a macOS BES
Agent via the `QnA` binary, one query per file, e.g.:

```bash
echo '(it as string) of casts' | sudo /Library/BESAgent/BESAgent.app/Contents/MacOS/QnA | grep '^A: ' | sed 's/^A: //' > client_relevance_casts_macos.txt
```

with the same substitution as the REST API queries above for `binary
operators`, `unary operators` and `types`. `sudo` is required because `QnA`
needs root to read the client's local action site. See "Introspection
meta-layer" above for the remaining platform gap (Ubuntu, Debian, RHEL).

## Regenerating

From a BES Client (per platform, for the `client_relevance_*.txt` files) or a
Web Reports/console session (for `session_relevance_properties_web_reports.txt`),
evaluate `properties` - e.g. via the Fixlet Debugger's QnA view, a REST API
session relevance query, or the BigFix SaaS MCP server's
`bigfix_query_session_relevance` tool:

```
properties
```

Casting each result `as string` already produces exactly this folder's
`<signature>: <return type>` format - a property's string representation is
its signature and result type, pre-joined by BigFix itself:

```
(it as string) of properties
```

verified against a live session, e.g. filtered to one property:

```
(it as string) of properties whose (usual name of it as string = "properties")
-> "properties: property"
```

To pull several derived fields per property at once instead of one query per
field, evaluate a tuple:

```
(usual names of it, singular names of it, plural names of it) of properties
```

`properties`, `usual name of <property>`, `singular name of <property>`, and
`plural name of <property>` are themselves entries in every file here - the
introspection is self-hosting. Availability and exact wording of
meta-inspectors like these can vary by BigFix version - if a recipe here
fails, consult `bigfix_get_session_relevance_reference` or the console's
built-in relevance help for the equivalent on your version.

## Further reading

Authoritative but not exhaustive - useful for looking up an inspector's full
signature, argument types, and prose description beyond what these plain-text
dumps capture:

- [BigFix Relevance Language documentation](https://developer.bigfix.com/relevance/) -
  guide-level docs: syntax, types, operators, control flow.
- [BigFix Relevance Language reference](https://developer.bigfix.com/relevance/reference/) -
  searchable inspector/operator reference, the closest official equivalent to
  what's captured in this folder's `.txt` files.
- `bigfix_get_session_relevance_reference` - a session relevance syntax
  reference with live-verified recipes, exposed by the BigFix SaaS MCP
  server (not part of this repo).
