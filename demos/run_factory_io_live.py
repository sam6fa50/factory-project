from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model_blame.adapters.factory_io.adapter import FactoryIOAdapter, FactoryIOConfig  # noqa: E402
from model_blame.agent_api.client import SimClient  # noqa: E402
from model_blame.blame.hypotheses import BlameHypothesisGenerator  # noqa: E402
from model_blame.residuals.engine import ResidualEngine  # noqa: E402
from model_blame.residuals.rules import load_expectation_rules  # noqa: E402


def main() -> None:
    config_path = ROOT / "config" / "backends" / "factory_io.yaml"
    expectations_path = ROOT / "config" / "expectations" / "conveyor_rules.yaml"
    config = FactoryIOConfig.from_yaml(config_path)
    config.tag_map_path = str(ROOT / config.tag_map_path)

    adapter = FactoryIOAdapter(config)
    rules = load_expectation_rules(expectations_path)
    sim = SimClient(adapter, ResidualEngine(rules), BlameHypothesisGenerator())

    result = adapter.connect()
    if not result.ok:
        print("Factory I/O live connection is not ready:")
        print(result.message)
        print("")
        print("Use demos/run_mock_demo.py now, then fill config/backends/factory_io.yaml for your live bridge.")
        return

    sim.start()
    sim.poll_for(10.0, sleep=True)
    print(sim.blame_report())
    sim.pooler.stop_run()
    adapter.disconnect()


if __name__ == "__main__":
    main()
