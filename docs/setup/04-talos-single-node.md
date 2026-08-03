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

## Path B — Omni later

Omni is a control plane for managing many Talos machines with GitOps-ish cluster templates. Use it when:

- You add bare metal nodes
- You want UI + sequential upgrades catalog
- You accept running Omni as another LXC/VM

Day 1: **talosctl is enough**.

## Single-node notes

- Control plane and workloads share the node — size RAM generously (8 GiB+ guest).
- Allow scheduling on control plane (Talos/k8s config or taint removal as per current docs).
- Disk: separate volume for ephemeral/container data if you can.

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
