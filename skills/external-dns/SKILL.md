---
name: external-dns
description: >
  Dual external-dns: Cloudflare for public (tunnel targets) and RFC2136 to
  Technitium for private A records on internal Gateway. Triggers: /external-dns,
  cloudflare-all, rfc2136, split DNS automation, HTTPRoute DNS.
version: 1.0.0
---

# external-dns (Cloudflare + Technitium)

Full guide: `docs/setup/12-external-dns.md`.

## Two controllers

| Deploy | Provider | Gateway | Target |
|--------|----------|---------|--------|
| public | cloudflare | external | tunnel hostname |
| private | rfc2136 | internal | INTERNAL_GW_VIP |

## Secrets OOB

- `CF_API_TOKEN`  
- TSIG secret for Technitium  

## GitOps

`cluster-gitops/infra/external-dns/{cloudflare-all,technitium}/`

## Footguns

- Manual DNS without matching txtOwner blocks updates  
- Writing RFC2136 to secondary  
- Huge batch sizes crash small Technitium VMs  
- Duplicate `--interval` flags  

## Verify

```bash
kubectl -n network get deploy | grep external-dns
dig A app.example.com @<TECHNITIUM> +short
```
