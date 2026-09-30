#!/usr/bin/env python3
"""netbench: a repeatable network benchmark against the site-10 iperf boxes.

Usage:
  netbench.py --target <iperf3-server> [--label "laptop wifi livingroom"] [--time 10] [--quick]
  netbench.py --compare benchmarks/A.json benchmarks/B.json

Targets: an iperf3 server (see docs/network/testing-and-benchmarks.md). Use an address on your own
VLAN for a same-network test and one on another VLAN for a routed test through your gateway.

Each run saves every raw iperf3 JSON plus a summary to ./benchmarks/<timestamp>-<label>.json
and prints a table and a NetBench score. The score is deliberately simple so it stays comparable:
  throughput  = geometric mean of the 5 TCP results (Mbit/s)
  reliability = 1 - mean UDP loss (0..1)
  latency     = idle ping p50 and ping under load p95 (bufferbloat), reported, not in the score
  score       = throughput x reliability
"""
import argparse, datetime, json, math, os, re, statistics, subprocess, sys, threading, time

OUT = os.path.join(os.getcwd(), "benchmarks")

TESTS = [  # name, iperf3 args, kind
    ("tcp_up_1",     ["-P", "1"],               "tcp"),
    ("tcp_down_1",   ["-P", "1", "-R"],         "tcp"),
    ("tcp_up_4",     ["-P", "4"],               "tcp"),
    ("tcp_down_4",   ["-P", "4", "-R"],         "tcp"),
    ("tcp_bidir",    ["--bidir"],               "bidir"),
    ("udp_up_200",   ["-u", "-b", "200M"],      "udp"),
    ("udp_down_200", ["-u", "-b", "200M", "-R"], "udp"),
    ("udp_down_600", ["-u", "-b", "600M", "-R"], "udp"),
]


def sh(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def iperf(target, args, secs, retries=5):
    cmd = ["iperf3", "-c", target, "-t", str(secs), "-O", "1", "-J", "--connect-timeout", "3000"] + args
    for i in range(retries):
        r = sh(cmd, timeout=secs + 30)
        try:
            j = json.loads(r.stdout)
        except Exception:
            j = {"error": (r.stderr or r.stdout)[:300]}
        if "busy" in json.dumps(j.get("error", "")):
            time.sleep(3 + 2 * i)
            continue
        return j
    return j


def summarize(kind, j):
    if "error" in j and "end" not in j:
        return {"error": j["error"]}
    e = j["end"]
    if kind == "tcp":
        return {"mbps": round(e["sum_received"]["bits_per_second"] / 1e6, 1),
                "retransmits": e.get("sum_sent", {}).get("retransmits")}
    if kind == "bidir":
        up = e["sum_received"]["bits_per_second"] / 1e6
        down = e["sum_received_bidir_reverse"]["bits_per_second"] / 1e6
        return {"mbps": round(up + down, 1), "up": round(up, 1), "down": round(down, 1)}
    s = e.get("sum_received") or e["sum"]  # UDP: receiver side (what actually arrived)
    loss = s.get("lost_percent", e["sum"].get("lost_percent", 0))
    mbps = s["bits_per_second"] / 1e6
    if "sum_received" not in e:  # older iperf3: sum is the sender rate
        mbps *= 1 - loss / 100
    return {"mbps": round(mbps, 1), "loss_pct": round(loss, 2),
            "jitter_ms": round(s.get("jitter_ms", e["sum"].get("jitter_ms", 0)), 3)}


def ping(target, n):
    r = sh(["ping", "-n", "-c", str(n), "-i", "0.2", target], timeout=n + 20)
    rtts = [float(x) for x in re.findall(r"time=([\d.]+)", r.stdout)]
    if not rtts:
        return {"error": "no replies"}
    rtts.sort()
    return {"p50_ms": round(statistics.median(rtts), 2), "p95_ms": round(rtts[int(0.95 * (len(rtts) - 1))], 2),
            "max_ms": round(rtts[-1], 2), "loss_pct": round(100 * (1 - len(rtts) / n), 1)}


def wifi_info():
    r = sh(["system_profiler", "SPAirPortDataType"], timeout=30).stdout
    blk = r.split("Current Network Information:")[1] if "Current Network Information:" in r else ""
    g = lambda k: (re.search(k + r": (.+)", blk) or [None, None])[1]
    return {"channel": g("Channel"), "signal_noise": g("Signal / Noise"), "tx_rate": g("Transmit Rate"),
            "mcs": g("MCS Index"), "phy": g("PHY Mode")}


def route_iface(target):
    r = sh(["route", "-n", "get", target]).stdout
    m = re.search(r"interface: (\S+)", r)
    return m.group(1) if m else None


def geomean(xs):
    xs = [x for x in xs if x and x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else 0


def run(a):
    os.makedirs(OUT, exist_ok=True)
    tests = TESTS[:5] + TESTS[6:7] if a.quick else TESTS
    meta = {"when": datetime.datetime.now().isoformat(timespec="seconds"), "label": a.label, "target": a.target,
            "secs": a.time, "iface": route_iface(a.target), "wifi": wifi_info(), "host": os.uname().nodename}
    print(f"netbench -> {a.target} via {meta['iface']}  wifi={meta['wifi'].get('channel')} {meta['wifi'].get('signal_noise')}")
    res, raw = {}, {}
    res["ping_idle"] = ping(a.target, 30)
    print(f"  {'ping_idle':14} {res['ping_idle']}")
    for name, args, kind in tests:
        loaded = {}
        if name == "tcp_down_4":  # measure latency under load (bufferbloat) during this test
            t = threading.Thread(target=lambda: loaded.update(ping(a.target, int(a.time * 4))))
            t.start()
        j = iperf(a.target, args, a.time)
        if name == "tcp_down_4":
            t.join()
            res["ping_loaded"] = loaded
        raw[name] = j
        res[name] = summarize(kind, j)
        print(f"  {name:14} {res[name]}")
        time.sleep(1)
    if "ping_loaded" in res:
        print(f"  {'ping_loaded':14} {res['ping_loaded']}")
    tput = geomean([res[n].get("mbps") for n, _, k in tests if k in ("tcp", "bidir")])
    losses = [res[n].get("loss_pct", 100) for n, _, k in tests if k == "udp"]
    rel = max(0.0, 1 - (sum(losses) / len(losses)) / 100) if losses else 1
    score = {"throughput_mbps": round(tput, 1), "reliability": round(rel, 3), "netbench_score": round(tput * rel, 1),
             "idle_p50_ms": res["ping_idle"].get("p50_ms"), "loaded_p95_ms": res.get("ping_loaded", {}).get("p95_ms")}
    print(f"\n  NetBench score {score['netbench_score']}  (throughput {score['throughput_mbps']} Mbit/s x reliability {score['reliability']})"
          f"  latency idle p50 {score['idle_p50_ms']} ms, under load p95 {score['loaded_p95_ms']} ms")
    fn = os.path.join(OUT, datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" +
                      re.sub(r"[^a-zA-Z0-9]+", "-", a.label or a.target).strip("-") + ".json")
    with open(fn, "w") as f:
        json.dump({"meta": meta, "score": score, "results": res, "raw": raw}, f, indent=1)
    print(f"  saved {os.path.relpath(fn)}")


def compare(files):
    rows = [json.load(open(f)) for f in files]
    keys = ["netbench_score", "throughput_mbps", "reliability", "idle_p50_ms", "loaded_p95_ms"]
    tests = [t[0] for t in TESTS]
    w = 22
    print("".ljust(16) + "".join((r["meta"].get("label") or r["meta"]["target"])[:w - 2].ljust(w) for r in rows))
    for k in keys:
        print(k.ljust(16) + "".join(str(r["score"].get(k)).ljust(w) for r in rows))
    for t in tests:
        vals = []
        for r in rows:
            x = r["results"].get(t, {})
            vals.append(f"{x.get('mbps','-')}" + (f" ({x['loss_pct']}%)" if "loss_pct" in x else ""))
        print(t.ljust(16) + "".join(v.ljust(w) for v in vals))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--target", help="iperf3 server address")
    p.add_argument("--label", default="")
    p.add_argument("--time", type=int, default=10)
    p.add_argument("--quick", action="store_true", help="6 tests instead of 8")
    p.add_argument("--compare", nargs="+")
    a = p.parse_args()
    if not a.compare and not a.target:
        p.error("--target is required")
    compare(a.compare) if a.compare else run(a)
