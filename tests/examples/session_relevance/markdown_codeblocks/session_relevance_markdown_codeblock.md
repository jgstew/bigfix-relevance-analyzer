# Relevance reference links

Session relevance run in the BigFix console/WebUI against the `types`
inspector. Note that `types` is *not* a session-only inspector, despite reading
like one: every client platform sampled in `../../relevance_properties/` ships
the same introspection meta-layer. So nothing in this statement identifies its
dialect, and the content classifier is right to have no opinion on it -- this
example is the regression test for that trap.

```
( it, ("https://developer.bigfix.com/relevance/reference/" & it & ".html") of (concatenations "-" of substrings separated by " " of it) ) of (it as string as trimmed string) whose("" != it) of types
```
