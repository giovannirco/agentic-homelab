---
name: waha-mcp
description: >
  WAHA (GOWS) WhatsApp HTTP API with MCP app for Hermes/Grok agents. Pairing,
  ClusterIP MCP URL, OOB MCP keys, rotate. Chatwoot and other inboxes are out of
  scope. Triggers: /waha-mcp, WAHA MCP, WhatsApp agent, GOWS, SCAN_QR_CODE.
version: 1.0.0
---

# WAHA + MCP (agents)

Full write-up: `docs/agents/waha-and-mcp.md`.

## Scope

**In:** WAHA session, MCP app, agent wiring.  
**Out:** Chatwoot, other CRM inboxes, marketing automation.

## Non-negotiables

1. MCP key (`key_…`) is **OOB Secret**, never git.  
2. In-cluster agents use **ClusterIP** MCP URL.  
3. Engine: **GOWS** unless you have a reason otherwise.  
4. Dashboard API key ≠ MCP app key.

## Wire Hermes

```yaml
waha:
  url: "http://waha.<ns>.svc.cluster.local:3000/mcp"
  headers:
    X-Api-Key: "${WAHA_MCP_KEY}"
```

## Pairing

Session → `WORKING` via QR. Pre-link history not imported.

## Rotate MCP key

Delete MCP app → create → update Secret → restart agent.

## Smoke

```bash
curl -sS http://waha.<ns>.svc.cluster.local:3000/ping
hermes mcp test waha
```
