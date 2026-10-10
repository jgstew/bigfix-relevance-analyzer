# BigFix Relevance Developer

Catch mistakes in BigFix Relevance while you write it. Problems are underlined
as you type, in the fixlets, tasks, analyses, dashboards and documents where
your relevance already lives. Relevance, ActionScript and the fixlets that hold
them get syntax highlighting.

## Features

### Diagnostics as you type

Every relevance statement in an open file is checked, and problems appear as
squiggles and in the **Problems** panel (Cmd+Shift+M on macOS, Ctrl+Shift+M on
Windows and Linux).
Each one names its rule, for example `[unknown-inspector]`, so it's easy to look
up. Checks include:

- **Statements that can't run:** parse errors, unterminated strings and
  comments, `it` with nothing to refer to, and type errors such as comparing a
  number with a string.
- **Inspector names:** names no known inspector defines, with "did you mean"
  suggestions; and client-only and session-only inspectors mixed in one
  statement.
- **Plural and singular:** a singular spelling where more than one value can
  come back, which fails when it does, and plurals where the engine needs a
  single value.
- **Version comparisons** that quietly compare the wrong way, such as
  `version "14.6" > version "14"` truncating, or version-like strings compared
  as text.
- **ActionScript:** substitutions (`{...}`) that are never closed, that can
  produce several values, or that produce something with no text form; and
  ActionScript command words used inside relevance.
- **Complexity:** statements whose structure or evaluation cost is far above
  what ordinary content needs.

### Hover

Point at part of a statement to see what it is. On an inspector, the hover
shows the definitions it matches there: the signature, what it returns, whether
it is singular or plural as written, and the platforms (client) or contexts
(session) that have it. It also explains literals, what `it` refers to, and
keywords and operators such as `whose`, `of`, `|` and `as`, with links to the
reference documentation.

### Completion

Inspector names are suggested as you type, in three places:

- **After `of`:** what can go there, most likely first. After `files of`,
  `folders` comes first, then `csidl folders`, `windows folders` and the
  other things that hold files.
- **Inside `whose (`:** properties of what is being filtered. After
  `files whose (`, `name` comes first.
- **At the start of a statement**, and after `exists`, `not`, `and`, `or` or an
  opening parenthesis.

Suggestions are ordered by how often real BigFix content uses them in that
place, and only names that fit are offered: client inspectors in client
relevance, session inspectors in session relevance. A name usually written in
the plural is suggested in the plural, and one that usually takes an argument
is inserted with a placeholder for it (`folders "..."`). Suggestions appear as
you type a word; press `Ctrl+Space` to see them anywhere else, for example
right after `of `.

### Quick fixes

Some problems come with a fix the checker has worked out and checked is safe:
a name spelled in the singular where the plural is safer (`setting` becomes
`settings`), and a list of values where a single value is required (wrapped in
`unique value of`). A light bulb appears on the underlined text; click it, or
press `Ctrl+.` (`Cmd+.` on macOS), to apply the fix. **Fix all safe issues in
this file** applies every one at once.

A fix only adds the words it needs. Everything else in the file stays exactly
as you wrote it, including escaped characters such as `&lt;` and `&quot;` in
`.bes` files. A fix is not offered if it would cause a new problem anywhere in
the file, such as a statement becoming too complex.

To apply every safe fix each time you save, add this to your settings:

```json
"editor.codeActionsOnSave": { "source.fixAll.bigfix-relevance": "explicit" }
```

If your settings already fix everything on save for every language, as
ESLint, Ruff and other tools suggest:

```json
"editor.codeActionsOnSave": { "source.fixAll": "explicit" }
```

then these fixes run on save too. To keep the others but not these, add
`"source.fixAll.bigfix-relevance": "never"` beside it.

### Syntax highlighting

`.rel` and `.bsr` files, and relevance in Markdown code fences, are colored:
keywords such as `of`, `whose` and `if ... then ... else`, comparison, logical and
arithmetic operators (including `is not equal to` and `does not contain`),
`it`, strings, numbers and comments.

### ActionScript and BES files

`.bes` and `.bes.xml` files are colored as XML, with the code inside colored as
the language it is:

- **ActionScript** in action scripts: commands, `if`/`elseif`/`else`/`endif`,
  `//` comments, strings, URLs, and the relevance inside each `{...}`
  substitution. The text of a `createfile until` or `appendfile` block is
  shown as file content, not as commands, and the options of an
  `override run` or `override wait` block are shown as options. Action scripts
  in other languages (such as `application/x-sh` or PowerShell) stay plain.
- **Relevance** in relevance elements, success criteria and analysis
  properties.

ActionScript on its own, for example a template for an action, is colored in
files ending in `.actionscript`. Those files are highlighted only, not checked.

`.bes` files open as **BigFix BES XML**, which replaces VS Code's own XML
support for them. To have another XML extension handle them instead, map them
back to XML in your settings (you lose the ActionScript and relevance colors):

```json
"files.associations": { "*.bes": "xml", "*.bes.xml": "xml" }
```

### A language for relevance

**BigFix Relevance** is available as a language for any editor. Use
**Toggle Block Comment** to wrap a selection in `/* */`, and parentheses and
quotes are matched as you type. A new, unsaved file set to BigFix Relevance is
checked as you type too, before it has a name.

## Where relevance is found

| Files | What is checked |
|---|---|
| `.bes`, `.bes.xml` | Every relevance element, success criteria, analysis properties, and `{...}` substitutions in action scripts |
| `.ojo`, `.besrpt`, `.beswrpt`, `.webreport`, `.html`, `.htm` | `<?Relevance ...?>` blocks and relevance passed to JavaScript `Relevance(...)` calls |
| `.rel` | The whole file, as one client or session relevance statement |
| `.bsr` | The whole file, as one session relevance statement |
| `.md`, `.markdown` | Code fences tagged `relevance`, `client_relevance` or `session_relevance` |

In Markdown, only fenced blocks with one of those tags are read:

````markdown
```relevance
exists file "C:\Windows\notepad.exe"
```
````

## Settings

| Setting | Default | |
|---|---|---|
| `bigfixRelevance.maxDocumentBytes` | `1048576` (1 MiB) | Files larger than this are not checked; they get one information message instead, so a very large generated file can't slow the editor down. |
| `bigfixRelevance.trace.server` | `off` | Set to `messages` or `verbose` to log the extension's activity to its **Output** channel, for troubleshooting. |

## Commands

- **BigFix Relevance: Restart Language Server**: restarts the checker, for
  example after a settings change or if diagnostics stop updating.

## Known limitations

- A problem with a statement as a whole, such as one that is too complex, and
  a problem in the file around the relevance, such as an unclosed code fence,
  underline the whole line they are on. Every other problem underlines just
  the text it is about.
- Highlighting colors keywords and operators, not inspector names.
- In `.bes` files, relevance in descriptions, and in `<?Relevance ...?>`
  blocks of dashboards and reports, is checked but not colored. Nor is a
  relevance element whose start tag is split across lines (an action script's
  may be).
- A new, unsaved file set to BigFix BES XML is colored, but not checked until
  it is saved as a `.bes` file.
- Completion suggests inspector names after `of`, inside `whose (` and at the
  start of a statement. Elsewhere, such as after a comparison or `as`, it
  suggests nothing yet. Hover needs a statement that parses; on one with a
  syntax error there is no hover until it is fixed.
- A file is checked when its name ends in one of the file types above, or when
  its language is set to BigFix Relevance. Other files are left alone.
- The checker starts the first time you open a file with relevance to check,
  so it uses no memory in windows without any. Markdown and HTML files count
  only once they contain relevance, as described above.

## Feedback

Report problems or ideas at
[github.com/jgstew/bigfix-relevance-analyzer/issues](https://github.com/jgstew/bigfix-relevance-analyzer/issues).
The checks come from
[bigfix-relevance-analyzer](https://github.com/jgstew/bigfix-relevance-analyzer),
which also provides them on the command line and as a pre-commit hook.

## License

MIT
