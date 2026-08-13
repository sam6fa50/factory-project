# Orientation

This is the human-first map of the repository. Keep each entry short: purpose first, then one concrete example.

## Root Files

- `README.md`: Start here for the project summary, install steps, and run commands. Example: it shows how to run the baseline, active-diagnosis, and everyday toy-case experiments.
- `PROJECT.md`: Stable product and architecture context. Example: it records that Factory I/O is the current MVP proof track while active diagnosis is still research.
- `KNOWLEDGE.md`: Durable facts, assumptions, hypotheses, open questions, and source records. Example: it registers ingested chats and verified industrial-standard sources.
- `EXECUTION.md`: Current working state and next meaningful actions. Example: it tracks whether the next push should focus on live Factory I/O or deeper active diagnosis.
- `AGENTS.md`: Agent operating rules and repository authority. Example: it tells agents when to update canonical docs and which validation commands to run.
- `CLAUDE.md`: Thin Claude Code adapter. Example: it imports `AGENTS.md` so Claude uses the shared agent rules.
- `GEMINI.md`: Thin Gemini adapter. Example: it points Gemini-specific behavior back to `AGENTS.md`.
- `pyproject.toml`: Python package metadata, dependencies, and test configuration. Example: it declares Pydantic, PyYAML, and pytest test paths.

## Directories

- `.gemini/`: Gemini CLI project configuration. Example: `.gemini/settings.json` tells Gemini to load `AGENTS.md`.
- `config/`: Runtime configuration for backends, tag maps, expectations, and logging. Example: `config/expectations/conveyor_rules.yaml` defines the conveyor entry-to-exit deadline rule.
- `demos/`: Convenience entry points for quick manual runs. Example: `demos/run_mock_demo.py` delegates to the Factory I/O mock residual baseline.
- `experiments/`: Executable proof tracks with their own README files and runners. Example: `experiments/everyday_model_blame_toy_cases/` contains the laptop CPU-load fake scenario.
- `references/`: External surveys and supporting research notes that are too detailed for `KNOWLEDGE.md`. Example: `references/ai-native-repository-survey.md` compares agent-memory and spec tooling.
- `runs/`: Generated experiment outputs, intentionally ignored by Git. Example: running an experiment writes summaries under `runs/<experiment_name>/`.
- `src/`: Product/source package code. Example: `src/model_blame/simir/models.py` defines canonical telemetry, residual, and blame models.
- `tests/`: Automated verification for source code and experiment contracts. Example: `tests/test_everyday_toy_cases.py` checks the laptop CPU-load case ranks the intended hidden cause first.

## Maintenance

Update this file when a change adds, removes, renames, or repurposes a root file or directory, or when a directory gains a new kind of content that would surprise a new human reader.
