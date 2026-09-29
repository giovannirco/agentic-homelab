# 02 — Proxmox base

## Goal

One hypervisor that runs:

1. Agent VM (always on)
2. Talos VM (Kubernetes)
3. Optional: DNS VM later

## Install

1. Download latest **Proxmox VE** ISO from upstream.
2. Install to NVMe; set a strong root password.
3. Set static management IP on the LAN.
4. Enable enterprise repo **or** switch to `no-subscription` repo per Proxmox docs (homelab common).
5. Apply updates **from the console or a detached unit** (`systemd-run --unit=upgrade apt-get -y full-upgrade`), never over a bare SSH session: a power cut or dropped session mid-`update-initramfs` can leave a `grub>` prompt. Review `apt list --upgradable` first and **pin the running kernel** (`proxmox-boot-tool kernel pin`) before trying a new one.

## First hardening (minimum)

- [ ] Change default root password if reusing image  
- [ ] Create a non-root admin later if you want  
- [ ] Firewall: allow admin IPs only when comfortable  
- [ ] Backups: see **Backups** below (do it on day 1, not "when available")  
- [ ] Note: Proxmox host RAM is shared with VMs — leave headroom  

## Storage

- Local LVM-thin or ZFS (your choice; ZFS needs more RAM).
- For single mini-PC, **local-lvm** is fine to start.

## Networks

- Make `vmbr0` **VLAN-aware** (`bridge-vlan-aware yes`, `bridge-vids 2-4094`) and give the switch port a trunk profile (management untagged, everything else tagged). The host stays on management; each VM/container picks its VLAN with `tag=`.
- Changing the bridge remotely? Use a dead-man switch: `systemd-run --on-active=180 --unit=netrevert /bin/sh -c 'cp /root/interfaces.bak /etc/network/interfaces && ifreload -a'`, test, then `systemctl stop netrevert.timer`.
- Give guests **DHCP reservations** rather than static IPs so the gateway knows their names (automatic DNS names, see [network-foundation](../network/network-foundation.md)). Keep static IPs only for the DNS servers themselves.
- Check the NIC negotiated **1000/full** (`ethtool`): a bad patch cable often links at 100 Mb/s and looks like "Proxmox is flaky".

## Create VMs (shell outline)

```bash
# Example only — adjust storage, IDs, ISO paths
# Agent VM: Ubuntu cloud image or ISO, 4 vCPU / 4–8G RAM / 40G disk
# Talos VM: will boot Talos ISO/metal image, 4 vCPU / 8G+ RAM / 60G+ disk
```

Prefer **q35** machine type, **host** CPU type for nested virt if needed, and **VirtIO** disks/NICs.

## Backups (day 1)

- An NFS storage on the NAS pointing at a **redundant volume** (RAID1/5/6/SHR). **Never RAID0** for backups.
- Retention on the storage (e.g. `keep-daily=7,keep-weekly=4,keep-monthly=3`); a nightly job for **all** guests, snapshot mode, fleecing for VMs.
- Weak hardware / small PSU: throttle in `/etc/vzdump.conf` (`bwlimit`, `ionice: 7`, `zstd: 1`).
- Proxmox doesn't back up **its own config**: a small timer that tars `/etc/pve`, `/etc/network`, apt sources, the kernel pin and custom units to the NAS.
- **Restore test** once: `pct restore <new-id> <archive> --unique 1`, inspect without starting (it keeps the original IP and onboot), destroy.
- After changing the host's IP, existing NFS mounts keep the **old source IP** and hang: `umount -f -l` and let Proxmox remount.

## Snapshot habit

Before risky experiments on the agent or Talos VM: snapshot in Proxmox UI.

## Done when

- [ ] Proxmox UI reachable on LAN  
- [ ] Two empty VMs created (or one + ISO ready)  
- [ ] Host has free RAM after VMs sized

Topology choices: [hardware-topologies.md](../platform/hardware-topologies.md).
