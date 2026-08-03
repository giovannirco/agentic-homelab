# 07 — Cloudflare Tunnel (public edge without open ports)

## Goal

Expose selected apps to the internet **without** port-forwarding 80/443 on your home router.

```text
Browser → Cloudflare edge → cloudflared (in cluster or VM) → Service/Gateway
```

## Why tunnel

- No CGNAT pain
- Free tier is enough for personal apps
- Pairs with Cloudflare Access for auth later

## Day-1 path (simplest)

1. Domain on Cloudflare DNS.
2. Create a Tunnel in Zero Trust dashboard.
3. Run `cloudflared` either:
   - as a **Deployment in Kubernetes**, or
   - on the agent / a small VM
4. Map hostname → `http://service.namespace.svc:port` (in-cluster) or LAN IP.

## Kubernetes-native path (better)

1. Install Gateway API controller (Envoy Gateway or Cilium Gateway).
2. Deploy cloudflared with ingress pointing at the **external** gateway Service.
3. external-dns (optional) creates CNAMEs → `*.cfargotunnel.com`.
4. HTTPRoutes define hostnames.

## Token hygiene

| Token | Scope |
|-------|-------|
| Tunnel token | Only that tunnel |
| DNS edit token | Only required zones |
| Avoid | Global “Edit zone DNS” forever on one overpowered token |

Store tokens as **Kubernetes Secrets** (out-of-band) or in the agent password manager — not git.

## Footguns

- HTTP vs HTTPS origin mismatch → **301 loops**
- Split-horizon DNS: laptop on public DNS may hit tunnel while LAN should hit internal VIP
- Cloudflare Access policies that lock you out of admin UIs

## Verify

```bash
curl -sI https://app.YOUR_DOMAIN/ | head
# From LAN, decide whether you want internal VIP or always tunnel
```

## Done when

- [ ] One hostname works publicly  
- [ ] Tunnel pods/process healthy  
- [ ] You can revoke/rotate the tunnel token  
