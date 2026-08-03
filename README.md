# agentic-homelab

Opinionated path from a home lab to **platform engineering**, with **AI agents** in the loop.

Build Proxmox → Talos/Kubernetes → GitOps → edge DNS/tunnel → apps, and wire Hermes (or similar) with GitHub + cluster access so work is executed through **skills**, **issues**, and **git** — not ad-hoc kubectl.

## Why this exists

Most tutorials stop at “cluster is up.” Real platform work is the rest: CNI and load balancers, split-horizon DNS, dual GitOps repos, secrets that never land in git, observability that does not eat the node, and agents that must follow runbooks.

This repository is a **quick start + operator handbook** for that stack. Fill in your own CIDRs, domains, and versions; pin latest stable upstream releases when you install.

## Architecture (day-1 shape)

```text
Mini-PC + Proxmox
  ├── VM: Agent (Hermes / OpenClaw)
  ├── VM: Technitium (split-DNS)
  └── VM: Talos (Kubernetes)

GitHub
  ├── cluster-gitops     (infra)
  ├── platform-gitops    (apps)
  └── GitHub App → Agent

Cluster
  ├── Cilium (CNI + LB-IPAM + L2)
  ├── Envoy Gateway (internal + external)
  ├── Argo CD
  ├── external-dns → Cloudflare + Technitium
  └── cloudflared → public edge

Agent skills (this repo) + learning/ops channel
```

**Mental model:** Kubernetes is the *road*. GitOps, ingress, databases, and agents ride on it.

## Start here

| # | Doc | Outcome |
|--:|-----|---------|
| 0 | [docs/00-philosophy.md](docs/00-philosophy.md) | Principles and control loop |
| 1 | [docs/setup/01-shopping-list.md](docs/setup/01-shopping-list.md) | Hardware and accounts |
| 2 | [docs/setup/02-proxmox-base.md](docs/setup/02-proxmox-base.md) | Hypervisor |
| 3 | [docs/setup/03-agent-vm.md](docs/setup/03-agent-vm.md) | Hermes / OpenClaw VM |
| 4 | [docs/setup/04-talos-single-node.md](docs/setup/04-talos-single-node.md) | First Kubernetes node |
| 5 | [docs/setup/05-cilium-and-lb.md](docs/setup/05-cilium-and-lb.md) | CNI + LAN LoadBalancer |
| 6 | [docs/setup/06-gitops-argocd.md](docs/setup/06-gitops-argocd.md) | Argo CD + apps repo |
| 7 | [docs/setup/07-cloudflare-tunnel.md](docs/setup/07-cloudflare-tunnel.md) | Public edge without open ports |
| 8 | [docs/setup/08-wire-agent-permissions.md](docs/setup/08-wire-agent-permissions.md) | GitHub App + cluster access |
| 9 | [docs/setup/09-first-app.md](docs/setup/09-first-app.md) | First GitOps app |
| 10 | [docs/setup/10-learning-board.md](docs/setup/10-learning-board.md) | Issues + project board |
| 11 | [docs/setup/11-technitium-split-dns.md](docs/setup/11-technitium-split-dns.md) | Split-horizon DNS |
| 12 | [docs/setup/12-external-dns.md](docs/setup/12-external-dns.md) | Cloudflare + Technitium automation |
| 13 | [docs/setup/13-observability.md](docs/setup/13-observability.md) | Cloud Free / light / full LGTM |

### Platform reference

| Doc | Topic |
|-----|--------|
| [docs/platform/hardware-topologies.md](docs/platform/hardware-topologies.md) | 1-box · hybrid · HA + Proxmox |
| [docs/platform/gitops-repo-models.md](docs/platform/gitops-repo-models.md) | cluster-gitops vs platform-gitops (simple / multi-org) |
| [docs/platform/networking-decisions.md](docs/platform/networking-decisions.md) | Cilium LB, Multus, dual Gateway |
| [docs/platform/observability-tiers.md](docs/platform/observability-tiers.md) | Observability tier cheat sheet |
| [docs/platform/architecture.md](docs/platform/architecture.md) | Target architecture summary |
| [docs/network/home-network-controllers.md](docs/network/home-network-controllers.md) | UniFi / MikroTik / Omada |
| [docs/agents/](docs/agents/) | Hermes VM vs k8s, WAHA MCP |
| [docs/lessons/hard-won.md](docs/lessons/hard-won.md) | Operational footguns |
| [path/90-day-curriculum.md](path/90-day-curriculum.md) | 90-day progression |
| [docs/MAP.md](docs/MAP.md) | Full doc ↔ skill index |
| [docs/pt/README.md](docs/pt/README.md) | Resumo em português |

## Skills (for agents)

```bash
bash scripts/install-skills.sh          # ~/.grok/skills
bash scripts/install-skills.sh --hermes # ~/.hermes/skills
bash scripts/install-skills.sh --both
```

| Skill | When |
|-------|------|
| `lab-bootstrap` | Stand up Proxmox + Talos + first cluster |
| `onboard-app` | Install or upgrade an app (version pin required) |
| `out-of-band-secrets` | Secrets that must not live in git |
| `gitops-platform` | Argo App-of-Apps / app layout |
| `gitops-repo-models` | Simple vs multi-org repo layout |
| `cilium-networking` | Cilium CNI + LB-IPAM + L2 announcement |
| `multus-secondary-net` | Multus macvlan second NIC |
| `cloudflare-tunnel` | Public exposure via tunnel |
| `technitium-split-dns` | Split-horizon DNS |
| `external-dns` | Cloudflare + RFC2136 → Technitium |
| `home-network-controllers` | UniFi / MikroTik / Omada |
| `hermes-agent` | Hermes on VM or Kubernetes |
| `waha-mcp` | WAHA GOWS + MCP for agents |
| `homelab-databases` | MariaDB / CNPG / Redis |
| `talos-upgrade` | Sequential Talos + Kubernetes upgrades |
| `observability` | Cloud Free, light stack, full LGTM |
| `explain-as-you-go` | Narrate why while executing |

## Templates

- `templates/platform-gitops/` — starter app chart layout  
- `templates/issues/` — install and incident issue bodies  
- `templates/project/` — project board columns  

## Hard rules

1. Prefer **GitOps** over long-lived `kubectl edit` when Argo self-heals.  
2. **Never commit secrets** — out-of-band Secrets + `envFrom`.  
3. **Pin explicit image/chart versions** after looking up latest stable.  
4. **Verify live** before mutating.  
5. **Sequential upgrades** for Talos and Kubernetes minors.  
6. **Never paste secrets** into chat or issue comments.  

## License

See [LICENSE](LICENSE).
