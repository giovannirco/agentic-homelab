---
name: out-of-band-secrets
description: >
  Pattern for secrets that must not live in GitOps values: create k8s Secrets via
  kubectl/password manager, wire via extraEnvFrom, rotate without commits. Triggers:
  /out-of-band-secrets, secret not in git, rotate MCP key, GitHub App PEM, OAuth.
version: 1.0.0
---

# Out-of-band Kubernetes secrets

## When

| Secret class | In git? |
|--------------|---------|
| Non-sensitive config | Often yes |
| App passwords in private GitOps | Team policy |
| **OAuth client secrets** | **No** |
| **GitHub App private key** | **No** |
| **MCP API keys** | **No** |

## Recipe

```bash
kubectl -n <ns> create secret generic <name> \
  --from-literal=KEY='value' \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n <ns> label secret <name> app.kubernetes.io/component=oob-secret --overwrite

# Helm values (no secret material):
# extraEnvFrom:
#   - secretRef: { name: <name> }

kubectl -n <ns> rollout restart deploy/<app>
```

## Anti-patterns

1. `WAHA_MCP_KEY: "key_…"` in values then “fix later”
2. Chart Secret with `REPLACE_ME` that selfHeals over live secret
3. Pasting PEMs into chat or PR comments

## Rotate

1. Mint new credential at source  
2. Update OOB Secret only  
3. Restart consumers; smoke-test  
4. Revoke old credential  
