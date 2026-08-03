# AGENTS.md — agentic-homelab

Entry for AI agents (Grok, Hermes, OpenClaw, Cursor, Claude) working in this lab curriculum repo.

## Mission

Help the human build and operate a **learning homelab** that teaches **platform engineering**, using skills in this repo. Prefer teaching *why* while executing *how*.

## Preconditions

1. Install skills: `bash scripts/install-skills.sh` (or `--hermes` / `--both`).
2. Read `docs/00-philosophy.md` once per new learner.
3. Never invent cluster hostnames, IPs, or secrets — use placeholders or ask.

## Hard rules

1. Prefer GitOps over bare kubectl mutates when the cluster is Argo-managed.
2. Never commit secrets. Never paste secrets into chat channels.
3. Pin latest **stable** upstream image/chart tags after looking them up (`gh api …/releases/latest`, crane/skopeo).
4. Fail fast: no silent fallbacks that hide misconfiguration.
5. Sequential upgrades only (Talos minor gates k8s max).
6. One operator per engine (e.g. single mariadb-operator).
7. Explain-as-you-go when the user is in learning mode (`skills/explain-as-you-go`).

## Repo map

| Path | Role |
|------|------|
| `docs/setup/` | Ordered bootstrap guides (incl. DNS, external-dns, observability) |
| `docs/platform/` | Topologies, GitOps models, networking decisions |
| `docs/network/` | Home controllers (UniFi/MikroTik/Omada) |
| `docs/agents/` | Hermes / OpenClaw / MCP |
| `docs/lessons/` | Hard-won footguns |
| `skills/` | Portable agent skills (incl. cilium LB-IPAM, multus, hermes dual, waha) |
| `docs/platform/networking-decisions.md` | Real networking choices, placeholders |
| `templates/` | Copy-paste starters |
| `path/` | Curriculum timelines |
| `scripts/` | Install helpers |

## Workflow for "set up my lab"

1. Load `lab-bootstrap` skill.
2. Walk shopping list → Proxmox → agent VM → Talos → Cilium → Argo → tunnel.
3. Open learning-board issues for remaining work.
4. For each app: load `onboard-app`, pin version, GitOps PR/commit, verify.

## Workflow for "install app X"

1. Load `onboard-app`.
2. Research upstream + latest stable tag.
3. Scaffold under learner’s `platform-gitops/apps/<name>/`.
4. Storage + secrets + HTTPRoute design first.
5. Push → Argo sync → dig/curl/pods verify.
6. Document first-login in issue comment.

## Out of scope unless asked

- Multi-org tenant fan-out
- Production multi-tenant WAHA fleets (document generically only)
- Breaking-glass Omni recovery (link skill, only if learner uses Omni)

## Security

- Treat all `.local/`, PEMs, kubeconfigs as toxic.
- Prefer namespace-scoped RBAC for agents over cluster-admin once lab is past day-1.
