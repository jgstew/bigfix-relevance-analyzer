"""``python -m bigfix_relevance_analyzer.lsp``: the language server over stdio.

Also installed as the ``bigfix-relevance-lsp`` console script.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from bigfix_relevance_analyzer.lsp.server import Server
from bigfix_relevance_analyzer.lsp.stdio import run


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bigfix-relevance-lsp",
        description="A BigFix Relevance language server, speaking LSP over stdio.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="logging threshold; logs go to stderr, never stdout (default: %(default)s)",
    )
    # Accepted and ignored: stdio is the only transport. Many clients append it
    # anyway -- vscode-languageclient always does for a stdio transport -- so
    # refusing it would make the server exit before `initialize`.
    parser.add_argument("--stdio", action="store_true", help="use stdio (the only transport)")
    args = parser.parse_args(argv)
    logging.basicConfig(stream=sys.stderr, level=args.log_level)
    return run(Server(), sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    raise SystemExit(main())
