---
name: local-ai-gpu-node
description: >
  Run and measure local AI on a Talos GPU worker: storage off the node disk, one GPU app
  at a time, thermal profile per card, power limits from a privileged pod, benchmarks with
  temperature and token counts, model licences. Triggers: /gpu-node, GPU node, local LLM,
  image generation, ComfyUI, Ollama, thermal throttling, power limit, benchmark a model,
  nvidia-smi, disk pressure on the GPU node.
version: 1.0.0
---

# Local AI on a GPU node

Full guides: `docs/platform/gpu-node-local-ai.md`, `docs/platform/know-your-hardware.md`.

## Before touching anything

```bash
kubectl -n <ns> get deploy,pods          # which app holds the cards
kubectl describe node <gpu-node> | sed -n '/Conditions/,/Addresses/p'   # disk pressure?
# from a pod with the GPUs:
nvidia-smi --query-gpu=index,pci.bus_id,temperature.gpu,power.draw,power.limit,clocks_event_reasons.sw_thermal_slowdown --format=csv
```

## Rules

1. **One GPU app at a time.** Scale the others to zero first; each app requests every card.
2. **Nothing is installed on the node's disk.** Models on the NAS share; environments and caches on the fast share. The kubelet evicts below 15 % free.
3. **Every number comes from a log** that is saved next to the write-up. Temperature and throttle flags are logged beside each result.
4. **Vary the seed** when timing image jobs (identical input returns from cache).
5. **Print which physical card ran each job** (bus ID). App-level device numbers change with the default-device flag.
6. **For long-context LLM tests**, disable silent truncation and record the prompt token count from the response.
7. **Keep failed and distorted runs**, labelled with the cause.
8. **Record the licence** of every model whose output may be published, read in the model's own repository that day.

## Tuning (needs the operator's OK)

- Power limit, target temperature, clock offsets and fans need a **privileged** pod; a normal pod gets "Insufficient Permissions".
- Choose a limit by timing two real jobs (one short, one long) at three limits, not from a synthetic load.
- Persist the choice with a DaemonSet in git; say in every later benchmark which limit was in force.
- Don't point a vendor tool at a power supply or fan controller before reading what its "initialise" does.

## Thermal profile (per card)

Idle → that card alone at full load, one sample per second → note seconds to the first throttle flag and the temperature → the other card → both. Save the CSV.

## Stop conditions

- The node has disk pressure: free space first (old model caches), then continue.
- A card reports hardware thermal slowdown or shutdown temperatures: stop the load and report.
- A request to open the machine, repaste or reseat: that is the operator's job; write the checklist and the before/after test instead.

## Related

`skills/omni-netboot` · `skills/long-session-goal` · `docs/agents/mcp-on-the-lan.md`
