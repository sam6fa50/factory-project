from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from model_blame.agent_api.service import create_mock_service  # noqa: E402
from model_blame.blame.hypotheses import BlameHypothesisGenerator  # noqa: E402


SCENARIOS = ("normal", "missing_exit", "delayed_transition")
DEFAULT_OUTPUT_ROOT = ROOT / "runs" / "factory_io_mock_residual_baseline"


def run_case(
    scenario: str,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    duration_seconds: float = 8.0,
) -> dict[str, Any]:
    output_dir = Path(output_root) / scenario
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "telemetry.jsonl"
    if log_path.exists():
        log_path.unlink()

    sim = create_mock_service(scenario=scenario, jsonl_log_path=log_path)
    sim.start(scenario=scenario)
    sim.poll_for(duration_seconds)

    residuals = sim.recent_residuals()
    features = sim.pooler.features()
    hypotheses = BlameHypothesisGenerator().generate(residuals, sim.recent_samples(), features)
    report = sim.blame_report()

    (output_dir / "residuals.json").write_text(
        json.dumps([residual.model_dump(mode="json") for residual in residuals], indent=2),
        encoding="utf-8",
    )
    (output_dir / "hypotheses.json").write_text(
        json.dumps([hypothesis.model_dump(mode="json") for hypothesis in hypotheses], indent=2),
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    sim.pooler.stop_run()
    sim.adapter.disconnect()

    return {
        "scenario": scenario,
        "output_dir": str(output_dir),
        "telemetry_log": str(log_path),
        "residual_types": [residual.type for residual in residuals],
        "hypotheses": [hypothesis.primary_blame for hypothesis in hypotheses],
        "throughput_count": features.throughput_count,
        "blocked_assets": features.blocked_assets,
    }


def run_all_cases(
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    duration_seconds: float = 8.0,
) -> list[dict[str, Any]]:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    summaries = [run_case(scenario, output_root, duration_seconds) for scenario in SCENARIOS]
    (output_root / "summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    return summaries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Factory I/O mock residual baseline experiment.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--duration-seconds", type=float, default=8.0)
    args = parser.parse_args(argv)

    summaries = run_all_cases(args.output_root, args.duration_seconds)
    print("Factory I/O mock residual baseline")
    print(f"Artifacts written under {args.output_root}")
    for item in summaries:
        residuals = ", ".join(item["residual_types"]) or "none"
        hypotheses = ", ".join(item["hypotheses"]) or "none"
        print(f"- {item['scenario']}: residuals={residuals}; hypotheses={hypotheses}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
