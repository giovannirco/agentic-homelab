# 12 — external-dns: Cloudflare + Technitium

**Goal:** HTTPRoutes automatically publish DNS:

| Plane | Controller | Target |
|-------|------------|--------|
| **Public** | external-dns **Cloudflare** | Tunnel hostname (CNAME, proxied) |
| **Private** | external-dns **RFC2136 → Technitium** | Internal Gateway VIP (A record) |

Two deployments (or two AppSet children). **Do not** merge them into one process.

Lives in **cluster-gitops** (infra), not app repos.

## Prerequisites

- [ ] Envoy (or other) Gateways: `envoy-internal` + `envoy-external` (names yours)  
- [ ] Cloudflare API token: Zone Read + DNS Edit on needed zones  
- [ ] Technitium primary + TSIG key  
- [ ] OOB Secrets in cluster (never git)  

## Secret shapes (OOB)

```bash
# Cloudflare
kubectl -n network create secret generic external-dns-cloudflare-secret \
  --from-literal=CF_API_TOKEN='…' \
  --dry-run=client -o yaml | kubectl apply -f -

# Technitium TSIG (base64/secret per chart docs)
kubectl -n network create secret generic external-dns-technitium-secret \
  --from-literal=tsig-secret='…' \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Cloudflare instance (public)

**Recommended settings:**

| Setting | Guidance |
|---------|----------|
| provider | `cloudflare` |
| sources | `gateway-httproute` (Gateway API) |
| gateway filter | **external** gateway name/namespace |
| default targets | `<tunnel-id>.cfargotunnel.com` |
| proxied | true (orange cloud) when using tunnel |
| txtOwnerId | unique, e.g. `cloudflare-all` |
| txtPrefix | optional `k8s.` |
| domainFilters | only zones the token can edit |
| policy | `sync` or `upsert-only` (team choice) |

**Token hygiene:** one scoped token (DNS edit on listed zones). Prefer not a global account key.

**Ownership:** external-dns will not overwrite records it does not own (TXT ownership). Delete manual conflicting records first.

## Technitium instance (private)

| Setting | Guidance |
|---------|----------|
| provider | `rfc2136` |
| host | **primary** Technitium IP only |
| port | 53 |
| zones | each private zone |
| TSIG | key name + alg + secret from OOB |
| sources | `gateway-httproute` (+ optional `crd` for DNSEndpoint) |
| gateway filter | **internal** gateway |
| default targets | **INTERNAL_GW_VIP** |
| txtOwnerId | e.g. `external-dns-technitium` |
| batch size | keep small on tiny DNS VMs (e.g. 5) |
| request timeout | ≥ 2m if many HTTPRoutes |

### Stability tips (hard-won)

- Do **not** flood RFC2136 with huge restore CRDs.  
- Wildcard TXT: use `--txt-wildcard-replacement=wildcard` when needed.  
- Chart may already set `--interval` — do not duplicate flags.  
- Memory: give Technitium enough RAM; external-dns can be small.

## GitOps layout

```text
cluster-gitops/infra/external-dns/
  cloudflare-all/
    values.yaml
    config.yaml      # AppSet metadata if used
  technitium/
    values.yaml
    config.yaml
```

AppSet generates one Application per folder.

## HTTPRoute responsibility

Apps only declare HTTPRoutes with correct `parentRefs`:

- LAN name → parents include **internal** gateway  
- Public name → parents include **external** gateway  
- Both → dual parentRefs  

DNS controllers watch routes and write the right plane.

## Verify

```bash
kubectl -n network get deploy | grep external-dns
kubectl -n network logs deploy/external-dns-cloudflare-all --tail=50
kubectl -n network logs deploy/external-dns-technitium --tail=50

# Private
dig A app.example.com @<TECHNITIUM> +short    # INTERNAL_GW_VIP

# Public (from a resolver that is not split)
dig CNAME app.example.com +short              # *.cfargotunnel.com or CF flattened
```

## Done when

- [ ] New HTTPRoute on internal GW creates/updates private A  
- [ ] New HTTPRoute on external GW creates/updates public record → tunnel  
- [ ] No CrashLoop on either external-dns  
- [ ] Secrets not in git  
