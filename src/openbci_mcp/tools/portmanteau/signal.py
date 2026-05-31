"""OpenBCI signal processing portmanteau."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from openbci_mcp.board_manager import get_board_manager
from openbci_mcp.mcp_app import mcp


def _err(message: str) -> ToolResult:
    return ToolResult(content={"success": False, "error": message}, is_error=True)


@mcp.tool(version="1.0.0")
async def openbci_signal(
    operation: Annotated[
        Literal["band_power", "filter"],
        Field(description="Signal processing operation."),
    ],
    channel_name: Annotated[str | None, Field(description="EEG channel name for filter op")] = None,
    filter_type: Annotated[
        Literal["bandpass", "lowpass", "highpass", "notch"],
        Field(description="Filter type for filter operation"),
    ] = "bandpass",
    start_freq: Annotated[float, Field(description="High-pass / bandpass start Hz")] = 8.0,
    stop_freq: Annotated[float, Field(description="Low-pass / bandpass stop Hz")] = 30.0,
    max_samples: Annotated[int, Field(ge=32, le=5000)] = 256,
) -> ToolResult:
    """
    Real-time EEG signal analysis via BrainFlow DataFilter.

    OPERATIONS:
    - band_power: Delta/theta/alpha/beta/gamma per channel from latest buffer.
    - filter: Apply bandpass, lowpass, highpass, or 60Hz notch to one channel.
    """
    mgr = get_board_manager()
    try:
        if operation == "band_power":
            return ToolResult(content=mgr.band_power(max_samples=max_samples))
        if operation == "filter":
            if not channel_name:
                st = mgr.status_dict()
                names = st.get("eeg_channel_names") or []
                return _err(f"channel_name required. Connected channels: {names}")
            return ToolResult(
                content=mgr.apply_filter(
                    channel_name=channel_name,
                    filter_type=filter_type,
                    start_freq=start_freq,
                    stop_freq=stop_freq,
                    max_samples=max_samples,
                )
            )
        return _err(f"Unknown operation {operation!r}")
    except Exception as exc:
        return _err(str(exc))
