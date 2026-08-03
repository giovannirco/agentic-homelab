# 13 — Observability (pick a tier by hardware)

Observability should **not** starve the lab. On a single-node “everything on Proxmox” box, full distributed LGTM is usually the wrong first move.

This guide defines **three tiers**:

| Tier | Name | Fits |
|------|------|------|
| **0** | Grafana Cloud Free + Alloy | Topology A (1 box), week-1 learning |
| **1** | Light self-hosted (Grafana + Prometheus + Loki single) | 1-node k8s with headroom |
| **2** | Full LGTM (Mimir + Loki + Tempo + Grafana + Alloy) | Multi-node / HA-ish lab (mature path) |

Agent skill: `skills/observability/`.

## What you are collecting

```text
Workloads + k8s control plane
        │
   Grafana Alloy (or prometheus-agent)
        ├── metrics  → Prometheus | Mimir | Grafana Cloud Metrics
        ├── logs     → Loki       | Grafana Cloud Logs
        └── traces   → Tempo      | Grafana Cloud Traces (optional)
        │
   Grafana (UI + dashboards + alert rules)
```

**LGTM** = Loki + Grafana + Tempo + Mimir (plus a collector, usually **Alloy**).

---

## Tier 0 — Grafana Cloud Free (recommended first on 1-node)

### Why

- Almost **zero cluster RAM** for storage backends  
- Real Grafana UX, multi-signal  
- Free tier is enough to learn queries, dashboards, k8s-monitoring patterns  
- Overages are **discarded** on Free (not surprise bills) — still stay under limits  

### Free tier allowances (verify on [grafana.com/pricing](https://grafana.com/pricing/) — numbers change)

Typical always-free stack (as of 2026 docs/pricing):

| Signal | Free allowance (order of magnitude) | Retention |
|--------|-------------------------------------|-----------|
| Metrics | ~**10k active series** / month | ~**14 days** |
| Logs | ~**50 GB** ingest / month | ~**14 days** |
| Traces | ~**50 GB** ingest / month | ~**14 days** |
| Grafana users | ~**3** active | — |
| Support | Community | — |

Above Free limits on Free plan: **new samples discarded** for the month (metrics series / log GB), not silently billed. Re-check live pricing before teaching workshops.

### Architecture

```text
Cluster (single node OK)
  └── Grafana Alloy / k8s-monitoring chart
        remote_write  → Grafana Cloud Prometheus
        loki.write    → Grafana Cloud Loki
        otlp          → Grafana Cloud Tempo (optional)

Grafana Cloud UI (hosted)
  └── dashboards, Explore, alert contact points
```

No in-cluster Mimir/Loki/Tempo pods.

### Bootstrap steps

1. Create free Grafana Cloud stack (no card required for Free).  
2. In Cloud UI: copy **Prometheus remote_write** URL + user/token, **Loki** push URL + token, optional **OTLP** endpoint.  
3. Store tokens as **OOB Secrets** in the cluster (never git).  
4. Install **Grafana k8s-monitoring** Helm chart (or Alloy) with destinations pointed at Cloud.  
5. Enable only what you need first:  
   - `clusterMetrics`  
   - `clusterEvents` → Loki  
   - pod logs (alloy-logs)  
   - skip GPU/extra scrapes until series count is under control  
6. Open Cloud Grafana → Explore → confirm metrics + logs.

### Stay inside Free

| Do | Don’t |
|----|--------|
| Scrape interval 30–60s for node/kubelet | 15s everywhere |
| Use integration allow-lists / drop high-cardinality labels | Label pods with unique request IDs as metric labels |
| Sample or drop noisy namespaces (`kube-system` verbose logs) | Ingest every container log line forever |
| One cluster name label | Multiple test clusters without filters |
| Watch Billing/Usage dashboard in Cloud | Ignore discarded series panels |

### When Free is not enough

- Need >14d retention locally  
- >10k series (busy multi-tenant lab)  
- Offline / air-gapped preference  
- Want full control of retention and cost model  

→ Move to Tier 1 or 2 (or Grafana Cloud Pro with a budget cap).

---

## Tier 1 — Light self-hosted (1-node friendly)

**Goal:** local Grafana + metrics + logs **without** distributed Mimir/Loki/Tempo.

### Recommended components

| Piece | Choice | Why |
|-------|--------|-----|
| UI | Grafana Deployment (1 replica) | Same as everywhere |
| Metrics | **kube-prometheus-stack** (Prometheus) **or** **Mimir monolithic / single-binary** | Prometheus is simpler; Mimir mono is closer to Tier 2 APIs |
| Logs | **Loki SingleBinary** (1 replica) | Chart mode `singleBinary.replicas: 1`, scalable components 0 |
| Traces | **Optional** Tempo single-binary **or skip** | Traces are the first thing to cut on small boxes |
| Collector | Alloy or prometheus-operator + promtail/alloy-logs | Prefer **one** Alloy chart |

### Resource budget (order of magnitude)

On a shared single-node lab, aim roughly:

| Component | RAM ballpark |
|-----------|----------------|
| Grafana | 256–512 Mi |
| Prometheus | 1–2 Gi (retention short!) |
| Loki single | 512 Mi–1 Gi |
| Alloy | 256–512 Mi |
| **Total** | ~2–4 Gi **extra** on top of apps |

Tune:

- Prometheus retention **7–15 days**, small PVC or emptyDir for experiments  
- Loki retention short; filesystem or small MinIO bucket  
- Disable kube-state-metrics extras you do not use  

### Lightweight Mimir note

Full **distributed** Mimir (ingester + store-gateway + compactor + … × N) is a bad fit for 1 node. If you want Mimir specifically:

- Prefer **monolithic** / single-process mode from the official Helm chart, **or**  
- Stay on Prometheus until you have a second NVMe node  

Loki **SimpleScalable** with multiple write/backend replicas is also heavy for 1 node — use **SingleBinary**.

### Architecture

```text
Alloy ──remote_write──► Prometheus (or Mimir mono)
Alloy ──loki.write───► Loki SingleBinary
Grafana ──datasources──► both (in-cluster URLs)
```

### GitOps placement

`cluster-gitops/infra/apps/{grafana,loki,kube-prometheus or mimir,k8s-monitoring}/`

---

## Tier 2 — Full LGTM (mature multi-node pattern)

This matches a **production-shaped homelab**: distributed backends, object storage for blocks, Alloy via **k8s-monitoring**, RF=1 dual-write style when only two NVMe nodes exist.

### Components

| Component | Role | Typical mode |
|-----------|------|----------------|
| **Grafana** | UI, dashboards, alerting | 1+ replica |
| **Mimir** | Long-term Prometheus-compatible metrics | Distributed, classic (no Kafka ingest unless you choose it) |
| **Loki** | Logs | SimpleScalable or distributed |
| **Tempo** | Traces | Distributed |
| **Alloy** (k8s-monitoring chart) | Scrape + ship metrics/logs/traces/events | DaemonSets + deployments |
| **MinIO / S3** | Blocks for Mimir/Loki/Tempo | Off-cluster NAS or in-cluster MinIO |
| **prometheus-operator CRDs** | ServiceMonitor / PodMonitor | CRDs only if needed |

### RF=1 dual-node pattern (important)

When only **two** storage-capable nodes exist:

- Set **replication_factor: 1** on Mimir/Loki/Tempo  
- Run **2** write-path pods (ingesters / write) pinned to those two nodes  
- Load is split; **unflushed WAL on a dead node can still be lost**  
- Object storage holds **flushed** blocks (durable once compacted/uploaded)  
- This is **not** the same as RF=2/3 HA  

Document for learners:

> RF=1 + 2 pods = better availability for *new* writes after ring timeout, not zero data loss on node death.

When a third NVMe node exists → plan RF=3 and 3 pods.

### Storage split

| Data | Where |
|------|--------|
| WAL / working set | Local NVMe PVC (strict-local / hostpath class) |
| Blocks / chunks / indexes | S3 API (MinIO on NAS or dedicated) |

Never put large block stores only on tiny root disks.

### Alloy / k8s-monitoring destinations (shape)

```yaml
# Conceptual — pin chart version; schema differs 3.x vs 4.x
cluster:
  name: lab-prod

destinations:
  - name: local-mimir
    type: prometheus
    url: http://mimir-gateway.../api/v1/push
  - name: local-loki
    type: loki
    url: http://loki-gateway.../loki/api/v1/push
  - name: local-tempo
    type: otlp
    url: http://tempo-distributor...:4317

clusterMetrics:
  enabled: true
  destinations: [local-mimir]
clusterEvents:
  enabled: true
  destinations: [local-loki]
alloy-logs:
  enabled: true
alloy-metrics:
  enabled: true
# Optional: ServiceMonitor scrape via prometheusOperatorObjects
```

### Optional dual-write (advanced)

Alloy can remote_write to **both** local Mimir and Grafana Cloud for:

- Local fast queries + Cloud backup/share  
- Migrating off Free tier gradually  

Keep cardinality low or Cloud Free will discard.

### Footguns (full stack)

1. Chart major (k8s-monitoring 3.x list destinations vs 4.x map) — pin and read changelog.  
2. OOM on single node if you copy multi-node replica counts.  
3. MinIO credentials OOB; reloader annotations help rotations.  
4. ServiceMonitor CRDs missing → no operator scrapes.  
5. High-cardinality pod labels → Mimir/Prometheus explosion.  
6. Expecting RF=1 to survive node loss without gaps.

---

## Decision matrix

| Topology | Start with | Later |
|----------|------------|--------|
| A — 1× Proxmox everything | **Tier 0** Cloud Free | Tier 1 if offline needed |
| B — Proxmox + bare metal Talos | Tier 0 or **Tier 1** | Tier 2 when RAM/disk allow |
| C — 3× Talos + Proxmox | Tier 1 then **Tier 2** | RF=3 when 3 NVMe |

| Goal | Tier |
|------|------|
| Learn PromQL/LogQL fast | 0 |
| Air-gapped weekend lab | 1 |
| Mimic production LGTM | 2 |
| Agent demos only | 0 (least distraction) |

---

## Minimal verify checklist

```bash
# Tier 0
# Cloud Explore: up{job=~".*"} and {cluster="lab-prod"}

# Tier 1/2
kubectl -n observability get pods   # or your ns
kubectl get svc -A | rg -i 'grafana|loki|mimir|tempo|alloy'
# Grafana → Connections → test datasources
```

## Related

- Skill: `skills/observability/`  
- Hardware: `docs/platform/hardware-topologies.md`  
- GitOps apps live under `cluster-gitops`  
- Secrets: `skills/out-of-band-secrets/`  
