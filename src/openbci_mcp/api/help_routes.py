"""Serve bundled documentation markdown for the webapp Help page."""

from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

_PKG = Path(__file__).resolve().parents[1]
_REPO_ROOT = _PKG.parents[1]
_DOCS = _REPO_ROOT / "docs"
_BUNDLED = _PKG / "bundled_docs"

DOC_INDEX: dict[str, str] = {
    "overview": "README.md",
    "install": "INSTALL.md",
    "scenarios": "USAGE_SCENARIOS.md",
    "wearable": "WEARABLE_STYLING.md",
    "neurofeedback": "NEUROFEEDBACK.md",
    "bci_control": "BCI_CONTROL.md",
    "vr_creative": "VR_CREATIVE.md",
    "hybrid_emg": "HYBRID_EMG_EEG.md",
    "configuration": "CONFIGURATION.md",
    "tools": "TOOLS.md",
    "development": "DEVELOPMENT.md",
    "troubleshooting": "TROUBLESHOOTING.md",
    "osc": "OSC_INTEGRATION.md",
    "skill": "SKILL.md",
}


def _resolve_doc_path(doc_id: str) -> Path | None:
    filename = DOC_INDEX.get(doc_id)
    if not filename:
        return None
    if doc_id == "skill":
        skill = _PKG / "skills" / "openbci" / "SKILL.md"
        return skill if skill.is_file() else None
    if doc_id in {"overview", "install"}:
        root_file = _REPO_ROOT / filename
        if root_file.is_file():
            return root_file
    bundled = _BUNDLED / filename
    if bundled.is_file():
        return bundled
    repo_doc = _DOCS / filename
    if repo_doc.is_file():
        return repo_doc
    return None


async def api_help_index(_: Request) -> JSONResponse:
    available = [doc_id for doc_id in DOC_INDEX if _resolve_doc_path(doc_id) is not None]
    return JSONResponse(
        {
            "success": True,
            "docs": available,
            "labels": {
                "overview": "Overview",
                "install": "Install",
                "scenarios": "All usage scenarios",
                "wearable": "Wearable and helmet styling",
                "neurofeedback": "Alpha and neurofeedback",
                "bci_control": "Mouse and BCI control",
                "vr_creative": "VR and live performance",
                "hybrid_emg": "EMG + EEG hybrid",
                "configuration": "Configuration",
                "tools": "MCP Tools",
                "development": "Development",
                "troubleshooting": "Troubleshooting",
                "osc": "OSC Integration",
                "skill": "Agent Skill",
            },
            "webapp_port": 10758,
            "backend_port": 10759,
        }
    )


async def api_help_doc(request: Request) -> JSONResponse:
    doc_id = request.path_params.get("doc_id", "overview")
    path = _resolve_doc_path(doc_id)
    if path is None:
        return JSONResponse({"success": False, "error": f"Unknown doc {doc_id!r}"}, status_code=404)
    return JSONResponse(
        {
            "success": True,
            "id": doc_id,
            "title": DOC_INDEX.get(doc_id, doc_id),
            "markdown": path.read_text(encoding="utf-8"),
            "path": str(path),
        }
    )
