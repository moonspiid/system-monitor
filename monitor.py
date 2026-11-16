#!/usr/bin/env python3
"""Log system CPU and memory usage to a file.

Uses psutil when it is installed and falls back to /proc on Linux, so it runs
with a bare Python 3 install.

Examples:
    python3 monitor.py                      # 60s interval, forever, monitor.log
    python3 monitor.py --interval 5 -n 12   # 12 samples, 5s apart
    python3 monitor.py --log /var/tmp/sys.log
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time

DEFAULT_LOG = "monitor.log"


def _psutil_sample():
    """Return (cpu_percent, mem_percent, mem_used_mb, mem_total_mb) or None."""
    try:
        import psutil
    except ImportError:
        return None

    mem = psutil.virtual_memory()
    return (
        psutil.cpu_percent(interval=None),
        mem.percent,
        mem.used / (1024 * 1024),
        mem.total / (1024 * 1024),
    )


def _read_proc_stat():
    """Return (idle, total) jiffies from /proc/stat."""
    with open("/proc/stat", "r", encoding="utf-8") as handle:
        fields = handle.readline().split()[1:]
    values = [int(value) for value in fields]
    idle = values[3] + (values[4] if len(values) > 4 else 0)  # idle + iowait
    return idle, sum(values)


def _read_proc_meminfo():
    """Return (used_mb, total_mb) from /proc/meminfo."""
    info = {}
    with open("/proc/meminfo", "r", encoding="utf-8") as handle:
        for line in handle:
            key, _, rest = line.partition(":")
            info[key] = int(rest.split()[0])  # kB
    total = info["MemTotal"]
    used = total - info.get("MemAvailable", info.get("MemFree", 0))
    return used / 1024, total / 1024


class ProcSampler:
    """CPU/memory sampler for Linux without psutil."""

    def __init__(self) -> None:
        self._last = _read_proc_stat()

    def sample(self):
        idle, total = _read_proc_stat()
        last_idle, last_total = self._last
        self._last = (idle, total)

        total_delta = total - last_total
        idle_delta = idle - last_idle
        cpu = 0.0 if total_delta <= 0 else 100.0 * (total_delta - idle_delta) / total_delta

        used_mb, total_mb = _read_proc_meminfo()
        mem = 100.0 * used_mb / total_mb if total_mb else 0.0
        return cpu, mem, used_mb, total_mb


def make_sampler():
    """Pick psutil if present, otherwise the /proc sampler."""
    probe = _psutil_sample()
    if probe is not None:
        time.sleep(0.2)  # let psutil establish a baseline
        return lambda: _psutil_sample() or probe

    if os.path.exists("/proc/stat"):
        sampler = ProcSampler()
        sampler.sample()  # prime the baseline
        return sampler.sample

    sys.exit("monitor.py needs psutil or Linux /proc to read system usage.")


def format_line(cpu: float, mem: float, used_mb: float, total_mb: float) -> str:
    stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"{stamp} cpu={cpu:6.2f}% "
        f"mem={mem:6.2f}% ({used_mb:.0f}/{total_mb:.0f} MB)\n"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Log system CPU and memory usage.")
    parser.add_argument(
        "-i", "--interval", type=float, default=60.0,
        help="seconds between samples (default: 60)",
    )
    parser.add_argument(
        "-n", "--samples", type=int, default=0,
        help="stop after N samples (default: 0, run until interrupted)",
    )
    parser.add_argument(
        "-l", "--log", default=DEFAULT_LOG,
        help=f"log file to append to (default: {DEFAULT_LOG})",
    )
    args = parser.parse_args(argv)

    if args.interval <= 0:
        parser.error("--interval must be greater than 0")

    sample = make_sampler()

    try:
        with open(args.log, "a", encoding="utf-8", buffering=1) as log:
            if log.tell() == 0:
                log.write("# timestamp cpu mem (used/total MB)\n")
                log.flush()

            count = 0
            while args.samples <= 0 or count < args.samples:
                cpu, mem, used_mb, total_mb = sample()
                line = format_line(cpu, mem, used_mb, total_mb)
                log.write(line)
                log.flush()
                sys.stdout.write(line)
                count += 1
                if args.samples > 0 and count >= args.samples:
                    break
                time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    except OSError as exc:
        sys.exit(f"cannot write {args.log}: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
