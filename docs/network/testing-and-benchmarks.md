# Network testing: a test box on every VLAN, and one benchmark score

"The internet speed test is fine" tells you almost nothing about your LAN. An internet test measures one path (device → Wi-Fi → gateway → ISP). Copying from your NAS uses another (device → Wi-Fi → AP uplink → gateway routing → storage VLAN). Problems hide in the difference.

This page gives you two tools:
1. A **test container with one address per VLAN, same last octet everywhere** (e.g. `.25`), running iperf3/iperf2 (server and client) and optional browser speed tests.
2. A **repeatable benchmark with one score** ([`scripts/netbench.py`](../../scripts/netbench.py)), so "is it better now?" has a number.

## 1. Same-network vs routed, in one command
With the box at `<subnet>.25` on every VLAN:

| Target | Measures |
|---|---|
| `<your-vlan>.25` | device → Wi-Fi/switch → box. **No router in the path** |
| `<servers-vlan>.25` | device → gateway routing + zone firewall → box |

If routed is much worse than same-network, the problem is between the device and the gateway (AP uplink, trunk, gateway CPU), not the radio.

## 2. Build the box (Proxmox LXC, unprivileged)
- `net0` on the servers VLAN with a gateway; one extra NIC per VLAN, static `<subnet>.25/24`, **no gateway**, named after the network (`main`, `iot`, `guest`…). Skip networks it has no business joining (DNS-only, DMZ, load-balancer ranges).
- `/etc/sysctl.d/90-multinic.conf`:
  ```
  net.ipv4.ip_forward = 0
  net.ipv4.conf.all.arp_ignore = 1
  net.ipv4.conf.all.arp_announce = 2
  net.ipv4.conf.all.rp_filter = 2
  ```
- **Source routing** so replies leave the way requests came in (one table per address):
  ```bash
  ip route replace <subnet>/24 dev <if> table <n>
  ip route replace default via <subnet>.1 dev <if> table <n>
  ip rule add from <subnet>.25 table <n> priority 100
  ```
- **nftables inside the CT:** unrestricted on the admin interfaces; on every other VLAN only the test ports (iperf3 5201–5210, iperf2 5001, web 80/3000) and ICMP, **in and out**. The box can't be used as a pivot between networks.
- **One iperf3 server per address:** a systemd template `iperf3@.service` with `ExecStart=/usr/bin/iperf3 -s -p 5201 -B %i`, then `systemctl enable --now iperf3@<ip>` for each address. Same for `iperf -s` / `iperf -s -u` on 5001 if you have iperf2-only peers (many NAS boxes).
- **Client helper** so the box can *act as* a device on any VLAN:
  ```bash
  # iperf-from <vlan> <target> [iperf3 args]
  src=$(ip -4 -o addr show dev "$1" | awk '{sub("/.*","",$4); print $4}'); t=$2; shift 2
  exec iperf3 -B "$src" -c "$t" "$@"
  ```
- Optional browser tests: LibreSpeed (tunable duration/streams) and OpenSpeedTest (static files + nginx). **Read the code before installing** any speed-test project: what the JS sends, and where; external URLs; eval/beacons.
- Clone the box to other hosts with `vzdump` + `pct restore --unique` and a different last octet (`.26`, `.27`), e.g. one on a 1G host and one on a 10G host.

## 3. Traps we hit
- **Asymmetric replies:** without source routing, a request to the servers-VLAN address arrives via the gateway, but the reply leaves directly on the client's VLAN. Tests look routed but aren't, and UDP breaks.
- **iperf3 UDP on multi-homed hosts:** a wildcard-bound server replies from whatever address the routing table picks → `unable to read from stream socket`. Bind one server per address.
- **Mellanox ConnectX-3 hosts:** a fixed hardware VLAN filter (~128 IDs); Proxmox's default `bridge-vids 2-4094` makes **every tagged VLAN silently fail**. Set `bridge-vids` to the range you use.
- **Unprivileged CTs** can't raise `net.core.rmem_max` (host setting).

## 4. How to measure (iperf3 cheat sheet)
```bash
iperf3 -c <ip> -P 4            # upload, 4 streams
iperf3 -c <ip> -P 4 -R         # download
iperf3 -c <ip> --bidir         # both at once
iperf3 -c <ip> -u -b 300M -R   # UDP: look at Lost/Total %; this is the honest number
iperf3 -c <ip> -t 60 -O 3 -i 5 # longer run, skip ramp-up, report every 5 s
```
Other knobs: `-l` (packet size: small packets stress packets-per-second), `-w` (window), `-M` (MSS), `-S 0xB8` (DSCP), `-n 2G` (fixed amount), `-Z` (zero-copy), `-J` (JSON).

**Method:** one variable at a time; keep a **control** (a second AP, a wired client, a path that avoids the suspect link); check port error counters and negotiated link speeds first; when changing radios, confirm from the controller which AP/band the client is actually on (macOS hides the SSID from scripts, and radio changes make it roam).

## 5. NetBench: one number
`scripts/netbench.py --target <ip> --label "<where/what>"` runs 8 iperf3 tests (TCP 1 and 4 streams each way, bidir, UDP 200M up/down and 600M down) plus ping at idle and **ping during the download test** (bufferbloat), saves raw JSON, and prints:

**score = geometric mean of the 5 TCP results (Mbit/s) × (1 − mean UDP loss)**

The geometric mean stops one great test from hiding a bad one; UDP loss penalises links that are fast but drop packets. Latency is reported next to the score, not folded in. Compare runs with `--compare benchmarks/*.json`.

Example from a real hunt (same Wi-Fi client, same AP): same-VLAN target **339**, routed target **65**, which pointed straight at the AP's uplink path. The unit turned out to be faulty.
