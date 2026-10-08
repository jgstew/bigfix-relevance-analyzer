# BigFix Relevance Developer

Catch mistakes in BigFix Relevance while you write it. Problems are underlined
as you type, in the fixlets, tasks, analyses, dashboards and documents where
your relevance already lives. Whole-file relevance gets syntax highlighting.

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

### Syntax highlighting

`.rel` and `.bsr` files, and relevance in Markdown code fences, are colored:
keywords such as `of`, `whose` and `if ... then ... else`, comparison, logical and
arithmetic operators (including `is not equal to` and `does not contain`),
`it`, strings, numbers and comments.

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

- An underline covers the whole line that a problem is on, not just the
  offending word. The message says what is wrong.
- Highlighting colors keywords and operators, not inspector names.
- Hover information and completion are not available yet.
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
