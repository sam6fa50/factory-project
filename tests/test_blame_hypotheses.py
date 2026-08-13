from __future__ import annotations

from pathlib import Path

from model_blame.blame.hypotheses import BlameHypothesisGenerator
from model_blame.residuals.engine import ResidualEngine
from model_blame.residuals.rules import load_expectation_rules
from tests.test_residual_engine import collect_samples


ROOT = Path(__file__).resolve().parents[1]


def test_blame_hypothesis_generation_for_missing_transition() -> None:
    samples = collect_samples("missing_exit")
    rules = load_expectation_rules(ROOT / "config" / "expectations" / "conveyor_rules.yaml")
    residuals = ResidualEngine(rules).evaluate(samples)

    hypotheses = BlameHypothesisGenerator().generate(residuals, samples)

    assert hypotheses[0].primary_blame == "exit_sensor_or_tag_mapping"
    assert hypotheses[0].confidence > 0.5
    assert "Entry sensor" in hypotheses[0].explanation
