"""Completion: what fits where the cursor is, ranked by how real content uses it.

Relevance flows right to left and is typed left to right. In ``files of |`` the
text to the left is the *consumer*, and what completion suggests is a
*producer* of what it takes: ``files of`` takes a ``<folder>``, so ``folders``,
``windows folder``, ``parent folder of ...``. That makes completion a reverse
lookup by type, ranked by a table mined from real content, rather than a parse
of a half-written statement (#127).

Two halves, kept apart so a later error-recovering parser (#96 item 3) drops
in as a second producer of the same context:

* :mod:`~bigfix_relevance_analyzer.completion.context` -- where the cursor is
  and what must fit there, as a :class:`~.context.CompletionContext`. Today's
  only producer of one is :func:`~.context.scan_context`, a backward scan over
  tokens.
* :mod:`~bigfix_relevance_analyzer.completion.rank` -- ordered candidates for a
  context. It reads only the context, never tokens or the scan.

No protocol here; :meth:`~bigfix_relevance_analyzer.lsp.linter.DocumentLinter.completions`
is the editor's way in.
"""
