---
name: observability
description: >
  Choose observability tier by hardware: Grafana Cloud Free + Alloy (light),
  self-hosted Grafana+Prometheus+Loki single, or full LGTM (Mimir/Loki/Tempo RF=1+).
  Triggers: /observability, LGTM, Mimir, Loki, Tempo, Alloy, Grafana Cloud free,
  k8s-monitoring, light metrics.
version: 1.0.0
---

# Observability

Full guide: `docs/setup/13-observability.md`.

## Tiers

| Tier | Stack | Use when |
|------|--------|----------|
| **0** | Grafana Cloud Free + Alloy | 1-node, lowest pressure |
| **1** | Grafana + Prometheus + Loki SingleBinary | Local, still light |
| **2** | Mimir + Loki + Tempo + Grafana + Alloy | Multi-node mature lab |

## Rules

1. Do not deploy distributed LGTM on a single overloaded mini-PC.  
2. Free Cloud: watch **10k series / 50GB logs**; excess discarded on Free.  
3. RF=1 ≠ HA; document data-loss window on node death.  
4. Blocks on S3/MinIO; WAL on local NVMe.  
5. Pin k8s-monitoring chart major; schemas change.  
6. Secrets OOB for Cloud tokens and MinIO keys.

## Default recommendation

- Topology A → Tier 0  
- Learning PromQL → Tier 0  
- Want full LGTM story → Tier 2 only with disk/RAM budget  

## Verify

```bash
kubectl get pods -A | rg -i 'alloy|grafana|loki|mimir|tempo|prometheus'
```
