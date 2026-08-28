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
| `session_relevance_properties_rest_api.txt` | 1756 | The REST API, enriched (see below) |

The two console/Web Reports session dumps are byte-identical: the console and Web Reports expose the
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

Client-side, captured on Windows and macOS:

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

And now on Ubuntu, Debian, and the RHEL family, via
`bigfix_remote_client_relevance` against Docker containers (see Provenance
below) - closing the platform-breadth gap the previous paragraph used to
describe:

| File | Signatures | Query | Covers |
| --- | --- | --- | --- |
| `client_relevance_casts_ubuntu.txt` | 225 | `(it as string) of casts` | Ubuntu 24.04, 22.04, 20.04 |
| `client_relevance_binary_operators_ubuntu.txt` | 371 | `(it as string) of binary operators` | Ubuntu 24.04, 22.04, 20.04 |
| `client_relevance_unary_operators_ubuntu.txt` | 6 | `(it as string) of unary operators` | Ubuntu 24.04, 22.04, 20.04 |
| `client_relevance_types_ubuntu.txt` | 238 | `(it as string) of types` | Ubuntu 24.04, 22.04, 20.04 |
| `client_relevance_casts_debian.txt` | 225 | `(it as string) of casts` | Debian latest, Debian 11 |
| `client_relevance_binary_operators_debian.txt` | 371 | `(it as string) of binary operators` | Debian latest, Debian 11 |
| `client_relevance_unary_operators_debian.txt` | 6 | `(it as string) of unary operators` | Debian latest, Debian 11 |
| `client_relevance_types_debian.txt` | 238 | `(it as string) of types` | Debian latest, Debian 11 |
| `client_relevance_casts_rhel.txt` | 224 | `(it as string) of casts` | AlmaLinux 9, Rocky Linux 9, Oracle Linux 9, Amazon Linux 2023 |
| `client_relevance_binary_operators_rhel.txt` | 374 | `(it as string) of binary operators` | AlmaLinux 9, Rocky Linux 9, Oracle Linux 9, Amazon Linux 2023 |
| `client_relevance_unary_operators_rhel.txt` | 6 | `(it as string) of unary operators` | AlmaLinux 9, Rocky Linux 9, Oracle Linux 9, Amazon Linux 2023 |
| `client_relevance_types_rhel.txt` | 236 | `(it as string) of types` | AlmaLinux 9, Rocky Linux 9, Oracle Linux 9, Amazon Linux 2023 |

Ubuntu and Debian are byte-identical to each other across all four of these
categories (unlike `properties`, where they differ - see the platform-specific
surface table below); every distro within the RHEL family agrees with the
other three, same as it does for `properties`.

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
`dialects={client, session}`: every client platform sampled here genuinely
defines the same introspection meta-layer the session engine does. All five
platforms now have all five categories captured, so the earlier "platform
breadth, not dialect" gap for Ubuntu/Debian/RHEL is closed; the remaining gaps
are the ones in "Still not exhaustive" below (AIX/Solaris/HP-UX, other session
contexts, one client version per platform). `tools/generate_inspector_data.py`
(see "Filenames are the provenance" below) picks up a new dump with no code
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

### Enriched columns

`session_relevance_properties_rest_api.txt`, and the `casts`/`binary_operators`/
`unary_operators`/`types` REST API dumps, carry extra tab-separated columns
after the legacy text, queried from BigFix's own introspection of the
`property`, `binary operator`, `unary operator`, and `type` types (see
`developer.bigfix.com/relevance/reference/property.html`). Column 1 is always
the legacy `signature: type` text verbatim, so these files are a strict
superset of the bare format:

- `properties`: `signature: type`, singular name, plural name, usual name,
  `1`/`0` for multivalued, result type, direct object type (empty if none),
  index type (empty if none).
- `casts`: `signature: type`, name, operand type, result type.
- `binary_operators`: `signature: type`, name, symbol, left operand type,
  right operand type, result type.
- `unary_operators`: `signature: type`, name, symbol, operand type, result
  type.
- `types`: name, parent type (empty for a root type), size in bytes (empty
  if unknown) - no `signature: type` column, since a type's own `as string`
  form is just its name.

A dump without these columns (every client dump today) leaves the
corresponding `Inspector`/`RelevanceType` fields as `None`; the generator
merges rows across dumps by their pre-tab text, so a bare client line and an
enriched session line for the same inspector become one row, not two.

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
needs root to read the client's local action site.

The Ubuntu, Debian and RHEL-family `casts`/`binary_operators`/
`unary_operators`/`types` files, plus a fresh `properties` capture per
platform used only to cross-check the committed dumps (see the note below),
were captured with
[`jgstew/bigfix_remote_client_relevance`](https://github.com/jgstew/bigfix_remote_client_relevance)
against qna 11.0.6.137, provisioned on-the-fly into Docker containers - no
BigFix install, SSH, or hand-run `QnA` needed:

```bash
bigfix-remote-client-relevance --container ubuntu:22.04 --qna-version 11.0 "(it as string) of casts"
bigfix-remote-client-relevance --container debian:11 --qna-version 11.0 "(it as string) of casts"
```

repeated for `binary operators`, `unary operators` and `types`. The RHEL
family needed the target's platform forced explicitly - the tool's
`uname`/`os-release` probe otherwise guesses `ubuntu` (the deb family is the
more common default) rather than detecting the rpm family from the container's
`ID`/`ID_LIKE` - via an inventory file:

```toml
[defaults]
transport = "container"
platform = "rhel"
qna_version = "11.0"

[hosts.almalinux9]
image = "almalinux:9"
```

```bash
bigfix-remote-client-relevance --inventory hosts.toml "(it as string) of casts"
```

Rocky Linux 9 and Amazon Linux 2023's base images additionally needed `cpio`
(to unpack the rpm) and `dbus-libs` (a `qna` runtime dependency the minimal
images don't ship) installed before qna would run; AlmaLinux 9 and Oracle
Linux 9 worked from their unmodified base images. All four RHEL-family images
produced byte-identical output once qna could run, matching the precedent
`client_relevance_properties_rhel.txt` already set.

Re-running `properties` the same way against qna 11.0.6.137 (newer than the
version that produced the committed `client_relevance_properties_*.txt`
files) reproduced each committed dump as a strict subset - a handful of new
`yaml`-inspector lines on top, nothing removed or changed - so those files
were left as-is rather than churned for a version bump alone; see "One client
version per platform" under "Still not exhaustive".

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
