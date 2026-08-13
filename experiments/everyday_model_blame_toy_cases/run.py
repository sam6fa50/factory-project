from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "runs" / "everyday_model_blame_toy_cases"


Series = list[float]


@dataclass(frozen=True)
class ToyCandidate:
    key: str
    label: str
    variable_name: str
    unit: str
    grid: Series
    predict: Callable[[float], Series]
    next_check: str
    explanation: Callable[[float, float], str]


@dataclass(frozen=True)
class ToyCase:
    key: str
    title: str
    model: str
    observed_variable: str
    hidden_break: str
    time: Series
    expected: Series
    observed: Series
    candidates: list[ToyCandidate]
    observation_unit: str
    observation_scale: float


@dataclass(frozen=True)
class ToyScore:
    key: str
    label: str
    variable_name: str
    best_value: float
    unit: str
    loss: float
    confidence: float
    explanation: str
    next_check: str


@dataclass(frozen=True)
class ToyReport:
    case: ToyCase
    scores: list[ToyScore]

    @property
    def winner(self) -> ToyScore:
        return self.scores[0]

    def to_markdown(self) -> str:
        lines = [
            f"### {self.case.title}",
            "",
            f"- Model: {self.case.model}",
            f"- Observed variable: {self.case.observed_variable}",
            f"- Hidden break: {self.case.hidden_break}",
            (
                f"- Top blame: {self.winner.label} "
                f"({self.winner.variable_name}={format_value(self.winner.best_value, self.winner.unit)}, "
                f"{self.winner.confidence:.1%} confidence)"
            ),
            "",
            "| Rank | Suspect | Best value | Loss | Confidence |",
            "| --- | --- | --- | ---: | ---: |",
        ]
        for index, score in enumerate(self.scores, start=1):
            lines.append(
                "| {rank} | {label} | {name}={value} | {loss:.4g} | {confidence:.1%} |".format(
                    rank=index,
                    label=score.label,
                    name=score.variable_name,
                    value=format_value(score.best_value, score.unit),
                    loss=score.loss,
                    confidence=score.confidence,
                )
            )
        lines.extend(
            [
                "",
                f"Why: {self.winner.explanation}",
                "",
                f"Next check: {self.winner.next_check}",
            ]
        )
        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "case": self.case.key,
            "title": self.case.title,
            "model": self.case.model,
            "observed_variable": self.case.observed_variable,
            "hidden_break": self.case.hidden_break,
            "winner": self.winner.key,
            "scores": [
                {
                    "key": score.key,
                    "label": score.label,
                    "variable_name": score.variable_name,
                    "best_value": score.best_value,
                    "unit": score.unit,
                    "loss": score.loss,
                    "confidence": score.confidence,
                    "explanation": score.explanation,
                    "next_check": score.next_check,
                }
                for score in self.scores
            ],
        }


def format_value(value: float, unit: str) -> str:
    if unit == "":
        return f"{value:.2f}"
    if abs(value) >= 10.0:
        return f"{value:.1f} {unit}"
    return f"{value:.2f} {unit}"


def linspace(start: float, stop: float, count: int) -> Series:
    if count < 2:
        return [float(start)]
    step = (stop - start) / (count - 1)
    return [start + (step * index) for index in range(count)]


def piecewise(time: Series, default: float, spans: list[tuple[float, float, float]]) -> Series:
    values = [float(default) for _ in time]
    for index, item in enumerate(time):
        for start, end, value in spans:
            if start <= item < end:
                values[index] = float(value)
                break
    return values


def integrate_rate(time: Series, rate: Series, start_value: float) -> Series:
    values = []
    current = start_value
    previous_time = time[0]
    for item_time, item_rate in zip(time, rate):
        dt = item_time - previous_time
        current -= item_rate * dt
        values.append(current)
        previous_time = item_time
    return values


def add_series(a: Series, b: Series) -> Series:
    return [left + right for left, right in zip(a, b)]


def scale_series(values: Series, scale: float) -> Series:
    return [scale * value for value in values]


def clipped_load(values: Series) -> Series:
    return [max(0.0, min(1.0, value)) for value in values]


def rank_toy_case(case: ToyCase) -> ToyReport:
    raw_scores = []
    for candidate in case.candidates:
        best_value = candidate.grid[0]
        best_loss = float("inf")
        for value in candidate.grid:
            prediction = candidate.predict(value)
            residuals = [
                (observed - predicted) / case.observation_scale
                for observed, predicted in zip(case.observed, prediction)
            ]
            loss = sum(value * value for value in residuals) / len(residuals)
            if loss < best_loss:
                best_value = value
                best_loss = loss
        raw_scores.append((candidate, best_value, best_loss))

    log_likelihoods = [-0.5 * 60.0 * loss for _, _, loss in raw_scores]
    max_log_likelihood = max(log_likelihoods)
    weights = [math.exp(value - max_log_likelihood) for value in log_likelihoods]
    total_weight = sum(weights)
    confidences = [weight / total_weight for weight in weights]

    scores = [
        ToyScore(
            key=candidate.key,
            label=candidate.label,
            variable_name=candidate.variable_name,
            best_value=best_value,
            unit=candidate.unit,
            loss=best_loss,
            confidence=confidence,
            explanation=candidate.explanation(best_value, best_loss),
            next_check=candidate.next_check,
        )
        for (candidate, best_value, best_loss), confidence in zip(raw_scores, confidences)
    ]
    return ToyReport(case=case, scores=sorted(scores, key=lambda item: item.loss))


def laptop_temperature_case() -> ToyCase:
    time = linspace(0.0, 12.0, 121)
    reported_load = piecewise(
        time,
        default=0.18,
        spans=[(2.0, 5.0, 0.55), (5.0, 7.5, 0.82), (7.5, 10.0, 0.35)],
    )
    ambient = 23.0
    temp_gain = 42.0
    expected = [ambient + (temp_gain * load) for load in reported_load]
    hidden_extra_load = 0.22
    observed = [ambient + (temp_gain * load) for load in clipped_load([load + hidden_extra_load for load in reported_load])]

    return ToyCase(
        key="laptop_temperature",
        title="Laptop Temperature",
        model="temperature = room temperature + heat gain from reported CPU load",
        observed_variable="CPU temperature in deg C",
        hidden_break="The reported CPU load missed a background workload.",
        time=time,
        expected=expected,
        observed=observed,
        observation_unit="deg C",
        observation_scale=2.0,
        candidates=[
            ToyCandidate(
                key="background_cpu_load",
                label="Unmodeled background CPU load",
                variable_name="extra_cpu_load",
                unit="load",
                grid=linspace(0.0, 0.35, 36),
                predict=lambda value: [
                    ambient + (temp_gain * load)
                    for load in clipped_load([item + value for item in reported_load])
                ],
                next_check="Open the task manager and compare reported app load with total CPU load.",
                explanation=lambda value, loss: (
                    f"Adding {format_value(value, 'load')} of hidden CPU load lines up the hottest and coolest parts of the temperature curve."
                ),
            ),
            ToyCandidate(
                key="warm_room",
                label="Room is warmer than assumed",
                variable_name="room_temp_error",
                unit="deg C",
                grid=linspace(0.0, 14.0, 57),
                predict=lambda value: [item + value for item in expected],
                next_check="Compare the model's room-temperature input with a room thermometer.",
                explanation=lambda value, loss: "A constant room-temperature shift helps, but it cannot match the load-shaped residual as well.",
            ),
            ToyCandidate(
                key="fan_underperforming",
                label="Fan is underperforming",
                variable_name="extra_heat_at_high_load",
                unit="deg C",
                grid=linspace(0.0, 18.0, 73),
                predict=lambda value: [
                    item + (value * load * load)
                    for item, load in zip(expected, reported_load)
                ],
                next_check="Check fan RPM and vents during high load.",
                explanation=lambda value, loss: "The best fan-loss explanation mostly helps at high load, but the mismatch also appears during moderate load.",
            ),
            ToyCandidate(
                key="sensor_bias",
                label="Temperature sensor offset",
                variable_name="sensor_offset",
                unit="deg C",
                grid=linspace(-6.0, 14.0, 81),
                predict=lambda value: [item + value for item in expected],
                next_check="Compare CPU temperature against another sensor source.",
                explanation=lambda value, loss: "A fixed sensor offset would shift every point equally.",
            ),
        ],
    )


def phone_battery_case() -> ToyCase:
    time = linspace(0.0, 6.0, 121)
    screen_on = piecewise(time, default=0.0, spans=[(0.5, 1.4, 1.0), (2.0, 3.0, 1.0), (4.3, 5.2, 1.0)])
    gps_on = piecewise(time, default=0.0, spans=[(1.0, 2.2, 1.0), (4.1, 4.9, 1.0)])
    base_rate = 2.0
    screen_rate = 8.0
    expected_rate = [base_rate + (screen_rate * item) for item in screen_on]
    expected = integrate_rate(time, expected_rate, start_value=100.0)
    hidden_gps_rate = 10.0
    observed = integrate_rate(time, add_series(expected_rate, scale_series(gps_on, hidden_gps_rate)), start_value=100.0)

    return ToyCase(
        key="phone_battery",
        title="Phone Battery Drain",
        model="battery drain = baseline drain + screen-on drain",
        observed_variable="battery percentage",
        hidden_break="Location/GPS work was active but missing from the model.",
        time=time,
        expected=expected,
        observed=observed,
        observation_unit="percent",
        observation_scale=2.5,
        candidates=[
            ToyCandidate(
                key="gps_background",
                label="Background GPS/location drain",
                variable_name="gps_drain_rate",
                unit="%/hr",
                grid=linspace(0.0, 16.0, 33),
                predict=lambda value: integrate_rate(
                    time,
                    add_series(expected_rate, scale_series(gps_on, value)),
                    start_value=100.0,
                ),
                next_check="Review location-permission and map/navigation activity logs.",
                explanation=lambda value, loss: f"Adding {format_value(value, '%/hr')} only during location-active windows removes the stair-step battery residual.",
            ),
            ToyCandidate(
                key="old_battery",
                label="Battery capacity is lower",
                variable_name="drain_multiplier",
                unit="x",
                grid=linspace(1.0, 1.8, 33),
                predict=lambda value: integrate_rate(time, scale_series(expected_rate, value), start_value=100.0),
                next_check="Check battery health and compare drain across a full day.",
                explanation=lambda value, loss: "A lower-capacity battery makes every activity drain faster, not just the location-heavy intervals.",
            ),
            ToyCandidate(
                key="screen_brightness",
                label="Screen brightness underestimated",
                variable_name="extra_screen_drain",
                unit="%/hr",
                grid=linspace(0.0, 16.0, 33),
                predict=lambda value: integrate_rate(
                    time,
                    add_series(expected_rate, scale_series(screen_on, value)),
                    start_value=100.0,
                ),
                next_check="Compare brightness and screen-on logs against the model input.",
                explanation=lambda value, loss: "Extra screen drain helps during screen-on periods but misses location drain that happens off-screen.",
            ),
            ToyCandidate(
                key="battery_meter_offset",
                label="Battery meter offset",
                variable_name="meter_offset",
                unit="%",
                grid=linspace(-20.0, 5.0, 51),
                predict=lambda value: [item + value for item in expected],
                next_check="Recalibrate the battery meter after a full charge cycle.",
                explanation=lambda value, loss: "A meter offset shifts the curve without explaining the changing slope.",
            ),
        ],
    )


def coffee_cooling_case() -> ToyCase:
    time = linspace(0.0, 60.0, 121)
    room = 21.0
    initial = 88.0
    nominal_k = 0.035
    expected = [room + ((initial - room) * math.exp(-nominal_k * item)) for item in time]
    hidden_heat_loss_scale = 0.55
    observed = [room + ((initial - room) * math.exp(-(nominal_k * hidden_heat_loss_scale) * item)) for item in time]

    return ToyCase(
        key="coffee_cooling",
        title="Coffee Cooling",
        model="temperature cools exponentially toward room temperature",
        observed_variable="coffee temperature in deg C",
        hidden_break="The mug/lid retained heat better than the model assumed.",
        time=time,
        expected=expected,
        observed=observed,
        observation_unit="deg C",
        observation_scale=3.0,
        candidates=[
            ToyCandidate(
                key="insulated_mug",
                label="Heat-loss rate too high",
                variable_name="heat_loss_scale",
                unit="x",
                grid=linspace(0.35, 1.20, 86),
                predict=lambda value: [room + ((initial - room) * math.exp(-(nominal_k * value) * item)) for item in time],
                next_check="Compare an open mug and a lidded mug under the same room conditions.",
                explanation=lambda value, loss: f"Scaling the cooling rate to {format_value(value, 'x')} matches the whole curved temperature trace.",
            ),
            ToyCandidate(
                key="warmer_room",
                label="Room temperature too high",
                variable_name="room_temp_error",
                unit="deg C",
                grid=linspace(-5.0, 15.0, 81),
                predict=lambda value: [
                    (room + value) + ((initial - (room + value)) * math.exp(-nominal_k * item))
                    for item in time
                ],
                next_check="Measure the room temperature during the cooling test.",
                explanation=lambda value, loss: "A warmer room changes the final temperature more than the early cooling shape.",
            ),
            ToyCandidate(
                key="initial_temp",
                label="Initial coffee temperature wrong",
                variable_name="initial_temp_error",
                unit="deg C",
                grid=linspace(-15.0, 15.0, 121),
                predict=lambda value: [room + ((initial + value - room) * math.exp(-nominal_k * item)) for item in time],
                next_check="Measure the initial pour temperature directly.",
                explanation=lambda value, loss: "Changing the initial temperature mostly affects the beginning of the curve.",
            ),
            ToyCandidate(
                key="thermometer_offset",
                label="Thermometer offset",
                variable_name="thermometer_offset",
                unit="deg C",
                grid=linspace(-10.0, 20.0, 121),
                predict=lambda value: [item + value for item in expected],
                next_check="Check the thermometer in ice water and boiling water.",
                explanation=lambda value, loss: "A thermometer offset shifts every point by the same amount.",
            ),
        ],
    )


def video_call_latency_case() -> ToyCase:
    time = linspace(0.0, 30.0, 301)
    download_load = piecewise(time, default=0.20, spans=[(5.0, 12.0, 0.45), (12.0, 20.0, 0.35), (20.0, 28.0, 0.55)])
    cloud_backup_on = piecewise(time, default=0.0, spans=[(10.0, 16.0, 1.0), (22.0, 27.0, 1.0)])
    far_from_router = piecewise(time, default=0.0, spans=[(8.0, 19.0, 1.0)])
    base_latency = 35.0
    download_coeff = 26.0
    expected = [base_latency + (download_coeff * item) for item in download_load]
    hidden_upload_penalty = 80.0
    observed = add_series(expected, scale_series(cloud_backup_on, hidden_upload_penalty))

    return ToyCase(
        key="video_call_latency",
        title="Video-Call Latency",
        model="latency = base network latency + download-load penalty",
        observed_variable="round-trip latency in ms",
        hidden_break="Cloud backup upload traffic was missing from the model.",
        time=time,
        expected=expected,
        observed=observed,
        observation_unit="ms",
        observation_scale=12.0,
        candidates=[
            ToyCandidate(
                key="cloud_backup_upload",
                label="Cloud backup upload traffic",
                variable_name="upload_latency_penalty",
                unit="ms",
                grid=linspace(0.0, 120.0, 61),
                predict=lambda value: add_series(expected, scale_series(cloud_backup_on, value)),
                next_check="Pause cloud sync and rerun the call-latency measurement.",
                explanation=lambda value, loss: f"Adding {format_value(value, 'ms')} during backup windows explains the latency spikes without moving the quiet periods.",
            ),
            ToyCandidate(
                key="isp_base_latency",
                label="ISP base latency changed",
                variable_name="base_latency_shift",
                unit="ms",
                grid=linspace(0.0, 90.0, 46),
                predict=lambda value: [item + value for item in expected],
                next_check="Ping a stable endpoint before and after the spike windows.",
                explanation=lambda value, loss: "A base-latency shift moves every minute equally, so it cannot explain isolated spikes.",
            ),
            ToyCandidate(
                key="download_underestimated",
                label="Download load underestimated",
                variable_name="extra_download_penalty",
                unit="ms",
                grid=linspace(0.0, 120.0, 61),
                predict=lambda value: add_series(expected, scale_series(download_load, value)),
                next_check="Compare router download counters with the app-level estimate.",
                explanation=lambda value, loss: "Download-load error follows download usage, not the upload-only backup windows.",
            ),
            ToyCandidate(
                key="wifi_distance",
                label="Wi-Fi distance penalty",
                variable_name="wifi_penalty",
                unit="ms",
                grid=linspace(0.0, 120.0, 61),
                predict=lambda value: add_series(expected, scale_series(far_from_router, value)),
                next_check="Repeat the call near the router.",
                explanation=lambda value, loss: "A room-distance penalty covers one broad interval but misses the second backup spike.",
            ),
        ],
    )


def all_toy_cases() -> list[ToyCase]:
    return [
        laptop_temperature_case(),
        phone_battery_case(),
        coffee_cooling_case(),
        video_call_latency_case(),
    ]


def run_all_cases(output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> dict[str, object]:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    reports = [rank_toy_case(case) for case in all_toy_cases()]

    summary = {
        "question": "Can model-blame be demonstrated with everyday fake scenarios?",
        "reports": [report.to_dict() for report in reports],
    }
    (output_root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    markdown = ["# Everyday Model-Blame Toy Cases", ""]
    for report in reports:
        markdown.extend([report.to_markdown(), ""])
    (output_root / "summary.md").write_text("\n".join(markdown), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run everyday model-blame toy cases.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)

    summary = run_all_cases(args.output_root)
    print("Everyday model-blame toy cases")
    print(f"Artifacts written under {args.output_root}")
    for report in summary["reports"]:
        winner = report["scores"][0]
        print(
            f"- {report['case']}: top_blame={winner['key']}; "
            f"confidence={winner['confidence']:.3f}; loss={winner['loss']:.4g}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
