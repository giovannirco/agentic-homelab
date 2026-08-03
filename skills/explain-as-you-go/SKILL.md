---
name: explain-as-you-go
description: >
  Narrate why before how on ops channels; link issues; keep scope tight.
  Triggers: /explain, learning mode, teach me, explain as you go.
version: 1.0.0
---

# Explain as you go

## When

User is learning DevOps/platform or said they want guidance, not only execution.

## Behavior

1. **State the goal** in one sentence  
2. **Why this tool** (platform tradeoff in one sentence)  
3. **Steps** with commands  
4. **Verify**  
5. **What could go wrong**  
6. **Issue comment** summarizing outcome  

## Cadence

- Prefer small commits  
- One theme per session  
- Open follow-up issues instead of infinite scope  

## Tone

- Direct, concise, no fluff  
- Portuguese OK if user speaks PT; technical terms can stay English  

## Anti-patterns

- Silent kubectl that user cannot reproduce  
- Skipping verify  
- Dumping secrets “for convenience”  
