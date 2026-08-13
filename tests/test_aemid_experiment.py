from __future__ import annotations

import json

from experiments.aemid_motor_active_diagnosis.run import run_all_cases


def test_active_motor_diagnosis_beats_passive_idle(tmp_path) -> None:
    summary = run_all_cases(tmp_path)

    passive = summary["policies"]["passive_idle"]
    active = summary["policies"]["active_probe"]

    assert active["average_final_entropy_bits"] < passive["average_final_entropy_bits"] - 0.2
    assert active["top1_accuracy"] == 1.0
    assert active["safety_violations"] == []

    cases = summary["cases"]
    active_cases = [case for case in cases if case["policy"] == "active_probe"]
    assert all(case["hidden_hypothesis"] == case["top_hypothesis"] for case in active_cases)

    summary_path = tmp_path / "summary.json"
    assert summary_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8"))["policies"] == summary["policies"]
