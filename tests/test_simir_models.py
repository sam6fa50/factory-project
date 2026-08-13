from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_blame.simir.models import FaultInjection, Quality, TelemetrySample


def test_telemetry_sample_accepts_canonical_payload() -> None:
    sample = TelemetrySample(
        timestamp="2026-08-13T12:00:00Z",
        sim_time=10.0,
        run_id="run_001",
        backend="factory_io",
        asset_id="conveyor_1",
        tag="entry_sensor",
        kind="sensor",
        value=True,
        quality="good",
    )

    assert sample.full_tag == "conveyor_1.entry_sensor"
    assert sample.quality == Quality.GOOD
    assert sample.timestamp.isoformat().startswith("2026-08-13T12:00:00")


def test_telemetry_sample_rejects_unknown_quality() -> None:
    with pytest.raises(ValidationError):
        TelemetrySample(
            run_id="run_001",
            backend="factory_io",
            asset_id="conveyor_1",
            tag="entry_sensor",
            kind="sensor",
            value=True,
            quality="sparkly",
        )


def test_fault_injection_model_has_generated_id() -> None:
    fault = FaultInjection(fault_type="stuck_sensor", tag_id="conveyor_1.exit_sensor")

    assert fault.fault_id.startswith("flt_")
    assert fault.enabled is True
