---
name: onboard-app
description: >
  Research, version-pin, GitOps-deploy, expose, and verify a new application on a
  homelab Kubernetes cluster (platform-gitops + Gateway/tunnel). Triggers:
  /onboard-app, install app, new app, deploy app, version bump, image tag.
version: 1.0.0
---

# Onboard a new homelab app

## Hard rule — versions

Before writing charts/values, **look up the latest stable release** and pin an **explicit tag**. Never invent tags. Avoid floating `latest` / `stable` in GitOps.

```bash
gh api repos/<org>/<repo>/releases/latest --jq '.tag_name'
crane manifest <image>:<tag> >/dev/null && echo OK
```

## Checklist

1. Research upstream (storage, DB, redis, env, UID).
2. Resolve latest stable version; record in app README.
3. Choose path: `platform-gitops/apps/<name>/`.
4. Design storage + secrets + exposure.
5. Scaffold Helm (or plain manifests) + HTTPRoute/Ingress.
6. Push → Argo sync (no long-lived kubectl mutates).
7. Verify pods, DNS/tunnel, HTTP.
8. Document first-login on the issue.
9. Update dashboards if applicable.

## Layout

```text
apps/<name>/
  config.yaml
  README.md
  helm/
    Chart.yaml
    values.yaml      # image.repository + image.tag PINNED
    templates/
```

## Storage defaults

| Data class | Choice |
|------------|--------|
| Small RWO / SQLite | local path / OpenEBS hostpath / single-replica CSI |
| Large media | NFS or object storage |
| Postgres/MySQL | operator (CNPG/MariaDB) preferred over random containers |

Match image UID/fsGroup. On NFS with root_squash: never chown as root in initContainers.

## Exposure

- LAN: internal Gateway or LB VIP
- Public: Cloudflare Tunnel → external Gateway
- Avoid mixing http/https origins (301 loops)

## Verify

```bash
kubectl get application -n argocd | grep <name>
kubectl get pods -n <ns> -o wide
kubectl logs -n <ns> deploy/<name> --tail=50
curl -skI https://<host>/ | head
```

## Footguns

1. selfHeal undoes kubectl scale/edit
2. Wrong node for strict-local PVC → Pending
3. Shell-expanded `$PASSWORD` empty in env — put full URL in Secret
4. Major jumps without reading migrations
5. Blog-post tags from 2022
