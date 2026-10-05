---
name: lab-bootstrap
description: >
  Bootstrap an agentic homelab: Proxmox, agent VM, Talos, Cilium, Argo CD,
  Cloudflare Tunnel, Technitium split-DNS, external-dns, agent GH App + kube
  access, first app, observability tier. Triggers: /lab-bootstrap, new lab,
  first cluster, setup homelab, start from zero.
version: 1.2.0
---

# Lab bootstrap

Follow `docs/setup/01` through `docs/setup/13` for the topology in use
(`docs/platform/hardware-topologies.md`).

## Default order (Topology A — single Proxmox)

1. Shopping list (hardware, domain, GitHub org, chat)
2. Proxmox installed and updated
3. Agent VM with Hermes/OpenClaw + skills from this repo
4. Talos single-node Ready
5. Cilium CNI + LB-IPAM/L2 pool
6. Argo CD + cluster-gitops / platform-gitops model
7. Technitium split-DNS + client DHCP/DNS path
8. Cloudflare Tunnel + dual external-dns (public + private)
9. Wire GitHub App + Kubernetes access into the agent
10. First app via GitOps
11. Observability Tier 0 (Cloud Free) or Tier 1 light stack
12. Issue board for remaining work

## Later chapters (only when asked)

- More than one cluster, or machines that change roles → `omni-netboot` (`docs/platform/omni-and-netboot.md`)
- LoadBalancer IPs over BGP → `cilium-networking` (`docs/platform/loadbalancer-l2-vs-bgp.md`)
- A GPU node for local AI → `local-ai-gpu-node`
- Second-hand hardware → audit it first (`docs/platform/know-your-hardware.md`)
- Work that spans hours → `long-session-goal`

## Agent behavior

- Prefer GitOps and skills over ad-hoc cluster edits.
- After each major step: verify + short issue comment.
- Never invent IPs or domains — ask or use documented examples.
- Report numbers only from logs; label an unmeasured explanation as a hypothesis.
- Use `explain-as-you-go` when the operator wants guided narration.

## Verify skeleton

```bash
kubectl get nodes
kubectl get pods -A | head
kubectl get applications -n argocd 2>/dev/null || true
bash scripts/verify-lab.sh
```

## Stop conditions

- Node NotReady without a recovery plan
- Talos secrets about to be committed to git
- Secrets about to land in git — use out-of-band Secrets
