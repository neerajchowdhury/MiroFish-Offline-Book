# Token Budget Reference

Use this before large Reader Swarm Lab tasks.

## Budgets

| Task | Target context | Rule |
|---|---:|---|
| Repo orientation | <= 4k tokens | tree + package files + route/module map only |
| One backend slice | <= 8k tokens | read target module + direct dependencies only |
| One frontend screen | <= 8k tokens | read screen + reusable components only |
| Prompt-module work | <= 6k tokens | read prompt + schema + one fixture |
| Security review | <= 10k tokens | changed files + boundary files + config |
| Simulation run design | <= 8k tokens | schemas + orchestrator + one platform model |

## Compression Patterns

- Convert long prose to schemas.
- Convert repeated persona prompts to trait vectors.
- Convert manuscript passages to scene/chapter summaries.
- Store generated posts only when needed; otherwise store sentiment metadata.
- Use IDs for recurring agents, platforms, beats, tropes, and chapters.

## File Card Format

Add to `docs/reader-swarm/context-map.md`:

```text
File:
Purpose:
Public interface:
Reads/writes:
Security sensitivity:
Last relevant change:
```
