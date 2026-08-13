# Everyday Model-Blame Toy Cases

## Question

Can the model-blame idea be shown without industrial context?

## Hypothesis

Small everyday systems can demonstrate the same pattern as machine diagnostics:

```text
expected model -> observed reality -> residual shape -> ranked broken assumptions
```

## Setup

The experiment contains four deterministic fake scenarios:

- Laptop temperature: expected CPU temperature is wrong because reported CPU load missed background work.
- Phone battery drain: expected battery drain is wrong because GPS/location activity was missing.
- Coffee cooling: expected cooling is wrong because the mug or lid retained heat better than assumed.
- Video-call latency: expected latency is wrong because cloud backup upload traffic was running.

Each case has one observed curve, several candidate explanations, a grid of candidate parameter values, and a plain-English next check.

## Procedure

Run:

```powershell
python experiments/everyday_model_blame_toy_cases/run.py
```

The runner writes:

- `runs/everyday_model_blame_toy_cases/summary.json`
- `runs/everyday_model_blame_toy_cases/summary.md`

## Expected Result

Each hidden explanation should rank first:

- `background_cpu_load`
- `gps_background`
- `insulated_mug`
- `cloud_backup_upload`

## Limits

These are explanatory cases, not industrial validation. Their purpose is to make the product idea easy to show before discussing motors, PLCs, simulators, or Factory I/O.

## Next Action

Use these cases in README/demo material when explaining model-component blame to non-industrial audiences.
