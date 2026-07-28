"""OSC trigger rules portmanteau (pairs with osc-mcp targets)."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp
from openbci_mcp.osc_client import send_osc
from openbci_mcp.trigger_engine import get_trigger_engine


def _err(message: str) -> ToolResult:
    return ToolResult(content={"success": False, "error": message}, is_error=True)


@mcp.tool(version="1.0.0")
async def openbci_trigger(
    operation: Annotated[
        Literal[
            "send_osc",
            "list_rules",
            "add_rule",
            "remove_rule",
            "evaluate",
            "history",
            "fire_test",
        ],
        Field(description="OSC trigger operation."),
    ],
    osc_host: Annotated[str | None, Field(description="OSC target host (default from OPENBCI_OSC_HOST)")] = None,
    osc_port: Annotated[int | None, Field(description="OSC target port (default OPENBCI_OSC_PORT=9000)")] = None,
    osc_address: Annotated[str | None, Field(description="OSC address e.g. /bci/focus")] = None,
    osc_values: Annotated[list[float] | None, Field(description="OSC argument list")] = None,
    rule_id: Annotated[str | None, Field(description="Rule UUID for remove/fire_test")] = None,
    name: Annotated[str | None, Field(description="Human-readable rule name")] = None,
    channel: Annotated[str | None, Field(description="EEG channel or * for average")] = None,
    band: Annotated[
        Literal["delta", "theta", "alpha", "beta", "gamma"] | None,
        Field(description="Frequency band for threshold rule"),
    ] = None,
    operator: Annotated[Literal["gt", "gte", "lt", "lte"] | None, Field(description="Comparison operator")] = None,
    threshold: Annotated[float | None, Field(description="Band power threshold")] = None,
    hold_seconds: Annotated[float, Field(description="Seconds condition must hold before firing")] = 0.5,
    osc_value: Annotated[float, Field(description="Primary OSC payload when rule fires")] = 1.0,
) -> ToolResult:
    """
    OSC triggers for BCI neurofeedback and osc-mcp downstream apps.

    OPERATIONS:
    - send_osc: Fire a one-shot OSC message (VRChat, Reaper, osc-mcp listener).
    - list_rules: List persisted threshold rules.
    - add_rule: Create band-power rule that emits OSC when matched.
    - remove_rule: Delete rule by id.
    - evaluate: Run rules against current stream band power.
    - history: Recent trigger firings.
    - fire_test: Test OSC path for a rule or custom address.

    Default target: 127.0.0.1:9000 (configure osc-mcp or app listener).
    """
    engine = get_trigger_engine()
    mgr = get_board_manager()

    try:
        if operation == "send_osc":
            from openbci_mcp.config import load_settings

            settings = load_settings()
            host = osc_host or settings.osc_host
            port = osc_port or settings.osc_port
            addr = osc_address or "/bci/event"
            return ToolResult(content=send_osc(host, port, addr, osc_values or [1.0]))

        if operation == "list_rules":
            return ToolResult(content={"success": True, "rules": engine.list_rules()})

        if operation == "add_rule":
            if not all([name, channel, band, operator is not None, threshold is not None, osc_address]):
                return _err("add_rule requires name, channel, band, operator, threshold, osc_address")
            return ToolResult(
                content=engine.add_rule(
                    name=name,
                    channel=channel,
                    band=band,
                    operator=operator,
                    threshold=float(threshold),
                    hold_seconds=hold_seconds,
                    osc_address=osc_address,
                    osc_value=osc_value,
                    osc_host=osc_host,
                    osc_port=osc_port,
                )
            )

        if operation == "remove_rule":
            if not rule_id:
                return _err("rule_id required")
            return ToolResult(content=engine.remove_rule(rule_id))

        if operation == "history":
            return ToolResult(content={"success": True, "events": engine.history()})

        if operation == "fire_test":
            return ToolResult(content=engine.fire_test(rule_id=rule_id, address=osc_address, value=osc_value))

        if operation == "evaluate":
            bp = mgr.band_power()
            if not bp.get("success"):
                return ToolResult(content=bp)
            bands = bp.get("bands", {})
            fired = engine.evaluate_bands(bands)
            return ToolResult(content={"success": True, "fired": fired, "bands": bands})

        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        return _err(str(exc))
