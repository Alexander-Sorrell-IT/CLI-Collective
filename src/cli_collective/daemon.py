"""cli-collective daemon — umbrella that manages all stack daemons together.

Starting the collective daemon starts all three underlying daemons:
  - wikia daemon    (keep wikis up to date, auto-detect CLI changes)
  - enforcement daemon  (auto-sync deployed projects when wikia changes)
  - fleet daemon    (monitor active fleets headlessly)

Each daemon runs independently in its own process with its own PID file and
log. The collective daemon is a thin coordinator — it starts the ones that
aren't already running, and stopping it stops all three.

Commands:
  cli-collective daemon start [--foreground]   # start all daemons
  cli-collective daemon stop                    # stop all daemons
  cli-collective daemon status                  # show all daemon states
  cli-collective daemon logs [-n N]             # tail all logs interleaved
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time

from . import __version__


# ---------------------------------------------------------------------------
# Helpers to delegate to each package's daemon CLI
# ---------------------------------------------------------------------------

def _run(*argv, capture: bool = True):
    """Run a CLI command. Returns (returncode, stdout+stderr) when capture=True."""
    try:
        r = subprocess.run(list(argv), capture_output=capture, text=True, timeout=30)
        return r.returncode, (r.stdout + r.stderr).strip() if capture else ""
    except Exception as e:
        return 1, str(e)


def _wikia_daemon(*sub):
    return ["wikia", "daemon", *sub]


def _enforcement_daemon(*sub):
    return ["cli-enforcement", "daemon", *sub]


def _fleet_daemon(*sub):
    return ["cli-fleet", "daemon", *sub]


# ---------------------------------------------------------------------------
# Package availability
# ---------------------------------------------------------------------------

def _available(pkg: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(pkg.replace("-", "_")) is not None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_start(args):
    foreground_flag = ["--foreground"] if getattr(args, "foreground", False) else []
    started = []
    skipped = []

    for name, cmd_fn, pkg in [
        ("wikia", _wikia_daemon, "cli_wikia"),
        ("enforcement", _enforcement_daemon, "cli_enforcement"),
        ("fleet", _fleet_daemon, "cli_fleet"),
    ]:
        if not _available(pkg):
            skipped.append(f"{name} (not installed)")
            continue
        rc, out = _run(*cmd_fn("start", *foreground_flag))
        if rc == 0:
            started.append(name)
            print(f"  ✓ {name} daemon started")
        else:
            # May already be running — show output and continue
            print(f"  {name} daemon: {out[:120]}")

    if skipped:
        print(f"  skipped: {', '.join(skipped)}")
    if started:
        print(f"\nAll daemons running. Use `cli-collective daemon status` to check.")


def cmd_stop(args):
    stopped = []
    for name, cmd_fn, pkg in [
        ("fleet", _fleet_daemon, "cli_fleet"),
        ("enforcement", _enforcement_daemon, "cli_enforcement"),
        ("wikia", _wikia_daemon, "cli_wikia"),
    ]:
        if not _available(pkg):
            continue
        rc, out = _run(*cmd_fn("stop"))
        print(f"  {name}: {out[:120]}" if out else f"  {name}: stopped")
        stopped.append(name)


def cmd_status(args):
    print(f"cli-collective daemon status (v{__version__})\n")
    for name, cmd_fn, pkg in [
        ("wikia", _wikia_daemon, "cli_wikia"),
        ("enforcement", _enforcement_daemon, "cli_enforcement"),
        ("fleet", _fleet_daemon, "cli_fleet"),
    ]:
        if not _available(pkg):
            print(f"  {name:12} NOT INSTALLED")
            continue
        rc, out = _run(*cmd_fn("status"))
        # Print the first line of status compactly
        first = (out.splitlines()[0] if out.splitlines() else "no output").strip()
        print(f"  {name:12} {first}")


def cmd_logs(args):
    n = getattr(args, "lines", 40)
    for name, cmd_fn, pkg in [
        ("wikia", _wikia_daemon, "cli_wikia"),
        ("enforcement", _enforcement_daemon, "cli_enforcement"),
        ("fleet", _fleet_daemon, "cli_fleet"),
    ]:
        if not _available(pkg):
            continue
        print(f"\n=== {name} daemon log (last {n} lines) ===")
        _run(*cmd_fn("logs", "-n", str(n)), capture=False)
