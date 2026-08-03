# 08 — Wire agent permissions (GitHub App + Kubernetes)

## Goal

Your agent can:

1. Read/write **lab** GitHub repos  
2. Talk to the cluster with a **service account** (not your human admin forever)

## GitHub App (preferred over personal PAT)

1. In your **lab org**: Settings → Developer settings → GitHub Apps → New.
2. Permissions (start small): Contents R/W, Issues R/W, Metadata R, Pull requests R/W, Actions R if needed.
3. Install the app on `platform-gitops` (+ notes repo).
4. Download **private key PEM** once.
5. Record App ID + Installation ID.

### Put secrets on the agent (out-of-band)

```bash
# On agent host or in k8s Secret if Hermes runs in-cluster
export GITHUB_APP_ID=...
export GITHUB_APP_INSTALLATION_ID=...
export GITHUB_APP_PRIVATE_KEY_PATH=~/.hermes/secrets/gh-app.pem
# Never commit the PEM
```

Generate installation tokens as needed (`github-app-token` script pattern) and set `GH_TOKEN` for `gh` CLI.

### Git identity for bot commits

```text
{APP_ID}+lab-agent[bot]@users.noreply.github.com
```

## Kubernetes access

### Day 1 (bootstrap only)

Copy admin kubeconfig to the agent with mode `0600`. Label it temporary.

### Day 2+ (better)

```bash
kubectl create serviceaccount lab-agent -n lab-system
# Bind Role or ClusterRole carefully
kubectl create rolebinding lab-agent-admin \
  -n lab-system --clusterrole=edit --serviceaccount=lab-system:lab-agent
# Issue token / kubeconfig for the SA
```

Prefer **namespace-scoped** edit first. Expand only when GitOps cannot do the job.

## MCP bridges (optional)

Examples:

- WAHA MCP for WhatsApp tool use  
- Browser / docs MCP  

Keys for MCP apps are **out-of-band Secrets**, rotated by recreating the app — never in values.yaml.

## Verify

```bash
gh auth status
gh repo list YOURORG
kubectl auth can-i get pods -A --as=system:serviceaccount:lab-system:lab-agent
```

## Done when

- [ ] Agent can open a PR or commit to platform-gitops  
- [ ] Agent can list pods  
- [ ] PEM and kubeconfig are not in git  
- [ ] Chat allowlist prevents random users from driving the agent  
