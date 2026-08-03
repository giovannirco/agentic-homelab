---
name: waha-chatwoot
description: >
  Wire WAHA (GOWS) to Chatwoot with ClusterIP integrations, optional public dashboards,
  conversation mode sync, MCP keys for Hermes/Grok. Triggers: /waha-chatwoot, WAHA,
  Chatwoot WhatsApp, SCAN_QR_CODE, WAHA MCP, GOWS.
version: 1.0.0
---

# WAHA + Chatwoot

Full write-up: `docs/agents/waha-and-chatwoot.md`.

## Non-negotiables

1. WAHA↔Chatwoot use **ClusterIP**, not public hostnames.
2. MCP app key is **OOB Secret**, never git.
3. Align Chatwoot “single conversation” lock with WAHA conversation sort/status.
4. Engine: GOWS unless you have a reason otherwise.

## Create Chatwoot app (shape)

```json
{
  "session": "default",
  "app": "chatwoot",
  "config": {
    "url": "http://chatwoot.<ns>.svc.cluster.local:3000",
    "accountId": 1,
    "accountToken": "<admin PAT>",
    "inboxId": 1,
    "inboxIdentifier": "<from inbox>",
    "locale": "pt-BR",
    "conversations": { "sort": "created_newest", "status": null, "markAsRead": true }
  },
  "enabled": true
}
```

## MCP for Hermes

```yaml
waha-<name>:
  url: "http://waha.<ns>.svc.cluster.local:3000/mcp"
  headers:
    X-Api-Key: "${WAHA_MCP_KEY}"
```

## Pairing

Session → WORKING via QR on `WAHA_PUBLIC_URL`. History pre-link not imported.

## Debug public-URL failures

```bash
# From WAHA pod — public may 400
curl -sk -H "api_access_token: $TOKEN" https://chatwoot.example/api/v1/profile
# ClusterIP works
curl -sS -H "api_access_token: $TOKEN" http://chatwoot.<ns>.svc.cluster.local:3000/api/v1/profile
```
