from __future__ import annotations

from pathlib import Path

from model_blame.adapters.factory_io.tag_mapper import TagMapper


ROOT = Path(__file__).resolve().parents[1]


def test_tag_mapping_converts_raw_factoryio_tags_to_simir_samples() -> None:
    mapper = TagMapper.from_file(ROOT / "config" / "tag_maps" / "factory_io_demo_scene.yaml")

    batch = mapper.batch_from_raw(
        {"SensorEntry": "true", "SensorExit": False, "ConveyorMotor": 1},
        run_id="run_001",
        backend="factory_io",
        sim_time=1.0,
    )

    entry = next(sample for sample in batch.samples if sample.full_tag == "conveyor_1.entry_sensor")
    motor = next(sample for sample in batch.samples if sample.full_tag == "conveyor_1.motor_command")

    assert entry.value is True
    assert motor.value is True
    assert entry.metadata["raw_name"] == "SensorEntry"
