---
name: cilium-networking
description: >
  Cilium as cluster CNI, optional LB IPAM / L2 announcements, Gateway API notes,
  and learning-oriented verify steps. Triggers: /cilium, CNI, LoadBalancer IP,
  Hubble, kube-proxy replacement.
version: 1.0.0
---

# Cilium networking (learning lab)

## Why Cilium here

- Real CNI literacy (not “default worked”)
- LB IPAM for LAN Services
- Path to NetworkPolicy + Hubble

## Install

Follow **current** Cilium docs for your k8s/Talos version. Pin Helm chart version.

## Concepts to explain when teaching

| Term | Meaning |
|------|---------|
| Pod CIDR | Address space for pods |
| Service CIDR | ClusterIP range |
| kube-proxy replacement | eBPF datapath |
| LB pool | LAN IPs for type LoadBalancer |

## Verify

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl get nodes -o wide
# cilium status (CLI)
```

## Footguns

- Replacing Cilium with another CNI during upgrades by accepting wrong bootstrap manifests
- Exhausting LB pool
- Expecting LoadBalancer IPs without IPAM/L2 configured
