# 11 — Technitium split-DNS (bootstrap + operate)

**Goal:** On LAN, `app.example.com` resolves to your **internal Gateway VIP**. On the internet, the same name is a **Cloudflare / tunnel** path. That is split-horizon DNS.

Deep skill: `skills/technitium-split-dns/`.  
external-dns: [12-external-dns.md](12-external-dns.md).

## Why Technitium

- Full DNS server (zones, TSIG, catalog/secondary, API)
- Better teaching surface than “router static hosts only”
- Works with **external-dns RFC2136** for automatic private A records

Day-1 alternative: router static DNS host overrides (limited). Prefer Technitium once Gateway VIPs exist.

## Topology (reference)

```text
Client (home VLAN)
  → DNS: Technitium primary (or DNAT :53 → primary)
      → local zone?  → AA private A → INTERNAL_GW_VIP
      → else         → forwarders 1.1.1.1 / 1.0.0.1 / 8.8.8.8

external-dns-technitium (in cluster)
  → RFC2136 + TSIG → PRIMARY only
      → optional catalog AXFR → secondary

Public resolvers / phones on LTE
  → Cloudflare public records → tunnel → envoy-external
```

## Bootstrap — primary VM (Topology A/B/C)

### 1. Create VM on Proxmox

| Resource | Suggestion |
|----------|------------|
| OS | Debian/Ubuntu |
| vCPU | 1–2 |
| RAM | 1–2 GiB |
| Disk | 16 GiB+ |
| IP | **static** on LAN (reserve in DHCP) |

### 2. Install Technitium

Follow upstream install docs (native package or their install script). Enable API; set admin password; bind DNS on `:53`.

### 3. Resolver settings (important)

| Setting | Guidance |
|---------|----------|
| Forwarders | Explicit `1.1.1.1`, `1.0.0.1`, `8.8.8.8` (UDP) |
| Recursion | Allow only private networks (or equivalent) |
| DNSSEC validation | On after forwarders work |

**Empty forwarders + broken recursion = whole-internet outage** for clients using only Technitium.

### 4. Create primary zones

For each domain you use on LAN (e.g. `lab.example.com`):

1. Create **Primary** zone in Technitium.  
2. Allow updates from external-dns via **TSIG** key (create key e.g. name `external-dns`, algorithm hmac-sha256).  
3. ACL: allow that TSIG for updates on the zone.

### 5. Optional secondary + catalog (HA)

Only when you have a second DNS host:

1. Create catalog zone (e.g. `dns-catalog.lab.local`).  
2. **Every new private zone must join the catalog** or secondary serves public/empty data.  
3. Transfer/NOTIFY to secondary IP with TSIG.  
4. **external-dns must write to primary only** — never the secondary.

### 6. Point clients at Technitium

Options:

| Method | Notes |
|--------|-------|
| DHCP option 6 = primary IP | Simplest |
| Controller DNAT :53 → primary | Forces clients that ignore DHCP DNS (see controller doc) |
| Manual on laptop | Good for debug |

## Critical footguns

1. **Do not DNAT the “servers” VLAN port 53 to DNS if that rewrites the DNS server’s own upstream queries** — primary cannot reach `1.1.1.1:53` → SERVFAIL for the world.  
2. **Main/client VLAN DNAT → primary only** is usually OK when primary is on another subnet.  
3. **DoH / iCloud Private Relay** bypasses split-DNS → users hit Cloudflare Access / public IPs on LAN.  
4. **AAAA public records** can still win in browsers if IPv6 path uses public DNS — empty AAAA on private zone is often correct for dual-stack confusion.  
5. New zone with **no A records** → NXDOMAIN on LAN even when public CNAME exists.

## Verify

```bash
# Private path (expect INTERNAL_GW_VIP)
dig A app.example.com @<TECHNITIUM_IP> +short

# Recursion / forwarders still work
dig youtube.com @<TECHNITIUM_IP> +short

# From a client that should be intercepted
dig A app.example.com @8.8.8.8 +short   # only if DNAT forces :53
```

## Done when

- [ ] Primary answers private A for lab zone  
- [ ] Public names still resolve via forwarders  
- [ ] TSIG ready for external-dns  
- [ ] Clients on LAN use Technitium (DHCP or DNAT)  
