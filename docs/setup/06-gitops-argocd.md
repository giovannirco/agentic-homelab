# 06 — GitOps with Argo CD + platform-gitops

## Goal

Make **git the source of truth** for cluster apps.

```text
GitHub: YOURORG/platform-gitops
        └── apps/<name>/...
Argo CD Application / AppSet
        └── reconciles to cluster
```

## Install Argo CD

Prefer official install (Helm or manifests). Pin chart version.

```bash
kubectl create namespace argocd
# helm upgrade --install argocd ... -n argocd  (pin version)
# OR kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/.../install.yaml
```

Give the controller enough memory on small nodes (homelab tip: controller can OOM under load — **≥1–2 Gi** request/limit when possible).

## Repo layout (recommended)

```text
platform-gitops/
  bootstrap/           # root app or AppSets
  apps/
    example-app/
      config.yaml      # AppSet metadata (if used)
      README.md
      helm/
        Chart.yaml
        values.yaml    # image.tag PINNED
        templates/
  infra/               # optional: move to cluster-gitops later
```

Copy `templates/platform-gitops/` from this repo as a starter.

## Root application pattern

1. Create a root `Application` pointing at `bootstrap/` or `apps/`.
2. Use **AppSet** with git directory generator for `apps/*`.
3. Enable automated sync with `prune` + `selfHeal` for apps you trust.

**Warning:** selfHeal will revert kubectl edits. That is a feature.

## Cluster vs platform split (later)

| Repo | Contents |
|------|----------|
| `cluster-gitops` | Cilium values history, cert-manager, external-dns, operators |
| `platform-gitops` | User-facing apps |

Day 1: one `platform-gitops` is fine.

## Register repo in Argo

- HTTPS + deploy key / GitHub App / PAT  
- Prefer GitHub App for agent-driven commits later  

## Verify

```bash
kubectl get applications -n argocd
argocd app list   # if CLI configured
```

## Done when

- [ ] Argo UI or CLI works  
- [ ] Empty or example app syncs Healthy  
- [ ] You understand Application vs AppSet  
