"""cli-collective — umbrella for the stack. Installing it pulls in all three
tools; the `cli-collective` command just shows what's present and what each does."""
from __future__ import annotations

__version__ = "0.1.3"

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


def main(argv=None):
    print("The Collective — AI coding-agent stack\n")
    for mod, cmd, desc in LAYERS:
        v = _version(mod)
        mark = f"v{v}" if v else "NOT INSTALLED"
        print(f"  {cmd:16} {mark:14} {desc}")
    print("\nLayering:  cli-wikia  ->  cli-enforcement  ->  cli-fleet")
    print("Try:       wikia models | cli-enforcement deploy claude | cli-fleet launch <config>")


if __name__ == "__main__":
    main()
