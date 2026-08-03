# 03 — Agent VM (Hermes / OpenClaw)

## Goal

A small always-on Linux VM where your agent lives:

- Chat: Discord, Telegram, WhatsApp (pick one first)
- Tools: `gh`, `kubectl`, `git`, optional MCP servers
- Skills: this repo’s `skills/` installed into the agent skill path

## Hermes vs OpenClaw

| | Hermes | OpenClaw |
|--|--------|----------|
| Layout | `~/.hermes/` (`SOUL.md`, `AGENTS.md`, `skills/`) | `~/.openclaw/` (similar workspace files) |
| Migration | `hermes claw migrate` can import OpenClaw persona/skills | Source for older installs |
| Skills | `skills/<name>/SKILL.md` | Same idea |
| k8s deploy | Helm chart exists for multi-tenant fleets | Often VM/systemd gateway |

**Recommendation for new labs:** start with **Hermes** (or the agent you already use). Personality files (`SOUL.md`, `USER.md`, `AGENTS.md`) matter more than the brand.

## VM sizing

| Resource | Day 1 | Comfortable |
|----------|-------|-------------|
| vCPU | 2–4 | 4–8 |
| RAM | 4 GiB | 6–8 GiB |
| Disk | 40 GiB | 80 GiB+ if many sessions |

## OS bootstrap

```bash
# Ubuntu 24.04 example
sudo apt update && sudo apt install -y git curl jq unzip
# Install gh, kubectl, docker (optional), python3
```

## Install agent (conceptual)

Follow **current upstream** Hermes/OpenClaw install docs (they change). Typical shape:

1. Install binary or pip/npm package.
2. `hermes onboard` / equivalent.
3. Configure LLM provider (OAuth or API key in **env file**, not git).
4. Connect one chat channel with **allowlists**.
5. Clone this repo; run `bash scripts/install-skills.sh --hermes`.

## Persona files (minimum)

| File | Purpose |
|------|---------|
| `SOUL.md` | Tone and boundaries |
| `USER.md` | Who the human is, timezone, prefs |
| `AGENTS.md` | Hard rules for this lab (copy/adapt root AGENTS.md) |
| `MEMORY.md` | Long-term notes the agent may update |

**Rule:** agent must **ask** before messaging third parties, deleting data, or spending money.

## Day-1 permissions (temporary)

Early on, the agent may need broad access to bootstrap. Document that you will **reduce** to:

- GitHub App (only lab repos)
- Kubernetes Role in one namespace (then expand)

See [08-wire-agent-permissions.md](08-wire-agent-permissions.md).

## OpenClaw → Hermes (if migrating)

Shared conventions make migration easy:

- Same skill layout
- Similar SOUL/AGENTS/USER files
- Prefer official migrator when available
- Rotate chat bot tokens during cutover
- Do not migrate huge caches/venvs — reinstall

## Security

- Bind admin UIs to LAN or tunnel + auth, not open WAN.
- No secrets in Discord/WhatsApp replies.
- Prefer Media-only / scoped API keys for bridges (e.g. WAHA MCP keys out-of-band).

## Done when

- [ ] You can chat with the agent from your phone  
- [ ] Agent can run `gh auth status` (or will after step 08)  
- [ ] Skills from this repo are installed  
- [ ] SOUL/USER/AGENTS present  
