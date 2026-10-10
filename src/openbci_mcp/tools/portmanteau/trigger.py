"""OSC trigger rules portmanteau (pairs with osc-mcp targets)."""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp
from openbci_mcp.osc_client import send_osc
from openbci_mcp.trigger_engine import get_trigger_engine

logger = logging.getLogger(__name__)


def _err(message: str) -> ToolResult:
    return ToolResult(content={"success": False, "error": message, "message": message}, is_error=True)


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

    TIMING (issue #1): live rules are evaluated on a FIXED 10 Hz hop, not on
    BrainFlow's native packet cadence. The ``/api/ws/eeg`` loop sleeps 0.1 s,
    snapshots <=64 samples, computes band power over <=128 samples, and calls
    ``TriggerEngine.evaluate_bands``. A rule fires only after its condition
    holds continuously for ``hold_seconds``; after firing, the hold timer
    resets, so the minimum retrigger interval is also ``hold_seconds``.
    ``evaluate`` runs the same engine once, on demand, against the current
    snapshot — use it for reproducible, agent-driven event streams.

    ## Return Format
    ``{"success": bool, "message": str, ...operation payload}`` — every success
    carries a human-readable ``message``; failures carry ``error``.

    ## Examples
    ``openbci_trigger(operation="list_rules")`` -> ``{"success": True, "rules": [...]}``
    ``openbci_trigger(operation="send_osc", osc_address="/bci/focus", osc_values=[1.0])`` -> one-shot fire.
    ``openbci_trigger(operation="add_rule", name="focus", channel="*", band="beta", operator="gt", threshold=2.5, osc_address="/bci/focus")`` -> persisted rule.
    """

    def _ok(message: str, **payload: object) -> ToolResult:
        return ToolResult(content={"success": True, "message": message, **payload})

    engine = get_trigger_engine()
    mgr = get_board_manager()

    try:
        if operation == "send_osc":
            from openbci_mcp.config import load_settings

            settings = load_settings()
            host = osc_host or settings.osc_host
            port = osc_port or settings.osc_port
            addr = osc_address or "/bci/event"
            result = send_osc(host, port, addr, osc_values or [1.0])
            return _ok(f"OSC sent to {host}:{port} {addr}", **result)

        if operation == "list_rules":
            rules = engine.list_rules()
            return _ok(f"{len(rules)} rules", rules=rules)

        if operation == "add_rule":
            if not all([name, channel, band, operator is not None, threshold is not None, osc_address]):
                return _err("add_rule requires name, channel, band, operator, threshold, osc_address")
            result = engine.add_rule(
                name=name,
                channel=channel,
                band=band,
                operator=operator,
                threshold=float(threshold),  # type: ignore[arg-type]
                hold_seconds=hold_seconds,
                osc_address=osc_address,
                osc_value=osc_value,
                osc_host=osc_host,
                osc_port=osc_port,
            )
            rule = result.get("rule", {})
            return _ok(f"Rule {rule.get('name', name)!r} added", **result)

        if operation == "remove_rule":
            if not rule_id:
                return _err("rule_id required")
            result = engine.remove_rule(rule_id)
            if not result.get("success"):
                return _err(str(result.get("error", "remove failed")))
            return _ok(f"Rule {rule_id} removed", **result)

        if operation == "history":
            events = engine.history()
            return _ok(f"{len(events)} events", events=events)

        if operation == "fire_test":
            result = engine.fire_test(rule_id=rule_id, address=osc_address, value=osc_value)
            return _ok("Test OSC sent", **result)

        if operation == "evaluate":
            bp = mgr.band_power()
            if not bp.get("success"):
                return ToolResult(content={**bp, "message": str(bp.get("error", "band_power failed"))})
            bands = bp.get("bands", {})
            fired = engine.evaluate_bands(bands)
            return _ok(f"{len(fired)} triggers fired", fired=fired, bands=bands)

        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        logger.exception("openbci_trigger failed")
        return _err(str(exc))
