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
