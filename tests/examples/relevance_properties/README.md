# Relevance properties / inspectors

Raw dumps of the inspectors (built-in properties/operators) that BigFix
relevance exposes, one per line, in two different evaluation contexts. This is
reference data for the analyzer's inspector/operator tables, not parsed by any
test yet - there is no `tests/test_*.py` that reads these files. See the
parent [`tests/examples/README.md`](../README.md) for the client relevance vs.
session relevance distinction these files are organized around.

## Files

| File | Context | Lines |
| --- | --- | --- |
| `client_relevance_windows.txt` | Client relevance, as seen by the BES Client on a **Windows** endpoint | 2883 |
| `session_relevance_web_reports.txt` | Session relevance, as seen by a **Web Reports** session | 1644 |

Both were produced by introspection - running the `properties` inspector (and
its variants: `properties <string>`, `properties of <type>`,
`properties returning <type>`, etc.) in each context and recording every
inspector it returned, one line per inspector.

**This is not exhaustive:**

- `client_relevance_windows.txt` excludes Linux-only and Unix-only inspectors
  (it was captured on Windows), but it is not Windows-*only* content - most of
  its ~2883 entries are cross-platform inspectors (string/integer/time/regex/
  etc.) that also exist on Linux and Mac; only a subset (registry, WMI,
  security accounts, Windows services, ...) are Windows-specific.
- `session_relevance_web_reports.txt` reflects what one Web Reports session
  exposed; a console session, the Fixlet Debugger's QnA view, or a different
  server version could expose a slightly different set (e.g. REST API-only
  inspectors).
- Client relevance and session relevance are genuinely different dialects
  (see the parent README): of the ~3,700 distinct signatures across both
  files, only 817 are shared, 2066 are client-only, and 827 are session-only.
  Do not assume an inspector present in one file is valid in the other.

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
  both files).
- No header, footer, or blank lines; every line in both files is a
  `signature: type` entry with no exceptions.

## Regenerating

From a BES Client (Windows, for `client_relevance_windows.txt`) or a Web
Reports/console session (for `session_relevance_web_reports.txt`), evaluate
`properties` - e.g. via the Fixlet Debugger's QnA view, a REST API session
relevance query, or the BigFix SaaS MCP server's
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
`plural name of <property>` are themselves entries in
`session_relevance_web_reports.txt` - the introspection is self-hosting.
Availability and exact wording of meta-inspectors like these can vary by
BigFix version - if a recipe here fails, consult
`bigfix_get_session_relevance_reference` or the console's built-in relevance
help for the equivalent on your version.

## Further reading

Authoritative but not exhaustive - useful for looking up an inspector's full
signature, argument types, and prose description beyond what these plain-text
dumps capture:

- [BigFix Relevance Language documentation](https://developer.bigfix.com/relevance/) -
  guide-level docs: syntax, types, operators, control flow.
- [BigFix Relevance Language reference](https://developer.bigfix.com/relevance/reference/) -
  searchable inspector/operator reference, the closest official equivalent to
  what's captured in this folder's `.txt` files.
