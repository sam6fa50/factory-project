from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from model_blame.simir.models import Severity


class ExpectationRule(BaseModel):
    rule_id: str
    type: Literal["transition_deadline", "actuator_effect"]
    asset_id: str
    description: str = ""
    severity: Severity = Severity.MEDIUM
    start_tag: str | None = None
    end_tag: str | None = None
    command_tag: str | None = None
    effect_tag: str | None = None
    expected_command_value: object = True
    max_seconds: float = 3.0
    candidate_causes: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


def load_expectation_rules(path: str | Path) -> list[ExpectationRule]:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to load SimIR YAML configuration.") from exc
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return [ExpectationRule.model_validate(item) for item in data.get("rules", [])]
