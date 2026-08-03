---
name: hermes-agent
description: >
  Operate Hermes Agent (VM or Kubernetes): persona files, skills install, GitHub
  App tokens, MCP servers, channel allowlists, OpenClaw migration notes. Triggers:
  /hermes-agent, Hermes, OpenClaw, SOUL.md, WAHA MCP, github-app-token.
version: 1.0.0
---

# Hermes agent (lab)

## VM install (day 1)

1. Ubuntu VM with enough RAM  
2. Install Hermes per upstream docs  
3. Configure LLM provider in config/env  
4. Connect one chat channel with allowlist  
5. `bash scripts/install-skills.sh --hermes` from agentic-homelab  
6. Write SOUL / USER / AGENTS  

## GitHub App

Env or Secret keys:

- `GITHUB_APP_ID`
- `GITHUB_APP_INSTALLATION_ID`
- `GITHUB_APP_PRIVATE_KEY` (PEM)

Mint installation token → `GH_TOKEN` for `gh`.

## MCP

- HTTP MCP (e.g. WAHA): URL + `X-Api-Key` from OOB Secret  
- stdio MCP: binaries on PATH or PVC  

```bash
hermes mcp list
hermes mcp test <name>
```

## Kubernetes deploy (advanced)

- Helm chart for Hermes  
- `extraEnvFrom` for OOB secrets  
- Internal-only dashboard HTTPRoute  
- Namespace-scoped RBAC when possible  
- Workspace PVC: SOUL seed + repo clones  

## OpenClaw migration

Shared skill layout and persona MD names. Prefer official migrator. Rotate bot tokens. Do not copy venv/cache.

## Hard rules

- Never paste secrets into Discord/WhatsApp  
- Prefer GitOps  
- Explain-as-you-go in learning mode  
