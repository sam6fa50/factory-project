# AGENTS.md

## Purpose

This repository is the canonical shared operating state for a business and engineering project: a Factory I/O model-blame MVP, active-diagnosis research track, and explanatory toy-case demos that normalize telemetry into SimIR or comparable toy observations, detect residuals, and produce blame hypotheses.

AI conversations, memory entries, research notes, and pasted chats are inputs. They are not authoritative until reconciled into Git-tracked source, tests, experiments, or canonical project documents.

## Read First

For most tasks, read only the smallest useful set:

1. `README.md` for orientation and commands.
2. `ORIENTATION.md` when directory purpose, repo layout, or "where does this belong?" matters.
3. `EXECUTION.md` for current state and next actions.
4. `PROJECT.md` when scope, product, architecture, or business intent matters.
5. `KNOWLEDGE.md` when durable facts, assumptions, provenance, or open questions matter.
6. Task-local source files, tests, configs, or experiment README files.

Do not load the whole repository knowledge base when a small code change only needs nearby code and tests.

## Authority

Use this source hierarchy when project truth conflicts:

1. Verified current behavior, tests, measured experiment results.
2. Accepted specs or living execution plans.
3. Explicit current decisions in `PROJECT.md` or `KNOWLEDGE.md`.
4. Current source code and configuration.
5. Durable verified knowledge in `KNOWLEDGE.md`.
6. `EXECUTION.md` operational notes.
7. Memory systems, AI conversation summaries, raw chats, and unsourced AI inference.

If sources disagree, surface the conflict and update the canonical files only after reconciliation.

## Task Routing

- Code change: inspect relevant `src/`, `tests/`, and `config/` files first. Keep edits scoped and run `python -m pytest`.
- Simulator adapter work: preserve the `SimulatorAdapter` and SimIR boundary. Backend quirks belong in adapters, not residual or blame logic.
- Residual or blame logic: update tests and the baseline experiment notes when behavior changes.
- Experiment work: put executable experiments under `experiments/<purpose>/` with a README covering question, hypothesis, setup, procedure, expected result, observed result, limits, and next action.
- Knowledge ingestion: extract claims, requirements, decisions, contradictions, code, experiment ideas, and sources from incoming chats. Promote concise reconciled knowledge only; do not paste transcripts.
- Research: prefer primary sources, record provenance, and distinguish facts from hypotheses or assumptions.

## Planning

Small tasks can proceed directly with code and tests. For substantial multi-file or multi-session work, create a self-contained living plan under `plans/<short-purpose>.md`. Follow the OpenAI ExecPlan principle: an unfamiliar contributor should be able to resume from the plan and current working tree without the original chat.

Do not create heavyweight specs for trivial tasks. Evaluate OpenSpec or Spec Kit only when a feature needs durable behavioral agreement beyond a normal plan and tests.

## Validation

Default validation:

```powershell
python -m pytest
```

Useful experiment check:

```powershell
python experiments/factory_io_mock_residual_baseline/run.py
```

Useful research-track check:

```powershell
python experiments/aemid_motor_active_diagnosis/run.py
```

Useful explanation-demo check:

```powershell
python experiments/everyday_model_blame_toy_cases/run.py
```

Do not claim live Factory I/O behavior is verified unless a real live endpoint or driver was used and the result is recorded.

## Knowledge Updates

Update canonical files when work changes project truth:

- `PROJECT.md`: slow-changing product, architecture, scope, constraints, or accepted decisions.
- `ORIENTATION.md`: human-first map of root files and directories. Update it when a change adds, removes, renames, or repurposes a root file/directory, or when a directory gains a new kind of content.
- `KNOWLEDGE.md`: durable findings, evidence, hypotheses, uncertainties, and source records.
- `EXECUTION.md`: current objective, active work, next actions, blockers, risks, or recently completed handoff notes.
- Experiment README files: experiment-specific setup, observed results, interpretation, and limits.

Delete or move obsolete operational notes instead of accumulating stale logs.

## Security And Dependencies

Do not commit secrets, credentials, customer confidential data, personal data, or unreviewed licensed material. Prefer local processing by default. Do not enable cloud sync, telemetry, remote indexing, or third-party storage without identifying what data would leave local infrastructure.

No external memory, spec, MCP, or agent framework is adopted by default. Basic Memory, projectmem, MemoryCustodian, OpenSpec, Spec Kit, and agentmemory are evaluated in `references/ai-native-repository-survey.md`; install or configure them only after an explicit project decision.
