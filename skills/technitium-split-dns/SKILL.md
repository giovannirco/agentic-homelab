---
name: technitium-split-dns
description: >
  Bootstrap and operate Technitium for LAN split-horizon DNS: primary zones,
  forwarders, optional catalog secondary, client DHCP/DNAT, diagnose public CF
  vs private Gateway VIP. Triggers: /technitium-split-dns, split-DNS, Technitium,
  dig returns Cloudflare, DNS_PROBE_POSSIBLE, catalog zone.
version: 1.0.0
---

# Technitium split-DNS

Full guide: `docs/setup/11-technitium-split-dns.md`.

## Goal

LAN: `app.example.com` → **INTERNAL_GW_VIP**.  
WAN: same name → Cloudflare/tunnel.

## Bootstrap order

1. Static IP VM/LXC for Technitium on Proxmox  
2. Install Technitium; set admin + API  
3. Explicit **forwarders** (1.1.1.1 / 1.0.0.1 / 8.8.8.8)  
4. Primary zone(s) + **TSIG** for external-dns  
5. Point DHCP DNS at primary  
6. Optional: catalog + secondary; never write external-dns to secondary  

## Hard rules

1. external-dns → **primary only**  
2. Do not NAT-hijack DNS server’s own upstream :53  
3. New zones join catalog if secondary exists  
4. DoH/Private Relay bypasses split-DNS  

## Verify

```bash
dig A app.example.com @<TECHNITIUM> +short   # private VIP
dig youtube.com @<TECHNITIUM> +short         # public IPs
```

## Related

`skills/external-dns` · `skills/home-network-controllers`
