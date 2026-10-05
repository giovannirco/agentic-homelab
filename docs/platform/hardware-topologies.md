# Hardware topologies (pick your scale)

Same software path, different boxes. Choose by budget and how much HA you need **now**.

## Topology A — Single Proxmox (everything)

**Best for:** first agentic lab, one mini-PC/NUC.

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

**A common real-world B:** a low-power mini PC as the always-on **utility host** (UniFi/network controller VM, 2× DNS LXCs, Home Assistant VM, an agent LXC, a speedtest) plus a **GPU tower** as the single Talos node. Watch the mini PC's RAM (16 GB fills up fast) and its PSU (throttle heavy I/O). The NAS can serve both an old and a new network during a migration (two NICs, static routes for the new ranges).

> **What happened to this plan (2026-10):** an earlier version of this page said single-node Rook-Ceph on the GPU tower was viable for block, file and S3 on day one. It was planned and never built. The tower turned out to have less usable RAM than planned and a small system disk, and it became a **worker** instead (Topology D). Models and caches went to the NAS. If you want S3 on one node, a single-binary object store is a smaller commitment than Ceph.

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

## Topology D — one big hypervisor for clusters, a bare-metal GPU worker, a utility host

**Best for:** learning cluster shapes cheaply, plus local AI. This is what a lab grows into when a second-hand server with a lot of RAM appears.

```text
┌─ Utility host (mini PC) ─┐   ┌─ Big hypervisor (many cores, 128 GB) ─┐   ┌─ GPU tower (bare metal) ─┐
│  network controller        │   │  lab cluster A: 1 CP + 1 worker        │   │  Talos worker of cluster A │
│  DNS ×2, netboot           │   │  lab cluster B: 3 CP + 1 worker        │   │  2 GPUs, models on the NAS │
│  Omni, agent, printing…    │   │  lab cluster C: 1 CP + 2 workers       │   └────────────────────────────┘
└────────────────────────────┘   └────────────────────────────────────────┘
        Omni owns every machine · machines enrol by netboot · templates in git
```

| Pros | Cons |
|------|------|
| Clusters are built and destroyed in minutes | One hypervisor is one failure domain: these are labs, not production |
| The GPU box can be opened or re-imaged without losing a control plane | Needs a netboot path and Omni ([omni-and-netboot](omni-and-netboot.md)) |
| Control planes are cheap as VMs (2 vCPU / 4 GB each) | etcd shares the hypervisor's disk: use a real SSD pool with an ARC cap if ZFS |

**GitOps:** one fleet repo for the platform layer of every cluster, per-cluster overlays, app repos on top.

## Decision guide

| Constraint | Pick |
|------------|------|
| One box only | **A** |
| Have a second PC/server | **B** |
| Three+ identical boxes + utility | **C** |
| Want Omni day 1 | **C** (or B with Omni on Proxmox + 1 node — limited value) |
| Learning only | **A**, upgrade path documented |
| A big second-hand server + a GPU box | **D** |
| Thinking about three small PCs for HA | **C**, after reading [disk-and-etcd-health.md](disk-and-etcd-health.md): the disks decide whether it feels stable |

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

Before planning around any second-hand box: [know-your-hardware.md](know-your-hardware.md).
