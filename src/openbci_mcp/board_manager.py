"""BrainFlow board session lifecycle and signal helpers."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

try:
    from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams
    from brainflow.data_filter import DataFilter, DetrendOperations

    HAS_BRAINFLOW = True
except ImportError:  # pragma: no cover
    HAS_BRAINFLOW = False
    BoardIds = None  # type: ignore[misc, assignment]
    BoardShim = None  # type: ignore[misc, assignment]
    BrainFlowInputParams = None  # type: ignore[misc, assignment]
    DataFilter = None  # type: ignore[misc, assignment]
    DetrendOperations = None  # type: ignore[misc, assignment]


SUPPORTED_BOARDS: dict[str, dict[str, Any]] = {
    "cyton": {"board_id": 0, "label": "OpenBCI Cyton (8ch EEG)", "connection": "serial"},
    "ganglion": {"board_id": 1, "label": "OpenBCI Ganglion (4ch)", "connection": "ble"},
    "cyton_daisy": {"board_id": 2, "label": "OpenBCI Cyton+Daisy (16ch)", "connection": "serial"},
    "galea": {"board_id": 46, "label": "OpenBCI Galea", "connection": "serial"},
    "synthetic": {"board_id": -1, "label": "BrainFlow Synthetic (dev/test)", "connection": "none"},
    "streaming": {"board_id": -4, "label": "Streaming Board (OpenBCI GUI multicast)", "connection": "udp"},
}


@dataclass
class BoardState:
    connected: bool = False
    streaming: bool = False
    board_key: str | None = None
    board_id: int | None = None
    serial_port: str | None = None
    mac_address: str | None = None
    sampling_rate: int = 0
    num_eeg_channels: int = 0
    eeg_channel_names: list[str] = field(default_factory=list)
    last_error: str | None = None
    stream_started_at: float | None = None


class BoardManager:
    """Thread-safe singleton for one BrainFlow session at a time."""

    _instance: BoardManager | None = None
    _lock = threading.RLock()

    def __new__(cls) -> BoardManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        with self._lock:
            if getattr(self, "_initialized", False):
                return
            self._board: Any = None
            self._state = BoardState()
            self._initialized = True

    @property
    def state(self) -> BoardState:
        with self._lock:
            return BoardState(
                connected=self._state.connected,
                streaming=self._state.streaming,
                board_key=self._state.board_key,
                board_id=self._state.board_id,
                serial_port=self._state.serial_port,
                mac_address=self._state.mac_address,
                sampling_rate=self._state.sampling_rate,
                num_eeg_channels=self._state.num_eeg_channels,
                eeg_channel_names=list(self._state.eeg_channel_names),
                last_error=self._state.last_error,
                stream_started_at=self._state.stream_started_at,
            )

    def _require_brainflow(self) -> None:
        if not HAS_BRAINFLOW:
            raise RuntimeError("brainflow is not installed. Run: uv sync")

    def list_serial_ports(self) -> list[dict[str, str]]:
        ports: list[dict[str, str]] = []
        try:
            import serial.tools.list_ports

            for p in serial.tools.list_ports.comports():
                ports.append({"device": p.device, "description": p.description or "", "hwid": p.hwid or ""})
        except Exception as exc:
            logger.warning("serial port enumeration failed: %s", exc)
        return ports

    def supported_boards(self) -> list[dict[str, Any]]:
        return [{"key": k, **v} for k, v in SUPPORTED_BOARDS.items()]

    def connect(
        self,
        *,
        board_key: str = "cyton",
        serial_port: str | None = None,
        mac_address: str | None = None,
        ip_address: str | None = None,
        ip_port: int | None = None,
        master_board_key: str | None = None,
    ) -> dict[str, Any]:
        self._require_brainflow()
        spec = SUPPORTED_BOARDS.get(board_key)
        if spec is None:
            raise ValueError(f"Unknown board_key {board_key!r}. Use openbci_board(operation='list_boards').")

        with self._lock:
            if self._board is not None:
                self.disconnect()

            board_id = int(spec["board_id"])
            params = BrainFlowInputParams()
            conn = spec["connection"]

            if conn == "serial":
                if not serial_port:
                    raise ValueError("serial_port is required for Cyton/Galea boards (e.g. COM3)")
                params.serial_port = serial_port
            elif conn == "ble":
                if not mac_address:
                    raise ValueError("mac_address is required for Ganglion BLE")
                params.mac_address = mac_address
            elif conn == "udp":
                params.ip_address = ip_address or "225.1.1.1"
                params.ip_port = ip_port or 6677
                master = SUPPORTED_BOARDS.get(master_board_key or "synthetic")
                params.master_board = int(master["board_id"]) if master else BoardIds.SYNTHETIC_BOARD

            BoardShim.enable_board_logger()
            self._board = BoardShim(board_id, params)
            self._board.prepare_session()

            eeg_channels = BoardShim.get_eeg_channels(board_id)
            eeg_names = BoardShim.get_eeg_names(board_id)
            sampling_rate = BoardShim.get_sampling_rate(board_id)

            self._state = BoardState(
                connected=True,
                streaming=False,
                board_key=board_key,
                board_id=board_id,
                serial_port=serial_port,
                mac_address=mac_address,
                sampling_rate=int(sampling_rate),
                num_eeg_channels=len(eeg_channels),
                eeg_channel_names=list(eeg_names),
                last_error=None,
            )
            return self.status_dict()

    def disconnect(self) -> dict[str, Any]:
        with self._lock:
            try:
                if self._board is not None and self._state.streaming:
                    self._board.stop_stream()
            except Exception as exc:
                logger.warning("stop_stream on disconnect: %s", exc)
            try:
                if self._board is not None:
                    self._board.release_session()
            except Exception as exc:
                logger.warning("release_session on disconnect: %s", exc)
            self._board = None
            self._state = BoardState()
            return self.status_dict()

    def start_stream(self, buffer_size: int = 450000) -> dict[str, Any]:
        with self._lock:
            if self._board is None or not self._state.connected:
                raise RuntimeError("Board not connected. Call connect first.")
            if not self._state.streaming:
                self._board.start_stream(buffer_size)
                self._state.streaming = True
                self._state.stream_started_at = time.time()
            return self.status_dict()

    def stop_stream(self) -> dict[str, Any]:
        with self._lock:
            if self._board is not None and self._state.streaming:
                self._board.stop_stream()
                self._state.streaming = False
                self._state.stream_started_at = None
            return self.status_dict()

    def insert_marker(self, marker: str) -> dict[str, Any]:
        with self._lock:
            if self._board is None or not self._state.streaming:
                raise RuntimeError("Stream must be running to insert markers")
            self._board.insert_marker(marker)
            return {"success": True, "marker": marker}

    def get_board_data(self, max_samples: int = 250) -> dict[str, Any]:
        with self._lock:
            if self._board is None:
                raise RuntimeError("Board not connected")
            if not self._state.streaming:
                raise RuntimeError("Stream not started")

            data = self._board.get_board_data()
            if data.size == 0:
                return {
                    "success": True,
                    "samples": 0,
                    "timestamps": [],
                    "channels": {},
                    "sampling_rate": self._state.sampling_rate,
                }

            board_id = int(self._state.board_id or 0)
            eeg_idx = BoardShim.get_eeg_channels(board_id)
            names = self._state.eeg_channel_names or [f"CH{i}" for i in range(len(eeg_idx))]

            # BrainFlow layout: rows are channels, cols are samples (most recent at end)
            if max_samples > 0 and data.shape[1] > max_samples:
                data = data[:, -max_samples:]

            channels: dict[str, list[float]] = {}
            for name, row_idx in zip(names, eeg_idx, strict=False):
                channels[name] = [float(x) for x in data[row_idx].tolist()]

            ts_row = BoardShim.get_timestamp_channel(board_id)
            timestamps = [float(x) for x in data[ts_row].tolist()] if ts_row < data.shape[0] else []

            return {
                "success": True,
                "samples": int(data.shape[1]),
                "timestamps": timestamps,
                "channels": channels,
                "sampling_rate": self._state.sampling_rate,
                "board_key": self._state.board_key,
            }

    def band_power(self, max_samples: int = 256) -> dict[str, Any]:
        payload = self.get_board_data(max_samples=max_samples)
        if payload.get("samples", 0) < 32:
            return {
                "success": False,
                "error": "Not enough samples for band power (need stream running, >=32 samples)",
            }

        board_id = int(self._state.board_id or 0)
        eeg_idx = BoardShim.get_eeg_channels(board_id)
        sampling_rate = self._state.sampling_rate
        bands: dict[str, dict[str, float]] = {}

        with self._lock:
            if self._board is None:
                raise RuntimeError("Board not connected")
            raw = self._board.get_board_data()
            if max_samples > 0 and raw.shape[1] > max_samples:
                raw = raw[:, -max_samples:]

            names = self._state.eeg_channel_names or [f"CH{i}" for i in range(len(eeg_idx))]
            for name, row_idx in zip(names, eeg_idx, strict=False):
                channel_data = raw[row_idx].astype(np.float64)
                DataFilter.detrend(channel_data, DetrendOperations.CONSTANT.value)
                _, _, alpha, beta, gamma = DataFilter.get_avg_band_powers(
                    channel_data,
                    len(channel_data),
                    float(sampling_rate),
                    True,
                )
                theta = DataFilter.get_band_power(
                    channel_data, len(channel_data), float(sampling_rate), 4.0, 8.0, True
                )
                delta = DataFilter.get_band_power(
                    channel_data, len(channel_data), float(sampling_rate), 1.0, 4.0, True
                )
                bands[name] = {
                    "delta": float(delta),
                    "theta": float(theta),
                    "alpha": float(alpha),
                    "beta": float(beta),
                    "gamma": float(gamma),
                }

        return {
            "success": True,
            "bands": bands,
            "sampling_rate": sampling_rate,
            "samples_used": int(raw.shape[1]),
        }

    def apply_filter(
        self,
        *,
        channel_name: str,
        filter_type: str = "bandpass",
        start_freq: float = 8.0,
        stop_freq: float = 30.0,
        max_samples: int = 512,
    ) -> dict[str, Any]:
        with self._lock:
            if self._board is None or not self._state.streaming:
                raise RuntimeError("Board must be connected and streaming")

            board_id = int(self._state.board_id or 0)
            eeg_idx = BoardShim.get_eeg_channels(board_id)
            names = self._state.eeg_channel_names or [f"CH{i}" for i in range(len(eeg_idx))]
            if channel_name not in names:
                raise ValueError(f"Unknown channel {channel_name!r}. Available: {names}")

            row_idx = eeg_idx[names.index(channel_name)]
            raw = self._board.get_board_data()
            if max_samples > 0 and raw.shape[1] > max_samples:
                raw = raw[:, -max_samples:]
            channel_data = raw[row_idx].astype(np.float64).copy()
            sr = float(self._state.sampling_rate)

            DataFilter.detrend(channel_data, DetrendOperations.CONSTANT.value)
            if filter_type == "bandpass":
                DataFilter.perform_bandpass(
                    channel_data, len(channel_data), sr, start_freq, stop_freq, 4, 0, 1
                )
            elif filter_type == "lowpass":
                DataFilter.perform_lowpass(channel_data, len(channel_data), sr, stop_freq, 4, 0, 1)
            elif filter_type == "highpass":
                DataFilter.perform_highpass(channel_data, len(channel_data), sr, start_freq, 4, 0, 1)
            elif filter_type == "notch":
                DataFilter.perform_bandstop(channel_data, len(channel_data), sr, 59.0, 61.0, 4, 0, 1)
            else:
                raise ValueError(f"Unsupported filter_type {filter_type!r}")

            return {
                "success": True,
                "channel": channel_name,
                "filter_type": filter_type,
                "samples": [float(x) for x in channel_data.tolist()],
                "sampling_rate": self._state.sampling_rate,
            }

    def add_streamer(self, streamer_params: str) -> dict[str, Any]:
        """BrainFlow streamer, e.g. file://recording.csv or streaming_board://225.1.1.1:6677."""
        with self._lock:
            if self._board is None:
                raise RuntimeError("Board not connected")
            self._board.add_streamer(streamer_params)
            return {"success": True, "streamer": streamer_params}

    def status_dict(self) -> dict[str, Any]:
        s = self.state
        return {
            "success": True,
            "connected": s.connected,
            "streaming": s.streaming,
            "board_key": s.board_key,
            "board_id": s.board_id,
            "serial_port": s.serial_port,
            "mac_address": s.mac_address,
            "sampling_rate": s.sampling_rate,
            "num_eeg_channels": s.num_eeg_channels,
            "eeg_channel_names": s.eeg_channel_names,
            "last_error": s.last_error,
            "stream_started_at": s.stream_started_at,
        }

    def probe(self, board_key: str = "synthetic") -> dict[str, Any]:
        """Shallow connectivity probe for lifespan startup."""
        try:
            self.connect(board_key=board_key)
            self.start_stream()
            time.sleep(0.5)
            snap = self.get_board_data(max_samples=32)
            self.disconnect()
            return {"success": True, "probe_board": board_key, "samples": snap.get("samples", 0)}
        except Exception as exc:
            self.disconnect()
            return {"success": False, "probe_board": board_key, "error": str(exc)}


def get_board_manager() -> BoardManager:
    return BoardManager()
