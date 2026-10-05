# Long agent sessions: a goal file, checkpoints, and evidence

An agent that works for hours loses its working memory several times (context compaction, a restart, a new day). Each loss is a chance to redo finished work, forget a rule the operator set an hour ago, or report a number that no log contains. Three habits removed most of that.

## 1. One file that says what the goal is
A file in the ops repo, next to the work, that an agent reads first and updates last. Chat history is not a plan; this file is.

```markdown
# <Project>: the standing goal, its state, and how to resume it

## The goal prompt            ← pasted to start a session
Work through "Next" below, top to bottom, without asking what to do next.
Done when every item is ticked or moved to "Waiting for <operator>" with the reason,
and the last message lists, per repo, the commits pushed.
Rules that never bend: <the five or six that matter>.

## Resume routine             ← session start, and after every compaction
1. Read this file, then the memory note and any handoff newer than it.
2. Load the skills the work needs.
3. Check live state before touching it: what is running, disk space, `git status`
   in every repo, background jobs left behind.
4. Open the newest evidence.

## Checkpoint routine         ← after every finished item
1. Evidence out of scratch and into the repo.
2. Run record updated.
3. Commit and push every repo touched.
4. Tick the item here, with the commit id. Update the memory note.

## State
### Done
### Next
### Waiting for <operator>    ← decisions only a human can make; the agent goes on with the next item
```

What makes it work:
- **"Done when…" is checkable.** "Improve the setup" never ends; "every item ticked or parked with a reason" does.
- **"Waiting for the operator" is a list, not a stop.** A question that only a human can answer is written down and the agent continues with what doesn't depend on it.
- **The file is the source of truth.** A memory service mirrors the state section and a handoff note carries the next three steps; if they disagree with the file, the newer one wins and the file gets updated.

## 2. Three kinds of memory, three jobs
| Kind | Holds | Lifetime |
|---|---|---|
| The repo (goal file, run records, journal) | what was done, with evidence | permanent, reviewed |
| A memory service (notes per project) | facts and preferences an agent needs at the start of any session | long, pruned |
| A handoff | "here is where I stopped and the next three steps" | single use |

Rules and corrections from the operator go into the **instruction file of the repo** (`AGENTS.md`), where every agent reads them, not only into one agent's private memory. Retrieved memory is history: it never outranks the current instructions.

## 3. Evidence rules
1. **Numbers only from logs.** A figure in a report exists in a file in the repo. An explanation that wasn't measured is labelled a hypothesis.
2. **Capture proof when it happens.** Pods restart and logs vanish. Save the command output, the event, the flag, at that moment.
3. **Keep the runs that went wrong.** Copy partial output out of scratch, name it for what it is, and write one paragraph on the cause. A distorted benchmark that is labelled is evidence; one that is deleted is a hole.
4. **Every generated file gets its context:** model, workflow, prompt, seed, settings, time, hardware state, licence.
5. **Verify claims against the system, not against the notes.** Notes describe what was true when they were written.

## Mistakes the agent made, and the rule each one produced
These are from recent sessions on one lab. They are the reason the rules above exist.

| What happened | Rule |
|---|---|
| A confident explanation for a slow graphics card (hot memory chips) was wrong; measuring the memory temperature disproved it | A plausible theory is a hypothesis until measured. Say which it is |
| A ninety-minute benchmark sweep had no temperature in its log; the same test read 1,010 tokens/s early and 449 at the end, because one card was throttling | Log temperature and throttle state beside every result |
| A long system upgrade ran over a plain SSH session, three steps batched into one; the host lost power mid-way and booted to a `grub>` prompt | Long jobs run detached, with a log, one step at a time, with a known-good kernel pinned |
| Two "measurements" took half a second each: the application had returned cached results | Vary the input when timing; treat an impossible number as a bug in the test |
| A comparison between two devices ran on the same device twice, because the numbering changed with a config flag | Print which physical device each run used |
| Blocked from one source, the agent settled for a weaker one (video descriptions instead of transcripts); the operator had asked for the real thing, and there was a way to get it | Blocked is not the end: say what is blocked, try another route, never substitute without saying so |
| A command's output contained a credential and went to a scratch file | Redact at the source; scan scratch afterwards; never write it to a repo or a reply |
| A background waiter used `pgrep -f` with a pattern that matched its own command line, and never finished | Wait on a PID or a file, not on a process-name search |
| A pod was started with output attached and the command hung | Detach background commands in pods: redirect output and stdin |
| A recovery note still said "fall back to the old network" four days after that network was unplugged | Re-read plans and recovery notes after every migration step |
| After a compaction, the state had to be re-derived from logs and git history | The goal file and the resume routine |

## What the operator can expect at the end
A report that can be acted on: what changed, where it lives (path, commit), what is waiting for a decision, and the next command if there is one. Not a list of everything that was tried.

## Related
- [hermes-and-openclaw.md](hermes-and-openclaw.md) · [mcp-on-the-lan.md](mcp-on-the-lan.md) · [00-philosophy.md](../00-philosophy.md)
- Skill `long-session-goal`
