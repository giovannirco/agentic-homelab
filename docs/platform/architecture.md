# Target architecture (single-node learning lab)

```text
                         Internet
                             │
                    Cloudflare DNS + Tunnel
                             │
                      cloudflared
                             │
                 Gateway / Service (LAN VIP optional)
                             │
┌────────────────── Kubernetes (Talos single-node) ──────────────────┐
│  Argo CD  ←── git ──  YOURORG/platform-gitops                      │
│  Cilium                                                            │
│  Apps: life-ops, dashboards, bots, …                               │
│  Optional: CNPG / MariaDB operator / Redis                         │
└────────────────────────────────────────────────────────────────────┘
         ▲ kube SA                              ▲
         │                                      │
   Agent VM (Hermes) ◄── GitHub App ── YOURORG
         ▲
    Discord/Telegram/WhatsApp
```

## Components checklist

| Layer | Choice (default here) | Alternatives |
|-------|----------------------|--------------|
| Hypervisor | Proxmox | bare metal Talos only |
| k8s distro | Talos | k3s, kubeadm |
| CNI | Cilium (native routing + kube-proxy replacement) | Calico, Flannel |
| LoadBalancer | Cilium LB-IPAM + L2 Announcement | MetalLB project |
| Secondary NIC | Multus macvlan (optional) | hostNetwork |
| L7 | Envoy Gateway dual (internal + external) | nginx-ingress only |
| GitOps | Argo CD | Flux |
| Edge | Cloudflare Tunnel → external gateway | open home ports |
| DNS LAN | router + optional Technitium | Pi-hole |
| Agent | Hermes VM and/or k8s tenant | OpenClaw legacy |
| Secrets | OOB + private git values | ESO + 1Password (later) |

## Growth path

1. Single-node + tunnel + 3 apps  
2. Operators (DB) + backups  
3. Observability (Grafana + logs)  
4. Second node / Omni  
5. Multi-repo cluster-gitops vs platform-gitops  
6. Multi-tenant org fan-out (advanced)

See also: [networking-decisions.md](networking-decisions.md), [hermes-vm-vs-kubernetes.md](../agents/hermes-vm-vs-kubernetes.md), [waha-and-mcp.md](../agents/waha-and-mcp.md).

Also: [hardware-topologies.md](hardware-topologies.md), [gitops-repo-models.md](gitops-repo-models.md).
