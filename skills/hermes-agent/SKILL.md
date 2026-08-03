---
name: hermes-agent
description: >
  Hermes Agent on Proxmox VM (multi-profile fleet) or Kubernetes (tenant GitOps):
  SOUL/skills, GitHub App, MCP (including WAHA), dashboard, s6 entrypoint footguns,
  OpenClaw migration. Triggers: /hermes-agent, Hermes, OpenClaw, SOUL.md, gateway run,
  hermes k8s, hermes VM.
version: 1.1.0
---

# Hermes agent

Full dual-path write-up: `docs/agents/hermes-vm-vs-kubernetes.md`.

## VM fleet (day-1 learning)

1. Ubuntu VM on Proxmox (6–8G RAM, linger on)
2. Install Hermes per upstream; `hermes update`
3. One chat channel + allowlist
4. `bash scripts/install-skills.sh --hermes`
5. SOUL / USER / AGENTS present; secrets in `~/.hermes/.env` only

Optional: multiple profiles = multiple user systemd gateways (non-multiplex).

## Kubernetes tenant (after GitOps)

1. App under `platform-gitops/apps/hermes/`
2. Chart: community Helm that preserves image init/s6; pin image
3. PVC for `/opt/data`; internal HTTPRoute only
4. OOB Secrets: dashboard auth, GitHub App PEM, WAHA MCP key via `extraEnvFrom`
5. Do not override ENTRYPOINT with bare `hermes` — use gateway args only

### GitHub App verify

```bash
kubectl -n <ns> exec deploy/<hermes> -- sh -c 'echo $GITHUB_APP_ID; /opt/data/bin/github-app-token | wc -c'
```

### MCP

```bash
kubectl -n <ns> exec deploy/<hermes> -- hermes mcp list
kubectl -n <ns> exec deploy/<hermes> -- hermes mcp test waha-<name>
```

HTTP MCP example:

```yaml
waha-tenant:
  url: "http://waha.<ns>.svc.cluster.local:3000/mcp"
  headers:
    X-Api-Key: "${WAHA_MCP_KEY}"
```

## Hard rules

- Never paste secrets into Discord/WhatsApp
- Prefer GitOps for k8s agents
- Scope GH App to lab/tenant repos only
- Explain-as-you-go in learning mode
