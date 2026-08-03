---
name: cilium-networking
description: >
  Cilium as cluster CNI with kube-proxy replacement, Cilium LB-IPAM + L2
  Announcement for Service type LoadBalancer (not MetalLB), Gateway notes.
  Triggers: /cilium, CNI, LoadBalancer IP, LB-IPAM, L2 announcement, Hubble.
version: 1.1.0
---

# Cilium networking

## Defaults this skill encodes

1. **CNI = Cilium** (prefer over default flannel-style bootstrap).
2. **LoadBalancer IPs = Cilium LB-IPAM**, not the MetalLB project.
3. **Advertise VIPs on LAN = Cilium L2 Announcement** on host interfaces.
4. Pin fixed VIPs with annotations `lbipam.cilium.io/ips` + `lbipam.cilium.io/ip-pool`.

## Install

Follow current Cilium docs for your k8s/Talos version. Pin Helm chart.

```bash
helm repo add cilium https://helm.cilium.io/
# helm upgrade --install cilium cilium/cilium -n kube-system --version <PIN>
```

Enable features per docs for your version: kube-proxy replacement, LB IPAM, L2 announcements.

## Pool + L2 (required for LAN VIPs)

```yaml
# CiliumLoadBalancerIPPool — DHCP-excluded CIDR on YOUR LAN
# CiliumL2AnnouncementPolicy — interfaces regex matching node NICs
```

See `docs/platform/networking-decisions.md` for full examples.

## Fixed VIP on a Service

```yaml
metadata:
  annotations:
    lbipam.cilium.io/ips: "<VIP>"
    lbipam.cilium.io/ip-pool: servers-pool
spec:
  type: LoadBalancer
```

## Concepts to teach

| Term | Meaning |
|------|---------|
| Pod CIDR | Pod address space (native routing or tunnel) |
| Service CIDR | ClusterIP range |
| LB pool | LAN addresses for type LoadBalancer |
| L2 announce | ARP so LAN hosts reach the VIP |

## Verify

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
kubectl get svc -A --field-selector spec.type=LoadBalancer
# From another LAN host: ping <VIP>
```

## Footguns

- Exhausting the pool or overlapping DHCP
- Wrong interface regex → no ARP, VIP unreachable
- Accepting bootstrap CNI that replaces Cilium during upgrades
- Calling this MetalLB in GitOps while implementing Cilium (confuses agents)

## Related

- Multus: `skills/multus-secondary-net/`
- Full write-up: `docs/platform/networking-decisions.md`
