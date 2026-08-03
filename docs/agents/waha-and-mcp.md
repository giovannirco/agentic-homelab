# WAHA + MCP (agent WhatsApp tools)

WhatsApp for **agents** (Hermes / Grok / others): WAHA (GOWS) exposes an **MCP app**. Chatwoot and other human inboxes are **optional** and out of scope here.

## Roles

| Component | Job |
|-----------|-----|
| **WAHA** (GOWS) | WhatsApp session, HTTP API, **MCP app** |
| **Agent** (Hermes / Grok) | Tools via MCP using the **MCP app key** (`key_…`), not the dashboard API key |

```text
Agent  ──HTTP MCP──►  WAHA /mcp  ──session──►  WhatsApp
                         │
                    dashboard / QR (humans)
```

## Env shape (WAHA)

```yaml
WAHA_APPS_ENABLED: "true"
WAHA_APPS_ON: "mcp"              # add other apps only if you need them
WHATSAPP_DEFAULT_ENGINE: GOWS
REDIS_URL: redis://...
WAHA_API_KEY_PLAIN: <dashboard/api key>
WAHA_PUBLIC_URL: https://waha.example    # humans / QR
WAHA_BASE_URL: http://waha.<ns>.svc.cluster.local:3000   # in-cluster base
```

## MCP app

1. Enable `mcp` in `WAHA_APPS_ON`.
2. Create MCP app on session `default` (dashboard or API).
3. Copy the **app key** (`key_…`) — this is **not** `WAHA_API_KEY_PLAIN`.
4. Store only as **out-of-band Secret** (never git).

```bash
kubectl -n <ns> create secret generic hermes-waha-mcp \
  --from-literal=WAHA_MCP_KEY='key_...' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Hermes config (shape)

```yaml
waha:
  url: "http://waha.<ns>.svc.cluster.local:3000/mcp"
  headers:
    X-Api-Key: "${WAHA_MCP_KEY}"
```

Laptop Grok: HTTP MCP transport + same header (local config only).

### Rotate

1. Delete old MCP app on WAHA; create new one.  
2. Update Secret only.  
3. Restart agent. Old key → 401.

## Pairing

```text
STOPPED → STARTING → SCAN_QR_CODE → WORKING | FAILED
```

- Scan QR from `WAHA_PUBLIC_URL` (or API flow).  
- FAILED → stop/start session; re-scan.  
- History before link is **not** auto-imported.

## Exposure

| Surface | Common choice |
|---------|----------------|
| WAHA dashboard / QR | LAN HTTPS or internal Gateway |
| MCP URL for agents in-cluster | ClusterIP only |
| MCP from laptop | VPN/LAN or carefully scoped access — not public without auth |

Agents in the same cluster should call:

`http://waha.<ns>.svc.cluster.local:3000/mcp`

not the public hostname (tunnel/CF can break or leak).

## Smoke

```bash
curl -sS http://waha.<ns>.svc.cluster.local:3000/ping
# Session WORKING
hermes mcp list
hermes mcp test waha
# Agent tool call that reads recent chats / sends a test (allowlisted)
```

## Media download

Scoped media keys (download-only) are safer to hand to tools than full API keys. Prefer short-lived or media-scoped credentials when the product supports them.

## Related

- Skill: `skills/waha-mcp/`
- Hermes: `docs/agents/hermes-vm-vs-kubernetes.md`
- Secrets: `skills/out-of-band-secrets/`
