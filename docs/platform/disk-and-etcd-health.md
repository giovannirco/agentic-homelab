# When a cluster "never feels stable": disks, etcd, and what monitoring missed

A three-node cluster of small PCs ran for most of a year with kubectl timeouts, nodes going NotReady together, and apps that restarted for no clear reason. A read-only investigation found the causes. None of them was Kubernetes. This page is the method and the findings, so you can run the same check on your own cluster before it surprises you.

## Findings, in order of damage
1. **A consumer NVMe that stopped completing I/O, for five days, without failing.** The drive stayed "live" to the kernel: 100 % busy, zero reads or writes completed, about 400 requests in flight. Every pod with data on it hung; three applications were down. Nothing alerted, because the usual alerts watch for full disks and failed disks, not for a disk that is busy doing nothing.
2. **etcd on DRAM-less SATA SSDs** shared with the container runtime. etcd logged 491–706 "apply request took too long" lines per node in about 12 hours and `fdatasync` calls of 1.2–3.8 seconds. etcd's guidance is a WAL fsync p99 under **10 ms**. A large image unpack on a control plane was enough to stall the API.
3. **Memory limits at 154–258 % of each node's RAM.** OOM kills every day.
4. **Crash-looping workloads** (thousands of restarts a month each), which means constant writes to etcd on the slow disks.
5. **Monitoring with two blind spots:** etcd wasn't scraped at all, and the kernel log on the worst node was flooded by audit messages, which pushed any disk error out of the buffer.

## The method (read-only)
Do it in this order. Each step narrows the next.

1. **Pressure first.** `/proc/pressure/io`, `/proc/pressure/memory`, `/proc/pressure/cpu` on each node. "some" I/O pressure near 98 % with CPU pressure under 1 % says "a device", not "too much load".
2. **Is the disk finishing anything?** Read `/proc/diskstats` twice, ten seconds apart. Compare the completed reads and writes, not the busy percentage. Then `/sys/block/<dev>/inflight`.
3. **When did it start?** Query the metrics history for the minute the completion rate went to zero. That minute tells you what else happened (a deploy, a reboot, a backup).
4. **etcd's own opinion.** Count "apply request took too long" and "slow fdatasync" in the etcd log per node, and look at the durations. Check the raft term: thousands of elections mean a long history of leader changes.
5. **Capacity that was promised.** `kubectl describe nodes` → "Allocated resources": memory limits as a percentage of the node.
6. **Who restarts.** Restart counts per pod over 30 days.

On Talos all of this is available through the API (`talosctl read /proc/…`, `talosctl logs etcd`) without a shell on the node.

Keep the raw outputs next to the write-up. The conclusions will be questioned later, usually by you.

## Two alerts that would have caught it
```promql
# a disk that is busy and completes nothing: fires in 10 minutes instead of 5 days
rate(node_disk_io_time_seconds_total[10m]) > 0.9
  and (rate(node_disk_reads_completed_total[10m]) + rate(node_disk_writes_completed_total[10m])) == 0

# etcd's disk is too slow (scrape etcd first; many setups don't)
histogram_quantile(0.99, rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])) > 0.05
```
And ship kernel logs off the node, so a flood of one message type can't hide the line that matters.

## What to buy, and what to stop using
| Part | Verdict |
|---|---|
| Efficient 8-core mini PCs | Fine. CPU pressure was under 1 %. |
| DRAM-less SATA SSDs for etcd | Stop. Small synchronous writes are exactly what they are worst at. |
| The cheapest NVMe for data | The one that hung was a DRAM-less model. A drive with power-loss protection is the right home for etcd; a mainstream TLC drive with DRAM is the minimum. |
| 32 GB per node | Enough only if limits are honest. |

A likely cause for the hang (not proven, because the kernel log was lost) is a power-state transition bug that affects several consumer NVMe controllers; the usual mitigation is the kernel argument `nvme_core.default_ps_max_latency_us=0`. Label a cause like this as a hypothesis in your notes until a log confirms it.

## Rules that came out of it
- A control plane that also runs workloads needs a disk for etcd that the workloads can't saturate.
- Roll out large images one at a time on nodes where the container runtime shares a disk with etcd.
- Don't reboot a control plane as a health fix. Find out what it is waiting for first; a dirty power-off can leave a filesystem in a long check.
- "Healthy" in the dashboard and "working" are different claims. Test the application path.

## References
- etcd hardware guidance: https://etcd.io/docs/v3.6/op-guide/hardware/
- Pressure stall information: https://docs.kernel.org/accounting/psi.html
- Related: [hardware-topologies.md](hardware-topologies.md) · [13-observability.md](../setup/13-observability.md) · lessons 71–76 in [hard-won.md](../lessons/hard-won.md)
