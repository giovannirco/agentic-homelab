# Hermes: Proxmox VM vs Kubernetes

A mature agentic lab often runs **both** patterns. They solve different problems.

## Comparison

| | **VM on Proxmox** (homelab fleet) | **Pod on Kubernetes** (tenant agent) |
|--|----------------------------------|--------------------------------------|
| Role | Personal / multi-profile “ops brain” | Company or product-scoped agent |
| Isolation | Whole guest OS | Namespace + RBAC + GitOps |
| Profiles | Many systemd user gateways / profiles | Usually one SOUL + one deploy |
| Disk | Large home (`~/.hermes`) for sessions, MCP venvs | PVC (e.g. 10Gi) under `/opt/data` |
| Chat | Discord/Telegram/WhatsApp on the VM | Optional; often Discord or none day-1 |
| Dashboard | Bind carefully; often LAN only | HTTPRoute **internal Gateway only** |
| GitHub | `gh` + optional App on host | **GitHub App** Secret + token scripts on PVC |
| MCP | Local stdio + HTTP to in-cluster WAHA | HTTP MCP to `waha.<ns>.svc` + stdio on PVC |
| Skills | `~/.hermes/skills` from this repo / homelab-skills | Seeded subset (tenant skills, not full lab dump) |
| When | Learning, multi-channel, heavy tools, SSH | Repeatable tenant stack, Argo-managed |

## Pattern A — Hermes on Proxmox (fleet host)

### Shape

```text
Proxmox
  └── Ubuntu VM (agent host)
        ├── hermes CLI + venv
        ├── systemd --user gateways (default + named profiles)
        ├── ~/.hermes/{SOUL,AGENTS,config,.env,skills,profiles}
        ├── kubectl / gh / omnictl as needed
        └── optional: native WhatsApp session under platforms/
```

### Sizing (starting point)

| Resource | Comfortable |
|----------|-------------|
| vCPU | 4–8 |
| RAM | 6–8 GiB fixed (no balloon reclaim under load) |
| Disk | 40–64 GiB |
| linger | enabled (`loginctl`) so user services survive logout |

### Profile idea

Non-multiplex: each profile has its own gateway unit and `HERMES_HOME` (or profiles dir). One profile owns WhatsApp/dashboard; others are channel-specialized (ops, finance, legal, …).

### Skills install

```bash
git clone https://github.com/giovannirco/agentic-homelab.git
cd agentic-homelab && bash scripts/install-skills.sh --hermes
```

### Secrets

Only on the VM: `~/.hermes/.env`, OAuth tokens, bot tokens. Never in git.

### Legacy note

OpenClaw VMs are a common previous generation. Shared skill/persona layout makes migration to Hermes practical (`hermes claw migrate` when available). Prefer **one primary runtime** per human.

## Pattern B — Hermes on Kubernetes (tenant)

### Shape

```text
platform-gitops/apps/hermes/
  helm values + chart (community Helm; official path is often Docker-only)
  ConfigMap: SOUL seed
  HTTPRoute → envoy-internal only
  PVC → /opt/data
OOB Secrets:
  hermes-*-dashboard-auth
  hermes-*-github-app   (PEM + IDs)
  hermes-*-waha-mcp     (MCP key)
```

### Chart lessons (real deploy footguns)

1. Prefer a chart that keeps image **ENTRYPOINT/s6 init** — do **not** replace with bare `command: ["hermes"]` or the dashboard never starts (Envoy **503**).
2. Use `args: [gateway, run]` (or chart equivalent) with empty command override.
3. Gitignore rules like `**/*secret*.yaml` can block chart templates — force-add templates or rename so Argo gets them.
4. Dashboard basic-auth is mandatory when not loopback-only.
5. Pin image tag explicitly (look up latest stable).

### Wiring

| Concern | Pattern |
|---------|---------|
| Model | Provider OAuth or API key via OOB Secret / envFrom |
| GitHub | App install limited to tenant org; mint installation token in-pod |
| WAHA MCP | `http://waha.<ns>.svc.cluster.local:3000/mcp` + `X-Api-Key` from Secret |
| Exposure | **Internal Gateway only** for company agents |
| RBAC | Prefer Role in tenant namespace over cluster-admin |

### Workspace seed

1. SOUL from ConfigMap (init container overwrite policy).
2. Clone allowed repos with installation token under workspace.
3. `chown` to Hermes UID (chart-specific, often non-root).
4. Tenant skills only — not the entire homelab skill dump.

## Choosing for a new lab

| Goal | Start with |
|------|------------|
| Learn platform + talk to agent on phone | **VM** first |
| Multi-tenant product agents | **k8s** per tenant after GitOps works |
| Both | VM for you; k8s for each “company” stack |

## Related

- Skill: `skills/hermes-agent/`
- WAHA: `docs/agents/waha-and-mcp.md`
- Permissions: `docs/setup/08-wire-agent-permissions.md`
