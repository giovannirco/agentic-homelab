# 04 — Talos single-node Kubernetes

## Goal

One Talos Linux machine (VM on Proxmox is fine) running a single-node Kubernetes control plane + worker.

## Why Talos

- Immutable, API-driven Linux for k8s
- Great learning surface for “platform thinks in machines + configs”
- Scales later with Omni (optional multi-machine control plane)

## Path A — talosctl (simplest for one node)

1. Download **Talos** metal ISO/image for your arch from upstream releases.
2. Attach ISO to Proxmox VM; boot.
3. From your laptop:

```bash
# Install talosctl (pin latest stable from GitHub releases)
curl -sL https://talos.dev/install | sh   # or use package method from docs

# Generate secrets + configs (names are examples)
talosctl gen secrets -o secrets.yaml
talosctl gen config lab-homelab https://<TALOS_IP>:6443 \
  --with-secrets secrets.yaml \
  -o _out/

# Apply to the machine (use the IP shown on console)
talosctl apply-config --insecure -n <TALOS_IP> -f _out/controlplane.yaml

# Bootstrap etcd (once)
talosctl bootstrap -n <TALOS_IP> -e <TALOS_IP> --talosconfig _out/talosconfig

# Kubeconfig
talosctl kubeconfig -n <TALOS_IP> -e <TALOS_IP> --talosconfig _out/talosconfig
kubectl get nodes
```

Store `secrets.yaml` / talosconfig in a **password manager** or encrypted backup — not in this git repo.

## Path B — Omni, when there is more than one

Omni manages many Talos machines from cluster templates in git. Use it when:

- you have a second cluster, or machines that change roles;
- you want machines to enrol by network boot and wait for a template;
- you accept running one more small service that must be backed up.

Day 1 with one node: **talosctl is enough**. The day a second cluster appears, read [omni-and-netboot.md](../platform/omni-and-netboot.md): the identity rules (domain, account ID, fixed IP) are decided once and are painful to change.

## Single-node notes

- Control plane and workloads share the node — size RAM generously (8 GiB+ guest).
- Allow scheduling on control plane (Talos/k8s config or taint removal as per current docs).
- Disk: separate volume for ephemeral/container data if you can. etcd wants a disk that nothing else can saturate ([disk-and-etcd-health.md](../platform/disk-and-etcd-health.md)).
- VM CPU type: Talos 1.13 and newer need **x86-64-v2**. Use `x86-64-v2-AES` or `host`; the hypervisor's oldest default panics at boot.
- Pod Security is `baseline` out of the box: a namespace that needs privileged or host-network pods must be labelled `pod-security.kubernetes.io/enforce: privileged`.

## Install Cilium next

Do **not** leave a default CNI you do not understand. Continue to [05-cilium-and-lb.md](05-cilium-and-lb.md).

## Verify

```bash
kubectl get nodes -o wide
kubectl get pods -A
kubectl version
```

## Done when

- [ ] Node Ready  
- [ ] system pods healthy (CNI pending until Cilium)  
- [ ] kubeconfig on laptop **and** copied carefully to agent VM (or use SA later)  
