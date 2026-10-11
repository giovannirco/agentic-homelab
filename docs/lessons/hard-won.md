# Operational footguns

Recurring failures worth preventing on day one. The numbers are stable identifiers in order of discovery, not a reading order; sections are by topic.

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
56. **Find where packets die with interface counters, not theories.** Diff `/proc/net/dev` on the AP before/after an iperf3 run: a radio `tx_errors` rate of 35–63% vs 0.02% on an identical AP proved a faulty unit after a factory reset changed nothing.
57. **One `top` frame lies** on small devices (it includes your SSH login): use `top -bn2 -d 4`.
58. **A switch cable from the old network in a new trunk port merges both LANs** (two DHCP servers, two spanning trees). After any cable move check the port's learned MACs and PoE draw; disable first, investigate after.
59. **UniFi saves a settings page as one form**: one invalid field (e.g. an empty SNMP v1/v2c community while enabling v3) makes every change on that page fail.
60. **Give the printer its own network**: it's the least-patched device in the house. DNS only, no internet, print/scan ports from the people network.
61. **Firewall zones can't separate devices on the same VLAN**: if two device types shouldn't talk, they need different networks, not a rule.
62. **Use your country's regulatory domain.** Rules change (e.g. Brazil limits 6 GHz Wi-Fi to 5925–6425 MHz from 2027); pick channels that stay legal.

## Netboot and second-hand hardware

87. **A gateway's "network boot" option is one filename per network**, so it serves UEFI or BIOS, not both. A proxyDHCP answers only the PXE part and can serve each firmware its own file ([omni-and-netboot](../platform/omni-and-netboot.md)).
88. **Never write iPXE scripts through an SSH heredoc**: the local shell expands every `${…}` to nothing and the menu boots into "nothing to boot".
89. **Slot labels and slot sizes prove nothing.** Read the memory channels from EDAC and measure; read `LnkSta` for every PCIe slot. A physical x4 slot wired as Gen 2 x1 caps a 10 GbE card at 3–4 Gbit/s ([know-your-hardware](../platform/know-your-hardware.md)).
90. **A tool's "initialise" step can reset the device it reads** (a power supply's protection and fan modes, in our case). Read the source before pointing a vendor tool at hardware.
91. **Adopting a switch into a new controller replaces its port configuration.** Save the old port overrides as data and re-apply them right after adoption, or trunks become "all networks".
92. **Moving the wrong end of an uplink joins two routers on one subnet.** Before enabling a port after a cable move, read its LLDP neighbour.
93. **An immutable OS can't do one-time hardware chores** (RGB, firmware tools, undervolting): no I2C device nodes, no `/dev/mem`. Do them once from a netbooted live Linux.
94. **Test RAM sticks one at a time before planning around the new total.** A two-stick upgrade that didn't boot ended a planned change; a stick taken from a dead machine is a suspect, not a spare.

## Storage

11. **HA disks ≠ free HA** — multi-replica RWO over slow links fails; local path + app-level HA may be better.
12. **Never put Galera/data dirs on NFS.**
13. **NFS root_squash** — do not initContainer chown; match app UID.
14. **Strict-local volumes** pin pods to nodes; wrong node → Pending/faulted forever.
15. **Backups are mandatory even with 2 replicas** — HA is not backup. **Never back up to RAID0**, and restore-test once.

## Disks and etcd

71. **A disk can be 100 % busy and complete nothing, for days, without failing.** Alert on "busy and zero completions", not only on full or failed ([disk-and-etcd-health](../platform/disk-and-etcd-health.md)).
72. **etcd on DRAM-less SATA SSDs:** `fdatasync` took 1.2–3.8 s where etcd wants a p99 under 10 ms. Give etcd a drive with power-loss protection, and don't share it with the container runtime.
73. **Scrape etcd, and ship kernel logs off the node.** One message type flooding the kernel buffer hid the disk errors that would have explained a five-day outage.
74. **Memory limits at 150–250 % of a node's RAM are a schedule of OOM kills**, not headroom.
75. **Large image unpacks on a control plane stall the API** when the runtime shares a disk with etcd. Roll heavy images out one at a time.
76. **The kubelet evicts at 15 % free on the image filesystem.** A model cache inside a container fills a small node disk in an afternoon; caches and environments belong on network storage.
105. **A ZFS pool on a client SSD under VMs needs TRIM more often than monthly.** The installer's pool had `autotrim` off, and the distribution trims on the first Sunday of the month. Fifteen small VMs ran a day without trouble; then, in three minutes and with no change in load, I/O pressure went from 0 to 18 %, and to 50 % by noon: 43 ms per write. One `zpool trim` (2 min 18 s) brought it to 9 ms. Check `zpool get autotrim` and `zpool status -t` on any pool an installer made.
106. **Seven etcd members at rest ask a drive for about ninety flushes a second.** Workers ask for almost none. Size the control planes' disk by flushes, not by megabytes.

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

## Agents: long sessions

95. **A goal file with a checkable "done when"** and a resume routine survives what chat history doesn't ([long-sessions](../agents/long-sessions.md)).
96. **A plausible theory is a hypothesis until measured.** Label which one you are reporting (see also 47).
97. **Keep the runs that went wrong**, named and explained. A labelled bad benchmark is evidence.
98. **Blocked is not the end.** Say what is blocked, try another route, and never swap in a weaker source without saying so. The operator asked for the real thing.
99. **Redact at the source.** Inventory commands print credentials (kernel command lines, environment dumps); a scratch file is still a file.
100. **Background waiters wait on a PID or a file**, never on a process-name search that matches their own command line.
101. **"Waiting for the operator" is a list, not a stop.** Write the question down and continue with what doesn't depend on it.
102. **Operator corrections go into the repo's instruction file**, where every agent reads them, not only into one agent's memory.

## Upgrades

29. **Talos minor gates max k8s** — no skip minors.
30. **Upgrade Talos before k8s when required by catalog.**
31. **Review bootstrap manifests after k8s bumps** — do not replace Cilium with a default CNI.
32. **GPU nodes need per-minor extension schematics.**

## Talos and Omni

63. **Omni's domain and account ID are the machines' identity.** Changing either disconnects every machine; recovery needs break-glass configs and a CA rotation.
64. **The join token is in the kernel command line of every netbooted node, and any pod can read `/proc/cmdline`.** The console prints it during enrolment too. Redact it in scripts, screenshots and chat.
65. **Talos 1.13+ needs an x86-64-v2 CPU.** A VM created with the hypervisor's oldest CPU type panics at boot.
66. **Maintenance mode asks for DHCP on every NIC.** Pin interfaces in a patch; a MAC selector also matches VLAN interfaces on that NIC unless you add `physical: true`.
67. **L2 announcements on a NIC without an IP fail after five idle minutes:** the NIC never transmits, switches forget its MAC, frames flood to every node and every node answers. Send a keepalive ARP, or use BGP ([loadbalancer-l2-vs-bgp](../platform/loadbalancer-l2-vs-bgp.md)).
68. **BGP graceful restart makes a hard node loss slower than L2** (23.8 s against 16.5 s; 2 s with a 3 s hold time and graceful restart off).
69. **Fast failover of the address doesn't fix slow failover of the endpoints:** with `externalTrafficPolicy: Cluster` a dead node's pods stay endpoints for about 40 s.
70. **A CNI in exclusive mode silently renames another CNI's config file** (Multus beside Cilium), and changing the chart value doesn't restart the agents by itself.

## GPUs and local AI

77. **Two cards of the same model are not twins.** Profile each alone: seconds until the first throttle flag, and at what temperature ([gpu-node-local-ai](../platform/gpu-node-local-ai.md)).
78. **Read the throttle reason and its lifetime counter**, not only the temperature. A card can throttle well below its target.
79. **Log temperature beside every benchmark.** The same test read 1,010 tokens/s early and 449 at the end of a long sweep.
80. **An LLM server may cut an oversized prompt and answer anyway.** Ask for an error instead, and check the prompt token count in the response.
81. **Choose power limits on real jobs.** A synthetic sweep promised a card 10 °C cooler for 13 % less work at one limit; real jobs lost 17–22 % there and ran one degree cooler.
82. **GPU knobs need a privileged pod and are lost at reboot.** Re-apply them from a small DaemonSet kept in git.
83. **System RAM, not GPU memory, was the first limit.** One GPU app at a time, the others scaled to zero.
84. **The same input returns from cache.** Vary the seed when timing, and treat an impossible number as a bug in the test.
85. **Read a model's licence in its own repository on the day you use it.** Labels on mirrors were wrong, and licences change between versions of the same family.
86. **Kubernetes injects `<SERVICE>_PORT=tcp://…` into every pod of the namespace.** A tool that reads that name as a number breaks; set `enableServiceLinks: false` ([mcp-on-the-lan](../agents/mcp-on-the-lan.md)).

## Process

33. **One theme per session** beats “fix everything.”
34. **Issues with full install context** beat tribal memory.
35. **First-login checklists** — deployed ≠ usable.
36. **Pin latest stable on install** — blog posts freeze ancient tags.

103. **Status lines rot first.** A plan still titled "not executed" after it ran, or a recovery document that says "fall back to the old network" after the old network is gone, will mislead the next person at the worst moment. Re-read plans and recovery notes after every migration step.
104. **A run record beats a plan.** Keep both: the plan says why, the record says what was typed and what came back.
107. **Read the history before naming a cause.** A snapshot gives you an explanation that fits; the record tells you whether it can be true. Find the minute it began and ask what changed at that minute, and what did not. The explanation "too many databases on one drive" fitted ten seconds of statistics and could not explain the sixteen quiet hours before them.
108. **A baseline you promise in a write-up is a baseline you take** before anyone quotes the write-up. The one that was owed here overturned the conclusion.
109. **A sentence about live state needs a live check and a date.** "Backups run daily" was copied from note to note for two months after the backup tool had stopped existing in the cluster.
110. **A number needs a record wherever it appears,** titles included. Forty video titles had passed a linter for length and shape; four contradicted the project's own run records and nine had no source at all.
111. **Config written by hand on a guest is committed the day it is written.** One log collector's three files existed only on a host that died; they were recovered from the transcript of the agent session that had typed them.
112. **A blocklist inflates the count of what it blocks.** One TV made 5,000 DNS lookups in a day; 3,863 were retries for two refused logging hosts. "It phones home N times a day" describes the block as much as the device.
113. **Copying a folder from a Mac with `tar` adds a hidden `._name` file beside each entry.** A program that reads every file in a config directory will choke on one. `COPYFILE_DISABLE=1 tar …` (the Mac's own `tar -t` hides them, so check with another reader).

## Platform: many small clusters, GitOps, addressing (2026-10-07 → 10-11)

114. **One cluster per owner, one GitHub App per owner** keeps a tenant's mistakes and credentials inside its own walls; the cost is a generator that renders every cluster's platform from one data file. Make that generator the only way platform files change.
115. **Before the first live step of a fleet-wide change, make the generator prove it changes nothing.** Add the new values beside the old ones with a phase switch per cluster (old / both / new); re-render every cluster at `old` and diff against Git: byte-identical, or stop.
116. **Changing an ApplicationSet's generator deletes the Applications it stops generating, PVCs included,** when the Applications carry the resources finalizer. Set `preserveResourcesOnDeletion` or move apps one by one.
117. **Local ZFS volumes through Proxmox CSI follow a pod only between VMs of the same host.** Plan nodes per host; a bare-metal node takes none.
118. **A single-node cluster out of memory fails as a crash-loop storm** (every leader-elected controller restarting, etcd slow), not as tidy OOM kills of an app. Alert on node memory, not only on the symptoms.
119. **`mc admin policy create` replaces the policy.** A script that recreates storage policies must know every bucket a client really uses, or it silently cuts its backups.
120. **A DNS updater that only adds (external-dns over RFC2136 without zone transfer) leaves the old A record when an address changes:** every name answers a live and a dead address, and browsers hide it. Delete the old records in the same step.
121. **Shrink a VLAN's subnet before you carve a routed pool out of the same /24:** while the VLAN is still /24, the new pool is on-link for every machine on it and nothing routes to the BGP next hop.
122. **Uploading an FRR config to a UniFi gateway resets every BGP session (~2 s), not just the changed peer:** batch all clusters into one upload.
123. **After a lone control plane changes its IP, restart kube-apiserver.** It reads its advertise address at start, so the `kubernetes` Service keeps pointing at the old one and every in-cluster API client crash-loops.
124. **A rehearsal only proves what you look at.** The throwaway cluster looked fine at 60 s; the real problem showed up minutes later in controllers nobody checked.
125. **Long `kubectl exec` streams through an API proxy die at exactly one hour.** Move big volumes node-to-node over the LAN instead, and restart nothing from zero by hand.
126. **A Cloudflare tunnel only serves zones in its own account,** so moving a zone between accounts is a tunnel change first and a nameserver change last; and an account may hand a new zone a different nameserver pair from its siblings.
127. **An API token cut for named zones can't see a zone added to the account later.** Tools using it skip the new zone silently. Update the token's policies when a zone joins.
128. **"Any valid service token" in an access policy lets every token in the account through,** including one you minted for a single friend and a single host.
129. **Gateway features can flip their default between patch releases.** Envoy Gateway 1.9.2 needs Lua enabled where 1.9.1 didn't; routes using it answer 500. And a Helm change to a controller's ConfigMap is not live until the controller restarts.
130. **Multus beside Cilium: patch the node before plugging the NIC, let Cilium share the CNI before installing Multus.** Otherwise the node takes an address on a house network, or Cilium renames Multus' config away.
131. **A metric that reads zero may be the query.** `rate()` of a gauge is ~0 whenever the gauge is steady; check freshness (`timestamp(up)`) before declaring an ingest outage.
132. **Say only what you saw.** "It was working all along, just not logging" is a claim about a pod nobody measured; write what was observed and what is unknown.

133. **One cause, one alert.** When an API stall restarts every controller, per-pod "crash loop" rules send a dozen lines. Write the cause rule (several control-plane pods restarting together; etcd write latency) and suppress the symptom rule with `unless on (cluster)` while it holds.
134. **An alert is a sentence:** what, where, how much, since when, the first step. Without a value and a time it is a notification, not information.
135. **The monitoring system must not page about itself many times.** Rules keep their last state when the backend errors; one dedicated rule reports "the metrics backend is down, alerts are blind".
136. **Validate a monitoring backend's config before rolling it.** A key that existed in an older major version crash-looped the metrics store for twelve minutes.
137. **Put etcd on a disk nobody else hammers.** On a cheap QLC drive shared with every guest, its fsync p95 was 348 ms; on an idle drive in the same host, 13 ms, after one online disk move.
138. **Collector annotations are not universal.** Grafana's k8s-monitoring discovers `k8s.grafana.com/scrape`, not `prometheus.io/scrape`; check that a target is actually scraped before writing alerts on it.

## Career

37. Write postmortems for yourself — keep them next to the issue that fixed them.
38. Prefer boring patterns you can explain under pressure.
