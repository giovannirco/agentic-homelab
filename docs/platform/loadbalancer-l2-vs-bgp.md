# LoadBalancer IPs: L2 announcements or BGP, measured

[networking-decisions.md](networking-decisions.md) picks Cilium LB-IPAM with L2 announcements as the default. This page is what happened when both were measured on the same hardware, and the traps of each.

Tested 2026-10 with Cilium 1.20 (L2 announcements, and the BGP control plane with v2 CRDs), MetalLB 0.16 in FRR mode, Talos 1.14, and a home gateway that runs FRR's `bgpd`.

## The numbers
A client ran `curl` in a loop against a LoadBalancer IP while the node that owned it was powered off.

| Setup | Outage after a hard node loss |
|---|---|
| L2 announcements (Cilium defaults) | 16.5 s |
| BGP, hold time 9 s, graceful restart on | 23.8 s |
| BGP, hold time 9 s | 7.3 s |
| BGP, hold time 3 s | 2.0–2.2 s |
| Planned drain, `externalTrafficPolicy: Local` | 0.2 s |

Two things to take from the table. L2 is fine for a home: 16 seconds once in a while is not an incident. And **BGP with the wrong option is worse than L2**: graceful restart tells the gateway to keep a dead speaker's routes as "stale" for the restart time, which is the opposite of what you want when a node dies.

## Which one
| | L2 announcements | BGP |
|---|---|---|
| Needs from the gateway | nothing | a BGP daemon you can configure |
| Addresses | a range inside a VLAN the nodes are attached to | a range that is **not** a network anywhere; the gateway learns /32 routes |
| Load spreading | one node owns each IP | ECMP across every node that advertises it |
| Failover | ~15–20 s (lease timings) | ~2 s with a 3 s hold time |
| Moving parts | a pool + a policy | an AS per cluster, peer groups, prefix lists, timers |

Start with L2. Move to BGP when you have more than one cluster behind the same gateway, or when the 16 seconds matter.

## L2 on a dedicated VLAN: the trap that costs a day
Giving the nodes a second NIC on a load-balancer VLAN, **with no IP address on it**, keeps the VIPs in their own firewall zone. It works until the cluster has been idle for five minutes:

- **Symptom:** connection resets after idle time. A packet capture shows one SYN answered by several nodes.
- **Cause:** a NIC without an address never transmits. Its MAC ages out of every bridge and switch (300 s), so frames for the VIP are flooded to all nodes, and all of them answer.
- **Check:** the forwarding table of the switch or hypervisor bridge has no entry for the NIC's MAC.
- **Fix:** a small host-network DaemonSet that sends one gratuitous ARP probe from that NIC every 60 seconds (`arping -D -c 1 -I <lb-nic> <lb-gateway>`). Or use BGP.

Other L2 notes:
- The reply leaves through the node's default route, not the LB VLAN. A stateful gateway accepted this asymmetry in our tests; check yours.
- Select the interface exactly in the policy (`interfaces: ["^<lb-nic>$"]`), and exclude control planes with a `nodeSelector` in clusters whose control planes run nothing else.
- Cilium drops VLAN-tagged frames on its devices unless the VLAN is listed in `bpf.vlanBypass`.

## BGP with a home gateway
Design that stayed simple:
- one network per cluster for its nodes, and one LB range per cluster that exists only as BGP routes;
- one private AS for the gateway, one per cluster;
- on the gateway, per cluster: a peer group with a **listen range** (the node network, so new nodes peer without config), an inbound prefix list that accepts only that cluster's LB range, and **deny-all outbound** (nodes keep their DHCP default route);
- only workers advertise, in clusters whose control planes run nothing else.

```text
router bgp <gateway-as>
 no bgp default ipv4-unicast
 bgp bestpath as-path multipath-relax
 neighbor CL-A peer-group
 neighbor CL-A remote-as <cluster-a-as>
 neighbor CL-A timers 3 9
 bgp listen range <cluster-a-nodes-cidr> peer-group CL-A
 address-family ipv4 unicast
  neighbor CL-A activate
  neighbor CL-A route-map CL-A-IN in
  neighbor CL-A route-map DENY-ALL out
  maximum-paths 8
 exit-address-family
ip prefix-list CL-A-LB seq 10 permit <cluster-a-lb-cidr> le 32
route-map CL-A-IN permit 10
 match ip address prefix-list CL-A-LB
route-map DENY-ALL deny 10
```

Cluster side, either:
- **Cilium:** `bgpControlPlane.enabled: true`, then a `CiliumBGPClusterConfig` (local AS, the peer = the node network's gateway), a `CiliumBGPPeerConfig` (`holdTimeSeconds: 3`, `keepAliveTimeSeconds: 1`, **`gracefulRestart.enabled: false`**) and a `CiliumBGPAdvertisement` for `LoadBalancerIP`;
- **MetalLB** (any CNI): FRR mode, an `IPAddressPool`, a `BGPPeer` with `holdTime: 3s` / `keepaliveTime: 1s`, a `BGPAdvertisement`. Its namespace needs the `privileged` Pod Security label.

## Traps
- **Graceful restart lengthens hard failures** (the table above).
- **New timers need a session reset** on the gateway (`clear bgp <peer>`).
- **Check that BFD really runs** before relying on it. On our gateway the `neighbor … bfd` line was accepted and the BFD daemon wasn't running.
- **ECMP hashes on addresses only.** One client always lands on one node; with `externalTrafficPolicy: Local` that is one pod. Don't expect per-request spreading from one test machine.
- **`externalTrafficPolicy: Cluster` keeps a dead node's pods as endpoints for about 40 s**, until the node is marked NotReady, whatever announces the IP. Fast failover of the address doesn't fix slow failover of the endpoints.
- **A BGP route takes the firewall zone of the network it points to.** Allow clients to the LB range in that zone.
- **Controller APIs for BGP config may want snake_case fields** and answer "must not be empty" to camelCase ones. Read the config back after uploading.
- **Talos 1.14 moved kube-proxy and the default CNI to their own config documents.** Disabling them belongs on the control-plane machine set; the same document on workers is rejected.

## Verify
```bash
# gateway
vtysh -c "show bgp summary"; vtysh -c "show ip bgp"     # one /32 per Service, every node a next hop
# cluster
cilium-dbg bgp peers                                     # or the MetalLB speaker logs
# failover: curl in a loop, power a node off, read the gap
```

## References
- Cilium L2 announcements: https://docs.cilium.io/en/stable/network/l2-announcements/
- Cilium BGP control plane: https://docs.cilium.io/en/stable/network/bgp-control-plane/bgp-control-plane/
- MetalLB BGP: https://metallb.io/concepts/bgp/
- FRR BGP: https://docs.frrouting.org/en/latest/bgp.html · graceful restart, RFC 4724: https://www.rfc-editor.org/rfc/rfc4724
- Related: [networking-decisions.md](networking-decisions.md) · skill `cilium-networking`
