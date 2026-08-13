from __future__ import annotations

from pathlib import Path

from model_blame.adapters.factory_io.adapter import FactoryIOConfig


ROOT = Path(__file__).resolve().parents[1]


def test_factory_io_config_allows_blank_endpoint_placeholders() -> None:
    config = FactoryIOConfig.from_yaml(ROOT / "config" / "backends" / "factory_io.yaml")

    assert config.protocol == "web_api"
    assert "read_tags" in config.endpoints
