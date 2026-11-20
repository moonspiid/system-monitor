# System Monitor

<p>
  <img alt="python, 3.8+" src="https://img.shields.io/badge/python-3.8%2B-3776ab?labelColor=30363d">
  <img alt="dependencies, none required" src="https://img.shields.io/badge/dependencies-none%20required-2ea043?labelColor=30363d">
  <img alt="platform, linux or macOS" src="https://img.shields.io/badge/platform-linux%20%7C%20macOS-8957e5?labelColor=30363d">
  <img alt="output to a log file" src="https://img.shields.io/badge/output-log%20file-bf8700?labelColor=30363d">
  <br>
  <img alt="single-file CLI" src="https://img.shields.io/badge/cli-single%20file-1f6feb?labelColor=30363d">
  <img alt="install, none" src="https://img.shields.io/badge/install-none-2ea043?labelColor=30363d">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-ea7a15?labelColor=30363d">
</p>

**CPU and memory usage, logged to a file on a schedule — one Python file, nothing to install.**

It uses `psutil` if it happens to be installed, and otherwise reads Linux's `/proc` files directly,
so a bare Python 3 install is all you need.

<h3 align="center">
  <a href="monitor.py">→ Download monitor.py</a>
</h3>

<p align="center">
  One file, no package manager, no virtualenv, no config file.
  <br>
  Copy it anywhere, run it, read the log.
</p>

## Contents

- [Why](#why)
- [Quick start](#quick-start)
- [Options](#options)
- [Examples](#examples)
- [How it works](#how-it-works)
- [Good to know](#good-to-know)
- [License](#license)

## Why

When a machine slows down, the useful question is never "is it slow now?" — it is "what was it doing
when it started?" A single number you read after the fact tells you nothing. A file of numbers, taken
every minute for a week, tells you the story.

This script is that file. No agent to install, no dashboard to host, no time-series database: one
line per sample, in a shape you can `grep`, plot, or paste into a spreadsheet.

## Quick start

1. Save [`monitor.py`](monitor.py) anywhere and open a terminal next to it.
2. Run it: `python3 monitor.py`
3. Watch `monitor.log` fill up in the same folder.

That samples every 60 seconds and appends a line to `monitor.log`. Each line looks like this:

```
2026-11-16T17:39:29+00:00 cpu=   0.00% mem=   9.06% (355/3915 MB)
```

Timestamp, CPU percentage, memory percentage, and memory used out of total in MB — all separated by
spaces, so the log is easy to grep or feed into a spreadsheet later. Stop it with `Ctrl+C`.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `-i`, `--interval` | `60` | Seconds between samples |
| `-n`, `--samples` | `0` | Number of samples to take, then exit (`0` means run until stopped) |
| `-l`, `--log` | `monitor.log` | File to append readings to |

## Examples

Take 12 readings, 5 seconds apart, then stop:

```bash
python3 monitor.py --interval 5 --samples 12
```

Write to a specific file:

```bash
python3 monitor.py --log /var/tmp/system-usage.log
```

Run it in the background and keep a record overnight:

```bash
nohup python3 monitor.py --interval 300 --log overnight.log &
```

## How it works

- `psutil`, when present, gives exact per-process and system totals in one call.
- Without it, the script reads `/proc/stat` twice and takes the difference to get CPU percentage, and
  `/proc/meminfo` for used and total memory.
- If neither is available (macOS or Windows without `psutil`), it exits with a clear message instead
  of logging wrong numbers.

Pick whichever path is available, sample on a timer, append one formatted line, flush. That is the
whole program.

## Good to know

- The log file is appended to, never overwritten, so you can restart the script without losing
  history. A header line is written the first time the file is created.
- `monitor.log` is listed in `.gitignore`, so your collected readings stay out of version control.
- On macOS or Windows, install `psutil` with `pip install psutil` — `/proc` only exists on Linux.
- The script stays quiet apart from the readings it prints and logs; it does not rotate or trim the
  log file, so delete or rotate it yourself if you run it for a long time.

## License

[MIT](LICENSE) © 2026 moonspiid — use it, modify it, ship it.
