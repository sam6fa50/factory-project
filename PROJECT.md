# Project

## Problem

Manufacturing and simulation teams can collect simulator and machine telemetry, but diagnosing why modeled behavior diverges from observed behavior is still labor-intensive. The project explores whether an agent-facing, simulator-neutral telemetry layer can identify residuals, produce useful first-pass blame hypotheses, and eventually choose safe experiments that reduce diagnostic ambiguity.

## Target Users

Current assumed users are controls engineers, simulation engineers, commissioning engineers, digital-twin/model credibility owners, factory automation teams, controls R&D teams, and AI agents assisting those teams. Customer and buyer evidence is not validated yet.

## Value Proposition

The intended value is faster diagnosis of model/component mismatches: normalize telemetry once, detect expectation violations, surface likely causes with supporting evidence, and identify the next diagnostic action. The deeper thesis is active, uncertainty-aware model blame: the system should know when passive observation is ambiguous and propose bounded experiments that distinguish physical faults, sensor/actuator faults, tag mapping errors, control behavior, and bad model assumptions.

## Proposed Solution

The MVP uses Factory I/O as the first simulator backend and SimIR as the stable boundary. Simulator-specific raw tags are mapped to canonical SimIR samples. A telemetry pooler buffers samples and derives features. A residual engine evaluates expectation rules. A blame generator turns residuals into hypotheses and reports.

```text
backend adapter -> SimIR telemetry -> features -> residuals -> blame hypotheses
```

The research track extends this with an epistemic loop:

```text
observe -> update hypotheses -> choose safe experiment -> act -> compare model vs observed behavior
```

Current code implements the first loop. The active-diagnosis loop is represented only by a toy executable experiment until it earns promotion into SimIR and product code.

## Scope

In scope now:

- Mock Factory I/O telemetry for deterministic MVP development.
- Factory I/O live adapter scaffold for Web API, OPC UA, and Modbus paths.
- SimIR models for assets, tags, telemetry, runs, commands, faults, capabilities, residuals, and blame hypotheses.
- Rule-based residual detection for conveyor transition deadlines.
- First-pass blame hypothesis generation and Markdown reports.
- Reproducible baseline experiment under `experiments/factory_io_mock_residual_baseline/`.
- Reproducible active-diagnosis toy experiment under `experiments/aemid_motor_active_diagnosis/`.
- Reproducible everyday toy cases under `experiments/everyday_model_blame_toy_cases/` for explaining the idea with laptop temperature, phone battery, coffee cooling, and video-call latency.
- Future real-factory telemetry adapters that map PLC/protocol, SCADA, historian/database, edge gateway/MQTT, and alarm/event evidence into SimIR.

## Non-Goals

Out of scope for the current MVP:

- Claiming validated live Factory I/O integration without a real endpoint.
- Claiming that real-vs-sim comparison is implemented before a real telemetry stream and simulator prediction stream exist together.
- Competing as generic predictive maintenance, generic anomaly detection, machine vision inspection, or a broad digital-twin platform.
- Inventing a competing industrial ontology instead of using established substrates where they fit.
- Sending commands to real factory systems before explicit safety, security, and customer-governance review.
- Installing a persistent AI memory system as project authority.
- Building a general knowledge-management product inside this repo.
- Creating heavyweight specs for every task.
- Replacing source code, tests, and experiment results with chat summaries.

## Architecture

Core package: `src/model_blame/`

- `simir/`: simulator-neutral data models and adapter interfaces.
- `adapters/mock/`: deterministic mock Factory I/O-style telemetry.
- `adapters/factory_io/`: live Factory I/O adapter and transport scaffolds.
- `telemetry/`: buffering, logging, polling, and derived features.
- `residuals/`: expectation rules and residual evaluation.
- `blame/`: hypothesis generation and report formatting.
- `agent_api/`: agent-facing client and service factory over SimIR.

Configuration lives in `config/`. Tests live in `tests/`. Executable experiments live in `experiments/`.

Future architecture should treat OPC UA/AAS as likely semantic/operational substrates and FMI as a likely simulation-model substrate rather than replacing them. SimIR remains the project-specific normalization layer for agent-facing diagnosis and experimental semantics.

## Settled Decisions

- DECISION: SimIR is the boundary between simulator-specific APIs and agent-facing diagnosis logic.
- DECISION: Factory I/O remains the current practical MVP proof track; active diagnosis is a research track until promoted by executable evidence.
- DECISION: Git-tracked source, tests, canonical docs, and experiment definitions are authoritative.
- DECISION: Root `AGENTS.md` is the portable cross-agent control plane.
- DECISION: Claude gets a tiny `CLAUDE.md` adapter that imports `AGENTS.md`; Gemini is configured to read `AGENTS.md` directly.
- DECISION: External memory/spec systems are deferred until the project has enough validated knowledge or durable feature behavior to justify them.
- DECISION: Real-factory adapters should default to read-only until write permission, safety envelope, credentials, and network boundaries are explicitly reviewed.

## Current Maturity

This is a tested local MVP plus toy research/explanation experiments, not a production system. Mock scenarios are executable and covered by tests. Live Factory I/O transport behavior is scaffolded but not verified against an actual Factory I/O deployment. The active diagnosis experiment supports the strategic thesis in a controlled toy setting only. The everyday toy cases are explanatory demos, not product validation.
