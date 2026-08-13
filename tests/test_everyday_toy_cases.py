from __future__ import annotations

import json

import pytest

from experiments.everyday_model_blame_toy_cases.run import (
    all_toy_cases,
    rank_toy_case,
    run_all_cases,
)


@pytest.mark.parametrize(
    ("case_key", "expected_winner"),
    [
        ("laptop_temperature", "background_cpu_load"),
        ("phone_battery", "gps_background"),
        ("coffee_cooling", "insulated_mug"),
        ("video_call_latency", "cloud_backup_upload"),
    ],
)
def test_everyday_toy_case_correct_blame_ranks_first(case_key: str, expected_winner: str) -> None:
    cases = {case.key: case for case in all_toy_cases()}

    report = rank_toy_case(cases[case_key])

    assert report.winner.key == expected_winner
    assert report.winner.loss < 1e-12


def test_everyday_toy_case_experiment_writes_artifacts(tmp_path) -> None:
    summary = run_all_cases(tmp_path)

    summary_path = tmp_path / "summary.json"
    markdown_path = tmp_path / "summary.md"
    assert summary_path.exists()
    assert markdown_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8")) == summary
    assert "Laptop Temperature" in markdown_path.read_text(encoding="utf-8")
