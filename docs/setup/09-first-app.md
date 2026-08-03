# 09 — First app end-to-end

## Goal

Ship something real through the full path:

**issue → research → pin version → GitOps → Argo → DNS/tunnel → verify → first-login notes**

Pick a simple app: **ntfy**, **Homepage**, **whoami**, or **Mealie** if you want a real UI.

## Steps

1. Open issue from `templates/issues/install-app.md`.
2. Load skill `onboard-app`.
3. Look up latest stable image/chart.
4. Scaffold `platform-gitops/apps/<name>/` from `templates/platform-gitops/`.
5. Decide storage (emptyDir vs PVC).
6. Decide secrets (generate or OOB).
7. Commit + push main (or PR).
8. Argo sync; watch pods.
9. Expose via Gateway/Tunnel or LAN LB.
10. Document URL + first login in the issue.

## Definition of done

- [ ] Application Healthy in Argo  
- [ ] Pod Ready  
- [ ] HTTP 200 from intended network path  
- [ ] Version pin recorded in README  
- [ ] No secrets in git  

## Next apps

Add a DB-backed app (e.g. n8n with Postgres + Redis) only after `homelab-databases` skill is comfortable.
