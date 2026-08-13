# Factory Model-Blame Workspace

This repository is an AI-native business and engineering workspace for an early model-blame product concept. The current practical MVP normalizes Factory I/O-style simulator telemetry into SimIR, detects residuals against expectation rules, and emits first-pass blame hypotheses.

The broader research direction is active, uncertainty-aware machine understanding: compare observed machine behavior against model expectations, identify whether the likely mismatch is in the model, component, tag mapping, sensor, actuator, or control behavior, and eventually choose safe experiments that reduce diagnostic ambiguity.

The working loop is:

```text
simulator telemetry -> SimIR samples -> telemetry features -> residuals -> blame hypotheses
```

The repository now treats Git-tracked source code, tests, experiments, and concise project documents as the canonical shared state for humans and AI agents. Incoming chats and research are inputs that must be extracted, reconciled, and promoted into the right canonical surface.

## Project State

The implementation is an MVP. It has a mock Factory I/O adapter, a live Factory I/O scaffold, a simulator-neutral SimIR boundary, a rule-based residual engine, blame hypothesis generation, and tests. The live Web API, OPC UA, and Modbus transports still need real Factory I/O endpoint wiring before they can be claimed as validated live integrations.

There are now three executable proof tracks:

- `experiments/factory_io_mock_residual_baseline/`: conveyor residual and blame baseline for the current MVP.
- `experiments/aemid_motor_active_diagnosis/`: toy active-diagnosis experiment for the longer research thesis.
- `experiments/everyday_model_blame_toy_cases/`: simple fake scenarios for explaining model blame outside industrial context.

Read these files for deeper context:

- `PROJECT.md`: stable product, architecture, scope, constraints, and decisions.
- `ORIENTATION.md`: human-first map of root files and directories.
- `KNOWLEDGE.md`: durable facts, hypotheses, open questions, and provenance.
- `EXECUTION.md`: current operating state and next actions.
- `AGENTS.md`: agent routing, validation, planning, and knowledge-update rules.
- `references/ai-native-repository-survey.md`: current survey of AGENTS.md, memory, spec, and agent compatibility systems.

## Install

```powershell
python -m pip install -e ".[dev]"
```

Optional live Factory I/O transports:

```powershell
python -m pip install -e ".[factoryio-web]"
python -m pip install -e ".[factoryio-opcua]"
python -m pip install -e ".[factoryio-modbus]"
```

## Run The Baseline Experiment

```powershell
python experiments/factory_io_mock_residual_baseline/run.py
```

The experiment runs three mock conveyor scenarios: normal behavior, missing exit transition, and delayed exit transition. Generated artifacts are written under `runs/factory_io_mock_residual_baseline/`, which is intentionally ignored because outputs are reproducible.

The old convenience command still works:

```powershell
python demos/run_mock_demo.py
```

## Run The Active Diagnosis Experiment

```powershell
python experiments/aemid_motor_active_diagnosis/run.py
```

This toy DC motor experiment compares passive idle observation against a bounded active probe. It is not an industrial validation; it is a small executable check that active experiments can reduce model-blame ambiguity.

## Run The Everyday Toy Cases

```powershell
python experiments/everyday_model_blame_toy_cases/run.py
```

These fake scenarios include the laptop CPU-load example, plus phone battery drain, coffee cooling, and video-call latency. They are meant as plain-language demos of expected model versus observed reality.

## Connect Factory I/O Later

Update:

```text
config/backends/factory_io.yaml
config/tag_maps/factory_io_demo_scene.yaml
```

The current live adapter has transport integration points under `src/model_blame/adapters/factory_io/`. The Web API scaffold expects configured endpoints that can read and write raw tag names. OPC UA and Modbus clients are placeholders until wired to real Factory I/O driver data.

## Tests

```powershell
python -m pytest
```

The test suite covers model validation, tag mapping, mock polling, residual detection, blame hypothesis generation, unsupported-operation behavior, and the experiment artifact contracts.
