# AEMID Motor Active Diagnosis

## Question

Can a small active experiment reduce diagnostic ambiguity better than passively watching a machine state?

## Hypothesis

An active probe that changes actuator input within a safety envelope should distinguish physical load/friction changes, actuator gain loss, and sensor bias more clearly than an idle observation window.

## Setup

This experiment uses a deterministic DC motor plus load toy model. The hidden condition is one of:

- nominal behavior
- increased load torque
- increased viscous friction
- actuator gain loss
- encoder bias
- current sensor bias

The diagnosis step compares observed speed/current traces against each candidate model and converts trace error into a posterior distribution over hypotheses.

## Procedure

Run:

```powershell
python experiments/aemid_motor_active_diagnosis/run.py
```

The runner evaluates two policies across every hidden condition:

- `passive_idle`: hold voltage at zero and observe.
- `active_probe`: issue a bounded voltage sequence that creates discriminating transients.

Generated artifacts are written under `runs/aemid_motor_active_diagnosis/`.

## Expected Result

The active policy should have lower average final entropy and perfect top-1 classification in this deterministic toy setup. The passive policy should remain ambiguous, especially between nominal behavior and actuator gain loss while the actuator is idle.

## Latest Observed Result

Verified on 2026-08-13: `active_probe` lowered average final entropy versus `passive_idle` and classified every hidden condition correctly while staying inside the configured safety envelope.

## Limits

This is not a validated industrial model. It is a small executable anchor for the product thesis from the chat ingestion pass: useful model blame may require safe, uncertainty-aware experiments, not only passive residual detection.

## Next Action

If this direction remains useful, promote the experiment interface concepts into SimIR: experiment specs, safety constraints, hypothesis posterior state, model-component validity state, and next-best experiment recommendations.
