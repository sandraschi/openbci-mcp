"""FastMCP tool registration entry."""

from openbci_mcp.mcp_app import mcp
from openbci_mcp.tools import portmanteau  # noqa: F401

__all__ = ["mcp"]
