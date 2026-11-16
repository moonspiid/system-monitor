# System Monitor

A small Python script that logs system CPU and memory usage to a file on a
schedule. It depends on nothing but Python 3: it uses `psutil` if it happens to
be installed, and otherwise reads Linux's `/proc` files directly.

## Requirements

- Python 3.8 or newer
- Linux or macOS (on Linux it works with no extra packages; on macOS or
  Windows, install `psutil` with `pip install psutil`)
- Optional: `pip install psutil` for more accurate readings

## Usage

Run it from a terminal:

```bash
python3 monitor.py
```

That samples every 60 seconds, appending a line to `monitor.log` in the current
directory. Each line looks like this:

```
2026-11-16T17:39:29+00:00 cpu=  0.00% mem=  9.06% (355/3915 MB)
```

The timestamp, CPU percentage, memory percentage and memory used out of total
(in MB) are separated by spaces, so the log is easy to grep or feed into a
spreadsheet later.

Stop it with `Ctrl+C`.

### Options

| Option | Default | Meaning |
| --- | --- | --- |
| `-i`, `--interval` | `60` | Seconds between samples |
| `-n`, `--samples` | `0` | Number of samples to take, then exit (`0` means run until stopped) |
| `-l`, `--log` | `monitor.log` | File to append readings to |

### Examples

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

## Notes

- The log file is appended to, never overwritten, so you can restart the script
  without losing history. A header line is written the first time the file is
  created.
- `monitor.log` is listed in `.gitignore` so your collected readings stay out of
  version control.
- The script stays quiet apart from the readings it prints and logs; it does not
  rotate or trim the log file, so delete or rotate it yourself if you run it for
  a long time.
