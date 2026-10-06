"""ActionScript command words that are never relevance. Do not edit by hand.

Regenerate with ``python tools/generate_actionscript_keywords.py``; see
that script for how the list is derived, and ``tests/test_lint.py`` for
the test pinning it against the inspector tables.
"""

from __future__ import annotations

from typing import Final

# 37 words
ACTIONSCRIPT_KEYWORDS: Final = frozenset(
    {
        "appendfile",
        "chmod",
        "copy",
        "delete",
        "dos",
        "download",
        "elseif",
        "endif",
        "exit",
        "extract",
        "move",
        "open",
        "prefetch",
        "quarantine",
        "reenroll",
        "refresh",
        "regdelete",
        "regdelete64",
        "regkeydelete",
        "regkeydelete64",
        "regset",
        "regset64",
        "remove",
        "reset",
        "restart",
        "run",
        "rundetached",
        "runhidden",
        "script64",
        "shutdown",
        "subscribe",
        "unenroll",
        "unsubscribe",
        "utility",
        "waitdetached",
        "waithidden",
        "wipe",
    }
)
