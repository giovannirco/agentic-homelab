---
name: long-session-goal
description: >
  Keep a multi-hour agent session on track across context loss: a goal file with a
  checkable end, a resume routine, a checkpoint routine, a "waiting for the operator"
  list, and evidence rules. Triggers: /goal, long session, resume after compaction,
  where did we stop, handoff, checkpoint, keep working on the goal, unattended run.
version: 1.0.0
---

# Long-session goal

Full guide: `docs/agents/long-sessions.md` (includes the file template).

## At session start, and after every context loss

1. Read the goal file. Then the memory note that mirrors it and any handoff newer than it; if they disagree, the newer wins and the file is updated.
2. Load the skills the work needs.
3. Check live state **before** acting: what is running, free disk, `git status` in every repo involved, background jobs left behind (by PID file).
4. Open the newest evidence.

## While working

- Work the "Next" list top to bottom. Don't ask what to do next.
- A decision only the operator can make goes under "Waiting for the operator", with the reason. Continue with the next item.
- Corrections from the operator are rules: write them into the repo's instruction file, not only into memory.
- Background waiters wait on a PID or a file. Detach commands started inside pods (redirect output and stdin).

## After every finished item

1. Evidence out of scratch and into the repo (logs, CSVs, manifests). Generated media to durable storage with a row per file: model, workflow, prompt, seed, settings, time, hardware state, licence.
2. Run record updated.
3. Commit and push every repo touched.
4. Tick the item in the goal file with the commit id; update the memory note.

## Evidence rules

1. Numbers only from logs. An unmeasured explanation is labelled a hypothesis.
2. Capture proof at the moment it happens.
3. Keep runs that went wrong, named and explained.
4. Say what you substituted when a source was blocked.
5. Redact credentials at the source; scan scratch afterwards.

## At the end

A report the operator can act on: what changed, where it lives (paths, commits per repo), what is waiting for a decision, the next command if there is one. Then a handoff note with the next three steps.

## Stop conditions

- The next item needs a destructive or outward-facing action that wasn't authorised.
- Every remaining item is waiting for the operator.
