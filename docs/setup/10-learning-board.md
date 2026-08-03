# 10 — Learning board (GitHub Projects + issues)

## Goal

Run the lab like a product team:

- **Issues** = work packages with full context  
- **Project board** = Todo / In progress / Done  
- **Notes** = lessons that become blog/interview stories  

## Suggested columns

| Column | Meaning |
|--------|---------|
| Backlog | Not started |
| Ready | Spec complete, can be agent-executed |
| In progress | Human or agent actively working |
| Blocked | Waiting on hardware/DNS/human |
| Done | Verified |

## Issue types

1. **Install app** — `templates/issues/install-app.md`  
2. **Incident** — what broke, impact, fix, prevent  
3. **Decision** — ADR-style choice (Ceph vs local path, etc.)  
4. **Spike** — time-boxed research  

## Labels (suggested)

`area/k8s` `area/gitops` `area/network` `area/agent`  
`type/onboarding` `type/fix` `type/decision`  
`priority/high|medium|low`

## Agent behavior

When the human says “I’m learning platform,” the agent:

1. Links the current issue  
2. Explains *why* before *how*  
3. Commits small slices  
4. Comments results on the issue  
5. Opens follow-ups instead of silent scope creep  

See skill `explain-as-you-go`.

## Portfolio export

Every closed epic with:

- problem  
- constraints  
- what you built  
- metrics (sync time, recovery steps)  
- what you would do differently  

…is an interview story.
