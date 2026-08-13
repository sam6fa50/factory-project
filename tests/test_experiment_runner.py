from __future__ import annotations

import json

from experiments.factory_io_mock_residual_baseline.run import run_all_cases


def test_mock_residual_baseline_experiment_writes_artifacts(tmp_path) -> None:
    summaries = run_all_cases(tmp_path)

    by_scenario = {item["scenario"]: item for item in summaries}
    assert by_scenario["normal"]["residual_types"] == []
    assert by_scenario["missing_exit"]["residual_types"] == ["missing_transition"]
    assert by_scenario["delayed_transition"]["residual_types"] == ["delayed_transition"]

    summary_path = tmp_path / "summary.json"
    assert summary_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8")) == summaries

    for scenario in by_scenario:
        assert (tmp_path / scenario / "telemetry.jsonl").exists()
        assert (tmp_path / scenario / "residuals.json").exists()
        assert (tmp_path / scenario / "hypotheses.json").exists()
        assert (tmp_path / scenario / "report.md").exists()
