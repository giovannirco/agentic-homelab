---
name: gitops-platform
description: >
  Argo CD App-of-Apps / ApplicationSet layout for platform-gitops and optional
  cluster-gitops split. Triggers: /gitops-platform, AppSet, root application,
  platform-gitops layout, Argo bootstrap.
version: 1.0.0
---

# GitOps platform layout

## Day-1 (one repo)

```text
platform-gitops/
  bootstrap/root.yaml      # Application → apps/
  apps/<name>/...
```

Root Application points at git; children are Applications or AppSet-generated.

## Growth split

| Repo | Owns |
|------|------|
| cluster-gitops | operators, CNI values history, external-dns, cert-manager |
| platform-gitops | user apps |

## AppSet directory generator

Generate one Application per `apps/*` with `config.yaml` metadata (project, path, namespace).

## Policy defaults

- `automated.prune=true`
- `automated.selfHeal=true` for apps
- Root: often `prune: false`

## Agent rules

- Edit git, not live objects, when selfHeal is on
- Pin chart versions in infra apps
- Register repo credentials via Argo Secret (OOB)
