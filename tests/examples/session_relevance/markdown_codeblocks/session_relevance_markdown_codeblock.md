# Relevance reference links

Session relevance run in the BigFix console/WebUI against the `types`
inspector, which only exists in a session relevance context (there is no
"types" of anything on a client).

```
( it, ("https://developer.bigfix.com/relevance/reference/" & it & ".html") of (concatenations "-" of substrings separated by " " of it) ) of (it as string as trimmed string) whose("" != it) of types
```
