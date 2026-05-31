"""FastMCP dual transport configuration (fleet template)."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from typing import Literal

logger = logging.getLogger(__name__)

TransportType = Literal["stdio", "http", "sse"]

ENV_TRANSPORT = "MCP_TRANSPORT"
ENV_HOST = "MCP_HOST"
ENV_PORT = "MCP_PORT"
ENV_PATH = "MCP_PATH"


def get_transport_config() -> dict:
    return {
        "transport": os.getenv(ENV_TRANSPORT, "stdio").lower(),
        "host": os.getenv(ENV_HOST, "127.0.0.1"),
        "port": int(os.getenv(ENV_PORT, "10759")),
        "path": os.getenv(ENV_PATH, "/mcp"),
    }


def create_argument_parser(server_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"{server_name} - FastMCP 3.2 Server")
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument("--stdio", action="store_true", help="Run in STDIO mode")
    transport_group.add_argument("--http", action="store_true", help="Run in HTTP Streamable mode")
    transport_group.add_argument("--sse", action="store_true", help="Run in SSE mode (deprecated)")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--path", default=None)
    parser.add_argument("--debug", action="store_true")
    return parser


def resolve_transport(args: argparse.Namespace) -> TransportType:
    if args.http:
        return "http"
    if args.sse:
        logger.warning("SSE transport is deprecated; use --http")
        return "sse"
    if args.stdio:
        return "stdio"
    env_transport = os.getenv(ENV_TRANSPORT, "stdio").lower()
    if env_transport not in ("stdio", "http", "sse"):
        logger.warning("Invalid MCP_TRANSPORT=%r, defaulting to stdio", env_transport)
        return "stdio"
    return env_transport  # type: ignore[return-value]


def resolve_config(args: argparse.Namespace) -> dict:
    env_config = get_transport_config()
    return {
        "transport": resolve_transport(args),
        "host": args.host if args.host is not None else env_config["host"],
        "port": args.port if args.port is not None else env_config["port"],
        "path": args.path if args.path is not None else env_config["path"],
    }


async def run_server_async(
    mcp_app,
    args: argparse.Namespace | None = None,
    server_name: str = "openbci-mcp",
) -> None:
    if args is None:
        parser = create_argument_parser(server_name)
        args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    config = resolve_config(args)
    transport = config["transport"]
    logger.info("Starting %s transport=%s", server_name, transport.upper())
    if transport == "stdio":
        await mcp_app.run_stdio_async()
    elif transport == "http":
        await mcp_app.run_http_async(
            host=config["host"],
            port=config["port"],
            path=config["path"],
        )
    elif transport == "sse":
        await mcp_app.run_sse_async(host=config["host"], port=config["port"])


def run_server(mcp_app, args: argparse.Namespace | None = None, server_name: str = "openbci-mcp") -> None:
    asyncio.run(run_server_async(mcp_app, args, server_name))
