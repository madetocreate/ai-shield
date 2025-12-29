# Guardrails für MCP Tool Calls

## Aktuelle Konfiguration

### Presidio Guardrail

In `config.ai_shield.yaml` ist Presidio konfiguriert:

```yaml
guardrails:
  - guardrail_name: ai-shield-presidio
    litellm_params:
      guardrail: presidio
      mode: [pre_call, post_call]
      default_on: true
      presidio_language: de
      presidio_filter_scope: both  # WICHTIG: Prüft sowohl Input als auch Output
      pii_entities_config:
        CREDIT_CARD: BLOCK
        EMAIL_ADDRESS: MASK
        PHONE_NUMBER: MASK
      presidio_score_thresholds:
        ALL: 0.7
```

**`presidio_filter_scope: both`** bedeutet:
- **pre_call**: Prüft User-Messages UND Tool-Arguments (wenn vorhanden)
- **post_call**: Prüft LLM-Responses UND Tool-Responses (wenn vorhanden)

### Tool Permission Guardrail

```yaml
  - guardrail_name: ai-shield-tool-permission
    litellm_params:
      guardrail: tool_permission
      mode: post_call
      default_on: true
      rules:
        - id: deny_destructive_tools
          tool_name: '(?i).*(delete|remove|drop|destroy|shutdown|wipe|truncate|rm|kill|exec|shell|bash|powershell).*'
          decision: deny
      default_action: allow
      on_disallowed_action: rewrite
      violation_message_template: "Tool '{tool_name}' blocked by AI Shield policy"
```

## MCP Tool Call Protection

### Was wird geschützt?

1. **Tool Arguments (pre_call):**
   - Presidio prüft Tool-Arguments automatisch (via `presidio_filter_scope: both`)
   - PII in Tool-Arguments wird maskiert/blockiert

2. **Tool Responses (post_call):**
   - Presidio prüft Tool-Responses automatisch
   - PII in Tool-Responses wird maskiert/blockiert

3. **Tool Permissions:**
   - Destruktive Tools werden blockiert (via `tool_permission` guardrail)
   - Risky Tools erfordern Approval (via `custom_callbacks.py`)

### Custom Callbacks

`custom_callbacks.py` enthält zusätzliche MCP-Logik:

- **Risky Tool Detection:** Tools mit riskanten Namen erfordern Approval
- **Auto-Approval:** Nur wenn Tool in Allowlist ist
- **MCP Server Registry:** Prüft Server-Konfiguration für Auto-Approval

## Testing

### Test 1: PII in Tool Arguments

```python
# Request mit PII in Tool Arguments
{
  "messages": [...],
  "tools": [{
    "type": "function",
    "function": {
      "name": "send_email",
      "arguments": '{"to": "john@example.com", "body": "Hello"}'
    }
  }]
}

# Erwartet: EMAIL_ADDRESS wird maskiert (z.B. "<EMAIL_ADDRESS>")
```

### Test 2: PII in Tool Response

```python
# Tool Response mit PII
{
  "tool_calls": [{
    "id": "call_123",
    "type": "function",
    "function": {
      "name": "get_contact",
      "arguments": '{"id": "123"}'
    }
  }],
  "tool_responses": [{
    "tool_call_id": "call_123",
    "content": "Contact: john@example.com, Phone: 555-1234"
  }]
}

# Erwartet: PII wird maskiert in Response
```

### Test 3: Destruktive Tool

```python
# Request mit destruktivem Tool
{
  "tools": [{
    "type": "function",
    "function": {
      "name": "delete_file",
      "arguments": '{"path": "/tmp/test.txt"}'
    }
  }]
}

# Erwartet: Tool wird blockiert (via tool_permission guardrail)
```

## Konfiguration

### Policy Presets (`policies/presets.yaml`)

```yaml
presets:
  public_website:
    pii:
      email: mask
      phone: mask
      credit_card: block
    mcp:
      auto_approve_requires_allowlist: true
      risky_tool_name_regex: "(?i)(create|update|delete|remove|drop|send|write|post|put|patch|exec|run|payment|transfer|email)"
```

## Verbesserungen (Optional)

### Expliziter pre_mcp_call Hook

Falls LiteLLM's Presidio nicht automatisch Tool-Arguments prüft, kann ein expliziter Hook hinzugefügt werden:

```python
async def async_pre_mcp_call_hook(
    self,
    tool_name: str,
    tool_args: dict,
    user_api_key_dict: UserAPIKeyAuth,
):
    # Prüfe PII in tool_args
    args_str = json.dumps(tool_args)
    if _find_credit_cards(args_str):
        raise ValueError("Credit card detected in tool arguments")
    
    # Maskiere PII
    masked_args = _mask_text(args_str, email_mode="mask", phone_mode="mask")
    return json.loads(masked_args)
```

**Hinweis:** Aktuell sollte `presidio_filter_scope: both` bereits Tool-Arguments prüfen. Falls nicht, muss dieser Hook implementiert werden.

## Status

✅ **Presidio konfiguriert:** `mode: [pre_call, post_call]`, `presidio_filter_scope: both`  
✅ **Tool Permissions:** Destruktive Tools werden blockiert  
✅ **MCP Approval:** Risky Tools erfordern Approval  
⚠️ **Verifikation nötig:** Testen ob Presidio tatsächlich Tool-Arguments prüft

