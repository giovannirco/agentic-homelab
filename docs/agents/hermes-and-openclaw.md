# Hermes, OpenClaw, and agent fleets

## Mental model

```text
Human chat (Discord / Telegram / WhatsApp)
        ↓
Agent runtime (Hermes or OpenClaw)
        ↓
Skills (SKILL.md runbooks) + tools (gh, kubectl, MCP)
        ↓
GitHub (desired state) + Kubernetes (live state)
```

## Hermes (recommended baseline)

Typical paths:

| Path | Use |
|------|-----|
| `~/.hermes/SOUL.md` | Personality |
| `~/.hermes/AGENTS.md` | Hard rules |
| `~/.hermes/USER.md` | Human profile |
| `~/.hermes/skills/` | Installed skills |
| `~/.hermes/config.yaml` | Model, channels |
| `~/.hermes/.env` | Secrets (never git) |

### LLM providers

- OAuth “Codex” style subscriptions (no raw OpenAI key)
- API keys via env
- Local models (Ollama) for offline/low-stakes

### Channels

Start with **one** channel. Allowlist user IDs. Add WhatsApp via bridges (e.g. WAHA) only after basics work.

## OpenClaw

Older / parallel agent stack:

- Workspace under `~/.openclaw/workspace/`
- Gateway process (systemd user service common)
- Skills under workspace skills/
- Same idea: persona MD + tools + chat

If both exist in a household, **pick one primary** per human to avoid split brain.

## In-cluster Hermes (advanced)

Pattern used in multi-tenant labs:

1. Helm chart deploys Hermes in a namespace.
2. OOB Secrets: dashboard auth, GitHub App PEM, WAHA MCP key.
3. `extraEnvFrom` wires secrets.
4. HTTPRoute **internal only** for dashboard.
5. Workspace PVC seeded with SOUL + cloned repos via installation token.
6. RBAC limited to tenant namespace when possible.

See skill `hermes-agent`.

## MCP

Model Context Protocol servers give tools:

| Type | Example |
|------|---------|
| stdio | local CLI MCP packages on the agent host |
| HTTP | WAHA `/mcp` with `X-Api-Key` |

Rotate MCP keys by recreating the app and updating only the Secret.

## Skills install

```bash
git clone <this-repo-url>
cd agentic-homelab
bash scripts/install-skills.sh --hermes
```

## SOUL.md starter principles

- Be direct and useful
- Prefer GitOps
- Never dump secrets in chat
- Explain why when user is learning
- Ask before destructive or third-party messaging

## What good looks like

- Human: “Install ntfy on the lab”
- Agent: opens issue, checks latest tag, commits Helm chart, waits Argo, comments URL + first login, explains storage choice in learning channel
