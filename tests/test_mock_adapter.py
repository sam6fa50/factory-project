from __future__ import annotations

from pathlib import Path

from model_blame.adapters.mock.adapter import MockFactoryIOAdapter, MockFactoryIOConfig
from model_blame.simir.models import FaultInjection


ROOT = Path(__file__).resolve().parents[1]


def make_adapter(scenario: str = "normal") -> MockFactoryIOAdapter:
    config = MockFactoryIOConfig.from_yaml(
        ROOT / "config" / "backends" / "mock_factory_io.yaml",
        scenario=scenario,
        tag_map_path=str(ROOT / "config" / "tag_maps" / "factory_io_demo_scene.yaml"),
    )
    return MockFactoryIOAdapter(config)


def test_mock_adapter_polling_returns_canonical_samples() -> None:
    adapter = make_adapter()
    adapter.connect()
    run = adapter.start_run()

    batch = adapter.poll()

    assert batch.run_id == run.run_id
    assert {sample.full_tag for sample in batch.samples} >= {
        "conveyor_1.entry_sensor",
        "conveyor_1.exit_sensor",
        "conveyor_1.motor_command",
    }


def test_mock_adapter_supports_writable_motor_override() -> None:
    adapter = make_adapter()
    adapter.connect()
    adapter.start_run()

    result = adapter.write_tag("conveyor_1.motor_command", False)
    batch = adapter.poll()
    motor = next(sample for sample in batch.samples if sample.full_tag == "conveyor_1.motor_command")

    assert result.ok
    assert motor.value is False


def test_mock_adapter_read_tags_returns_requested_tags_only() -> None:
    adapter = make_adapter()
    adapter.connect()
    adapter.start_run()

    batch = adapter.read_tags(["conveyor_1.entry_sensor"])

    assert not hasattr(batch, "ok")
    assert [sample.full_tag for sample in batch.samples] == ["conveyor_1.entry_sensor"]


def test_unsupported_fault_injection_returns_structured_error() -> None:
    adapter = make_adapter()

    result = adapter.inject_fault(FaultInjection(fault_type="stuck_sensor", tag_id="conveyor_1.exit_sensor"))

    assert not result.ok
    assert result.error_code == "unsupported"
