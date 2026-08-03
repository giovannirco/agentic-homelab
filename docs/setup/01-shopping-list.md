# 01 — Shopping list

## Hardware (minimum viable)

| Item | Guidance |
|------|----------|
| Mini-PC / NUC / small tower | 6+ cores, **32 GB RAM** preferred (16 GB bare minimum) |
| NVMe SSD | 512 GB+ for OS + VMs + local PVCs |
| Optional second disk | Media / backups later |
| Wired Ethernet | Prefer 2.5 GbE if possible; Wi‑Fi only for learning (not stable lab) |
| UPS | Optional but recommended once stateful |

## Accounts & free tiers

| Account | Why |
|---------|-----|
| **GitHub** | GitOps repos + Projects + optional GitHub App for agent |
| **Cloudflare** | DNS + Tunnel (free tier is enough to start) |
| **Domain** | Any registrar; point nameservers to Cloudflare |
| **Discord / Telegram / WhatsApp** | Agent chat surface (pick one for day 1) |
| LLM access | ChatGPT Plus (Codex OAuth), xAI, Anthropic, local Ollama — pick one primary |

## Software you will install (high level)

1. Proxmox VE on the box  
2. Ubuntu (or similar) VM for **agent**  
3. **Talos Linux** VM for Kubernetes  
4. **Cilium** as CNI  
5. **Argo CD**  
6. **cloudflared** (tunnel)  
7. Optional: Technitium or Pi-hole for LAN DNS later  

## Network plan (fill your own)

Use private RFC1918 ranges. Example placeholders — **replace with yours**:

| Role | Example placeholder |
|------|---------------------|
| LAN subnet | `10.0.0.0/24` |
| Proxmox host | `10.0.0.10` |
| Agent VM | `10.0.0.20` |
| Talos node | `10.0.0.30` |
| K8s API | node IP or VIP later |
| LB pool (Cilium/MetalLB) | e.g. `10.0.0.200–10.0.0.220` |

Write this in your private notes repo; **do not** commit real topology if the repo is shared widely.

## GitHub org recommendation

Create a **new GitHub organization** for the lab (not personal username clutter):

- `YOURORG/platform-gitops` — desired state
- `YOURORG/lab-notes` or use this curriculum as notes
- `YOURORG` GitHub App for the agent

Orgs make GitHub Apps, Projects, and team invites cleaner.

## Budget sketch

| Tier | Rough cost |
|------|------------|
| Used mini-PC | low–mid |
| Domain / year | low |
| Cloudflare free | $0 |
| Electricity | continuous |
| LLM subscription | optional |

## Done when

- [ ] Hardware powered and networked  
- [ ] GitHub org created  
- [ ] Domain on Cloudflare  
- [ ] Chat channel ready for the agent  
- [ ] Password manager ready for secrets (1Password, Bitwarden, …)  
