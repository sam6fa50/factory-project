# Execution

Last updated: 2026-08-13.

## Current Objective

Maintain the AI-native repository foundation while advancing the Factory I/O model-blame MVP and the active-diagnosis research track without confusing the two maturity levels.

## Current Implementation State

- Python MVP exists under `src/model_blame/`.
- Mock Factory I/O scenarios run locally without Factory I/O installed.
- Live Factory I/O adapter is scaffolded but not validated against a real endpoint.
- Tests cover SimIR models, tag mapping, mock adapter behavior, residual detection, blame hypotheses, live config scaffolding, and experiment artifact contracts.
- `experiments/factory_io_mock_residual_baseline/` is the current practical proof track.
- `experiments/aemid_motor_active_diagnosis/` is a toy research proof for active, uncertainty-aware diagnosis.
- `experiments/everyday_model_blame_toy_cases/` is an explanation-demo track for fake non-industrial model-blame scenarios.
- Repository has been initialized as Git metadata locally, but no initial commit has been made.

## Active Work

- The five supplied shared chats and the sister Candidate D toy-case task have been ingested, deduplicated, and promoted into canonical docs plus executable experiments.
- `ORIENTATION.md` is now the human-first directory map and must be updated when repo layout or directory purpose changes.
- No raw chat transcripts are stored in the repository.

## Next Meaningful Actions

1. Choose the next primary implementation path: live Factory I/O bridge validation or a deeper controlled active-diagnosis experiment.
2. If live Factory I/O comes first, choose the transport path: custom/Web API bridge, OPC UA, or Modbus TCP.
3. If active diagnosis comes first, promote a minimal experiment interface into SimIR: experiment spec, safety envelope, hypothesis posterior, and next-best experiment recommendation.
4. Add at least one more configured residual rule, preferably actuator command with no downstream effect.
5. Add focused tests for telemetry features and logging behavior.
6. Identify the first real telemetry source shape: PLC/protocol, SCADA API, historian/database, edge gateway/MQTT, or Factory I/O-specific bridge.
7. Decide whether the old NumPy/SciPy motor ranking implementation should remain superseded by `aemid_motor_active_diagnosis` or be ported as a separate experiment later.
8. Decide repository license before outside distribution.

## Open Decisions

- Which live transport should be implemented first: Web API bridge, OPC UA, or Modbus TCP?
- Should the next proof prioritize Factory I/O live validation or the active motor-diagnosis research track?
- Which timestamp should SimIR treat as authoritative when a real source provides device time, gateway time, historian insert time, and adapter receive time?
- Should real-factory adapters default to permanently read-only, or allow writes after an explicit safety/security review?
- Should generated experiment outputs remain ignored, or should selected stable snapshots be tracked as evidence?
- Should a local memory layer or project-specific knowledge-consolidation skill be adopted after more ingestion batches?

## Risks And Debt

- Live Factory I/O behavior is not verified.
- The two-stream real telemetry versus simulator prediction thesis is not implemented.
- Business/customer evidence is still mostly assumed.
- The active-diagnosis experiment is a toy model and should not be presented as industrial validation.
- No project license is declared.
- Generated caches and run outputs exist locally and should remain ignored unless intentionally promoted.
- Optional memory tools could create a competing source of truth if adopted without governance.

## Recently Completed

- Ingested five large shared ChatGPT chats and reconciled durable claims into canonical project files.
- Added source records for the shared chats and verified industrial standards/market-signal sources.
- Preserved Factory I/O as the current MVP proof track while adding active diagnosis as a separate research track.
- Added `experiments/aemid_motor_active_diagnosis/` with a deterministic DC motor active-probe experiment.
- Added `experiments/everyday_model_blame_toy_cases/` with the laptop CPU-load fake scenario and three additional plain-language model-blame cases.
- Added `ORIENTATION.md` plus thin agent-adapter instructions to keep human directory orientation current.
- Surveyed current AGENTS.md, Codex, Claude, Gemini, Cursor, Copilot, Agent Skills, ExecPlans, Basic Memory, OpenSpec, Spec Kit, MemoryCustodian, projectmem, and agentmemory sources.
- Chose plain Git plus Markdown as the repository authority.
- Deferred memory/spec framework installation pending demonstrated need.
- Created canonical repository files and thin agent adapters.
- Promoted the mock demo into `experiments/factory_io_mock_residual_baseline/`.
- Verified `python -m pytest` with 20 passing tests after the toy-case synthesis pass.
- Verified the baseline experiment command and recorded the expected scenario split.
- Verified the active motor-diagnosis experiment command: `active_probe` lowered average final entropy versus `passive_idle` and produced no safety violations.
- Verified the everyday toy-case experiment command: laptop/background CPU load, phone/GPS activity, coffee/insulated mug, and video/cloud backup upload all ranked the intended hidden explanation first.
