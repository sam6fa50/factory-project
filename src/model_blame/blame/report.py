from __future__ import annotations

from model_blame.simir.models import BlameHypothesis, Residual, SimulationRun
from model_blame.telemetry.features import DerivedFeatures


def build_blame_report(
    run: SimulationRun | None,
    residuals: list[Residual],
    hypotheses: list[BlameHypothesis],
    features: DerivedFeatures | None = None,
    title: str = "Model-Blame Report",
) -> str:
    lines = [f"# {title}", ""]
    if run is not None:
        lines.extend(
            [
                f"- Run: {run.run_id}",
                f"- Backend: {run.backend}",
                f"- Scenario: {run.scenario}",
                f"- Mode: {run.mode}",
                "",
            ]
        )

    if features is not None:
        lines.extend(
            [
                "## Derived Features",
                f"- Throughput count: {features.throughput_count}",
                f"- Cycle times: {features.cycle_times or 'none'}",
                f"- Blocked assets: {features.blocked_assets or 'none'}",
                "",
            ]
        )

    lines.append("## Residuals")
    if not residuals:
        lines.extend(["No residuals detected.", ""])
    else:
        for residual in residuals:
            lines.extend(
                [
                    f"### {residual.residual_id}: {residual.type}",
                    f"- Asset: {residual.asset_id}",
                    f"- Severity: {residual.severity}",
                    f"- Expected: {residual.expected}",
                    f"- Observed: {residual.observed}",
                    f"- Candidate causes: {', '.join(residual.candidate_causes) or 'none'}",
                    "",
                ]
            )

    lines.append("## Blame Hypotheses")
    if not hypotheses:
        lines.extend(["No blame hypotheses emitted.", ""])
    else:
        for hypothesis in hypotheses:
            lines.extend(
                [
                    f"### {hypothesis.hypothesis_id}: {hypothesis.primary_blame}",
                    f"- Residual: {hypothesis.residual_id}",
                    f"- Confidence: {hypothesis.confidence:.2f}",
                    f"- Explanation: {hypothesis.explanation}",
                    f"- Supporting evidence: {'; '.join(hypothesis.supporting_evidence) or 'none'}",
                    f"- Next actions: {'; '.join(hypothesis.next_diagnostic_actions) or 'none'}",
                    "",
                ]
            )

    return "\n".join(lines).strip() + "\n"
