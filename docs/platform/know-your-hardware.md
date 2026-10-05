# Know the box before you plan around it

Second-hand servers and budget boards are how most labs get big hardware. They are also where plans go wrong: the "quad-channel" board that runs two channels, the "x4" slot wired as x1, the RAM kit that doesn't boot. Two procedures: an audit **before** the machine has an OS, and reading and controlling hardware **after** it runs an immutable OS like Talos.

## 1. Audit through a KVM, without installing anything
With a network KVM (PiKVM or similar) an agent can do this alone: upload a live ISO to the virtual drive, boot it, type an SSH key into the console through the KVM's keyboard API, and work over SSH. Nothing is written to the machine's disks.

Record, in a table in your private notes:

| What | How | Why it matters |
|---|---|---|
| Board, firmware, CPU | `dmidecode -t 0,1,2`, `lscpu` | firmware date; microcode |
| Every DIMM | `dmidecode -t 17` | type, rank, speed, slot |
| **Memory channels really in use** | EDAC sysfs (`/sys/devices/system/edac/mc/…/dimm_location`), then measure with the STREAM benchmark | slot labels prove nothing; a result above the dual-channel peak proves quad channel |
| **How each PCIe slot is wired** | `lspci -vv` on each root port: `LnkCap` against `LnkSta` | CPU ports against chipset ports; a physical x4 slot can be Gen 2 x1 |
| Disks | `smartctl -H -A`, `lsblk -f` | health, wear, leftover pools |
| NICs | `ethtool -i`, `ethtool -m` | driver, SFP module, a MAC that was never programmed |
| Errors | `dmesg --level=err,crit`, EDAC counters | before you trust it |
| PSU and fans | hwmon, vendor USB telemetry | idle and peak power |
| Stability | a short `stress-ng` with `--verify`, temperatures sampled during the run | cheap insurance |

Things this caught on one board:
- A 10 GbE card sat in a slot wired to the chipset at **PCIe Gen 2 x1**: about 3–4 Gbit/s at best. Both CPU slots held graphics cards. The firmware's bifurcation menu showed where a second CPU-attached x4 device could go.
- Only two of four memory channels were populated.
- A RAM upgrade of two larger sticks didn't boot at all; one stick taken from another dead machine was the suspect. Test sticks one at a time before planning a workload around the new total.
- The firmware was in legacy boot mode: switch to UEFI before relying on UEFI-only netboot.

KVM practicalities: stream the ISO upload (`curl -T`; `--data-binary @file` loads the whole image into memory and fails), connect the virtual drive only while the target is the machine you mean, and change the KVM's factory login first.

## 2. Reading and controlling hardware on an immutable OS
Talos has no shell, no package manager, and a kernel built without several debug interfaces. What works:

| Source | How | Notes |
|---|---|---|
| CPU, NVMe temperatures | hwmon in sysfs | any pod |
| GPU state | `nvidia-smi -q`, NVML | any pod with the GPUs: temperature, fans, power, clocks, throttle reasons and their lifetime counters, PCIe link |
| Board sensor chip (fans, PWM, voltages) | add the kernel module (for example `nct6775`, `it87`) to `machine.kernel.modules` | loads without a reboot; then sysfs |
| USB devices (fan controllers, PSUs with a data port) | userspace HID tools from a privileged pod | no kernel drivers needed |
| Anything in `/proc` and `/sys` | the Talos API (`talosctl read`) | no pod needed |

What didn't exist on the kernel we ran: `i2c-dev` (so no `/dev/i2c-*`, and no RGB control for graphics cards), `/dev/mem`, MSR access (no CPU undervolting tools). Do those once from another OS; a netboot live Linux is the easy way in.

**A privileged probe pod** is the tool for the rest: `privileged: true` (which exposes the host's devices and a writable `/sys`), the GPU runtime class with every card visible, and a scratch volume on network storage for the tools it downloads. Create it when needed, delete it when done.

Knobs that need that pod (a normal pod gets "Insufficient Permissions"): GPU power limit, target temperature, clock offsets, fan speed; board PWM outputs; USB fan controllers.

Cautions that cost time:
- **Reading a device can change it.** One vendor tool's "initialise" step resets a power supply's protection and fan modes. Send only the handshake needed to read, and check the tool's source first.
- **A node's kernel command line can contain a join token** ([omni-and-netboot.md](omni-and-netboot.md)). Redact it in inventory scripts before the output touches a file.
- **Settings made from a pod are lost at reboot.** Re-apply them from a small DaemonSet, and keep the file that defines it in git.
- A fan controller reporting wild speeds on one header (hundreds of rpm, then thousands) is usually several fans on one tachometer line, or a fan that stalls. Look with the case open.

## 3. A thermal profile in ten minutes
For any part that throttles (graphics cards most of all):
1. Idle readings.
2. One device at full load, one sample per second: temperature, power, clock, throttle flag. Note **how many seconds until the first throttle flag** and at what temperature.
3. The other device alone.
4. Both together.
5. Repeat at two or three power limits.

Two devices of the same model can differ enormously in step 2 (ours: 2–3 seconds against 46). That number is what tells you which one needs service, and it is the "before" for the day you repaste it.

## References
- PiKVM HTTP API: https://docs.pikvm.org/api/
- Linux EDAC: https://docs.kernel.org/driver-api/edac.html · STREAM: https://www.cs.virginia.edu/stream/
- Talos kernel modules: https://docs.siderolabs.com/talos/latest/reference/configuration/v1alpha1/config#Config.machine.kernel
- liquidctl (USB coolers, controllers, PSUs): https://github.com/liquidctl/liquidctl
- Related: [gpu-node-local-ai.md](gpu-node-local-ai.md) · [hardware-topologies.md](hardware-topologies.md)
