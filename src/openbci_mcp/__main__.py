"""CLI entry: stdio MCP or HTTP serve."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

import uvicorn

from openbci_mcp.config import load_settings
from openbci_mcp.mcp_app import mcp
from openbci_mcp.tools import (
    agentic,  # noqa: F401
    portmanteau,  # noqa: F401
)


def _configure_logging(*, debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="openbci-mcp (FastMCP 3.2 + BrainFlow)")
    parser.add_argument("--serve", action="store_true", help="Run REST + MCP HTTP + WebSocket")
    parser.add_argument("--stdio", action="store_true", help="MCP stdio (default without --serve)")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    _configure_logging(debug=args.debug)

    transport = os.getenv("MCP_TRANSPORT", "").lower()
    use_http = args.serve or transport in {"http", "streamable"}
    if use_http and args.stdio:
        parser.error("Choose either --serve or --stdio, not both.")

    settings = load_settings()
    if use_http:
        uvicorn.run(
            "openbci_mcp.app:app",
            host=settings.host,
            port=settings.port,
            log_level="debug" if args.debug else "info",
        )
        return

    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
