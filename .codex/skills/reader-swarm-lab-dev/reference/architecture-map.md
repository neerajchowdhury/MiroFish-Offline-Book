# Reader Swarm Lab Architecture Map

## Bounded Contexts

1. Ingestion: safely parse files into chunks.
2. Manuscript Intelligence: produce book bible, beat map, DNF hotspots.
3. Persona Factory: produce compact reader agents.
4. Platform Models: translate reactions into platform-native behavior.
5. Simulation Engine: run rounds, exposure, opinion updates.
6. Scoring: produce distributions and risk scores.
7. Reporting: generate report from structured evidence.
8. Calibration: compare simulation against beta-reader and comp-title signals.
9. Safety: prevent prompt injection, data leakage, deceptive output.

## Boundary Rule

LLM calls must not be scattered across modules. Use one adapter layer:

```text
module -> PromptRequest DTO -> llm_adapter -> SchemaValidatedOutput -> module
```

## Default Storage

Start with local SQLite and project folders. Do not add cloud storage until the local workflow is validated.
