---
name: lab-bootstrap
description: >
  Bootstrap an agentic homelab from bare metal/mini-PC: Proxmox, agent VM,
  Talos single-node, Cilium, Argo CD, Cloudflare Tunnel, agent GH App + kube access.
  Triggers: /lab-bootstrap, new lab, first cluster, setup homelab, start from zero.
version: 1.0.0
---

# Lab bootstrap (agentic-homelab)

## Order (do not skip)

1. Shopping list complete (hardware, domain, GitHub org, chat)
2. Proxmox installed and updated
3. Agent VM online with Hermes/OpenClaw + this repo skills
4. Talos single-node Ready
5. Cilium CNI healthy
6. Argo CD + platform-gitops registered
7. Cloudflare Tunnel one hostname
8. Wire GitHub App + k8s SA into agent
9. First app via GitOps
10. Learning board issues for the rest

## Agent behavior

- Follow `docs/setup/0N-*.md` in order.
- After each major step: verify commands + short comment on the tracking issue.
- Never invent IPs — ask or use placeholders.
- Prefer teaching mode if user says they are learning.

## Verify skeleton

```bash
kubectl get nodes
kubectl get pods -A | head
kubectl get applications -n argocd 2>/dev/null || true
curl -sI https://<public-app-host>/ | head
gh repo view YOURORG/platform-gitops
```

## Stop conditions

- Node NotReady > 15m without plan
- No backup of talos secrets.yaml
- Secrets about to be committed — halt and use OOB pattern
