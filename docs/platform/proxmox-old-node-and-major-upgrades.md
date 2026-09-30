# Reviving an old Proxmox node: leave a dead cluster, upgrade a major version, re-IP safely

For the box in the cupboard that used to be half of a cluster. Tested on PVE 8.4 → 9.x (Debian 12 → 13), UEFI + GRUB, a node without guests.

## 1. Find it and get in
- If it doesn't answer at its old address: recreate the old subnet on **one** switch/gateway port in a restricted firewall zone, then look at the port's received-packet counter and the gateway's neighbour table. Zero packets = wrong NIC/port, not a wrong IP.
- SSH "suddenly rejects your key" after an IP change? Run `ssh -v`: your client config may only offer that key for the old subnet.

## 2. Leave the dead cluster
Two-node cluster, one node gone → no quorum, `/etc/pve` read-only. With no guests on the node (back them up first otherwise):
```bash
cp -a /etc/pve/corosync.conf /etc/pve/storage.cfg /root/   # backups
systemctl stop pve-cluster corosync
pmxcfs -l
rm /etc/pve/corosync.conf; rm -rf /etc/corosync/*
killall pmxcfs; systemctl start pve-cluster
rm -rf /etc/pve/nodes/<ghost-node>
pvesm remove <dead-storage>   # NFS shares / ZFS pools that no longer exist
```
Fix DNS and time sync before touching apt.

## 3. Upgrade like you've been burned before
- **Never over a bare SSH session.** Run long jobs as a detached unit with a log:
  ```bash
  systemd-run --unit=upg --collect bash -c 'DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold dist-upgrade > /root/upg.log 2>&1; echo EXIT=$? >> /root/upg.log'
  ```
- **Kernel safety net:** `proxmox-boot-tool kernel pin <known-good>`, then boot the new one once with `proxmox-boot-tool kernel pin <new> --next-boot`, verify, and only then pin `<new>`. A failed boot + power cycle returns to the known-good kernel.
- Order: update within the current major → reboot (as above) → `pve8to9 --full` and fix its findings → switch repos → **review** `apt -s dist-upgrade` (count, and removals: expect library renames, never `proxmox-ve`/`pve-manager`) → upgrade → reboot once into the new kernel → checker again (0/0).
- Typical checker findings on GRUB systems: remove the `systemd-boot` meta-package; let GRUB maintain the removable EFI path (`grub2/force_efi_extra_removable=true` + reinstall `grub-efi-amd64`).
- New repos use deb822 files (`/etc/apt/sources.list.d/proxmox.sources`); keep a copy of the old lists.
- Keep your `lvm.conf` if it only adds Proxmox's `global_filter`. A time-sync daemon may fail until the reboot (new daemon, old systemd).

## 4. New address with a parachute
```bash
cp -a /etc/network/interfaces /root/interfaces.pre; cp -a /etc/hosts /root/hosts.pre
systemd-run --on-active=300 --unit=revert sh -c 'cp -a /root/interfaces.pre /etc/network/interfaces; cp -a /root/hosts.pre /etc/hosts; ifreload -a'
# edit interfaces (VLAN-aware bridge, new address/gateway) AND /etc/hosts (the cluster filesystem resolves the node name)
ifreload -a
# move the switch port's native VLAN, confirm SSH on the new IP, then:
systemctl stop revert.timer; pvecm updatecerts --force; systemctl restart pvedaemon pveproxy
```

## 5. Old NICs, old assumptions
- **ConnectX-3:** `ethtool -k <nic>` shows `rx-vlan-filter: on [fixed]`. Use `bridge-vids <first>-<last>` for the VLANs you actually use instead of `2-4094`, or tagged guests never get traffic.
- Audit *every* interface of every old device you reconnect (the NAS's second port, the old node's other NIC): stale DHCP leases, default gateways and static routes from the previous network cause the strangest failures.
