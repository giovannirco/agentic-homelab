# Source themes (privacy map)

This curriculum was synthesized from real homelab ops themes. Personal names, IPs, orgs, and credentials were **removed**. Theme mapping for maintainers:

| Theme | Curriculum home |
|-------|-----------------|
| GitOps App-of-Apps, Argo hygiene | docs/setup/06, skill gitops-platform |
| Talos + sequential upgrades | docs/setup/04, skill talos-upgrade |
| Cilium / LB / Gateway | docs/setup/05, skill cilium-networking |
| Cloudflare tunnel + tokens | docs/setup/07, skill cloudflare-tunnel |
| Split DNS / external-dns | docs/lessons, future skill |
| Storage migration lessons | docs/lessons |
| DB operators single/multi | skill homelab-databases |
| App onboard + version pin | skill onboard-app |
| OOB secrets | skill out-of-band-secrets |
| Hermes / OpenClaw / MCP | docs/agents, skill hermes-agent |
| Learning board / issues process | docs/setup/10 |
| Life-ops / first-login | docs/setup/09 |
| Agent skill install | scripts/install-skills.sh |

Do not reintroduce private hostnames into this repository.

| Cilium LB-IPAM + L2 (not MetalLB) | docs/platform/networking-decisions, skill cilium-networking |
| Multus macvlan NADs | skill multus-secondary-net |
| Envoy dual gateway | networking-decisions, setup/05–07 |
| Hermes VM multi-profile fleet | docs/agents/hermes-vm-vs-kubernetes |
| Hermes k8s tenant + GH App + MCP | hermes-agent skill, hermes-vm-vs-kubernetes |
| WAHA GOWS + MCP (agents) | docs/agents/waha-and-mcp, skill waha-mcp |

| Technitium split-DNS + catalog | docs/setup/11, skill technitium-split-dns |
| external-dns CF + RFC2136 | docs/setup/12, skill external-dns |
| cluster-gitops vs platform-gitops / multi-org AppSet | docs/platform/gitops-repo-models |
| Hardware A/B/C topologies | docs/platform/hardware-topologies |
| UniFi / MikroTik / Omada DNS/VLAN | docs/network/home-network-controllers |

| Grafana Cloud Free + Alloy | docs/setup/13, skill observability |
| Light Prometheus + Loki SingleBinary | docs/setup/13 Tier 1 |
| Full LGTM RF=1 dual write + MinIO + k8s-monitoring | docs/setup/13 Tier 2 |
