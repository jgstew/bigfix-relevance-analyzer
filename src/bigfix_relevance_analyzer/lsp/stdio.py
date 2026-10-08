"""The stdio transport: ``Content-Length``-framed JSON-RPC around :class:`Server`.

The standard, editor-agnostic way to run a language server, and the way to test
this one with any LSP client -- Neovim, Helix, ``pytest-lsp``, or bytes piped
in by hand. Stdlib only, blocking, one message at a time: every handler is
synchronous, so there is nothing to interleave.

Only stdout carries protocol. Anything else written there corrupts the stream,
which is why the package never prints and the entry point sends logging to
stderr.
"""

from __future__ import annotations

import json
import logging
from typing import IO, Any

from bigfix_relevance_analyzer.lsp.server import ErrorCode, Message, Server, error_response

logger = logging.getLogger(__name__)

_CONTENT_LENGTH = b"content-length"


class _UnparsableError(Exception):
    """A frame arrived whole, but its body is not a JSON-RPC message."""


def read_message(stream: IO[bytes]) -> Any:
    """The next message on ``stream``, or ``None`` at end of input.

    Headers other than ``Content-Length`` (``Content-Type`` is the only other
    one the spec defines) are skipped. The length counts bytes, not
    characters. Raises :class:`ValueError` on a frame with no usable length --
    the stream cannot be resynchronized after that -- and ``_UnparsableError`` on
    a well-framed body that is not JSON, which can be answered and skipped.
    """
    length: int | None = None
    while True:
        line = stream.readline()
        if not line:
            return None
        line = line.rstrip(b"\r\n")
        if not line:
            break
        name, _, value = line.partition(b":")
        if name.strip().lower() == _CONTENT_LENGTH:
            length = int(value.strip())
            # `read(-1)` reads to end of input, swallowing every later message.
            if length < 0:
                raise ValueError(f"a negative Content-Length: {length}")
    if length is None:
        raise ValueError("a message header with no Content-Length")
    body = stream.read(length)
    if len(body) < length:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _UnparsableError(str(error)) from error


def write_message(stream: IO[bytes], message: Message) -> None:
    """Frame ``message`` onto ``stream`` and flush it."""
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    stream.write(b"Content-Length: %d\r\n\r\n" % len(body))
    stream.write(body)
    stream.flush()


def run(server: Server, stdin: IO[bytes], stdout: IO[bytes]) -> int:
    """Serve ``stdin`` to ``stdout`` until ``exit``; return the process exit code.

    End of input without ``exit`` is an unclean exit, 1, like ``exit`` without
    ``shutdown``: the client went away without saying goodbye.
    """
    while server.exit_code is None:
        try:
            message = read_message(stdin)
        except _UnparsableError as error:
            write_message(stdout, error_response(None, ErrorCode.PARSE_ERROR, str(error)))
            continue
        except ValueError:
            logger.exception("unreadable message frame; stopping")
            return 1
        if message is None:
            return 1
        for reply in server.handle(message):
            write_message(stdout, reply)
    return server.exit_code
