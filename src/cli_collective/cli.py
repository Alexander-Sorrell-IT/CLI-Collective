"""cli-collective — umbrella for the stack. Installing it pulls in all three
tools; the `cli-collective` command shows what's present, what each does, and
whether the collective models.json override is in effect."""
from __future__ import annotations

import argparse

from . import __version__

LAYERS = [
    ("cli_wikia", "wikia", "knowledge — what each AI CLI can do (hooks, MCP, config), derived from offline wikis"),
    ("cli_enforcement", "cli-enforcement", "control — hook-level points/tiers/KB-gates, deployed onto any model via wikia"),
    ("cli_fleet", "cli-fleet", "power — launch multiple enforced Claude agent teams in parallel, hardware-aware"),
]


def _version(mod):
    try:
        m = __import__(mod)
        return getattr(m, "__version__", "?")
    except ImportError:
        return None


def _override_status():
    """Report whether any model overrides are active in the collective models.json."""
    try:
        from importlib import resources
        import json
        text = (resources.files("cli_collective") / "models.json").read_text(encoding="utf-8")
        data = json.loads(text)
        sections = ["wikia", "enforcement", "fleet"]
        overrides = {}
        for s in sections:
            models = data.get(s, {}).get("models", {})
            if models:
                overrides[s] = sorted(models.keys())
        return overrides
    except Exception:
        return {}


def cmd_status(args=None):
    print("The Collective — AI coding-agent stack\n")
    for mod, cmd, desc in LAYERS:
        v = _version(mod)
        mark = f"v{v}" if v else "NOT INSTALLED"
        print(f"  {cmd:16} {mark:14} {desc}")
    print("\nLayering:  cli-wikia  ->  cli-enforcement  ->  cli-fleet")
    print("Try:       wikia models | cli-enforcement deploy claude | cli-fleet launch <config>")

    overrides = _override_status()
    if overrides:
        print("\ncollective model overrides active (models.json):")
        for section, models in overrides.items():
            print(f"  {section}: {', '.join(models)}")
    else:
        print("\ncollective models.json: no overrides (packages use their own defaults)")
        print("  edit cli_collective/models.json to override any model in all three packages at once")


def build_parser():
    p = argparse.ArgumentParser(
        prog="cli-collective",
        description="The Collective — one install for the whole AI coding-agent stack.",
    )
    p.add_argument("--version", action="version", version=f"cli-collective {__version__}")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status", help="show installed stack versions and override status").set_defaults(func=cmd_status)

    from . import daemon as DM

    dp = sub.add_parser("daemon", help="start/stop/status all stack daemons together")
    dsub = dp.add_subparsers(dest="daemon_cmd", required=True)

    d = dsub.add_parser("start", help="start all daemons (wikia + enforcement + fleet)")
    d.add_argument("--foreground", "-f", action="store_true", help="run in foreground (blocks)")
    d.set_defaults(func=DM.cmd_start)

    d = dsub.add_parser("stop", help="stop all running daemons")
    d.set_defaults(func=DM.cmd_stop)

    d = dsub.add_parser("status", help="show running state of all daemons")
    d.set_defaults(func=DM.cmd_status)

    d = dsub.add_parser("logs", help="tail logs from all daemons")
    d.add_argument("-n", "--lines", type=int, default=40, help="lines per daemon (default: 40)")
    d.set_defaults(func=DM.cmd_logs)

    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        # Default: show status (backward compat — bare `cli-collective` still works)
        cmd_status()


if __name__ == "__main__":
    main()
