# Observability tiers (quick reference)

See full bootstrap: [13-observability.md](../setup/13-observability.md).

```text
Tier 0  Grafana Cloud Free ◄── Alloy (in-cluster collector only)
Tier 1  Grafana + Prometheus + Loki SingleBinary (+ optional Tempo single)
Tier 2  Grafana + Mimir + Loki + Tempo (distributed) + Alloy + MinIO/S3
```

## Light Mimir+Loki on one node?

| Approach | Verdict |
|----------|---------|
| Distributed Mimir + SimpleScalable Loki (multi-replica) | **No** for 1-node “everything” |
| Loki **SingleBinary** + Prometheus | **Yes** |
| Mimir **monolithic** + Loki SingleBinary | **Maybe** if ≥16–32 Gi free for obs alone |
| Cloud Free metrics+logs | **Yes** (best pressure profile) |

Full LGTM with RF=1 dual write is a **multi-node / dual-NVMe** pattern, not Topology A day-1.
