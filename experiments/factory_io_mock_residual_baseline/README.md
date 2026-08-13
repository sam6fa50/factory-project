# Factory I/O Mock Residual Baseline

## Question

Can the current SimIR, residual, and blame pipeline distinguish normal conveyor behavior from missing and delayed exit transitions using deterministic mock Factory I/O telemetry?

## Hypothesis

If the mock adapter maps raw Factory I/O-style tags into SimIR samples correctly, the residual engine should emit no residual for the normal scenario, `missing_transition` for the missing-exit scenario, and `delayed_transition` for the delayed-transition scenario.

## Setup

```powershell
python -m pip install -e ".[dev]"
```

Inputs:

- `config/backends/mock_factory_io.yaml`
- `config/tag_maps/factory_io_demo_scene.yaml`
- `config/expectations/conveyor_rules.yaml`

## Procedure

```powershell
python experiments/factory_io_mock_residual_baseline/run.py
```

The runner writes reproducible artifacts to `runs/factory_io_mock_residual_baseline/`:

- `summary.json`
- `<scenario>/telemetry.jsonl`
- `<scenario>/residuals.json`
- `<scenario>/hypotheses.json`
- `<scenario>/report.md`

## Expected Result

- `normal`: no residuals and no blame hypotheses.
- `missing_exit`: one `missing_transition` residual and an `exit_sensor_or_tag_mapping` hypothesis.
- `delayed_transition`: one `delayed_transition` residual and a `cycle_time_assumption_or_conveyor_speed` hypothesis.

## Observed Result

Verified on 2026-08-13 with:

```powershell
python experiments/factory_io_mock_residual_baseline/run.py
```

Observed split:

- `normal`: no residuals and no hypotheses.
- `missing_exit`: `missing_transition` residual and `exit_sensor_or_tag_mapping` hypothesis.
- `delayed_transition`: `delayed_transition` residual and `cycle_time_assumption_or_conveyor_speed` hypothesis.

Re-run this experiment after any change to SimIR mapping, telemetry features, residual rules, or blame generation, then update this section with the new verification date and command.

## Interpretation

The baseline supports the MVP claim that a simulator-neutral telemetry boundary plus expectation rules can produce useful first-pass diagnostic hypotheses in a controlled mock Factory I/O conveyor case.

## Limitations

- The result uses synthetic telemetry, not a live Factory I/O scene.
- The residual logic is rule-based and covers only a transition-deadline rule in the default config.
- Hypothesis confidence values are heuristic.
- Generated run IDs and timestamps are not stable, so raw outputs remain ignored by Git.

## Next Action

Wire a real Factory I/O transport and compare live telemetry against this mock baseline.
