# VS Code's XML grammar, vendored for the grammar tests

`xml.tmLanguage.json` is VS Code's built-in XML grammar (`text.xml`), copied
unchanged, but for a final newline the repository's hooks add, from the
MIT-licensed VS Code source:

- repository: [microsoft/vscode](https://github.com/microsoft/vscode)
- tag `1.140.0`, commit `07f806f999227108933c2e30515b26eecc1fda74`
- path: `extensions/xml/syntaxes/xml.tmLanguage.json`

VS Code converted it from
[atom/language-xml](https://github.com/atom/language-xml) at commit
`7bc75dfe779ad5b35d9bf4013d9181864358cb49`, as the file's own `version` field
records. Both projects are MIT-licensed. Their license texts are here
unchanged: `LICENSE-vscode.txt` (VS Code at the same tag) and
`LICENSE-atom-language-xml.md` (atom/language-xml at the same commit, which
also carries the notice of the TextMate bundle it derives from).

`../../grammar.test.mjs` reads it because the `.bes` grammar hands
everything outside its bodies to `text.xml`, and VS Code (not this
extension) provides that grammar. With a copy here, every run, CI's included,
tests the two grammars together. Nothing under `test/` is packaged (see
`.vscodeignore`).

To update it, copy the file from a newer VS Code tag, update the tag and
commit above, and rerun `node --test test/grammar.test.mjs`.
