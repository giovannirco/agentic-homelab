---
name: homelab-databases
description: >
  Provision MariaDB, PostgreSQL (CNPG), and Redis for homelab: single vs multi-node
  decision matrix, one-operator rule, backups mandatory, affinity notes. Triggers:
  /homelab-databases, new MariaDB, new Postgres, CNPG, Galera, Redis Sentinel.
version: 1.0.0
---

# Homelab databases

## Hard rules

1. **One operator per engine** cluster-wide  
2. **Backups mandatory** even with replicas  
3. **No Galera on NFS**  
4. **Pin operator + image versions**  
5. Prefer **ClusterIP**; MetalLB only for real LAN clients  

## Decision matrix

| Need | MariaDB | Postgres (CNPG) | Redis |
|------|---------|-----------------|-------|
| Disposable cache | — | — | Single Deployment |
| Small app DB | Single MariaDB | instances: 1 | Single |
| Survive one node loss | Galera 2 + garbd | instances: 2 | replica + Sentinel |

## Operators (examples — pin current stable)

| Engine | Operator |
|--------|----------|
| MariaDB | mariadb-operator |
| Postgres | CloudNativePG |
| Redis | redis-operator or plain Deployment |

## Single CNPG sketch

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: app-postgres
  namespace: app
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:17
  instances: 1
  storage:
    size: 10Gi
  bootstrap:
    initdb:
      database: appdb
      owner: appuser
```

## Checklist

1. Pick matrix row  
2. Ensure single operator install  
3. Secrets OOB if needed  
4. GitOps manifests + affinity  
5. Backup CR / dump CronJob  
6. Wire app DSN to operator Service  
7. Smoke connect  

## Anti-patterns

- Second helm install of same operator  
- Skipping backups because “HA”  
- Exposing every DB on LAN LB  
