from __future__ import annotations

from model_blame.simir.models import BlameHypothesis, Residual, TelemetrySample
from model_blame.telemetry.features import DerivedFeatures


class BlameHypothesisGenerator:
    def generate(
        self,
        residuals: list[Residual],
        samples: list[TelemetrySample] | None = None,
        features: DerivedFeatures | None = None,
    ) -> list[BlameHypothesis]:
        hypotheses = []
        for index, residual in enumerate(residuals, start=1):
            hypotheses.append(self._hypothesis(index, residual, samples or [], features))
        return hypotheses

    def _hypothesis(
        self,
        index: int,
        residual: Residual,
        samples: list[TelemetrySample],
        features: DerivedFeatures | None,
    ) -> BlameHypothesis:
        if residual.type == "missing_transition":
            primary = "exit_sensor_or_tag_mapping"
            confidence = 0.68
            explanation = (
                "Entry sensor fired but the expected exit sensor transition did not arrive before the deadline."
            )
            actions = [
                "Check exit sensor tag mapping",
                "Check whether the part is blocked before the exit sensor",
                "Check the conveyor speed and travel-time assumptions",
            ]
        elif residual.type == "delayed_transition":
            primary = "cycle_time_assumption_or_conveyor_speed"
            confidence = 0.58
            explanation = "The expected transition occurred, but it arrived later than the model allowed."
            actions = [
                "Measure actual travel time between the entry and exit sensors",
                "Check conveyor speed parameters",
                "Check downstream blockage or accumulation logic",
            ]
        elif residual.type == "actuator_no_effect":
            primary = "actuator_effect_mapping_or_mechanical_response"
            confidence = 0.55
            explanation = "A commanded actuator state did not produce the expected downstream effect."
            actions = [
                "Check actuator output tag mapping",
                "Check the linked sensor or state tag",
                "Verify the simulated mechanism is enabled and not blocked",
            ]
        else:
            primary = residual.candidate_causes[0] if residual.candidate_causes else "unknown_model_or_component"
            confidence = 0.35
            explanation = "A residual was detected, but no specialized blame rule matched it yet."
            actions = ["Inspect candidate causes and add a more specific blame rule"]

        evidence = self._evidence(residual, features)
        return BlameHypothesis(
            hypothesis_id=f"hyp_{index:03d}",
            residual_id=residual.residual_id,
            primary_blame=primary,
            confidence=confidence,
            explanation=explanation,
            supporting_evidence=evidence,
            next_diagnostic_actions=actions,
            metadata={"candidate_causes": residual.candidate_causes},
        )

    def _evidence(self, residual: Residual, features: DerivedFeatures | None) -> list[str]:
        observed = residual.observed
        evidence: list[str] = []
        if "start_time" in observed:
            evidence.append(f"{residual.expected.get('start_tag', 'start tag')} changed at t={observed['start_time']}.")
        if observed.get("end_time") is None and "last_observed_time" in observed:
            evidence.append(
                f"{residual.expected.get('end_tag', 'end tag')} did not change through t={observed['last_observed_time']}."
            )
        elif "elapsed_seconds" in observed:
            evidence.append(
                f"Transition took {observed['elapsed_seconds']} seconds, beyond the {residual.expected.get('deadline_seconds')} second deadline."
            )
        if features and features.blocked_assets:
            evidence.append(f"Blocked heuristic active for assets: {', '.join(features.blocked_assets)}.")
        return evidence
