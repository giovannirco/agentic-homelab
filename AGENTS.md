# AGENTS.md — agentic-homelab

Entry for AI agents (Grok, Hermes, OpenClaw, Cursor, Claude, and similar) operating this stack.

## Mission

Help the operator build and run an **agentic homelab** that practices **platform engineering**. Prefer teaching *why* when asked; always execute through **skills** and **git**.

## Preconditions

1. Install skills: `bash scripts/install-skills.sh` (`--hermes` / `--both` as needed).  
2. Read `docs/00-philosophy.md` when starting a new lab.  
3. Do not invent hostnames, IPs, domains, or secrets — ask or use documented examples.  

## Hard rules

1. Prefer GitOps over bare kubectl when the cluster is Argo-managed.  
2. Never commit secrets. Never paste secrets into chat.  
3. Pin latest **stable** upstream tags after lookup (`gh api …/releases/latest`, crane/skopeo).  
4. Fail fast — no silent fallbacks that hide misconfiguration.  
5. Sequential upgrades only (Talos minor gates Kubernetes max).  
6. One operator per database engine cluster-wide.  
7. Use `explain-as-you-go` when the operator wants guided learning.  

## Repo map

| Path | Role |
|------|------|
| `docs/setup/` | Ordered bootstrap (01–13) |
| `docs/platform/` | Topologies, GitOps models, networking, observability |
| `docs/network/` | Home controllers |
| `docs/agents/` | Hermes, WAHA MCP |
| `docs/lessons/` | Operational footguns |
| `docs/MAP.md` | Doc ↔ skill index |
| `skills/` | Installable agent skills |
| `templates/` | Starter manifests and issues |
| `path/` | 90-day progression |
| `scripts/` | Skill install and lab verify |

## Workflow: bootstrap lab

1. Load `lab-bootstrap`.  
2. Follow setup docs 01 → 13 as far as the topology requires.  
3. Track remaining work as GitHub issues.  
4. For each app: `onboard-app`, pin version, commit, sync, verify.  

## Workflow: install app X

1. Load `onboard-app`.  
2. Research upstream + latest stable tag.  
3. Scaffold under `platform-gitops/apps/<name>/`.  
4. Design storage, secrets, and exposure first.  
5. Push → Argo sync → dig/curl/pods.  
6. Document first-login on the issue.  

## Out of scope unless requested

- Full multi-tenant company product stacks  
- Omni break-glass recovery procedures  
- Copying live production secrets or topology  

## Security

- Treat PEMs, kubeconfigs, `.env`, and API tokens as toxic.  
- Prefer namespace-scoped RBAC for agents after day-1 bootstrap.  
