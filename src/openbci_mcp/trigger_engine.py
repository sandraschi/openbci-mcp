"""Band-power threshold rules that emit OSC (osc-mcp / VRChat / Reaper targets)."""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from openbci_mcp.config import load_settings
from openbci_mcp.osc_client import send_osc

logger = logging.getLogger(__name__)

BandName = Literal["delta", "theta", "alpha", "beta", "gamma"]
Operator = Literal["gt", "gte", "lt", "lte"]


@dataclass
class TriggerRule:
    id: str
    name: str
    channel: str
    band: BandName
    operator: Operator
    threshold: float
    hold_seconds: float = 0.0
    osc_address: str = "/bci/event"
    osc_value: float = 1.0
    osc_host: str | None = None
    osc_port: int | None = None
    enabled: bool = True
    _above_since: float | None = field(default=None, repr=False)

    def to_public(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("_above_since", None)
        return d


class TriggerEngine:
    _instance: TriggerEngine | None = None
    _lock = threading.RLock()

    def __new__(cls) -> TriggerEngine:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        with self._lock:
            if getattr(self, "_initialized", False):
                return
            self._rules: dict[str, TriggerRule] = {}
            self._history: list[dict[str, Any]] = []
            self._path = self._resolve_path()
            self._load()
            self._initialized = True

    def _resolve_path(self) -> Path:
        import os

        raw = os.getenv("OPENBCI_TRIGGERS_FILE", "")
        if raw:
            return Path(raw)
        return Path.home() / ".openbci-mcp" / "triggers.json"

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            for item in data.get("rules", []):
                rule = TriggerRule(**{k: v for k, v in item.items() if k != "_above_since"})
                self._rules[rule.id] = rule
        except Exception as exc:
            logger.warning("Failed to load triggers: %s", exc)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"rules": [r.to_public() for r in self._rules.values()]}
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_rules(self) -> list[dict[str, Any]]:
        with self._lock:
            return [r.to_public() for r in self._rules.values()]

    def add_rule(self, **kwargs: Any) -> dict[str, Any]:
        with self._lock:
            rule_id = kwargs.pop("id", None) or str(uuid.uuid4())
            rule = TriggerRule(id=rule_id, **kwargs)
            self._rules[rule_id] = rule
            self._save()
            return {"success": True, "rule": rule.to_public()}

    def remove_rule(self, rule_id: str) -> dict[str, Any]:
        with self._lock:
            if rule_id not in self._rules:
                return {"success": False, "error": f"Rule {rule_id!r} not found"}
            removed = self._rules.pop(rule_id).to_public()
            self._save()
            return {"success": True, "removed": removed}

    def clear_history(self) -> dict[str, Any]:
        with self._lock:
            self._history.clear()
            return {"success": True}

    def history(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            return list(reversed(self._history[-limit:]))

    def _compare(self, value: float, op: Operator, threshold: float) -> bool:
        if op == "gt":
            return value > threshold
        if op == "gte":
            return value >= threshold
        if op == "lt":
            return value < threshold
        return value <= threshold

    def _pick_value(self, bands: dict[str, dict[str, float]], rule: TriggerRule) -> float | None:
        if rule.channel == "*":
            vals = [ch.get(rule.band, 0.0) for ch in bands.values()]
            return sum(vals) / len(vals) if vals else None
        ch = bands.get(rule.channel)
        if not ch:
            return None
        return float(ch.get(rule.band, 0.0))

    def evaluate_bands(self, bands: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
        settings = load_settings()
        fired: list[dict[str, Any]] = []
        now = time.time()

        with self._lock:
            for rule in self._rules.values():
                if not rule.enabled:
                    continue
                value = self._pick_value(bands, rule)
                if value is None:
                    rule._above_since = None
                    continue
                matched = self._compare(value, rule.operator, rule.threshold)
                if not matched:
                    rule._above_since = None
                    continue
                if rule._above_since is None:
                    rule._above_since = now
                if now - rule._above_since < rule.hold_seconds:
                    continue

                host = rule.osc_host or settings.osc_host
                port = rule.osc_port or settings.osc_port
                try:
                    result = send_osc(host, port, rule.osc_address, [rule.osc_value, value])
                    event = {
                        "time": now,
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "channel": rule.channel,
                        "band": rule.band,
                        "value": value,
                        "threshold": rule.threshold,
                        "osc": result,
                    }
                    self._history.append(event)
                    fired.append(event)
                    rule._above_since = now
                except Exception as exc:
                    logger.warning("Trigger OSC failed for %s: %s", rule.name, exc)

        return fired

    def fire_test(self, rule_id: str | None = None, address: str | None = None, value: float = 1.0) -> dict[str, Any]:
        settings = load_settings()
        with self._lock:
            if rule_id and rule_id in self._rules:
                rule = self._rules[rule_id]
                return send_osc(
                    rule.osc_host or settings.osc_host,
                    rule.osc_port or settings.osc_port,
                    rule.osc_address,
                    [rule.osc_value, value],
                )
            addr = address or "/bci/test"
            return send_osc(settings.osc_host, settings.osc_port, addr, [value])


def get_trigger_engine() -> TriggerEngine:
    return TriggerEngine()
