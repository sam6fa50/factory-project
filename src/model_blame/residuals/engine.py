from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from model_blame.residuals.rules import ExpectationRule
from model_blame.simir.models import Residual, Severity, TelemetrySample


@dataclass(frozen=True)
class Edge:
    time: float
    sample: TelemetrySample


class ResidualEngine:
    def __init__(self, rules: list[ExpectationRule]):
        self.rules = rules

    def evaluate(self, samples: list[TelemetrySample]) -> list[Residual]:
        if not samples:
            return []
        residuals: list[Residual] = []
        residual_index = 1
        for rule in self.rules:
            if rule.type == "transition_deadline":
                emitted = self._evaluate_transition(rule, samples, start_index=residual_index)
            elif rule.type == "actuator_effect":
                emitted = self._evaluate_actuator_effect(rule, samples, start_index=residual_index)
            else:
                emitted = []
            residuals.extend(emitted)
            residual_index += len(emitted)
        return residuals

    def _evaluate_transition(
        self,
        rule: ExpectationRule,
        samples: list[TelemetrySample],
        start_index: int,
    ) -> list[Residual]:
        if not rule.start_tag or not rule.end_tag:
            return []
        start_series = self._series(samples, rule.start_tag)
        end_series = self._series(samples, rule.end_tag)
        start_edges = self._rising_edges(start_series)
        end_edges = self._rising_edges(end_series)
        last_time = max((sample.sim_time or 0.0 for sample in samples), default=0.0)
        run_id = samples[-1].run_id
        residuals: list[Residual] = []

        for start_edge in start_edges:
            end_edge = next((edge for edge in end_edges if edge.time > start_edge.time), None)
            if end_edge is None:
                if last_time >= start_edge.time + rule.max_seconds:
                    residuals.append(
                        self._residual(
                            start_index + len(residuals),
                            rule,
                            run_id,
                            "missing_transition",
                            expected={
                                "start_tag": rule.start_tag,
                                "end_tag": rule.end_tag,
                                "deadline_seconds": rule.max_seconds,
                            },
                            observed={
                                "start_time": start_edge.time,
                                "end_time": None,
                                "last_observed_time": last_time,
                            },
                            time_window={"start": start_edge.time, "end": min(last_time, start_edge.time + rule.max_seconds)},
                        )
                    )
                continue

            elapsed = end_edge.time - start_edge.time
            if elapsed > rule.max_seconds:
                residuals.append(
                    self._residual(
                        start_index + len(residuals),
                        rule,
                        run_id,
                        "delayed_transition",
                        expected={
                            "start_tag": rule.start_tag,
                            "end_tag": rule.end_tag,
                            "deadline_seconds": rule.max_seconds,
                        },
                        observed={"start_time": start_edge.time, "end_time": end_edge.time, "elapsed_seconds": elapsed},
                        time_window={"start": start_edge.time, "end": end_edge.time},
                    )
                )
        return residuals

    def _evaluate_actuator_effect(
        self,
        rule: ExpectationRule,
        samples: list[TelemetrySample],
        start_index: int,
    ) -> list[Residual]:
        if not rule.command_tag or not rule.effect_tag:
            return []
        command_series = self._series(samples, rule.command_tag)
        effect_series = self._series(samples, rule.effect_tag)
        command_edges = [
            Edge(time, sample)
            for time, value, sample in command_series
            if value == rule.expected_command_value
        ]
        effect_edges = self._rising_edges(effect_series)
        if not command_edges:
            return []
        first_command = command_edges[0]
        effect = next((edge for edge in effect_edges if edge.time >= first_command.time), None)
        last_time = max((sample.sim_time or 0.0 for sample in samples), default=0.0)
        if effect is not None and effect.time - first_command.time <= rule.max_seconds:
            return []
        if last_time < first_command.time + rule.max_seconds:
            return []
        run_id = samples[-1].run_id
        return [
            self._residual(
                start_index,
                rule,
                run_id,
                "actuator_no_effect",
                expected={
                    "command_tag": rule.command_tag,
                    "effect_tag": rule.effect_tag,
                    "deadline_seconds": rule.max_seconds,
                },
                observed={"command_time": first_command.time, "effect_time": effect.time if effect else None},
                time_window={"start": first_command.time, "end": effect.time if effect else last_time},
            )
        ]

    def _residual(
        self,
        index: int,
        rule: ExpectationRule,
        run_id: str,
        residual_type: str,
        expected: dict[str, Any],
        observed: dict[str, Any],
        time_window: dict[str, Any],
    ) -> Residual:
        return Residual(
            residual_id=f"res_{index:03d}",
            run_id=run_id,
            asset_id=rule.asset_id,
            type=residual_type,
            severity=rule.severity if isinstance(rule.severity, Severity) else Severity(rule.severity),
            expected=expected,
            observed=observed,
            time_window=time_window,
            candidate_causes=rule.candidate_causes,
            metadata={"rule_id": rule.rule_id, "description": rule.description},
        )

    def _series(self, samples: list[TelemetrySample], full_tag: str) -> list[tuple[float, Any, TelemetrySample]]:
        series = []
        for sample in samples:
            if sample.full_tag != full_tag or sample.sim_time is None:
                continue
            series.append((sample.sim_time, sample.value, sample))
        return sorted(series, key=lambda item: item[0])

    def _rising_edges(self, series: list[tuple[float, Any, TelemetrySample]]) -> list[Edge]:
        edges: list[Edge] = []
        previous = False
        for time, value, sample in series:
            current = bool(value)
            if current and not previous:
                edges.append(Edge(time=time, sample=sample))
            previous = current
        return edges
