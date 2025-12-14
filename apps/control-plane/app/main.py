import os
import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

DATA_DIR = Path(os.environ.get("CONTROL_PLANE_DATA_DIR", "/app/data"))
REGISTRY_PATH = Path(os.environ.get("CONTROL_PLANE_REGISTRY_PATH", str(DATA_DIR / "mcp_registry.json")))

GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL", "http://gateway:4000").rstrip("/")
GATEWAY_ADMIN_KEY = os.environ.get("GATEWAY_ADMIN_KEY", "")
ADMIN_KEY = os.environ.get("CONTROL_PLANE_ADMIN_KEY", "")

TOOL_CAT_DANGEROUS = re.compile(r"(?i)\b(delete|remove|drop|destroy|revoke|shutdown|terminate|kill|rm|wipe)\b")
TOOL_CAT_WRITE = re.compile(r"(?i)\b(create|update|set|write|send|post|put|patch|run|exec|apply|deploy|transfer|charge|payment)\b")
TOOL_POISON = re.compile(r"(?i)(ignore\s+previous|system\s+prompt|do\s+not\s+tell|exfiltrat|secret|apikey|token|credential)")

class MCPServerIn(BaseModel):
    server_id: str = Field(..., min_length=2, max_length=64)
    url: str = Field(..., min_length=4, max_length=2048)
    transport: str = Field("streamable_http")
    auth_type: str = Field("none")
    headers: Dict[str, str] = Field(default_factory=dict)
    preset: str = Field("read_only")

class MCPPinResult(BaseModel):
    server_id: str
    pinned_tools_hash: str
    tool_count: int
    pinned_at: str

def _require_admin(x_ai_shield_admin_key: Optional[str]):
    if not ADMIN_KEY:
        raise HTTPException(status_code=500, detail="CONTROL_PLANE_ADMIN_KEY not set")
    if not x_ai_shield_admin_key or x_ai_shield_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="unauthorized")

def _load_registry() -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text(json.dumps({"servers": {}}, indent=2) + "\n", encoding="utf-8")
    try:
        obj = json.loads(REGISTRY_PATH.read_text(encoding="utf-8") or "{}")
    except Exception:
        obj = {"servers": {}}
    if not isinstance(obj, dict):
        obj = {"servers": {}}
    if "servers" not in obj or not isinstance(obj["servers"], dict):
        obj["servers"] = {}
    return obj

def _save_registry(obj: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(REGISTRY_PATH)

def _sha256_canonical(obj: Any) -> str:
    b = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def _classify_tool(name: str, description: str) -> str:
    if TOOL_POISON.search(description or ""):
        return "dangerous"
    if TOOL_CAT_DANGEROUS.search(name or ""):
        return "dangerous"
    if TOOL_CAT_WRITE.search(name or ""):
        return "write"
    return "read"

async def _gateway_get_tools(server_id: str) -> Any:
    if not GATEWAY_ADMIN_KEY:
        raise HTTPException(status_code=500, detail="GATEWAY_ADMIN_KEY not set")
    url = f"{GATEWAY_BASE_URL}/mcp-rest/tools/list"
    headers = {"Authorization": f"Bearer {GATEWAY_ADMIN_KEY}", "x-litellm-api-key": GATEWAY_ADMIN_KEY}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, params={"server_id": server_id}, headers=headers)
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail={"gateway_status": r.status_code, "gateway_body": r.text})
        try:
            return r.json()
        except Exception:
            raise HTTPException(status_code=502, detail="gateway returned non-json")

def _extract_tools(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        for k in ("tools", "data", "result"):
            v = payload.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        if "result" in payload and isinstance(payload["result"], dict):
            v = payload["result"].get("tools")
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return []

def _allowed_params_from_tool(tool: Dict[str, Any]) -> Optional[List[str]]:
    schema = tool.get("inputSchema")
    if not isinstance(schema, dict):
        return None
    props = schema.get("properties")
    if not isinstance(props, dict):
        return None
    return [str(k) for k in props.keys()]

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/v1/mcp/registry")
def get_registry(x_ai_shield_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_ai_shield_admin_key)
    return _load_registry()

@app.post("/v1/mcp/registry")
def upsert_registry(server: MCPServerIn, x_ai_shield_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_ai_shield_admin_key)
    reg = _load_registry()
    prev = reg["servers"].get(server.server_id, {})
    reg["servers"][server.server_id] = {
        "server_id": server.server_id,
        "url": server.url,
        "transport": server.transport,
        "auth_type": server.auth_type,
        "headers": server.headers,
        "preset": server.preset,
        "pinned_tools_hash": prev.get("pinned_tools_hash"),
        "auto_approve_tools": prev.get("auto_approve_tools", []),
        "hitl_tools": prev.get("hitl_tools", []),
        "allowed_params": prev.get("allowed_params", {}),
        "tool_categories": prev.get("tool_categories", {}),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_registry(reg)
    return {"ok": True, "server_id": server.server_id}

@app.post("/v1/mcp/pin/{server_id}", response_model=MCPPinResult)
async def pin_server(server_id: str, x_ai_shield_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_ai_shield_admin_key)
    reg = _load_registry()
    if server_id not in reg["servers"]:
        raise HTTPException(status_code=404, detail="server_id not found in registry")
    payload = await _gateway_get_tools(server_id)
    tools = _extract_tools(payload)
    pinned_hash = _sha256_canonical(tools)
    cats: Dict[str, str] = {}
    allowed_params: Dict[str, List[str]] = {}
    auto_approve: List[str] = []
    hitl: List[str] = []
    for t in tools:
        name = str(t.get("name") or "")
        desc = str(t.get("description") or "")
        if not name:
            continue
        cat = _classify_tool(name, desc)
        cats[name] = cat
        ap = _allowed_params_from_tool(t)
        if isinstance(ap, list):
            allowed_params[name] = ap
        if cat == "read":
            auto_approve.append(name)
        else:
            hitl.append(name)
    reg["servers"][server_id]["pinned_tools_hash"] = pinned_hash
    reg["servers"][server_id]["tool_categories"] = cats
    reg["servers"][server_id]["allowed_params"] = allowed_params
    reg["servers"][server_id]["auto_approve_tools"] = auto_approve
    reg["servers"][server_id]["hitl_tools"] = hitl
    reg["servers"][server_id]["pinned_at"] = datetime.now(timezone.utc).isoformat()
    _save_registry(reg)
    return MCPPinResult(server_id=server_id, pinned_tools_hash=pinned_hash, tool_count=len(tools), pinned_at=reg["servers"][server_id]["pinned_at"])

@app.get("/v1/mcp/litellm-snippet")
def litellm_snippet(x_ai_shield_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_ai_shield_admin_key)
    reg = _load_registry()
    lines: List[str] = []
    lines.append("mcp_servers:")
    for sid, s in reg["servers"].items():
        lines.append(f"  {sid}:")
        lines.append(f"    url: \"{s.get('url','')}\"")
        lines.append(f"    transport: \"{s.get('transport','streamable_http')}\"")
        lines.append(f"    auth_type: \"{s.get('auth_type','none')}\"")
        hdrs = s.get("headers") or {}
        if isinstance(hdrs, dict) and len(hdrs) > 0:
            lines.append("    headers:")
            for hk, hv in hdrs.items():
                lines.append(f"      {hk}: \"{hv}\"")
        cats = s.get("tool_categories") or {}
        preset = str(s.get("preset") or "read_only")
        if isinstance(cats, dict) and len(cats) > 0:
            if preset == "read_only":
                allowed = [k for k, v in cats.items() if v == "read"]
                disallowed = [k for k, v in cats.items() if v != "read"]
            else:
                allowed = [k for k, v in cats.items() if v != "dangerous"]
                disallowed = [k for k, v in cats.items() if v == "dangerous"]
            if allowed:
                lines.append("    allowed_tools:")
                for t in sorted(allowed):
                    lines.append(f"      - \"{t}\"")
            if disallowed:
                lines.append("    disallowed_tools:")
                for t in sorted(disallowed):
                    lines.append(f"      - \"{t}\"")
        ap = s.get("allowed_params") or {}
        if isinstance(ap, dict) and len(ap) > 0:
            lines.append("    allowed_params:")
            for tool_name, params in ap.items():
                if not isinstance(params, list):
                    continue
                lines.append(f"      {tool_name}:")
                for p in params:
                    lines.append(f"        - \"{p}\"")
    return {"yaml": "\n".join(lines) + "\n"}
