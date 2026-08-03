# Home network controllers: UniFi, MikroTik, Omada

The controller is how you make **split-DNS, VLANs, and stable infra IPs** real. Pick one ecosystem; concepts transfer.

## Why this belongs in an agentic lab

| Need | Controller feature |
|------|-------------------|
| Force clients to Technitium | DHCP DNS options and/or **NAT/redirect :53** |
| Isolate IoT / servers | VLANs + firewall |
| Stable infra | DHCP reservations |
| LB VIP range free | DHCP pool excludes Cilium LB CIDR |
| Debug “works on my phone off Wi‑Fi” | See if client bypasses LAN DNS (DoH) |

Without this layer, k8s DNS automation fights random client resolvers.

## Option comparison

| | **UniFi** | **MikroTik** | **TP-Link Omada** |
|--|-----------|--------------|-------------------|
| UX | Polished app/UI | WinBox/WebFig; steep | Cloud/controller app; mid |
| Homelab popularity | Very high | Power users / ISPs | Growing / cost-effective |
| VLANs | Easy | Full control | Good |
| NAT / DNS redirect | Supported (verify model) | Excellent (NAT rules) | Supported (model-dependent) |
| API automation | Limited official API | Strong (RouterOS API/script) | Controller API varies |
| Cost | Higher gear | Often best $/feature | Competitive |

**Recommendation:** use what you already own. For a greenfield curriculum lab, **UniFi** or **Omada** for speed; **MikroTik** if you want deep routing literacy.

## Shared design (any vendor)

```text
WAN
  └── Router / gateway (controller-managed)
        ├── LAN / Main VLAN     — laptops, phones (DNS → Technitium)
        ├── Servers VLAN        — Proxmox, Talos, DNS (careful with DNS NAT)
        └── optional IoT VLAN   — no lateral to servers
```

### DHCP

- Reservation for: Proxmox, Talos nodes, Technitium, agent VM  
- DNS servers option: Technitium primary (+ optional secondary)  
- **Exclude** Cilium LB pool from DHCP range  

### DNS redirect (optional but powerful)

DNAT or “DNS shield” style rule: client queries to any resolver on :53 → rewrite to Technitium.

**Hard rule from real outages:**

> Do **not** redirect **all** traffic on the servers VLAN port 53 toward a DNS box in a way that also rewrites the **DNS server’s own upstream** queries. Primary must reach public resolvers (1.1.1.1:53) unmolested.

Safe pattern:

- Redirect **client/main** VLANs → Technitium  
- Servers VLAN: set DHCP DNS to Technitium **without** hairpin DNAT, **or** exclude DNS host as source from redirect  

### Firewall

- Allow LAN → internal Gateway VIP :80/:443  
- Allow LAN → Technitium :53  
- Allow cluster nodes → each other  
- Optional: block IoT → servers  

## UniFi-oriented checklist

1. Site → Networks: Main + Servers VLANs  
2. DHCP DNS = Technitium IP  
3. Optional: Traffic/NAT rule DNS redirect Main → Technitium  
4. Disable or carefully scope any “Servers DNS redirect”  
5. Verify rule **destination IP** did not drift after UI edits  
6. IPv6: if public AAAA + broken split, simplify (many labs keep LAN IPv6 off at first)

## MikroTik-oriented checklist

1. Bridges/VLANs per role  
2. `/ip dhcp-server network` set `dns-server=`  
3. NAT: `dst-nat` chain for udp/tcp 53 from client VLAN to Technitium  
4. Firewall filter: accept established, VLAN isolation  
5. Address lists for infra hosts  

## Omada-oriented checklist

1. Networks/VLANs in controller  
2. DHCP DNS options per LAN  
3. Gateway ACL / NAT for DNS redirect if available on your gateway model  
4. Reserve IPs for infra  
5. Confirm firmware supports the NAT feature you rely on  

## Verify (any controller)

```bash
# From a laptop on Main Wi-Fi
dig app.example.com +short              # expect INTERNAL_GW_VIP if split works
dig youtube.com +short                  # expect public IPs
scutil --dns | head                     # macOS resolvers
# Temporarily: dig @1.1.1.1 app.example.com — if redirect works may still show private
```

If dig is private but browser hits Cloudflare Access: flush cache; disable DoH/Private Relay for test.

## Related

- [11-technitium-split-dns.md](../setup/11-technitium-split-dns.md)  
- [12-external-dns.md](../setup/12-external-dns.md)  
- [hardware-topologies.md](../platform/hardware-topologies.md)  
