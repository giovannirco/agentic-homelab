# 05 — Cilium networking + load balancer path

## Goal

Install **Cilium** as the cluster CNI so you learn:

- Cluster networking (pods, services)
- NetworkPolicy later
- Optional **L2/LB IPAM** so Services of type LoadBalancer get LAN IPs

Alternatives (MetalLB, Multus) exist; Cilium covers a lot for a learning lab.

## Why not “whatever default”

Default CNIs work until you need:

- Fixed LAN VIP for a service
- Hubble observability
- Policies
- Understanding of kube-proxy replacement

Interview signal: *“I chose Cilium and can explain tradeoffs.”*

## Install (conceptual)

Always pin chart/app version from Cilium release docs:

```bash
# Example shape — replace versions after looking up latest stable
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --namespace kube-system \
  --version <CHART_VERSION> \
  --set ipam.mode=kubernetes \
  --set kubeProxyReplacement=true \
  # enable L2 announcements / LB IPAM per current Cilium docs for your version
```

For single-node labs, follow Cilium’s official **kubeadm/talos** install guide for your k8s version.

## LB pool

Reserve a small range on your LAN that DHCP will not use, e.g. `10.0.0.200–10.0.0.220`.

Wire Cilium LB IPAM or MetalLB with that pool. Then:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo
  annotations:
    # annotation keys vary by LB implementation — use current Cilium docs
spec:
  type: LoadBalancer
  ports: [{ port: 80, targetPort: 8080 }]
```

## Gateway API (recommended later)

Prefer **Gateway API** (Envoy Gateway / Cilium Gateway) over legacy Ingress long-term:

- HTTPRoute resources
- Clear separation internal vs external listeners
- Matches how modern platform teams expose apps

Day 1 you can expose with NodePort or a single LB Service; day 7 move to Gateway + tunnel.

## Multus (optional)

Use Multus when a pod needs a second interface (e.g. macvlan onto LAN). Skip until you have a concrete need.

## Verify

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl get svc -A | head
cilium status   # if cilium CLI installed
```

## Done when

- [ ] CoreDNS works  
- [ ] Pods can reach cluster Services  
- [ ] You can explain pod CIDR vs service CIDR vs LAN  
- [ ] Optional: one LoadBalancer IP assigned from your pool  
