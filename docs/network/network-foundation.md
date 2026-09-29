# Network foundation (layer 0): before Proxmox and Kubernetes

Everything above (split-DNS, LoadBalancer VIPs, agents with cluster access) is easier and safer on a network that was **designed**, not accreted. This is the layer most homelab tutorials skip. Do it before the cluster, or at the latest before exposing anything.

## 1. Address plan that scales past one house
```text
routed       10.<site>.<role>.0/24     unique per site, may cross site-to-site VPN
local-only   192.168.<role>.0/24       identical at every site, never routed
VPN clients  172.16.<site>.0/24
VLAN ID = site × 100 + role            management untagged
```
| Role | Network | Class | Notes |
|---|---|---|---|
| 10 | Mgmt | routed | gateway, switches, APs, hypervisors, controller |
| 20 | Servers | routed | VMs/containers |
| 21 / 22 | K8s nodes / K8s LoadBalancer VIPs | routed | nodes get a tagged interface on 22 for L2 announcements |
| 23 | Storage | routed | NAS legs (NFS/SMB/S3) |
| 30 | Main | routed | people's devices |
| 35 | Media | routed | TVs/streamers (untrusted, need casting) |
| 40 / 41 | IoT / IoT-local | local-only | cloud devices / local-control devices (no internet) |
| 45 | Devices | local-only | printers, 3D printers |
| 50 | Guest | local-only | internet only, client isolation |
| 53 | DNS | routed | resolvers only (see §3) |
| 60 | Cameras | routed | default-block, per-camera rules |
Skip site numbers 96–111 and 244 (Kubernetes default CIDRs `10.96.0.0/12`, `10.244.0.0/16`). "Sites may talk" becomes one object (`10/8` + `172.16/12`), and local-only networks can't leak into tunnels.

## 2. Zones: default-deny, then named flows
Group networks into firewall zones (UniFi zone-based firewall, MikroTik address lists/chains, Omada ACLs). Between internal zones: **block by default**; allow a short list of flows, each with a one-line reason:
- every zone → DNS on 53
- people → media (casting), people → devices (printing ports), people → storage (SMB/NFS), people → k8s LB (80/443)
- media → storage (read-only NFS export), servers/k8s → storage
- **IoT-local → internet: block**, **cameras → internet: block**
- **Admin paths first**: management → infrastructure; your admin devices (by MAC) from the people network → infrastructure. Keep a **break-glass switch port** (management only) for when a rule locks you out.
Test from inside: a small container on a restricted network checking which ports are open.

## 3. A network just for DNS (enforcement + analytics)
If resolvers share a subnet with other servers, those servers query them on L2 and never cross the gateway: no redirect, no filtering, no logs. Put the resolvers on **their own network**, then:
1. allow every zone → DNS on 53
2. DHCP everywhere hands out the two resolvers
3. **DNAT per network (not the DNS network):** dst port 53 **and destination not the DNS network** → primary resolver
Devices with hard-coded DNS get your answers, and the resolver logs the **real client IP**. This replaces the older "never redirect DNS on the servers VLAN" rule: the resolvers' own upstream traffic comes from the excluded DNS network.

## 4. Every device gets a DNS name for free
Most gateways (UniFi, MikroTik, Omada) answer A/PTR for their DHCP clients under each network's **domain name**. Set domains like `<network>.local.<your-domain>` and add one **conditional-forwarder zone** on your resolver → the gateway. `laptop.main.local.example.com` just works. Keep `local.<domain>` **out of public DNS**. Give VMs/containers DHCP **reservations** (not static IPs) so they get names too.

## 5. Few SSIDs, many networks
Three SSIDs: main (people), **things** with per-device passwords (UniFi PPSK: the password picks the VLAN for media/IoT/devices), guest (WPA2, client isolation). Scope mDNS reflection to the networks that need discovery.

## 6. Admin path and risky changes
- Changing the management subnet with a self-hosted controller: give the controller a **temporary second IP** in the new subnet first, then change the network, then re-point the gateway (`set-inform`).
- Network changes on a remote hypervisor: a **dead-man switch** (`systemd-run --on-active=180` restoring the old config) that you cancel once verified.
- Your laptop is part of the change: wired on the break-glass port, forget other SSIDs (macOS auto-joins them).

## 7. When throughput looks wrong
Check **port error counters** (rx_errors / drops on every uplink) and **negotiated link speeds** before blaming Wi-Fi or hosts. Compare a path that avoids the suspect link (e.g. internet vs LAN), and **swap port roles** to learn whether the fault follows the cable or the port.

Related: [home-network-controllers.md](home-network-controllers.md), [11-technitium-split-dns.md](../setup/11-technitium-split-dns.md).
