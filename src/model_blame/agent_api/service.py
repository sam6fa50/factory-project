from __future__ import annotations

from pathlib import Path

from model_blame.adapters.mock.adapter import MockFactoryIOAdapter, MockFactoryIOConfig
from model_blame.agent_api.client import SimClient
from model_blame.blame.hypotheses import BlameHypothesisGenerator
from model_blame.residuals.engine import ResidualEngine
from model_blame.residuals.rules import load_expectation_rules
from model_blame.telemetry.pooler import TelemetryPooler


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def create_mock_service(
    scenario: str = "normal",
    config_path: str | Path | None = None,
    expectations_path: str | Path | None = None,
    tag_map_path: str | Path | None = None,
    jsonl_log_path: str | Path | None = None,
) -> SimClient:
    root = project_root()
    tag_map = Path(tag_map_path or root / "config" / "tag_maps" / "factory_io_demo_scene.yaml")
    config = MockFactoryIOConfig.from_yaml(
        config_path or root / "config" / "backends" / "mock_factory_io.yaml",
        scenario=scenario,
        tag_map_path=str(tag_map),
    )
    adapter = MockFactoryIOAdapter(config)
    rules = load_expectation_rules(expectations_path or root / "config" / "expectations" / "conveyor_rules.yaml")
    pooler = TelemetryPooler(adapter, jsonl_log_path=jsonl_log_path)
    return SimClient(adapter, ResidualEngine(rules), BlameHypothesisGenerator(), pooler=pooler)
