from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "runs" / "aemid_motor_active_diagnosis"


@dataclass(frozen=True)
class MotorParameters:
    load_torque: float = 0.20
    viscous_friction: float = 0.04
    actuator_gain: float = 1.0
    encoder_bias: float = 0.0
    current_bias: float = 0.0


@dataclass(frozen=True)
class SafetyEnvelope:
    max_abs_voltage: float = 7.0
    max_abs_speed: float = 40.0
    max_abs_current: float = 4.0


@dataclass(frozen=True)
class Observation:
    time: float
    voltage: float
    speed: float
    current: float


HYPOTHESES: dict[str, MotorParameters] = {
    "nominal": MotorParameters(),
    "increased_load": MotorParameters(load_torque=0.34),
    "increased_friction": MotorParameters(viscous_friction=0.07),
    "actuator_gain_loss": MotorParameters(actuator_gain=0.84),
    "encoder_bias": MotorParameters(encoder_bias=2.20),
    "current_sensor_bias": MotorParameters(current_bias=0.35),
}


def passive_idle_voltage(time: float) -> float:
    return 0.0


def active_probe_voltage(time: float) -> float:
    if time < 1.0:
        return 0.0
    if time < 3.0:
        return 3.0
    if time < 5.0:
        return 7.0
    if time < 6.5:
        return -2.0
    return 5.0


POLICIES: dict[str, Callable[[float], float]] = {
    "passive_idle": passive_idle_voltage,
    "active_probe": active_probe_voltage,
}


def simulate_trace(
    parameters: MotorParameters,
    policy: Callable[[float], float],
    *,
    duration_seconds: float = 8.0,
    dt_seconds: float = 0.05,
    sample_every_steps: int = 10,
) -> list[Observation]:
    speed = 0.0
    trace: list[Observation] = []
    resistance = 2.0
    torque_constant = 0.70
    back_emf_constant = 0.08
    inertia = 0.08

    steps = int(duration_seconds / dt_seconds)
    for step in range(steps):
        time = step * dt_seconds
        voltage = policy(time)
        current = ((parameters.actuator_gain * voltage) - (back_emf_constant * speed)) / resistance
        acceleration = (
            (torque_constant * current)
            - (parameters.viscous_friction * speed)
            - parameters.load_torque
        ) / inertia
        speed = max(-40.0, min(120.0, speed + (acceleration * dt_seconds)))

        if step % sample_every_steps == 0:
            trace.append(
                Observation(
                    time=round(time, 6),
                    voltage=voltage,
                    speed=speed + parameters.encoder_bias,
                    current=current + parameters.current_bias,
                )
            )

    return trace


def diagnose_trace(
    observed: list[Observation],
    policy: Callable[[float], float],
    *,
    speed_scale: float = 8.0,
    current_scale: float = 1.2,
) -> tuple[list[dict[str, float | str]], float]:
    scored: list[tuple[str, float]] = []
    for name, parameters in HYPOTHESES.items():
        predicted = simulate_trace(parameters, policy)
        score = 0.0
        for observed_point, predicted_point in zip(observed, predicted):
            speed_error = (observed_point.speed - predicted_point.speed) / speed_scale
            current_error = (observed_point.current - predicted_point.current) / current_scale
            score += (speed_error * speed_error) + (current_error * current_error)
        scored.append((name, score))

    best_score = min(score for _, score in scored)
    weights = [math.exp(-0.5 * (score - best_score)) for _, score in scored]
    total_weight = sum(weights)
    probabilities = [weight / total_weight for weight in weights]
    entropy = -sum(prob * math.log(prob, 2) for prob in probabilities if prob > 0.0)

    posterior = sorted(
        [
            {
                "hypothesis": name,
                "probability": probability,
                "score": score,
            }
            for (name, score), probability in zip(scored, probabilities)
        ],
        key=lambda item: float(item["probability"]),
        reverse=True,
    )
    return posterior, entropy


def safety_summary(trace: list[Observation], envelope: SafetyEnvelope) -> dict[str, object]:
    max_abs_voltage = max(abs(point.voltage) for point in trace)
    max_abs_speed = max(abs(point.speed) for point in trace)
    max_abs_current = max(abs(point.current) for point in trace)
    violations = []
    if max_abs_voltage > envelope.max_abs_voltage:
        violations.append("voltage")
    if max_abs_speed > envelope.max_abs_speed:
        violations.append("speed")
    if max_abs_current > envelope.max_abs_current:
        violations.append("current")

    return {
        "max_abs_voltage": max_abs_voltage,
        "max_abs_speed": max_abs_speed,
        "max_abs_current": max_abs_current,
        "violations": violations,
    }


def run_case(hidden_hypothesis: str, policy_name: str, envelope: SafetyEnvelope | None = None) -> dict[str, object]:
    envelope = envelope or SafetyEnvelope()
    policy = POLICIES[policy_name]
    trace = simulate_trace(HYPOTHESES[hidden_hypothesis], policy)
    posterior, entropy = diagnose_trace(trace, policy)
    top = posterior[0]
    return {
        "hidden_hypothesis": hidden_hypothesis,
        "policy": policy_name,
        "final_entropy_bits": entropy,
        "top_hypothesis": top["hypothesis"],
        "top_probability": top["probability"],
        "posterior": posterior,
        "safety": safety_summary(trace, envelope),
    }


def summarize_policy(cases: list[dict[str, object]]) -> dict[str, object]:
    average_entropy = sum(float(case["final_entropy_bits"]) for case in cases) / len(cases)
    correct = [
        case["hidden_hypothesis"] == case["top_hypothesis"]
        for case in cases
    ]
    violations = sorted(
        {
            violation
            for case in cases
            for violation in dict(case["safety"])["violations"]
        }
    )
    return {
        "average_final_entropy_bits": average_entropy,
        "top1_accuracy": sum(1 for item in correct if item) / len(correct),
        "safety_violations": violations,
    }


def run_all_cases(output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> dict[str, object]:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    envelope = SafetyEnvelope()

    cases = [
        run_case(hidden_hypothesis, policy_name, envelope)
        for policy_name in POLICIES
        for hidden_hypothesis in HYPOTHESES
    ]
    by_policy = {
        policy_name: summarize_policy([case for case in cases if case["policy"] == policy_name])
        for policy_name in POLICIES
    }
    summary: dict[str, object] = {
        "question": "Does active probing reduce diagnostic ambiguity versus passive idle observation?",
        "safety_envelope": asdict(envelope),
        "hypotheses": {name: asdict(parameters) for name, parameters in HYPOTHESES.items()},
        "policies": by_policy,
        "cases": cases,
        "interpretation": (
            "active_probe should beat passive_idle when average final entropy is lower, "
            "top-1 accuracy is no worse, and no safety violations are emitted."
        ),
    }
    (output_root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the active motor diagnosis toy experiment.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)

    summary = run_all_cases(args.output_root)
    print("AEMID motor active diagnosis")
    print(f"Artifacts written under {args.output_root}")
    for policy_name, policy_summary in dict(summary["policies"]).items():
        print(
            f"- {policy_name}: "
            f"average_final_entropy_bits={policy_summary['average_final_entropy_bits']:.3f}; "
            f"top1_accuracy={policy_summary['top1_accuracy']:.3f}; "
            f"safety_violations={policy_summary['safety_violations'] or 'none'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
