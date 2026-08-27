# Relevance properties / inspectors

Raw dumps of the inspectors (built-in properties/operators) that BigFix
relevance exposes, one per line, in several evaluation contexts. This is
reference data for the analyzer's inspector/operator tables, not parsed by any
test yet - `corpus_files()` in `tests/test_examples.py` deliberately skips this
directory, since these are inspector-name dumps rather than documents with
embedded relevance to extract. See the parent
[`tests/examples/README.md`](../README.md) for the client relevance vs. session
relevance distinction these files are organized around.

## Files

Client relevance, one file per *distinct* dump. Every platform in a "covers"
row produced byte-identical output, same order, so they are not stored
separately:

| File | Signatures | Covers |
| --- | --- | --- |
| `client_relevance_windows.txt` | 2883 | `windows-latest`, `windows-2025` |
| `client_relevance_macos.txt` | 2345 | `macos-latest` (macOS 26, arm64) |
| `client_relevance_ubuntu.txt` | 2124 | Ubuntu latest, 24.04, 22.04, 20.04 |
| `client_relevance_rhel.txt` | 2088 | AlmaLinux, Amazon Linux 2023, Oracle Linux 9, Rocky Linux 9 |
| `client_relevance_debian.txt` | 2073 | Debian latest, Debian 11 |

Session relevance:

| File | Signatures | Context |
| --- | --- | --- |
| `session_relevance_web_reports.txt` | 1644 | A **Web Reports** session |

Counts are lines; the three Linux files each contain 3 duplicate lines
(`device file <symlink>`, `fifo file <symlink>`, `socket file <symlink>`), kept
because these are verbatim captures. Deduplicated they are 2121 / 2085 / 2070.

## What the two dialects share

Computed from the files in this folder:

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

- **No session relevance from other contexts.** Only Web Reports is captured.
  A console session, the Fixlet Debugger's QnA view, the WebUI, or the REST
  API may each expose a different set. This is the largest remaining gap, and
  it is on the side that dialect detection depends on.
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
  e.g. `registry values <string> of <registry key>`. A bare placeholder type
  like `<string>` or `<html>` is itself the name of a first-class relevance
  type, not markup for "any string".
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

`client_relevance_windows.txt` predates this and was captured by hand; the
extraction above reproduces it byte-for-byte from the `windows-latest` job,
which is how the pipeline was validated.

## Regenerating

From a BES Client (per platform, for the `client_relevance_*.txt` files) or a
Web Reports/console session (for `session_relevance_web_reports.txt`),
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
