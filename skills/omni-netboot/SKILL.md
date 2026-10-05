---
name: omni-netboot
description: >
  Self-hosted Omni with netboot enrolment: identity rules (domain, account ID, fixed IP),
  enrolment images, cluster templates in git, lab clusters on VMs, the join-token rule.
  Triggers: /omni, Omni, SideroLink, netboot, PXE, proxyDHCP, cluster template,
  enrol machine, machine not connected, new Talos cluster from template.
version: 1.0.0
---

# Omni + netboot

Full guide: `docs/platform/omni-and-netboot.md`.

## Never, without the operator's explicit decision

1. Change Omni's **account ID**.
2. Change Omni's **domain** (every machine disconnects; recovery needs break-glass configs and a CA rotation).
3. Run **two copies** of Omni, or move it without moving its IP.
4. Skip an Omni minor version.

## The join token

It is in the kernel command line of every netbooted node, and any pod can read `/proc/cmdline`. The Talos console prints it during enrolment.

- Redact it in every inventory script **before** output reaches a file.
- Never paste a kernel command line, an enrolment screenshot or an iPXE entry into chat, an issue or a public repo.
- If it reached a file: redact the file, scan scratch directories, say so in the report.

## Workflow: a new cluster

1. Machines boot from the network and appear in `omnictl get machines` (maintenance mode).
2. Write the template (`Cluster`, `ControlPlane`, `Workers`, optional `Machine` documents) in the git repo.
3. `omnictl cluster template validate -f <file>` → `diff` → `sync`.
4. Install the CNI if the template disables the default one (nodes stay NotReady until then).
5. Verify, then record what was applied.

## Patches that are almost always needed

- Pin every NIC (maintenance mode asks for DHCP on all of them); add `physical: true` to MAC selectors.
- Hostname: a `HostnameConfig` with `auto: "off"` **and** `hostname` (a plain `machine.network.hostname` is rejected).
- Install disk on the `Machine` document, not in a patch.
- External cloud provider enabled from the first boot if a cloud controller will be used.
- VM CPU type `x86-64-v2-AES` or `host`.

## Verify

```bash
omnictl --version               # must match the server's API version
omnictl get machines
omnictl get clusterstatus
kubectl get nodes -o wide
```

## Stop conditions

- A machine shows as disconnected right after an Omni change: check the host (NIC, power) and the Talos API before touching Omni again.
- Tearing down a cluster with a disconnected machine: delete that machine's link first, and only with the operator's OK.
- Any step that would wipe a disk on a machine not named in the request.

## Related

`skills/talos-upgrade` · `skills/cilium-networking` · `docs/platform/loadbalancer-l2-vs-bgp.md`
