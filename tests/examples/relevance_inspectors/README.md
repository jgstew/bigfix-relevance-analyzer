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
| `client_relevance_properties_windows.txt` | 2902 | `windows-latest`, `windows-2025` |
| `client_relevance_properties_macos.txt` | 2369 | `macos-latest` (macOS 26, arm64) |
| `client_relevance_properties_ubuntu.txt` | 2134 | Ubuntu latest, 24.04, 22.04, 20.04 |
| `client_relevance_properties_rhel.txt` | 2151 | AlmaLinux, Amazon Linux 2023, Oracle Linux 9, Rocky Linux 9 |
| `client_relevance_properties_debian.txt` | 2134 | Debian latest, Debian 11 |

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
because these are verbatim captures. Deduplicated they are 2131 / 2148 / 2131.

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

Client-side, captured on Windows and macOS. Both are **enriched** now (see
"Enriched columns" below, and Provenance's "Re-capturing Windows" and
"Re-capturing macOS" for how each was done):

| File | Signatures | Query (column 1) |
| --- | --- | --- |
| `client_relevance_casts_windows.txt` | 235 | `(it as string) of casts` |
| `client_relevance_binary_operators_windows.txt` | 376 | `(it as string) of binary operators` |
| `client_relevance_unary_operators_windows.txt` | 6 | `(it as string) of unary operators` |
| `client_relevance_types_windows.txt` | 312 | `(it as string) of types` |
| `client_relevance_casts_macos.txt` | 188 | `(it as string) of casts` |
| `client_relevance_binary_operators_macos.txt` | 345 | `(it as string) of binary operators` |
| `client_relevance_unary_operators_macos.txt` | 7 | `(it as string) of unary operators` |
| `client_relevance_types_macos.txt` | 245 | `(it as string) of types` |

And now on Ubuntu, Debian, and the RHEL family, via
`bigfix_remote_client_relevance` against Docker containers (see Provenance
below) - closing the platform-breadth gap the previous paragraph used to
describe. These four are **enriched** (see "Enriched columns" below) - column 1
is the query below; the columns after it come from the tuple query in
Regenerating, not this bare form:

| File | Signatures | Query (column 1) | Covers |
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

All four macOS meta-layer files above are now enriched too, once local `sudo`
became available for a capture session (macOS's `QnA` needs root to read its
masthead/action-site) - see "Re-capturing macOS" under Provenance for one real
wrinkle it ran into: one property (`dmi`) makes this build's `result type of
it` fail outright, not just return empty, and the fix had to skip it rather
than suppress it with `|`.

Windows *was* bare through the first enrichment pass - a host reachable then
ran qna 10.0.7.52, older than the client that produced the committed dumps,
and re-capturing from it would have *removed* signatures
(`<uinteger>`/`<large integer>` casts and operators it does not define) rather
than only adding columns. A follow-up pass downloaded the matching 11.0.6.137
standalone `QNA.zip` from `software.bigfix.com` (the same version used for the
Linux captures) and staged it on that host - see "Re-capturing Windows" under
Provenance for exactly how and why the tool's own Windows auto-provisioning
couldn't be used unmodified.

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
| Client union (all five platforms) | 3736 |
| Cross-platform client core (present on all five) | 1775 |
| Session (Web Reports) | 1644 |
| Shared between client union and session | 828 |
| Client-only | 2908 |
| Session-only | 816 |
| Distinct signatures overall | 4552 |

Client relevance and session relevance are genuinely different dialects (see
the parent README) - only 828 of 4552 signatures are valid in both. Do not
assume an inspector present in one file is valid in the other.

### Platform-specific surface

Signatures unique to one platform, measured against the union of the other
four:

| Platform | Unique | Character of the unique set |
| --- | --- | --- |
| windows | 958 | registry, WMI, COM, Active Directory, security accounts |
| macos | 462 | `osxvalue`/`dictionary`/`array` plists, `applications`, macOS folder domains, **and the statistics/projection layer** (see the warning below) |
| rhel | 67 | `rpm`, `package`, `capability`, `rpm package version record`, `runlevels of <service>` |
| ubuntu | 0 | - |
| debian | 0 | - |

Ubuntu and Debian contribute no signatures of their own, and as of qna
11.0.6.137 they are **fully byte-identical to each other for `properties` too**
(0 lines differ either direction) - not merely a subset relationship. This
narrows an earlier finding: at whatever client version produced the currently
committed dumps, Ubuntu had 51 signatures Debian lacked (`cidr subnet`, perl
regexes, `display name of <operating system>`); re-capturing both at
11.0.6.137 shows Debian gained all 51, closing the gap. Treat "Ubuntu and
Debian differ for `properties`" as version-dependent, not structural - a
future qna release could reopen or re-close it. The four introspection
categories above stayed byte-identical between the two across both client
versions, unaffected by this convergence.

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
  BigFix client releases; each file is a single point in time. All five
  client platforms happen to agree on 11.0.6.137 as of the enriched
  re-capture above, but that is a snapshot, not a guarantee - a future
  capture on any one platform can drift again.
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
  every file). **That order is not guaranteed reproducible across captures**:
  re-running the identical query against the same live session returned
  `casts`, `unary operators` and `types` in the committed order byte-for-byte,
  but `binary operators` and `properties` came back in a different order with
  the same set of lines (verified by sha1 of the sorted set, not sequence -
  see Regenerating). A diff against a re-capture of these two categories
  should compare sorted content, not raw file order.
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

A dump without these columns leaves the corresponding `Inspector`/
`RelevanceType` fields as `None`; the generator merges rows across dumps by
their pre-tab text, so a bare client line and an enriched session line for the
same inspector become one row, not two - this is exactly what makes partial
enrichment (some platforms, not others) safe rather than a special case.

As of this writing, enriched: the four `*_rest_api.txt` session files, and
every client platform's dumps - all five categories on Windows, macOS,
Ubuntu, Debian and the RHEL family (`client_relevance_*_{windows,macos,
ubuntu,debian,rhel}.txt`, including `properties`). Still bare: only the two
`session_relevance_properties_{console,web_reports}.txt` files - no session
available to re-run them against.

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
`session_relevance_types_rest_api.txt`), and `session_relevance_properties_rest_api.txt`,
were captured directly through the BigFix SaaS MCP server's
`bigfix_query_session_relevance` tool against a live session - **not** with
the bare `(it as string) of casts` shape (an earlier version of this section
claimed that, which cannot have produced these files' extra columns; that was
wrong). The actual query is the enriched tuple form given for each category
under Regenerating below. Confirmed by re-running all five against a live
session and comparing sha1: `casts`, `unary operators` and `types` reproduce
the committed file byte-for-byte; `binary operators` and `properties`
reproduce it as a set (same 442 / 1756 lines, different order - see the row-
order caveat under Format).

The four `*_windows.txt` client meta-layer files
(`client_relevance_casts_windows.txt`,
`client_relevance_binary_operators_windows.txt`,
`client_relevance_unary_operators_windows.txt`,
`client_relevance_types_windows.txt`) were originally captured the same way as
`client_relevance_properties_windows.txt` above - bare. All five Windows files
were since superseded by an enriched re-capture; see "Re-capturing Windows"
below.

The four `*_macos.txt` client meta-layer files
(`client_relevance_casts_macos.txt`,
`client_relevance_binary_operators_macos.txt`,
`client_relevance_unary_operators_macos.txt`,
`client_relevance_types_macos.txt`), and `client_relevance_properties_macos.txt`,
were originally captured directly on a macOS BES Agent via the `QnA` binary,
one query per file, e.g.:

```bash
echo '(it as string) of casts' | sudo /Library/BESAgent/BESAgent.app/Contents/MacOS/QnA | grep '^A: ' | sed 's/^A: //' > client_relevance_casts_macos.txt
```

with the same substitution as the REST API queries above for `binary
operators`, `unary operators` and `types`. `sudo` is required because `QnA`
needs root to read the client's local action site. That recipe's plain
`sed 's/^A: //'` is why the originally-committed
`client_relevance_binary_operators_macos.txt` had 10 `mod`-operator lines with
a literal `%25` in them instead of `%` - it never decoded the percent-escape
documented under Regenerating, because this project didn't know about it yet.
All five macOS files were since superseded by an enriched re-capture that
fixes this; see "Re-capturing macOS" below.

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
`client_relevance_properties_rhel.txt` already set. The tool has no
pre-command hook to install `cpio` inside `--container`/`--inventory` runs, so
the enriched re-capture below used a base image pre-committed with it:
`docker run -d --name prep almalinux:9 sleep 300 && docker exec prep dnf
install -y cpio dbus-libs && docker commit prep almalinux9-qna-ready`, then
pointed the inventory's `image` at `almalinux9-qna-ready`.

### The enriched re-capture (this pass)

All five categories on Ubuntu, Debian and the RHEL family were re-captured
enriched using the tuple queries under Regenerating, via the same
`bigfix-remote-client-relevance` route and qna 11.0.6.137, run as
`uvx --from git+https://github.com/jgstew/bigfix_remote_client_relevance
bigfix-remote-client-relevance --container <image> --qna-version 11.0
-f <query-file>` (the `-f` flag reads the query from a file, avoiding shell
escaping issues with `&`/quoting that `--container image "query text"` runs
into). Column 1 of every re-capture matched the previously committed bare file
exactly for `casts`, `unary_operators` and `types` (all three platforms, 0
lines different); `properties` came back a strict superset on all three (new
`yaml`-related lines only, nothing removed), the same qna-version-bump effect
the paragraph above this section already documented for the bare properties
re-run - it applied here too, so those three `properties` files were updated
along with the meta-layer ones.

`binary_operators` also showed 0 lines different at the time - but that
was two wrongs matching, not a clean result: the committed bare file already
had `%25` in place of a literal `%` in its 10 `mod`-operator lines
(`<hertz> %25 <hertz>`), a pre-existing bug going back to the very first bare
capture in this project (commit `36caa72`, no tab delimiter involved at all -
`(it as string) of binary operators` alone triggers it). Column 1 of the
fresh enriched capture reproduced that same `%25` byte-for-byte because the
`%25`->`%` decode step wasn't identified yet at this point in the work (it
surfaced later, capturing Windows - see "Re-capturing Windows" below), so the
comparison matched two identically-wrong strings. It has since been corrected
in all three Linux files along with Windows and macOS - see the note under
"Producing the enriched format" below for why `%` needs decoding independent
of the tab, and note this confirms the escaping is a **QnA-client quirk, not
a relevance-engine-wide behavior**: `session_relevance_binary_operators_rest_api.txt`,
captured through the REST API/session path rather than through `QnA`, has
always had a literal `%`.

A Windows host was reachable this pass over `ssh <user>@<host>` (its `qna.exe`
found via `dir "C:\Program Files (x86)\BigFix Enterprise\BES Client"`, queries
piped in via a redirected file rather than `echo` on the command line - `&`
inside the query is a command separator to `cmd.exe`), but its installed qna
was 10.0.7.52 - older than whatever produced the committed
`client_relevance_*_windows.txt` files, which define `<uinteger>` and
`<large integer>` casts/operators this client does not. Re-capturing from the
*installed* client would have been a regression (signatures removed, not just
columns added). macOS's local `QnA` needs interactive `sudo` for its
masthead/action-site read, unavailable to a non-interactive capture session -
left untouched this pass; enriching it needs a human at the keyboard.

### Re-capturing Windows

Rather than touch the host's installed BES Client, a **standalone** qna was
staged side-by-side, matching the version used for the Linux captures:

1. Resolved the artifact - BigFix's Windows-specific standalone QnA download,
   distinct from every other platform (which extract qna out of the full
   agent package): `https://software.bigfix.com/download/bes/110/util/QNA11.0.6.137.zip`,
   sha256 `9a5af296b12d799e97b4baace1368cdc464fcf91744ee7f73b20961a7c6f8da7`.
2. Downloaded and verified that sha256 locally (17,443,147 bytes).
3. `scp`'d the zip to the host and extracted it with an explicit
   `powershell -Command "Expand-Archive -Path ... -DestinationPath ... -Force"`
   over the existing `ssh` session, landing `qna.exe` (11.0.6.137, confirmed via
   `(Get-Item qna.exe).VersionInfo.FileVersion`) next to - not over - the
   installed client.
4. Ran the five tuple queries against that binary the same way as the original
   capture (redirected query file, not `echo`), redirecting output to a file
   and `scp`-ing it back rather than reading it over the pipe directly.

**Why not the tool's own Windows auto-provisioning** (the same one-line
`--container`/`--inventory` flow used for Linux, just pointed at the SSH
host): it pushes the artifact and unpacks it by running `Expand-Archive`
directly, which requires the OpenSSH server's *default shell* already be set
to PowerShell (a `HKLM:\SOFTWARE\OpenSSH\DefaultShell` registry value) - `cmd.exe`
is the default and `Expand-Archive` is not a `cmd.exe` builtin. Changing that
default shell is itself a security-relevant host setting, not something to
flip in passing to capture a data file; running `powershell -Command` once,
explicitly, for the one command that needed it, made the tool's own bootstrap
path unnecessary.

**Two failure-prone details this recipe accounts for**, both because a raw
`qna.exe` pipe is much less filtered than the tool's own parsed output:

- `qna.exe`'s output includes a trailing `T: <microseconds>` timing line and a
  final bare `Q:` prompt after the real `A: `-prefixed answers. A naive
  `sed 's/^A: //'` substitution leaves lines it doesn't match *unchanged*
  rather than dropping them, so those two lines leak into the capture as
  garbage rows - `grep '^A: '` (drop non-matching lines) before stripping the
  prefix, not just substitution, e.g.:
  `grep -E '^(Q: )?A: ' out.txt | sed -E 's/^Q: A: //; s/^A: //'`.
- The `<hertz> % <hertz>` (mod) operator's `%` renders as `%25` in a client
  capture, on top of the tab-as-`%09` quirk already documented under
  Regenerating. This is **not specific to the tab delimiter** - `QnA`
  percent-encodes a literal `%` in its own answer-printing regardless of
  what else is in the string, confirmed by the very first bare capture in
  this project (commit `36caa72`, `(it as string) of binary operators`
  alone, no tab anywhere) already showing `%25`, undetected until this pass.
  It is also **specific to `QnA` itself, not the relevance engine**: the
  session/REST API path (`session_relevance_binary_operators_rest_api.txt`)
  has always printed a literal `%`. `grep -o '%[0-9A-Fa-f][0-9A-Fa-f]' file |
  sort -u` across every capture from every platform confirmed `%09` and
  `%25` are the *only* two sequences `QnA` ever produces; decode both
  (`sed 's/%09/\t/g; s/%25/%/g'`), in either order - a genuine tab or `%` in
  the source text never appears next to a digit pair that would make the two
  substitutions collide. `scp`'d output also carried CRLF line endings,
  stripped with `s/\r$//` before either percent-decode.

Column 1 of the result matched the previously committed bare file's content
as a strict superset for all five categories (`casts` +5, `binary_operators`
+2, `types` +3, `properties` +19, `unary_operators` +0 - nothing removed,
confirmed with `comm -23` in both directions before overwriting).

### Re-capturing macOS

Once local `sudo` for `/Library/BESAgent/BESAgent.app/Contents/MacOS/QnA`
became available in a capture session, the same five tuple queries ran
directly against the installed agent - already 11.0.6.137, matching every
other platform, so no download was needed here. Column 1 matched the
committed file as a strict superset for `casts` (+0, content-identical once
`%25`->`%` is decoded), `unary_operators` (+0), `types` (+1), and
`binary_operators` (content-corrected as above, same 345 lines) - except
`properties`, which hit a real bug:

The `properties` tuple query aborted partway with `E: Singular expression
refers to nonexistent object.`, silently truncating the answer stream at
whichever property triggered it and dropping everything after in QnA's
internal enumeration order - **only one property's error, but ~150 unrelated
properties never got a chance to evaluate**, because the plural query is not
per-row fault-isolated. Bisecting by re-running `(result type of it) of
properties whose (usual name of it as string = "dmi")` alone (isolating one
candidate at a time, since the raw output cut off right after `dmi`'s
neighbor in enumeration order) found the culprit: `result type of <dmi>`
throws on this property specifically, even though `dmi: dmi` itself evaluates
fine and every other property's `result type of it` is unremarkable.
`(name of X | "")` error-suppression, which correctly produces the empty
column for a property with no direct-object or index type, does not save a
sibling column whose right-hand side is a hard failure rather than an
absent-value error - the fix has to keep the failing row out of the plural
evaluation entirely:

```
(<the tuple query>) of (properties whose (exists result type of it))
```

That drops exactly the one broken row (`dmi`) rather than fabricating a
result type or index type for it, but `dmi` is a real property (`it as
string` alone evaluates it fine as `dmi: dmi`) and belongs in the file, so its
row was reconstructed by hand from the columns that *do* evaluate
(`singular name of it`, `plural name of it`, `usual name of it`, `multivalued
of it` all succeed individually) plus the bare signature for the result type:
`dmi: dmi\tdmi\tdmis\tdmi\t0\tdmi\t\t` - enriched except the one column QnA
itself cannot produce here. Before trusting any bisection like this again,
`grep -c '^E:' <raw capture>` on every category is cheap insurance - it is
what caught this one, since `casts`/`binary_operators`/`unary_operators`/
`types` all came back clean with no truncation to chase.

Re-running `properties` the same way against qna 11.0.6.137 (newer than the
version that produced the committed `client_relevance_properties_*.txt`
files) reproduced each committed dump as a strict subset - a handful of new
`yaml`-inspector lines on top, nothing removed or changed. That superset
relationship was originally the reason to leave a re-capture as-is rather
than churn it for a version bump alone; once the same re-capture also brought
enrichment, churning became worth it and the
`properties` file for every client platform was updated (see "The enriched
re-capture" and "Re-capturing Windows"/"Re-capturing macOS" above) - all five
platforms are now on qna 11.0.6.137 and enriched, closing what had been the
"one client version per platform" gap in "Still not exhaustive" below for
every platform this project can currently reach.

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

### Producing the enriched format

The tuple form at :398 above (`(usual names of it, singular names of it,
plural names of it) of properties`) is the wrong shape to capture from a
**client**: QnA renders a tuple comma-joined (`A: a, b, c`), which cannot be
split back apart when a value itself contains a comma - and one genuinely
does, the type `( string, string )` in the properties dump. Build the
delimiter inside the relevance expression instead with `character 9` (a tab;
both dialects define it - `character <integer>` is itself line 418 of the
Ubuntu properties dump and line 232 of the session capture), producing one
string per row with real tabs already in it. This is the query the
`*_rest_api.txt` files and the enriched Ubuntu/Debian/RHEL files (see
Provenance) actually used - the same text works unchanged in both dialects:

```
(it as string & character 9 & name of it & character 9 & name of operand type of it & character 9 & name of result type of it) of casts
```

```
(it as string & character 9 & name of it & character 9 & symbol of it & character 9 & name of left operand type of it & character 9 & name of right operand type of it & character 9 & name of result type of it) of binary operators
```

```
(it as string & character 9 & name of it & character 9 & symbol of it & character 9 & name of operand type of it & character 9 & name of result type of it) of unary operators
```

```
(it as string & character 9 & singular name of it & character 9 & plural name of it & character 9 & usual name of it & character 9 & (if multivalued of it then "1" else "0") & character 9 & name of result type of it & character 9 & (name of direct object type of it | "") & character 9 & (name of index type of it | "")) of properties
```

```
(name of it & character 9 & (name of parent of it | "") & character 9 & ((size of it as string) | "")) of types
```

`|` is error-suppression - it produces the empty cell the enriched files use
for "no direct object", "no index", "root type" or "unknown size", matching
the column semantics in "Enriched columns" above exactly. Column order follows
that section's field lists; `(if multivalued of it then "1" else "0")` is
confirmed as the source of the `properties` files' `1`/`0` column.

**Verified, not a guess**: re-running all five against a live session and
comparing sha1 against the committed `*_rest_api.txt` files -
`sha1 of (concatenation (character 10) of (<query>) & character 10)` matches
`shasum` on the file - showed `casts`, `unary operators` and `types`
byte-identical, and `binary operators`/`properties` identical once sorted (see
the row-order caveat under Format). Per-column sha1 (`cut -f<k> file | shasum`
against the same column projected in relevance) isolates a mismatch to one
column if a future recipe drifts.

**On a client, QnA percent-encodes at least two characters**: piping these
queries through a BES Client's `QnA` (Windows, macOS, or the containerized
Linux route in Provenance) prints `%09` where the session/REST API path
prints a literal tab, and prints `%25` for a literal `%` - the `<hertz> %
<hertz>` (`mod`) binary operator surfaces the second one. Confirmed on a
Windows 10.0.7.52 client, a Windows 11.0.6.137 standalone `qna.exe` (see
"Re-capturing Windows" under Provenance), and an Ubuntu/Debian/RHEL container
running qna 11.0.6.137: `grep -o '%[0-9A-Fa-f][0-9A-Fa-f]' file | sort -u`
across every capture from every platform found only `%09` and `%25` - never
another sequence, so decoding those two covers what QnA actually does, not
just what these particular dumps happened to need. Undo both after stripping
the `Q: `/`A: ` prefixes and before splitting on tab; a `scp`'d Windows
capture also needs `\r` stripped first:

```bash
sed -E 's/^[^\t]*\t[^\t]*\t//' | sed -E 's/^[0-9-]{10}T[0-9:.]+Z //; s/^Q: //' | grep '^A: ' | sed -E 's/^A: //; s/\r$//; s/%09/\t/g; s/%25/%/g'
```

A direct `QnA`/`qna.exe` pipe (no job-log framing) needs the trailer lines
filtered too - `qna.exe` appends a `T: <microseconds>` timing line and a
final bare `Q:` prompt after the real answers, and a bare `sed
's/^A: //'` leaves a non-matching line unchanged rather than dropping it, so
those leak into the capture as garbage rows if `grep` doesn't remove them
first:

```bash
grep -E '^(Q: )?A: ' | sed -E 's/^Q: A: //; s/^A: //; s/\r$//; s/%09/\t/g; s/%25/%/g'
```

(that is the existing `run_qna`/raw-job-log pipeline from Provenance with one
extra `s/%09/\t/g`; for a direct `QnA`/`qna.exe` pipe without job-log framing,
drop the two `sed -E` steps before `grep` and keep the rest.)

### Doing all of that in one command

`tools/generate_client_dumps.py` drives a local `QnA` through all five queries
above and writes this folder's files directly, so a platform or a client
version can be re-captured rather than transcribed:

```bash
python tools/generate_client_dumps.py --qna /path/to/QnA --context ubuntu
```

It handles both traps in code rather than by pipeline, and adds the check
neither the pipeline nor a byte comparison can make: **each category's row
count is compared against the engine's own `number of properties` / `number of
casts` / `number of binary operators` / `number of unary operators` / `number
of types`.** That is what catches the dropped first answer, which is invisible
in the output and shows up only as a table one row short. The counts are
verified where the engine is, at capture time; the per-file `Signatures`
columns above stay the record on this side. `--stdout` prints without writing,
`--out` writes elsewhere for review first, `--no-verify` skips the count check.

`tests/test_generate_client_dumps.py` pins the parsing against fixture
transcripts, and asserts the script's five queries are byte-identical to the
ones documented above -- so this section and the tool cannot drift apart.

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
