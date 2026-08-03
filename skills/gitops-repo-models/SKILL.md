---
name: gitops-repo-models
description: >
  Choose simple cluster-gitops + one platform-gitops vs multi-org platform-gitops
  AppSet fan-out; map model to hardware topology. Triggers: /gitops-repo-models,
  multi-org, platform-gitops-orgs, monorepo split, cluster-gitops.
version: 1.0.0
---

# GitOps repository models

Full guide: `docs/platform/gitops-repo-models.md`.

## Quick pick

| Situation | Model |
|-----------|--------|
| One human, one lab | cluster-gitops + **one** platform-gitops |
| Multiple companies/orgs | AppSet list → **one platform-gitops per org** |
| Day-0 only | monorepo OK → split soon |

## Rules

1. Infra in cluster-gitops; apps in platform-gitops  
2. Prefer GitOps over bare kubectl when selfHeal is on  
3. AppProjects can limit tenant blast radius  

## Related

`skills/gitops-platform` · `docs/platform/hardware-topologies.md`
