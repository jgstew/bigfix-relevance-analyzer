// The regression cases both runtimes' browser tests run, and the corpus the
// parity test compares them on.
//
// One copy on purpose: the whole value of having two playgrounds is that they
// must agree, and a case list that existed twice could drift into testing the
// two pages against different expectations -- which is exactly the failure the
// second playground was built to detect.
//
// Imported across package boundaries by relative path
// (`../../<runtime>/browser-test/`). Both browser-test packages are
// `private: true` and CI-only, so a relative import beats introducing an npm
// workspace to share ~40 lines.

// Each case is a relevance string plus the badge text run() should produce.
// Chosen to cover every failure mode a real bug has actually hit in this
// page: the happy path, an unresolved identifier, a parse error, and an
// it-binding (see template.html's renderPayload for what these read).
//
// The dialect badge reads `dialect.resolved` -- the inspector tables' own
// post-parse verdict -- rather than `dialect.classified`, which runs on raw
// text and is deliberately blind to common English words like `file`. The
// last two cases are the ones that distinguish them: a statement the text
// classifier has no opinion about is still definitely client relevance if
// every name in it resolves that way, and a statement it *does* have an
// opinion about is still valid as neither dialect when the names contradict.
export const CASES = [
  {
    text: 'exists running application "winlogon.exe" AND version of operating system >= "10.0"',
    expectBadges: "dialect: client parse: ok types: ok",
  },
  { text: "asdfdffds", expectBadges: "dialect: undetermined parse: ok types: ok" },
  {
    text: "exists ((( unclosed nonsense here",
    expectBadges: "dialect: undetermined parse: error types: n/a",
  },
  {
    text: 'exists file "x.txt" of folders "/" whose (size of it > 100)',
    expectBadges: "dialect: client parse: ok types: error",
  },
  {
    // `files`/`folders` are client-only, `bes computers` is session-only, so
    // no engine evaluates this. The text classifier calls it session on the
    // strength of the `bes ` prefix alone.
    text: '(exists files of folders "/") AND (exists bes computers)',
    expectBadges: "dialect: uncertain (client and session) parse: ok types: ok",
  },
];
