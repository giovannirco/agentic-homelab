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
5. Apply updates: `apt update && apt full-upgrade`.

## First hardening (minimum)

- [ ] Change default root password if reusing image  
- [ ] Create a non-root admin later if you want  
- [ ] Firewall: allow admin IPs only when comfortable  
- [ ] Backups: schedule vzdump to secondary disk or NFS when available  
- [ ] Note: Proxmox host RAM is shared with VMs — leave headroom  

## Storage

- Local LVM-thin or ZFS (your choice; ZFS needs more RAM).
- For single mini-PC, **local-lvm** is fine to start.

## Networks

- One bridge `vmbr0` bridged to physical NIC is enough for day 1.
- VLANs later (Servers / IoT / Guests) when you outgrow flat LAN.

## Create VMs (shell outline)

```bash
# Example only — adjust storage, IDs, ISO paths
# Agent VM: Ubuntu cloud image or ISO, 4 vCPU / 4–8G RAM / 40G disk
# Talos VM: will boot Talos ISO/metal image, 4 vCPU / 8G+ RAM / 60G+ disk
```

Prefer **q35** machine type, **host** CPU type for nested virt if needed, and **VirtIO** disks/NICs.

## Snapshot habit

Before risky experiments on the agent or Talos VM: snapshot in Proxmox UI.

## Done when

- [ ] Proxmox UI reachable on LAN  
- [ ] Two empty VMs created (or one + ISO ready)  
- [ ] Host has free RAM after VMs sized  
