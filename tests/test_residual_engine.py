from __future__ import annotations

from pathlib import Path

from model_blame.adapters.mock.adapter import MockFactoryIOAdapter, MockFactoryIOConfig
from model_blame.residuals.engine import ResidualEngine
from model_blame.residuals.rules import load_expectation_rules


ROOT = Path(__file__).resolve().parents[1]


def collect_samples(scenario: str):
    config = MockFactoryIOConfig.from_yaml(
        ROOT / "config" / "backends" / "mock_factory_io.yaml",
        scenario=scenario,
        tag_map_path=str(ROOT / "config" / "tag_maps" / "factory_io_demo_scene.yaml"),
    )
    adapter = MockFactoryIOAdapter(config)
    adapter.connect()
    adapter.start_run(scenario=scenario)
    samples = []
    for _ in range(17):
        samples.extend(adapter.poll().samples)
    return samples


def engine() -> ResidualEngine:
    rules = load_expectation_rules(ROOT / "config" / "expectations" / "conveyor_rules.yaml")
    return ResidualEngine(rules)


def test_normal_case_has_no_residuals() -> None:
    residuals = engine().evaluate(collect_samples("normal"))

    assert residuals == []


def test_missing_exit_transition_is_detected() -> None:
    residuals = engine().evaluate(collect_samples("missing_exit"))

    assert [residual.type for residual in residuals] == ["missing_transition"]
    assert residuals[0].observed["end_time"] is None


def test_delayed_transition_is_detected() -> None:
    residuals = engine().evaluate(collect_samples("delayed_transition"))

    assert [residual.type for residual in residuals] == ["delayed_transition"]
    assert residuals[0].observed["elapsed_seconds"] > 3.0
