---
name: home-network-controllers
description: >
  UniFi, MikroTik, or Omada for lab networking: VLANs, DHCP DNS, DNS redirect
  footguns, reserve infra IPs, free LB pool. Triggers: /home-network, UniFi,
  MikroTik, Omada, DNS DNAT, VLAN servers.
version: 1.0.0
---

# Home network controllers

Full guide: `docs/network/home-network-controllers.md`.

## Any vendor

1. VLANs: clients vs servers (optional IoT)  
2. DHCP DNS → Technitium  
3. Exclude Cilium LB range from DHCP  
4. DNS redirect only where it cannot blackhole DNS upstream  

## Hard rule

Never redirect **servers VLAN** :53 in a way that catches the DNS host’s own queries to 1.1.1.1.

## Related

`skills/technitium-split-dns` · `docs/platform/hardware-topologies.md`


## Layer-0 rules (added)
- Resolvers on a **dedicated DNS network**; per-network DNAT `dst 53 AND dst NOT the DNS network → primary` (covers servers too, no upstream blackhole).
- Zones: default-deny between internal zones; named allows with a one-line description; block IoT-local and cameras → internet; admin paths (management + admin MACs) before moving your own devices; a break-glass port.
- Device names: per-network domain `<network>.local.<domain>` + resolver forwarder zone → gateway; guests on DHCP reservations.
- Before blaming Wi-Fi: uplink error counters and negotiated link speeds.
- UniFi API: `setting_preference: manual` for WLAN advanced fields; unique NAT `rule_index`; one login per run (rate limit); read back every write.
Full doc: `docs/network/network-foundation.md`.
