import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple

import requests


def _sha256(obj: Any) -> str:
    b = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def _suspicious_tool(tool: Dict[str, Any]) -> Tuple[bool, str]:
    txt = ""
    if isinstance(tool.get("description"), str):
        txt += tool["description"]
    if isinstance(tool.get("name"), str):
        txt += " " + tool["name"]
    low = txt.lower()
    signals = [
        "ignore previous",
        "ignore all instructions",
        "system prompt",
        "developer message",
        "exfiltrate",
        "secret",
        "api key",
    ]
    for s in signals:
        if s in low:
            return True, s
    return False, ""


def fetch_tools(url: str, spec_version: str, origin: Optional[str]) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": spec_version,
            "capabilities": {},
            "clientInfo": {"name": "ai-shield", "version": "0.1.0"},
        },
    }
    if origin:
        headers["Origin"] = origin
    r1 = requests.post(url, headers=headers, json=init_req, timeout=20)
    r1.raise_for_status()
    session_id = r1.headers.get("Mcp-Session-Id") or r1.headers.get("mcp-session-id")
    if not session_id:
        raise RuntimeError("Kein Mcp-Session-Id Header erhalten")
    headers2 = dict(headers)
    headers2["Mcp-Session-Id"] = session_id
    headers2["MCP-Protocol-Version"] = spec_version

    notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
    r2 = requests.post(url, headers=headers2, json=notif, timeout=20)
    r2.raise_for_status()

    tools_list = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    r3 = requests.post(url, headers=headers2, json=tools_list, timeout=20)
    r3.raise_for_status()
    obj = r3.json()
    if not isinstance(obj, dict) or "result" not in obj:
        raise RuntimeError("Unerwartete tools/list Response")
    return {"session_id": session_id, "result": obj["result"]}


def load_pins(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--spec-version", default=os.environ.get("MCP_SPEC_VERSION", "2025-06-18"))
    ap.add_argument("--origin", default=os.environ.get("MCP_ORIGIN"))
    ap.add_argument("--pins", default=None)
    args = ap.parse_args()

    data = fetch_tools(url=args.url, spec_version=args.spec_version, origin=args.origin)
    result = data["result"]
    manifest_hash = _sha256(result)

    tools = []
    if isinstance(result, dict) and isinstance(result.get("tools"), list):
        tools = [t for t in result["tools"] if isinstance(t, dict)]

    suspicious = []
    for t in tools:
        bad, why = _suspicious_tool(t)
        if bad:
            suspicious.append({"name": t.get("name"), "reason": why})

    out = {
        "url": args.url,
        "spec_version": args.spec_version,
        "manifest_sha256": manifest_hash,
        "tool_count": len(tools),
        "suspicious_tools": suspicious,
    }

    if args.pins:
        pins = load_pins(args.pins)
        expected = None
        if isinstance(pins, dict) and isinstance(pins.get("servers"), list):
            for s in pins["servers"]:
                if isinstance(s, dict) and s.get("url") == args.url and s.get("spec_version", args.spec_version) == args.spec_version:
                    expected = s.get("manifest_sha256")
                    break
        if expected and expected != manifest_hash:
            out["pin_check"] = "mismatch"
            out["expected_sha256"] = expected
            print(json.dumps(out, ensure_ascii=False))
            return 2
        out["pin_check"] = "ok" if expected else "no_pin"

    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
