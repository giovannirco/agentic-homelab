# GitOps repository models

Separate **cluster infrastructure** from **applications** early — even if both live in one org.

## Mental model

```text
cluster-gitops          platform-gitops (×1 or ×N orgs)
  Argo root               AppSets / Applications
  CNI values history      User-facing apps
  Gateway, external-dns   Life-ops, agents, products
  Operators (CNPG, …)     Tenant-specific stacks
  cloudflared
```

| Repo | Owns | Who changes it |
|------|------|----------------|
| **cluster-gitops** | How the cluster works | Platform / lab owner |
| **platform-gitops** | What runs for users | App owners / same person at small scale |

## Model 1 — Simple (recommended day 1)

**One GitHub org (or user), two repos:**

```text
YOURORG/cluster-gitops
YOURORG/platform-gitops
```

```text
Argo CD
  └── Application: root → cluster-gitops/bootstrap
        ├── AppSet: infra-helm → cluster-gitops/infra/apps/*
        ├── AppSet: external-dns → cluster-gitops/infra/external-dns/*
        └── Application: platform → platform-gitops/bootstrap
              └── AppSet/apps → platform-gitops/apps/*
```

**When:** Topology A or B; one human; one domain family.

**Skip multi-org** until a second “product” or company needs isolation.

### Minimal platform-gitops layout

```text
platform-gitops/
  bootstrap/          # Applications or AppSet for apps/*
  apps/
    <name>/
      config.yaml
      helm/ or manifests/
      README.md
```

### Minimal cluster-gitops layout

```text
cluster-gitops/
  bootstrap/          # root + AppSets
  infra/
    apps/             # operators, gateway, multus, …
    external-dns/
      cloudflare-all/
      technitium/
  secrets/            # docs only — real secrets OOB
```

## Model 2 — Multi platform-gitops (one repo per org)

**When:** multiple companies/tenants, different GitHub orgs, different RBAC/domains.

```text
cluster-gitops
  AppSet platform-gitops-orgs:
    - orgA → https://github.com/orgA/platform-gitops
    - orgB → https://github.com/orgB/platform-gitops
    - lab  → https://github.com/lab/platform-gitops
```

Each tenant repo:

```text
platform-gitops/
  bootstrap/          # AppSets limited to that org’s apps
  apps/hermes/
  apps/waha/
  apps/…
```

**Argo project** allowlists namespaces/repos per tenant when possible.

### AppSet list generator (shape)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-gitops-orgs
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - org: lab
            repoURL: https://github.com/YOURORG/platform-gitops.git
          # - org: company-a
          #   repoURL: https://github.com/company-a/platform-gitops.git
  template:
    metadata:
      name: "{{.org}}-platform"
    spec:
      project: default   # or dedicated AppProject
      source:
        repoURL: "{{.repoURL}}"
        targetRevision: main
        path: bootstrap
      destination:
        server: https://kubernetes.default.svc
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

## Model 3 — Monorepo (acceptable only early)

Single repo with `infra/` + `apps/`. Faster to start; harder to invite others and harder to reason about blast radius. **Plan to split** when Argo is healthy.

## How topology influences model

| Topology | Suggested GitOps model |
|----------|------------------------|
| A single Proxmox | Model 1 or monorepo → graduate to Model 1 |
| B Proxmox + bare metal | Model 1 |
| C HA + utility | Model 1, then Model 2 if multi-tenant |

## Secrets

- Cluster secrets: OOB in `network` / operator namespaces  
- App secrets: OOB or private-repo values (team policy)  
- Never put PEMs/tokens in public forks of this curriculum  

## Related

- Skill `gitops-platform`  
- Skill `gitops-repo-models`  
- Setup `docs/setup/06-gitops-argocd.md`  
