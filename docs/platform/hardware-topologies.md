# Hardware topologies (pick your scale)

Same software path, different boxes. Choose by budget and how much HA you need **now**.

## Topology A — Single Proxmox (everything)

**Best for:** first agentic lab, friends learning, one mini-PC/NUC.

```text
┌──────────── One mini-PC / tower ────────────┐
│  Proxmox VE                                   │
│   ├── VM: Hermes agent                        │
│   ├── VM: Talos (single-node k8s)             │
│   ├── VM: Technitium primary (DNS)            │
│   └── optional: cloudflared or run in k8s     │
└───────────────────────────────────────────────┘
        │
   Home router / UniFi / MikroTik / Omada
```

| Pros | Cons |
|------|------|
| Cheap, simple, one UPS | No HA; reboot takes lab down |
| Easy snapshots | CPU/RAM contention |
| Enough to learn full stack | Storage is single disk risk |

**GitOps:** start with **one** `platform-gitops` (or even monorepo). Omni optional later.

## Topology B — Proxmox + bare-metal Talos

**Best for:** more CPU for apps without starving hypervisor; still one “control” box.

```text
┌── Server 1: Proxmox ──┐     ┌── Server 2: bare metal ──┐
│  Hermes VM              │     │  Talos (k8s node)         │
│  Technitium DNS         │     │  (or multi-disk worker)   │
│  Omni LXC (optional)    │     └───────────────────────────┘
│  light utility VMs      │
└─────────────────────────┘
```

| Pros | Cons |
|------|------|
| k8s has dedicated hardware | Two machines to power/network |
| Proxmox still hosts agents/DNS | Still single k8s node unless you grow |

**GitOps:** `cluster-gitops` + one `platform-gitops` recommended once Argo is stable.

## Topology C — HA Talos (3× bare metal) + separate Proxmox

**Best for:** serious lab / “platform-shaped” production mimic. Matches a mature homelab shape.

```text
┌─ Proxmox (utility) ─┐     ┌─ Talos CP/worker ─┐
│  Omni (optional)      │     │  node-01            │
│  Technitium ×1–2      │     ├─ Talos CP/worker ─┤
│  Hermes fleet VM      │     │  node-02            │
│  backups / PBS later  │     ├─ Talos CP/worker ─┤
└───────────────────────┘     │  node-03            │
                              └────────────────────┘
         Omni manages machines; Argo manages apps
```

| Pros | Cons |
|------|------|
| Real control-plane HA | Cost, power, noise |
| Omni upgrades / machine inventory shine | More networking discipline |
| Room for strict-local storage rules | Complexity for beginners |

**GitOps:** full **cluster-gitops + multi platform-gitops** (or multi-org) pattern.

## Decision guide

| Constraint | Pick |
|------------|------|
| One box only | **A** |
| Have a second PC/server | **B** |
| Three+ identical boxes + utility | **C** |
| Want Omni day 1 | **C** (or B with Omni on Proxmox + 1 node — limited value) |
| Learning only | **A**, upgrade path documented |

## Shared requirements (all topologies)

- Wired Ethernet preferred  
- DHCP reservations or statics for infrastructure  
- Free IP range for Cilium LB pool (not in DHCP)  
- Domain on Cloudflare (or similar) for public path  
- Password manager for secrets  

## Related

- [gitops-repo-models.md](gitops-repo-models.md)  
- [home-network-controllers.md](../network/home-network-controllers.md)  
- Setup: `docs/setup/02-proxmox-base.md`, `04-talos-single-node.md`

Observability pressure by topology: [observability-tiers.md](observability-tiers.md).
