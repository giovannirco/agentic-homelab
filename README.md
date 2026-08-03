# agentic-homelab

**AI-first homelab path to platform engineering.**

Build a real lab (Proxmox → Talos/Kubernetes → GitOps → public edge), wire an agent (Hermes / OpenClaw / Grok) with GitHub + cluster access, and use **skills + issues** so the agent *explains while it builds*. Compress months of trial-and-error into a guided weeks-long path.

This repo is **generic and shareable**: no personal IPs, no private orgs, no secrets. Patterns come from production homelab work, rewritten as templates.

## Who this is for

- Friends and peers learning **DevOps / platform engineering**
- People who want **agent-assisted** ops (Discord, WhatsApp, laptop IDE agents)
- Anyone building a **single-node** lab first, with a clear path to multi-node later

## The idea in one diagram

```text
Mini-PC + Proxmox
  ├── VM: Agent (Hermes / OpenClaw)  ← Discord/WhatsApp/Telegram
  └── VM: Talos (Kubernetes node)
Laptop agent (Grok / Claude / Cursor)
  └── bootstraps cluster + GitOps

GitHub Org
  ├── platform-gitops   (desired state)
  ├── lab-notes         (issues + board + lessons)
  └── GitHub App PEM → Agent

Cluster SA / kubeconfig → Agent
Cilium + LoadBalancer path
Cloudflare Tunnel + domain
Skills: how to run apps safely

Learning channel: "I'm learning platform"
Issues: one install = one issue with full context
Apps: shopping list, bots, whatever you care about
```

**Mental model:** Kubernetes is the *road*. GitOps, canary, blue/green, ingress, databases ride on it. The agent is a force multiplier — not a substitute for understanding.

## Start here

| Order | Doc | What you get |
|------:|-----|--------------|
| 0 | [docs/00-philosophy.md](docs/00-philosophy.md) | Why this path works for careers |
| 1 | [docs/setup/01-shopping-list.md](docs/setup/01-shopping-list.md) | Hardware, accounts, domain |
| 2 | [docs/setup/02-proxmox-base.md](docs/setup/02-proxmox-base.md) | Hypervisor base |
| 3 | [docs/setup/03-agent-vm.md](docs/setup/03-agent-vm.md) | Hermes/OpenClaw VM |
| 4 | [docs/setup/04-talos-single-node.md](docs/setup/04-talos-single-node.md) | First Kubernetes node |
| 5 | [docs/setup/05-cilium-and-lb.md](docs/setup/05-cilium-and-lb.md) | CNI + LAN LB |
| 6 | [docs/setup/06-gitops-argocd.md](docs/setup/06-gitops-argocd.md) | Argo CD + platform-gitops |
| 7 | [docs/setup/07-cloudflare-tunnel.md](docs/setup/07-cloudflare-tunnel.md) | Public secure ingress |
| 8 | [docs/setup/08-wire-agent-permissions.md](docs/setup/08-wire-agent-permissions.md) | GH App + k8s SA |
| 9 | [docs/setup/09-first-app.md](docs/setup/09-first-app.md) | First GitOps app end-to-end |
| 10 | [docs/setup/10-learning-board.md](docs/setup/10-learning-board.md) | Issues + Projects as curriculum |
| — | [path/90-day-curriculum.md](path/90-day-curriculum.md) | Career-shaped progression |
| — | [docs/lessons/hard-won.md](docs/lessons/hard-won.md) | Footguns from real ops |
| — | [docs/agents/hermes-and-openclaw.md](docs/agents/hermes-and-openclaw.md) | Agent fleet patterns |

## Skills (install for agents)

```bash
bash scripts/install-skills.sh          # → ~/.grok/skills
bash scripts/install-skills.sh --hermes # → ~/.hermes/skills
bash scripts/install-skills.sh --both
```

| Skill | Use when |
|-------|----------|
| `lab-bootstrap` | Standing up Proxmox + Talos + first cluster |
| `onboard-app` | Installing/upgrading any app (version pin mandatory) |
| `out-of-band-secrets` | Secrets that must never live in git |
| `gitops-platform` | Argo App-of-Apps / platform-gitops layout |
| `cilium-networking` | CNI, LB IPAM, Gateway API basics |
| `cloudflare-tunnel` | Public exposure without opening home ports |
| `hermes-agent` | Hermes install, GH App, MCP, workspace |
| `homelab-databases` | MariaDB / CNPG / Redis single vs multi |
| `talos-upgrade` | Sequential Talos + k8s upgrades |
| `explain-as-you-go` | Teach while executing (learning channel) |

## Templates

- `templates/platform-gitops/` — minimal App-of-Apps style app folder
- `templates/issues/` — issue bodies for installs and incidents
- `templates/project/` — suggested GitHub Project columns

## Hard rules (everyone)

1. **Prefer GitOps** over long-lived `kubectl edit` (selfHeal reverts bare mutations).
2. **Never commit secrets.** Use out-of-band Secrets + envFrom.
3. **Pin explicit image/chart versions** — look up latest stable; never invent tags.
4. **Verify live before mutate.**
5. **Sequential upgrades** for control planes (Talos minors, k8s minors).
6. **Do not paste secrets** into Discord, WhatsApp, or issue comments.

## Language

Docs are **English-first** (shareable, interview-ready). Skills are English. You can add `docs/pt/` later for Portuguese narratives.

## What this is not

- Not a dump of anyone’s production cluster state
- Not multi-tenant company stacks (that’s an advanced chapter later)
- Not a substitute for reading upstream Talos / Cilium / Argo docs

## License

Private repository. Share access with friends intentionally.
