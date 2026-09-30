# Operational footguns

Recurring failures worth preventing on day one.

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
9. **Do not DNAT all of DNS on a “servers” VLAN** without excluding the DNS servers themselves (forwarder blackhole). Better: resolvers on a **dedicated DNS network**, redirect "dst not DNS network" everywhere else.
10. **Cluster must resolve internal hostnames to in-cluster/LAN** or agents get Cloudflare 400s calling public URLs from pods.

## Network & hardware

39. **Check error counters before blaming Wi-Fi.** A LAN that's slow while the internet is fast on the same Wi-Fi → look at uplink rx_errors/drops; swap port roles to see if the fault follows the cable or the port.
40. **Re-check negotiated link speeds after any cable work**: a marginal patch cable links at 100 Mb/s and looks like a flaky server.
41. **Your admin path is part of the change**: laptops auto-join old SSIDs; a display's USB Ethernet sleeps. Wire into a management-only break-glass port.
42. **Temporary second IP** on the controller before renumbering its own network; dead-man switch before changing a remote host's network.
43. **NFS mounts keep their old source IP** after a host re-IP → hang; lazy-unmount and remount.
44. **CGNAT:** many ISPs will remove it if you ask for a dynamic public IPv4; still double NAT behind the ISP router → DMZ to your gateway's (pinned) WAN IP.
45. **Controller APIs can ignore fields silently** (e.g. UniFi `setting_preference: auto`): read back after every write.
46. **An internet speed test measures one path.** Fast speedtest + slow LAN copies → test same-VLAN vs routed against your own iperf3 box ([testing](../network/testing-and-benchmarks.md)).
47. **Keep a control.** A second AP on the same SSID/band/room settled in minutes what theories didn't in hours. When a user has a control measurement, it beats the agent's plausible theory.
48. **UDP loss % is the honest number**; TCP hides loss behind retransmits. Smaller packets doing *worse* = a packets-per-second limit (CPU/forwarding), not bandwidth.
49. **Pin your 6 GHz channel.** On auto, a 160 MHz radio can quietly run 80 MHz; pinning doubled real throughput. On an empty 6 GHz band, which channel barely matters.
50. **Thin/flat patch cables may hold 1G but not 2.5G.** Check the negotiated speed after every cable change.
51. **Set the switch-port profile before plugging in** a host with a DHCP reservation on another VLAN; otherwise it takes a lease on the default network (fix: bounce the port).
52. **Private Wi-Fi MACs change per SSID** (and rotate), breaking MAC-based admin rules: use hardware MACs on admin devices.
53. **A NAS static route broader than its own subnet** (e.g. a /16 via the gateway, consulted before the connected route) sends same-subnet traffic through the gateway; the flows become asymmetric and stateful firewalls drop them. Add a more specific on-link route for the local subnet.
54. **ConnectX-3 NICs silently drop tagged VLANs** with Proxmox's default `bridge-vids 2-4094` (fixed hardware VLAN filter). Limit the range.
55. **Multi-homed test hosts need source routing and per-address servers**, or replies leave the wrong interface and UDP tests fail.

## Storage

11. **HA disks ≠ free HA** — multi-replica RWO over slow links fails; local path + app-level HA may be better.
12. **Never put Galera/data dirs on NFS.**
13. **NFS root_squash** — do not initContainer chown; match app UID.
14. **Strict-local volumes** pin pods to nodes; wrong node → Pending/faulted forever.
15. **Backups are mandatory even with 2 replicas** — HA is not backup. **Never back up to RAID0**, and restore-test once.

## Databases

16. **One operator per engine cluster-wide** — dual mariadb-operators fight (CrashLoop, rewritten STS).
17. **Agent/init images must match operator version** for Galera.
18. **Shared platform DB vs dedicated** — small apps share; large tenants get own CNPG.
19. **LAN LoadBalancer VIP for DB only when clients need it** (Cilium LB-IPAM) — default ClusterIP.

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

37. Write postmortems for yourself — keep them next to the issue that fixed them.
38. Prefer boring patterns you can explain under pressure.
