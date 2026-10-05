# A GPU node for local AI on Talos

A used tower with two 24 GB graphics cards, running as a **bare-metal Talos worker** in a cluster whose control plane is a small VM. It serves an image workflow UI, a local LLM server and text-to-speech to the house network. This page is what worked, what the numbers were, and the traps. Most of it applies to one card as well.

Tested 2026-10 with Talos 1.14, Kubernetes 1.37, the NVIDIA open kernel modules as Talos extensions, the NVIDIA device plugin, ComfyUI 0.38 and Ollama 0.35.

## Why bare metal, why a worker
- **Bare metal instead of GPU passthrough:** no IOMMU groups to fight, no VM to keep in sync with the host's drivers, and the whole machine is described by one config patch.
- **A worker instead of a single-node cluster:** the box can be powered off, re-imaged or opened without losing the control plane. The control plane VM needs 2 vCPU and 4 GB.
- The price: the machine is immutable. Tools you would install on a normal Linux (fan control, RGB, vendor utilities) have to run in a pod or from another OS. See [know-your-hardware.md](know-your-hardware.md).

## Build
1. **Firmware:** Above 4G decoding on (two 24 GB cards need it), boot mode UEFI only, option ROMs UEFI. Resizable BAR was left off (no benefit expected for compute).
2. **Image:** an enrolment image with `nvidia-open-gpu-kernel-modules-<lts|production>` and `nvidia-container-toolkit-<same>` ([omni-and-netboot.md](omni-and-netboot.md)). Boot it from the network, or from a KVM's virtual CD when the board's PXE is unreliable.
3. **Machine patch:** kernel modules `nvidia`, `nvidia_uvm`, `nvidia_drm`, `nvidia_modeset`; sysctl `net.core.bpf_jit_harden: "1"`; NIC selectors with `physical: true`. Add the board's sensor module here too (for example `nct6775`); modules listed in the patch load without a reboot.
4. **Cluster:** a `RuntimeClass` named `nvidia`, the NVIDIA device plugin with `runtimeClassName: nvidia`, the node's NIC added to the CNI's device list, and the GPU node excluded from load-balancer announcement policies it can't serve.
5. **Namespace:** label it `pod-security.kubernetes.io/enforce: privileged` if anything in it needs host access (the tuning pod below does).

## Storage: nothing on the node's disk
The node had a 256 GB NVMe. One LLM server's model cache reached 171 GB, and the kubelet evicted pods **twice** and tainted the node with disk pressure. The event said it plainly: "image filesystem 85 % used", threshold 15 % free. Container images, model caches written inside containers and `emptyDir` volumes all share that one partition.

- **Models:** an NFS share on the NAS, mounted read-mostly by every app. A cold 14–20 GB model took 3.5–7 minutes to load.
- **Environments and caches** (Python virtual environments, package caches, per-app state): a second share on the NAS's fastest volume. Measure read and write from a pod separately; ours differed by four times, which pointed at a routing problem, not at the disks.
- **The node disk:** the OS and container images only.

Traps with NFS:
- App images that copy their bundle into place with `cp -a` fail on NFS (no `chown` with root squash). Mount the share beside the app and point the app at it with its own flags.
- Ollama's `OLLAMA_LOAD_TIMEOUT` defaults to 5 minutes; a cold load over NFS takes longer and the client sees HTTP 500. Raise it.
- Hugging Face downloads default to a 10 s read timeout: `HF_HUB_DOWNLOAD_TIMEOUT=120`.

## One GPU app at a time
With 32 GB of system RAM and two cards, running an LLM server, an image UI and a voice engine side by side ended in out-of-memory kills (the image UI at a 20 GiB limit, a voice engine twice while loading) and once in the node going NotReady from memory thrash. The cards still had free memory at that moment; system RAM was the limit. The rule that held: **one app holds both cards; the others are scaled to zero.** Each app requests `nvidia.com/gpu: 2`, so the scheduler enforces it.

For an image UI with two cards, the useful split is **which card is the default**, not spreading one model over two. Choosing the card that throttles later as the default device was 15–19 % faster on the same jobs. Splitting classifier-free guidance across both cards was slower than one card alone while one of them throttled.

## Two "identical" cards are not identical
Same model, same firmware, same limits on paper. Under load:

| | Card A | Card B |
|---|---|---|
| Alone, synthetic load | 34 it/s, thermal flag after 2–3 s at 72–73 °C | 43 it/s, flag after 46 s at 88 °C |
| Both loaded | 8.4 it/s (clock floor) | carries most of the work |
| Unthrottled, first seconds | both about 60 it/s | |

- Read the **throttle reason**, not just the temperature: `nvidia-smi -q` shows it, and the lifetime counters say how long the card has spent in thermal slowdown since boot.
- Card A throttled at a core temperature well under its target. The first hypothesis was hot memory chips. **Measuring said no:** memory was at 62 °C when throttling began. Memory temperature isn't exposed by the driver on these cards; it can be read from a GPU register through the PCI resource file from a privileged pod. The remaining explanation (a hot spot on the die from dried paste) is an inference until someone opens the card.
- The card with the KVM's display attached never stopped its fans, while the other stopped them at idle. Note differences like this; don't diagnose from them.

## Power limits: choose them on real jobs
A synthetic sweep suggested 225 W for the stronger card. Real image jobs disagreed:

| Limit | Short job | Long job |
|---|---|---|
| 350 W (default) | 4.78 s | 147 s |
| 250 W | 5.30 s (+11 %) | 158 s (+7 %) |
| 225 W | 5.85 s (+22 %) | 172 s (+17 %) |

The card reached 89–91 °C at every limit, so the limit bought less heat in the room and less fan noise, not a cooler die. 250 W for the strong card and 200 W for the weak one was the choice. A core clock offset gave nothing at the lower limit.

Mechanics:
- `nvidia-smi -pl`, target temperature, clock offsets and fan control return "Insufficient Permissions" from a normal pod. They need a **privileged** pod with the GPUs visible.
- Settings are lost at reboot. A small privileged DaemonSet that re-applies them every hour keeps them in force.
- Every benchmark taken before a limit was applied is a benchmark at the old limit. Write the limit next to each number.

## Benchmarks that lied
- **Heat:** the same LLM test read 1,010 tokens/s early in a 90-minute sweep and 449 tokens/s at the end. Log temperature and throttle flags beside every result, and mark rows taken on hot cards.
- **Silent truncation:** the LLM server cut prompts that were larger than the context window and answered anyway. A "long context" test passes while reading a fraction of the text. Ask for an error instead (`truncate: false` on the request) and check the prompt token count in the response.
- **Cache hits:** an image workflow with the same graph and seed returns the cached image in half a second. Vary the seed per run, or the "fastest configuration" is the one that didn't run.
- **Device numbering:** after changing the default device, "GPU 0" inside the app is the default card, not the first card on the bus. One comparison ran on the same card twice before this was noticed. Print which physical card each run used.
- **Context:** judge a model with a real context window in use, not with a 2,000-token prompt. A 27B model at 8-bit held 178k tokens on 48 GB and took 11 minutes to read them.

Keep the runs that went wrong, labelled, with the reason. They are the evidence for the rule.

## Licences of what the models produce
A monetised video is commercial use. Read the licence **in the model's own repository on the day you use it**: labels on mirrors and articles were wrong more than once, and licences change between versions of the same model family (one image model went from Apache 2.0 to a research-only licence between releases). Keep a row per generated file: model, workflow, prompt, seed, settings, time, licence.

## Exposing it
- The image UI and the LLM API have no authentication. Put their LoadBalancer IPs in a firewall zone and allow only the networks that should reach them.
- An MCP endpoint for the image UI lets agents generate images: [mcp-on-the-lan.md](../agents/mcp-on-the-lan.md).

## Verify
```bash
kubectl get nodes -l nvidia.com/gpu.present=true
kubectl -n <ns> run smi --rm -it --restart=Never --image=<cuda-image> \
  --overrides='{"spec":{"runtimeClassName":"nvidia"}}' -- nvidia-smi
df -h   # from a pod with the node filesystem: stay above the eviction threshold
```

## References
- Talos NVIDIA GPU guide: https://docs.siderolabs.com/talos/latest/configure-your-talos-cluster/hardware-and-drivers/nvidia-gpu
- NVIDIA device plugin: https://github.com/NVIDIA/k8s-device-plugin
- Kubelet eviction thresholds: https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/
- NVML reference (throttle reasons, clock offsets): https://docs.nvidia.com/deploy/nvml-api/
- Related: [know-your-hardware.md](know-your-hardware.md) · [omni-and-netboot.md](omni-and-netboot.md) · skill `local-ai-gpu-node`
