"""Fleet SOTA: auto-discover Ollama and LM Studio on startup."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LLMManager:
    """Track reachable local inference endpoints."""

    def __init__(self) -> None:
        self.providers: dict[str, dict[str, Any]] = {}

    def register(self, provider_type: str, base_url: str, *, models: list[str] | None = None) -> None:
        self.providers[provider_type] = {
            "type": provider_type,
            "base_url": base_url,
            "models": models or [],
            "reachable": True,
        }
        logger.info("LLM glom: registered %s at %s", provider_type, base_url)

    def list_providers(self) -> list[dict[str, Any]]:
        return list(self.providers.values())

    async def glom_local_providers_if_up(self) -> None:
        if os.getenv("OPENBCI_MCP_LLM_GLOM", "1").strip().lower() in ("0", "false", "no", "off"):
            return
        timeout = httpx.Timeout(2.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if "ollama" not in self.providers:
                try:
                    response = await client.get("http://127.0.0.1:11434/api/tags")
                    if response.status_code == 200:
                        payload = response.json()
                        models = [m.get("name", "") for m in payload.get("models", []) if m.get("name")]
                        self.register("ollama", "http://127.0.0.1:11434", models=models)
                except Exception:
                    logger.debug("LLM glom: Ollama not reachable", exc_info=True)
            if "lmstudio" not in self.providers:
                try:
                    response = await client.get("http://127.0.0.1:1234/v1/models")
                    if response.status_code == 200:
                        payload = response.json()
                        models = [m.get("id", "") for m in payload.get("data", []) if m.get("id")]
                        self.register("lmstudio", "http://127.0.0.1:1234", models=models)
                except Exception:
                    logger.debug("LLM glom: LM Studio not reachable", exc_info=True)


_llm_manager: LLMManager | None = None


def get_llm_manager() -> LLMManager:
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
