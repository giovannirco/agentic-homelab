# Philosophy: agentic homelab → platform engineer

## Kubernetes is the road

Kubernetes is not the destination. It is the **road** you build so you can run:

- GitOps (Argo CD / Flux)
- Progressive delivery (canary, blue/green)
- Gateways, DNS, certificates
- Databases, queues, observability
- Agents that can safely change the system

If you only “install k3s and a few Helm charts,” you practice *ops*. If you wire **desired state in git**, **edge exposure**, **identity**, and **an agent that must explain itself**, you practice *platform engineering*.

## AI is a multiplier, not a substitute

A good setup:

1. You choose architecture and constraints.
2. The agent executes bootstrap and app installs against **skills** (runbooks).
3. Every non-trivial step becomes a **GitHub issue** with context.
4. The agent narrates *why* (learning channel / Discord / WhatsApp).

Bad setup: agent with cluster-admin and no skills → silent drift and unexplainable breakage.

## The control loop

```text
Issue (what) → Skill (how) → Git commit (desired state) → Argo (reconcile)
     ↑                                                      │
     └────────── verify + note / lesson ────────────────────┘
```

Your “homelab notes” repo is portfolio material later (blog, interview stories). Your `platform-gitops` repo is the real product.

## Single-node first

Start with:

- One mini-PC (or small tower) + Proxmox
- One Talos VM (or bare metal later)
- One agent VM
- One domain on Cloudflare

Omni (Sidero control plane of control planes), multi-node HA, multi-tenant orgs are **later chapters**. Single-node teaches 90% of the concepts without the blast radius.

## Career mapping

| Lab activity | Interview language |
|--------------|-------------------|
| Argo App-of-Apps | “I designed a multi-app GitOps topology” |
| Cilium + LB IPAM | “I chose CNI and service exposure deliberately” |
| Cloudflare Tunnel + Gateway API | “I exposed apps without port-forwarding home WAN” |
| CNPG / Galera recipes | “I provisioned databases with operators and backups” |
| Out-of-band secrets | “I kept secrets out of git and rotation-friendly” |
| Agent + GH App | “I automated ops with least-privilege automation identity” |
| Issue board + postmortems | “I ran my lab like a product team” |

## Compressing time

Without structure, a serious lab is months of thrash. With:

- ordered docs
- version-pin policy
- skills for agents
- issues as work packages

…you can stand a *credible* platform core in **days to weeks**, then spend months **deepening** (storage, HA, multi-tenant, observability). Depth is optional; the skeleton is not.

## What we refuse

- Floating `latest` tags in GitOps
- Secrets in git “just for now”
- kubectl scale as permanent state
- Skipping CNI learning because “default worked”
- Pasting PEMs into chat
