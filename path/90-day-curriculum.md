# 90-day curriculum (platform engineer track)

Assume part-time evenings. Adjust freely.

## Days 1–14 — Platform skeleton

- [ ] Proxmox + agent VM + Talos Ready  
- [ ] Cilium installed; you can explain pod/service CIDR  
- [ ] Argo CD + empty platform-gitops  
- [ ] Cloudflare Tunnel: one public hostname  
- [ ] Agent has GH App + kubectl  
- [ ] Learning board live  

**Outcome:** you can deploy a static app via git.

## Days 15–30 — Real apps + discipline

- [ ] 3 apps via GitOps with pinned versions  
- [ ] One DB-backed app (CNPG or MariaDB single)  
- [ ] Out-of-band secret for one OAuth or API key  
- [ ] First-login docs on each issue  
- [ ] First incident write-up (anything that broke)  

**Outcome:** deploy loop is boring (good).

## Days 31–60 — Platform depth

- [ ] Gateway API dual path (LAN + public) or document why not  
- [ ] Backup job for DB → object storage or NFS  
- [ ] NetworkPolicy on one namespace  
- [ ] Sequential upgrade rehearsal (k8s patch)  
- [ ] Observability: metrics + logs for one app  
- [ ] Agent RBAC reduced from cluster-admin  

**Outcome:** you can talk storage, upgrades, and blast radius.

## Days 61–90 — Product + portfolio

- [ ] Ship something you *care* about (trading bot, family app, blog)  
- [ ] CI: commit → image → registry → GitOps tag bump  
- [ ] Chaos day: reboot node, restore from backup notes  
- [ ] Write 3 portfolio stories from issues  
- [ ] Optional: second node or Omni research spike  

**Outcome:** interview-ready narratives with receipts in git.

## Weekly habit

| Day | Habit |
|-----|--------|
| 1 | Pin/update one image if needed |
| 2 | Close or advance one issue |
| 3 | Read one upstream changelog |
| 4 | Agent-assisted chore (skill exercise) |
| 5 | Lesson note in lab-notes |

## Stretch (after 90)

- Multi-tenant platform-gitops  
- WAHA + Chatwoot  
- Forgejo mirrors  
- Offsite backups (3-2-1)  
- Full LGTM stack right-sized  
