---
name: talos-upgrade
description: >
  Sequential Talos + Kubernetes upgrades: compatibility gates, one minor at a time,
  CNI bootstrap caution, verify steps. Triggers: /talos-upgrade, upgrade Kubernetes,
  upgrade Talos, sequential minors.
version: 1.0.0
---

# Talos + Kubernetes upgrades

## Absolute rules

1. Walk **Talos minors** (no 1.11 → 1.13 direct)  
2. Walk **k8s minors** one at a time  
3. Talos version gates max k8s in catalogs (check live docs/Omni)  
4. Prefer Omni template sync if Omni manages machines; else talosctl carefully  
5. After k8s bumps, **diff bootstrap manifests** — do not replace Cilium  

## Example path shape

```text
Talos patch → k8s patch on same minor
→ Talos next minor → k8s next minor
→ repeat
```

## Prerequisites

- [ ] Nodes Ready  
- [ ] etcd healthy / backup understood  
- [ ] Maintenance window  
- [ ] CNI is Cilium (or known)  

## Verify each phase

```bash
kubectl get nodes -o wide
kubectl get pods -A | grep -v Running | grep -v Completed || true
kubectl get --raw /healthz?verbose | head
```

## Do not

- Skip minors  
- Upgrade during storage/network incident  
- Blindly accept conflicting CNI manifests  
