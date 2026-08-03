# Hard-won lessons (sanitized)

Patterns distilled from real multi-month homelab operations. No personal topology.

## GitOps

1. **selfHeal reverts kubectl** — scale/edit is temporary; git is truth.
2. **Root Application should not prune bootstrap** carelessly — protect the tree that installs Argo/AppSets.
3. **OutOfSync ≠ broken** — Gateway API HTTPRoutes often show defaulted-field drift while Healthy + curl works.
4. **Orphaned resources** after OOB Secrets — label clearly; prefer pure GitOps when possible.
5. **Document intentional non-GitOps bootstrap** — Talos, first CNI, first Argo install often start bare.

## Networking / edge

6. **Tunnel origin http vs https mismatch → 301 loops.**
7. **external-dns ownership TXT** — manual DNS records block automation; delete or adopt.
8. **Split-horizon DNS** — public DoH clients bypass LAN VIP and hit Cloudflare; teach users.
9. **Do not DNAT all of DNS on a “servers” VLAN** without excluding the DNS servers themselves (forwarder blackhole).
10. **Cluster must resolve internal hostnames to in-cluster/LAN** or agents get Cloudflare 400s calling public URLs from pods.

## Storage

11. **HA disks ≠ free HA** — multi-replica RWO over slow links fails; local path + app-level HA may be better.
12. **Never put Galera/data dirs on NFS.**
13. **NFS root_squash** — do not initContainer chown; match app UID.
14. **Strict-local volumes** pin pods to nodes; wrong node → Pending/faulted forever.
15. **Backups are mandatory even with 2 replicas** — HA is not backup.

## Databases

16. **One operator per engine cluster-wide** — dual mariadb-operators fight (CrashLoop, rewritten STS).
17. **Agent/init images must match operator version** for Galera.
18. **Shared platform DB vs dedicated** — small apps share; large tenants get own CNPG.
19. **MetalLB for DB only when LAN clients need it** — default ClusterIP.

## Secrets

20. **Never “temporary” secrets in git** — history keeps them.
21. **Helm-owned Secret with REPLACE_ME + selfHeal** clobbers live OAuth secrets.
22. **Out-of-band Secret + extraEnvFrom** for OAuth, GH App PEM, MCP keys.
23. **Never paste PEMs into Discord/WhatsApp/issue comments.**

## Agents

24. **cluster-admin for agents is day-1 only** — scope down.
25. **Skills > vibes** — without runbooks agents thrash.
26. **Allowlists on chat channels** — open bots get driven by strangers.
27. **OpenClaw and Hermes share skill layout** — migrate persona files; reinstall caches.
28. **Session noise (heartbeats/crons)** can drown signal — disable empty squad crons.

## Upgrades

29. **Talos minor gates max k8s** — no skip minors.
30. **Upgrade Talos before k8s when required by catalog.**
31. **Review bootstrap manifests after k8s bumps** — do not replace Cilium with a default CNI.
32. **GPU nodes need per-minor extension schematics.**

## Process

33. **One theme per session** beats “fix everything.”
34. **Issues with full install context** beat tribal memory.
35. **First-login checklists** — deployed ≠ usable.
36. **Pin latest stable on install** — blog posts freeze ancient tags.

## Career

37. Write postmortems for yourself — they become interview stories.
38. Prefer boring patterns you can explain under pressure.
