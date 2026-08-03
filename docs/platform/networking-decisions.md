# Networking decisions (reference architecture)

Opinionated networking for a Talos + Gateway API lab. Replace example CIDRs and interface regexes with your own. Re-check current Cilium and Envoy docs before applying.

## TL;DR

| Concern | Choice | Not chosen |
|---------|--------|------------|
| CNI | **Cilium** (native routing, kube-proxy replacement) | Flannel / Calico default |
| Service type LoadBalancer | **Cilium LB-IPAM** + **Cilium L2 Announcement** | Standalone MetalLB |
| Extra NICs on pods | **Multus** + macvlan NetworkAttachmentDefinitions | HostNetwork everywhere |
| L7 ingress | **Envoy Gateway** (Gateway API only; no legacy Ingress) | nginx-ingress as primary |
| Dual plane | **envoy-internal** (LAN) + **envoy-external** (tunnel/WAN) | Single gateway for everything |
| Public edge | **Cloudflare Tunnel** → external gateway | Open 80/443 on home router |

> Docs and skills sometimes say “MetalLB” colloquially for “LAN VIP on a Service.” In this architecture the implementation is **Cilium**, not the MetalLB project.

## Layer diagram

```text
                         Internet
                             │
                    Cloudflare Tunnel
                             │
                      cloudflared pods
                             │
              ┌──────────────┴──────────────┐
              │  Service LoadBalancer        │
              │  EXTERNAL_GW_VIP (Cilium)    │  ← L2 ARP on node NICs
              └──────────────┬──────────────┘
                             │
                    Envoy Gateway external
                             │
                         HTTPRoutes
                             │
              ┌──────────────┴──────────────┐
              │  Service LoadBalancer        │
              │  INTERNAL_GW_VIP (Cilium)    │  ← LAN clients / split-DNS
              └──────────────┬──────────────┘
                    Envoy Gateway internal
                             │
                           Pods
              (Cilium pod CIDR + optional Multus macvlan)
```

## 1. Cilium as CNI

**Why:** Learn a real CNI; kube-proxy replacement; LB IPAM + L2 without a second product; path to Hubble/NetworkPolicy later.

**Typical shape (fill your own):**

| Setting | Example placeholder |
|---------|---------------------|
| Pod CIDR / native routing | `10.42.0.0/16` |
| Service CIDR | `10.43.0.0/16` |
| IPAM | kubernetes |
| kube-proxy replacement | enabled |
| LB mode | DSR (if your Cilium version supports your topology) |

Install/upgrade: pin chart version from Cilium release notes; on Talos follow the Talos+Cilium guide for that minor.

## 2. LoadBalancer = Cilium LB-IPAM + L2 Announcement

### CiliumLoadBalancerIPPool

Reserve a **DHCP-excluded** range on your LAN (example shape only):

```yaml
apiVersion: cilium.io/v2
kind: CiliumLoadBalancerIPPool
metadata:
  name: servers-pool
spec:
  allowFirstLastIPs: "No"
  blocks:
    - cidr: 10.LAB.0.192/26   # REPLACE — pick free range on YOUR LAN
  disabled: false
```

### CiliumL2AnnouncementPolicy

Announces LoadBalancer (and optional externalIPs) via ARP on selected interfaces:

```yaml
apiVersion: cilium.io/v2alpha1
kind: CiliumL2AnnouncementPolicy
metadata:
  name: l2-policy
spec:
  loadBalancerIPs: true
  externalIPs: true
  interfaces:
    - "^enp.*"    # REPLACE — match your NIC names (enp*, eth*, etc.)
  nodeSelector:
    matchLabels:
      kubernetes.io/os: linux
```

### Pin a Service to a fixed VIP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: envoy-internal
  namespace: network
  annotations:
    lbipam.cilium.io/ips: "10.LAB.0.193"          # REPLACE
    lbipam.cilium.io/ip-pool: servers-pool
spec:
  type: LoadBalancer
  # ports, selector...
```

**What typically gets a LAN LB VIP:**

| Service | Role |
|---------|------|
| `envoy-internal` | LAN HTTP(S) Gateway |
| `envoy-external` | Gateway in front of tunnel + optional LAN |
| Optional DB primary | Only when real LAN clients need SQL (e.g. media boxes) |
| Optional apps | Syncthing discovery/sync, specialty L4 |

Default for app Services: **ClusterIP**. Do not LB-expose every DB.

## 3. Multus (secondary interfaces)

**When:** A pod needs a **second interface on the LAN** (static IP for DNS, special routing, GPU host NIC), not just ClusterIP.

**How:**

1. Install Multus (DaemonSet; GitOps chart common).
2. Define `NetworkAttachmentDefinition` (NAD) resources — usually macvlan bridge mode on the host NIC.
3. Annotate pods: `k8s.v1.cni.cncf.io/networks: <nad-name>`.

**Pattern categories (names are examples):**

| NAD role | Use |
|----------|-----|
| general servers macvlan | Optional attach for special pods |
| control-plane oriented | CP-local attach if needed |
| DNS / static IP | DNS server pod that must own a stable LAN IP |
| GPU NIC | Pods that should egress on GPU host interface |

**Footgun:** macvlan + static IP + init policy-routing can flap (`address already in use`, stuck Init). Prefer simpler DNS topologies on day 1 (DNS VM **outside** the cluster is often more reliable than Multus DNS).

## 4. Gateway API (Envoy Gateway)

**Choice:** No legacy `Ingress`. All L7 via **HTTPRoute** → Gateway.

| Gateway | Audience | Typical LB VIP |
|---------|----------|----------------|
| `envoy-internal` | LAN / split-DNS A records | internal VIP from pool |
| `envoy-external` | Tunnel origin + optional LAN | external VIP from pool |

HTTPRoutes attach with `parentRefs` and **sectionName** matching listeners / certs (e.g. `http`, `https-<domain>`).

**Footgun:** Cloudflare Tunnel origin `http` vs `https` must match the listener you target — mismatch → **301 loops**.

## 5. DNS glue (concept only)

| Path | Mechanism |
|------|-----------|
| Public | external-dns → Cloudflare CNAME → tunnel hostname |
| Private LAN | Technitium (or similar) A → **internal Gateway VIP** |
| Pods calling sibling apps | `http://svc.ns.svc.cluster.local` — **not** public hostnames (CF often returns 400 from inside) |

## 6. Validation checklist

1. Pick LAN subnet + free LB range; document in private notes.
2. Install Cilium; confirm pods Ready.
3. Apply IP pool + L2 policy; create a throwaway `LoadBalancer` Service; ping VIP from another LAN host.
4. Install Multus only when you have a concrete second-NIC need.
5. Install Envoy Gateway; dual Gateways when you add tunnel.
6. Prefer ClusterIP until you need a VIP.

## Related skills

- `skills/cilium-networking/`
- `skills/multus-secondary-net/`
- `skills/cloudflare-tunnel/`
- `docs/setup/05-cilium-and-lb.md`
