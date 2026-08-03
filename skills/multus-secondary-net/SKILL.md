---
name: multus-secondary-net
description: >
  Multus CNI for secondary pod interfaces (macvlan NADs on LAN), when to use vs
  ClusterIP/LB VIP, static-IP footguns. Triggers: /multus, macvlan, NetworkAttachmentDefinition,
  secondary NIC, extra interface.
version: 1.0.0
---

# Multus secondary networking

## When to use Multus

| Need | Multus? |
|------|---------|
| Normal app traffic | No — ClusterIP / Gateway |
| Stable LAN VIP for a Service | No — Cilium LB-IPAM |
| Pod must own a **LAN IP on a second NIC** (DNS, special L2) | **Yes** |
| GPU host NIC egress | Sometimes |

Day-1 labs can **skip Multus** entirely.

## Pattern

1. Install Multus DaemonSet (GitOps chart).
2. Create `NetworkAttachmentDefinition` (often macvlan bridge on host NIC).
3. Annotate pod: `k8s.v1.cni.cncf.io/networks: <nad>`.

## NAD roles (examples)

- general macvlan for experimental pods
- DNS-oriented NAD for static addressing
- GPU NIC NAD

Exact `master` interface names differ per node — discover live.

## Footguns

1. Static IP collision → Multus flaps interfaces; pod stuck Init
2. Policy-routing initContainers fighting host routes
3. In-cluster DNS on Multus often more fragile than a **DNS VM outside k8s**
4. Dual Multus installs — keep **one**

## Verify

```bash
kubectl get network-attachment-definitions -A
kubectl get pods -n kube-system | grep -i multus
kubectl describe pod <pod> | grep -i network
```

## Related

`docs/platform/networking-decisions.md` · `skills/cilium-networking/`
