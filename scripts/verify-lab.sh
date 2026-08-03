#!/usr/bin/env bash
# Smoke checks for a learning lab. Safe/read-only-ish.
set -euo pipefail
echo "== nodes =="
kubectl get nodes -o wide || true
echo "== non-running pods (sample) =="
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded 2>/dev/null | head -40 || true
echo "== argocd apps =="
kubectl get applications.argoproj.io -n argocd 2>/dev/null | head -30 || echo "(no argo crds)"
echo "== done =="
