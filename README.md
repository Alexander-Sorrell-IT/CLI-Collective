# CLI Collective

**One install for the whole stack.** The Collective bundles three tools that
build on each other:

```
cli-wikia        knowledge — what each AI CLI can do (hooks, MCP, config)
   ▲
cli-enforcement  control — hook-level points / tiers / KB-gates, on any model
   ▲
cli-fleet        power — launch many enforced Claude agent teams in parallel
```

## Install

```bash
pip install cli-collective      # pulls in cli-wikia + cli-enforcement + cli-fleet
cli-collective                  # show the stack + versions
```

Each tool is also installable on its own — use just `cli-wikia` for an offline
AI-CLI reference, add `cli-enforcement` for governance, add `cli-fleet` for
parallel agent teams.

## License
[PolyForm Noncommercial 1.0.0](LICENSE) — free for noncommercial use.
Commercial use requires a paid license: matrixbuilderops@proton.me
