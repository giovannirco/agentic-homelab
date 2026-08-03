# WAHA + Chatwoot + agent MCP

Reference integration pattern for WhatsApp in a GitOps lab. **No personal hostnames** — use your domains and namespaces.

## Roles

| Component | Job |
|-----------|-----|
| **WAHA** (GOWS engine) | WhatsApp session, HTTP API, optional MCP app |
| **Chatwoot** | Human inbox / CRM UI |
| **Hermes / Grok** | Agent tools via WAHA **MCP** key (not the dashboard API key) |

## Critical wiring rule

**Service-to-service must use ClusterIP DNS**, not public hostnames.

| Direction | Prefer | Avoid |
|-----------|--------|--------|
| WAHA → Chatwoot API | `http://chatwoot.<ns>.svc.cluster.local:3000` | Public URL (Cloudflare often **400** from pods) |
| Chatwoot → WAHA webhooks | `http://waha.<ns>.svc.cluster.local:3000/webhooks/...` | Public webhook when both in-cluster |
| Humans / QR | LAN or public HTTPS dashboard | — |

```text
WAHA_PUBLIC_URL  = human-facing dashboard URL
WAHA_BASE_URL    = http://waha.<ns>.svc.cluster.local:3000
```

## WAHA env (shape)

```yaml
WAHA_APPS_ENABLED: "true"
WAHA_APPS_ON: "chatwoot,mcp"
WHATSAPP_DEFAULT_ENGINE: GOWS
REDIS_URL: redis://...
WAHA_API_KEY_PLAIN: <plain>
WAHA_PUBLIC_URL: https://waha.example
WAHA_BASE_URL: http://waha.<ns>.svc.cluster.local:3000
```

## Chatwoot app on WAHA

Create via dashboard or `POST /api/apps` with **ClusterIP** `config.url`. After create, set inbox `webhook_url` to ClusterIP path including session + app id.

### Conversation mode sync

| Mode | Chatwoot | WAHA conversations |
|------|----------|--------------------|
| Single thread (WhatsApp-like) | Lock to single conversation ON | `sort: created_newest`, `status: null` |
| Multi | Lock OFF | activity_newest + open/pending/snoozed |

Mismatch → confusing reopen behavior.

## Exposure choices

| App | Common choice |
|-----|----------------|
| WAHA dashboard | Internal-only **or** public (QR needs human access) |
| Chatwoot | Public + internal OK for humans |
| Integrations | Always ClusterIP |

## MCP for agents

1. Enable `mcp` in `WAHA_APPS_ON`.
2. Create MCP app on session `default` → copy **`key_…`** (app key).
3. Store in OOB Secret; wire Hermes `extraEnvFrom` / Grok config header `X-Api-Key`.
4. Rotate: delete MCP app → create new → update Secret only → restart Hermes.

Never commit MCP keys to git.

## Pairing

```text
STOPPED → STARTING → SCAN_QR_CODE → WORKING | FAILED
```

- FAILED → stop/start; re-scan  
- History before link is not auto-imported  

## Failure: app create 500 / custom_attribute 400

Often **not** Chatwoot schema — WAHA called **public** Chatwoot and got CF 400.

Fix: ClusterIP URL in app config; recreate/PUT app.

## Smoke

```bash
curl -sS http://waha.<ns>.svc.cluster.local:3000/ping
# Chatwoot webhook POST → 201
hermes mcp test waha-<name>
# Send WhatsApp message → conversation appears
```

## Related

Skill `skills/waha-chatwoot/` · Hermes skill · `out-of-band-secrets`
