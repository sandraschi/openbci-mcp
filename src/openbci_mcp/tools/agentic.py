"""SEP-1577 agentic workflow for OpenBCI experiments."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastmcp import Context
from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.mcp_app import mcp

logger = logging.getLogger(__name__)

DEFAULT_TOOLS = [
    "openbci_board",
    "openbci_stream",
    "openbci_signal",
    "openbci_export",
    "openbci_trigger",
    "openbci_help",
]


def _err(error: str, code: str, message: str, recovery: list[str] | None = None) -> ToolResult:
    return ToolResult(
        content={
            "success": False,
            "error": error,
            "error_code": code,
            "message": message,
            "recovery_options": recovery or [],
        },
        is_error=True,
    )


@mcp.tool(version="1.0.0")
async def agentic_openbci_workflow(
    workflow_prompt: Annotated[
        str,
        Field(description="Goal in natural language, e.g. 'Connect Cyton on COM3, stream, report beta power'."),
    ],
    available_tools: Annotated[
        list[str] | None,
        Field(description="openbci_* tool names to expose to the sampler."),
    ] = None,
    max_iterations: Annotated[int, Field(description="Max sample_step rounds.", ge=1, le=20)] = 8,
    context: Annotated[Context | None, Field(description="Injected FastMCP Context")] = None,
) -> ToolResult:
    """
    Multi-step OpenBCI workflows via FastMCP sampling (SEP-1577).

    Example:
    agentic_openbci_workflow(
        workflow_prompt="Connect synthetic board, start stream, compute band power",
        available_tools=["openbci_board", "openbci_stream", "openbci_signal"],
    )
    """
    tools = available_tools or DEFAULT_TOOLS
    if not workflow_prompt.strip():
        return _err("Missing workflow_prompt", "MISSING_PROMPT", "workflow_prompt is required")
    if context is None:
        return _err(
            "No MCP context",
            "NO_CONTEXT",
            "Requires FastMCP Context from an MCP client",
            ["Invoke from Cursor/Claude with sampling enabled"],
        )
    if not hasattr(context, "sample_step"):
        return _err(
            "Sampling unavailable",
            "SAMPLING_UNAVAILABLE",
            "Context has no sample_step",
            ["Use fastmcp>=3.2 client with sampling", "Chain portmanteau tools manually"],
        )

    try:
        all_tools = await mcp.list_tools()
    except Exception as exc:
        logger.exception("list_tools failed")
        return _err("list_tools failed", "LIST_TOOLS_FAILED", str(exc))

    name_to_tool = {t.name: t for t in all_tools if getattr(t, "name", None)}
    tools_for_sampling = [name_to_tool[n] for n in tools if n in name_to_tool]
    missing = [n for n in tools if n not in name_to_tool]
    if not tools_for_sampling:
        return _err(
            "No matching tools",
            "TOOLS_NOT_FOUND",
            f"Registered: {sorted(name_to_tool.keys())}",
            ["Use openbci_board, openbci_stream, ..."],
        )

    system_prompt = (
        "You are an OpenBCI / BrainFlow assistant. Use only the listed tools. "
        "Typical flow: list_ports -> connect -> start stream -> band_power or snapshot. "
        "For OSC output use openbci_trigger. Summarize results clearly when done."
    )
    messages: list[Any] = [{"role": "user", "content": workflow_prompt}]
    executed: list[str] = []
    iterations = 0
    step: Any = None

    while iterations < max_iterations:
        iterations += 1
        step = await context.sample_step(
            messages,
            system_prompt=system_prompt,
            tools=tools_for_sampling,
            execute_tools=True,
            max_tokens=4096,
        )
        if hasattr(step, "history") and step.history:
            messages = list(step.history)
        if hasattr(step, "tool_calls") and step.tool_calls:
            for tc in step.tool_calls:
                name = getattr(tc, "name", None) or getattr(tc, "tool_name", str(tc))
                if name:
                    executed.append(str(name))
        if not getattr(step, "is_tool_use", True):
            return ToolResult(
                content={
                    "success": True,
                    "operation": "agentic_openbci_workflow",
                    "result": {
                        "final_output": getattr(step, "text", "") or "",
                        "iterations": iterations,
                        "executed_tools": list(dict.fromkeys(executed)),
                        "missing_tool_names": missing,
                    },
                }
            )

    return ToolResult(
        content={
            "success": True,
            "operation": "agentic_openbci_workflow",
            "message": "Stopped at max_iterations",
            "result": {
                "final_output": getattr(step, "text", "") if step else "",
                "iterations": iterations,
                "executed_tools": list(dict.fromkeys(executed)),
                "missing_tool_names": missing,
            },
        }
    )
