"""Local LLM provider status and chat bridge."""

from __future__ import annotations

from typing import Any

import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse

from openbci_mcp.activity_log import log_activity


async def api_llm_providers(_: Request) -> JSONResponse:
    providers = []
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://127.0.0.1:11434/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                providers.append(
                    {
                        "id": "ollama",
                        "label": "Ollama",
                        "type": "ollama",
                        "base_url": "http://127.0.0.1:11434/v1",
                        "models": models,
                        "needs_key": False,
                        "reachable": True,
                    }
                )
    except Exception:
        providers.append(
            {
                "id": "ollama",
                "label": "Ollama",
                "type": "ollama",
                "base_url": "http://127.0.0.1:11434/v1",
                "models": [],
                "needs_key": False,
                "reachable": False,
            }
        )
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://127.0.0.1:1234/v1/models")
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                providers.append(
                    {
                        "id": "lmstudio",
                        "label": "LM Studio",
                        "type": "lmstudio",
                        "base_url": "http://127.0.0.1:1234/v1",
                        "models": models,
                        "needs_key": False,
                        "reachable": True,
                    }
                )
    except Exception:
        providers.append(
            {
                "id": "lmstudio",
                "label": "LM Studio",
                "type": "lmstudio",
                "base_url": "http://127.0.0.1:1234/v1",
                "models": [],
                "needs_key": False,
                "reachable": False,
            }
        )
    return JSONResponse({"success": True, "providers": providers})


async def api_ai_chat(request: Request) -> JSONResponse:
    try:
        body: dict[str, Any] = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "invalid JSON"}, status_code=400)

    message = str(body.get("message", "")).strip()
    if not message:
        return JSONResponse({"success": False, "error": "message required"}, status_code=400)

    provider = str(body.get("provider") or "ollama")
    model = str(body.get("model") or "llama3.2")
    endpoint = str(body.get("endpoint") or "http://127.0.0.1:11434").rstrip("/")

    try:
        if provider == "ollama":
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{endpoint}/api/generate",
                    json={"model": model, "prompt": message, "stream": False},
                )
                response.raise_for_status()
                text = response.json().get("response", "No response from Ollama")
        elif provider == "lmstudio":
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{endpoint}/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": message}],
                        "model": model,
                        "temperature": 0.7,
                    },
                )
                response.raise_for_status()
                text = response.json()["choices"][0]["message"]["content"]
        else:
            return JSONResponse({"success": False, "error": f"unsupported provider {provider!r}"}, status_code=400)

        log_activity("tool_call", f"ai/chat via {provider}", meta={"model": model})
        return JSONResponse({"response": text, "tool_calls": []})
    except Exception as exc:
        log_activity("server", f"AI bridge error: {exc}", level="ERROR")
        return JSONResponse({"response": f"AI Bridge Error: {exc}", "tool_calls": []})
