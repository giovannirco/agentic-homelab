# Many machines: self-hosted Omni and netboot enrolment

`talosctl` is enough for one node ([04-talos-single-node](../setup/04-talos-single-node.md)). The moment you have a second cluster, or machines you want to wipe and reuse, the picture changes: you want a machine to **boot from the network, register itself, and wait** until a file in git says which cluster it belongs to. That is what Omni plus a netboot path gives you.

Tested 2026-10 with Omni 1.12, Talos 1.13 / 1.14, Kubernetes 1.36 / 1.37, on Proxmox VMs and one bare-metal box.

## When it is worth it
| You have | Use |
|---|---|
| one node, one cluster | `talosctl`, secrets in the password manager |
| two or more clusters, or machines that change roles | Omni + netboot |
| a lab where you build and destroy clusters to learn | Omni + netboot (a cluster is deleted and its machines are back in the pool in about a minute) |

Omni is one more service to run and back up. It holds the identity of every machine, so treat it like the DNS server: small, boring, backed up, never experimental.

## The pieces
```text
DHCP (your gateway)  +  proxyDHCP (tells PXE clients where to boot from)
        │
   iPXE menu  ──►  "Talos → Omni" entry (kernel + initramfs from local files)
        │
   Talos maintenance mode  ──SideroLink (WireGuard)──►  Omni
        │
   cluster template in git  ──omnictl cluster template sync──►  cluster
```

1. **Omni** in a container or small VM: its own domain with a real certificate, a fixed IP, an identity provider.
2. **A netboot path** on the network where Kubernetes machines live. A machine with an empty disk and "network boot" in its boot order lands in Omni by itself.
3. **Cluster templates** (`kind: Cluster`, `ControlPlane`, `Workers`, optional `Machine` documents) in a git repo. `omnictl cluster template validate`, then `diff`, then `sync`.
4. **Labels** on machines from the enrolment image (`site=…`, `role=…`), so a template can select machines by label instead of by ID.

## Lab shapes that taught the most
All three are VMs on one hypervisor, built and destroyed from templates:
- **one control plane + one worker**: the smallest thing that behaves like a cluster;
- **three control planes that also run workloads + one worker**: quorum, a virtual IP, rolling upgrades;
- **one control plane + two workers** with the hypervisor's cloud controller and CSI driver: volumes that follow a pod between workers.

Measured over a night with nine VMs on a 14-core / 128 GB host: a small control plane (CNI + etcd) used about 10 % of 2 vCPU and 1.2–1.35 GB of real memory; an idle worker about 4 % of 4 vCPU and 1 GB; Talos plus images took 1.2–2.8 GB of a thin 32 GB disk. So **2 vCPU / 4 GB per control plane is enough** for a lab. The hypervisor's per-VM memory graph includes guest cache; `talosctl memory` shows the real figure.

## Enrolment image
- `omnictl download iso --pxe --talos-version <v> --initial-labels site=<n>` prints an Image Factory URL for the kernel and initramfs. Add system extensions per role (`--extensions`): a plain image, a GPU image, and so on.
- Download the kernel and initramfs once and serve them **from your own HTTP server**. Old PXE ROMs and QEMU's built-in iPXE can't fetch over HTTPS.
- **The kernel command line carries the join token.** Keep the netboot files off public shares, and see "Traps" below.

## Netboot on a network you don't want to reconfigure
The gateway's DHCP "network boot" option is one filename per network, which means UEFI **or** BIOS, not both. A **proxyDHCP** (dnsmasq in proxy mode) answers only the PXE part of DHCP, leaves addressing to the gateway, and can serve a different first-stage file per firmware. One menu file then decides the default per network (by gateway address): the lab network defaults to a live Linux with SSH, the people network to the local disk, the Kubernetes network to "Talos → Omni".

## Traps
**Omni**
- **Never change the account ID.** It is the identity every machine was joined with.
- **Changing Omni's domain disconnects every machine.** Recovery needs break-glass Talos configs and a certificate-authority rotation afterwards. Decide the domain once.
- **The SideroLink endpoint is advertised as an IP address.** Moving Omni to a new host is easy if the IP moves with it (stop, back up, restore, same MAC or reservation). Never run two copies.
- **Upgrade one minor at a time**, and match `omnictl` to the server: after an API bump the old client fails with "client API version mismatch". Cluster health took 4–6 minutes to come back after each Omni restart.
- **Talos commands that wipe a machine are blocked through Omni**, even for admin service accounts. Removing a machine goes through the template or the UI.
- **A disconnected machine blocks the teardown of its cluster.** Delete its link first.
- **`machine.network.hostname` is rejected** ("static hostname is already set"). Omni generates a `HostnameConfig`; to set a name, use a `HostnameConfig` with `auto: "off"` **and** `hostname`.
- **The install disk belongs on the template's `Machine` document** (`install.disk`), not in a config patch.

**Machines and VMs**
- **Talos 1.13 and newer need an x86-64-v2 CPU.** A VM created from the command line with the hypervisor's oldest CPU type panics at boot. Use `x86-64-v2-AES` or `host`.
- **Talos asks for DHCP on every NIC in maintenance mode.** Pin each interface in a patch. A selector by MAC also matches VLAN interfaces stacked on that NIC: add `physical: true`.
- **Encode the role of each virtual NIC in its MAC address** (one byte for the network), so one cluster-wide patch can tell the node NIC from the load-balancer NIC.
- **Enable the external cloud provider from the first boot** if you'll use a cloud controller. Nodes that registered before it was enabled are never initialised.
- **Pod Security is `baseline` by default.** Privileged or host-network pods need a namespace labelled `pod-security.kubernetes.io/enforce: privileged`.
- **A drain deletes bare pods.** Use Deployments, even for tests.

**The join token**
- The Talos console prints it during enrolment: no screenshots of that screen in public.
- `/proc/cmdline` contains it on every machine that enrolled by netboot, and **any pod can read `/proc/cmdline`**. Redact it in every inventory script, and never paste a node's kernel command line into chat or an issue.

**Netboot**
- Never write iPXE scripts through an SSH heredoc: the local shell expands every `${…}` to nothing. Write the file locally and copy it.
- A live Linux booted over PXE takes a second DHCP lease once its own network service starts. Find machines by hostname, not by the first lease.
- Image Factory initramfs files differ per schematic even when the kernel is identical. Don't share one initramfs between images.
- The netboot server's TFTP runs unprivileged: files must be owned by its user.

## Verify
```bash
omnictl get machines            # the new machine appears, connected
omnictl get clusterstatus       # phase "running" after the sync
kubectl get nodes -o wide
```
Then destroy it: `omnictl delete cluster <name>`. The disks are wiped and the machines return to the pool. If that round trip is boring, the setup is right.

## References
- Omni: https://docs.siderolabs.com/omni/ · cluster templates: https://omni.siderolabs.com/reference/cluster-templates
- Registering machines over PXE: https://docs.siderolabs.com/omni/omni-cluster-setup/registering-machines/register-a-bare-metal-machine-pxe-ipxe
- Image Factory: https://factory.talos.dev
- netboot.xyz: https://netboot.xyz/docs · dnsmasq (proxy mode): https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
- Related: [loadbalancer-l2-vs-bgp.md](loadbalancer-l2-vs-bgp.md) · [gpu-node-local-ai.md](gpu-node-local-ai.md) · skill `omni-netboot`
