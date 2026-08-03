# 05 — Cilium networking + LoadBalancer (Cilium LB-IPAM)

## Goal

Install **Cilium** as CNI and give `Service type: LoadBalancer` real **LAN VIPs** using:

1. **CiliumLoadBalancerIPPool**
2. **CiliumL2AnnouncementPolicy**

This is **not** the MetalLB project. (People say “MetalLB” loosely for “LAN VIP”; here the implementation is Cilium.)

Deep reference: [networking-decisions.md](../platform/networking-decisions.md).

## Why Cilium

- Real CNI literacy
- kube-proxy replacement
- LB IPAM + L2 without a second stack
- Path to Hubble / policies

## Install

Pin chart from Cilium releases; follow Talos+Cilium docs for your versions.

## LB pool

1. Pick a DHCP-excluded range on your LAN.
2. Apply `CiliumLoadBalancerIPPool`.
3. Apply `CiliumL2AnnouncementPolicy` with interface regex matching node NICs.
4. Create a test LoadBalancer Service; **ping the VIP from another host**.

Pin fixed VIPs later with:

```yaml
annotations:
  lbipam.cilium.io/ips: "<VIP>"
  lbipam.cilium.io/ip-pool: servers-pool
```

Typical VIP consumers: Envoy internal/external Gateways. App Services stay ClusterIP by default.

## Multus (optional, later)

Secondary macvlan interfaces only when a pod needs a LAN NIC of its own (see Multus skill). Skip on day 1.

## Gateway API (next after LB works)

Prefer Envoy Gateway HTTPRoutes over legacy Ingress. Dual gateways (internal + external) when you add Cloudflare Tunnel.

## Verify

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl get ciliumloadbalancerippools
kubectl get ciliuml2announcementpolicies
kubectl get svc -A --field-selector spec.type=LoadBalancer
```

## Done when

- [ ] CoreDNS works
- [ ] Pods reach ClusterIP services
- [ ] At least one LB VIP pings on LAN
- [ ] You can explain pod CIDR vs service CIDR vs LB pool
