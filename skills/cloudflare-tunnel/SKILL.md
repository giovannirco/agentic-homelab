---
name: cloudflare-tunnel
description: >
  Expose lab apps via Cloudflare Tunnel without opening home WAN ports; token
  hygiene; 301 loop footguns. Triggers: /cloudflare-tunnel, cloudflared, public
  hostname, cfargotunnel.
version: 1.0.0
---

# Cloudflare Tunnel

## Pattern

```text
DNS CNAME → <tunnel-id>.cfargotunnel.com
cloudflared → http://gateway-or-service:port
```

## Rules

1. Scoped tokens (tunnel vs DNS edit)
2. Secrets OOB, not git
3. Match origin scheme to gateway listener (http vs https)
4. Optional Cloudflare Access for admin UIs

## Verify

```bash
kubectl -n network get pods -l app=cloudflared  # if in-cluster
curl -sI https://app.example.com/ | head
```

## Footguns

- 301 loops from scheme mismatch
- Public DNS while testing LAN-only apps
- Over-broad API tokens left forever
