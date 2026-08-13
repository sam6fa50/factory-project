# Knowledge

This file preserves durable project understanding. It is not a diary and should not contain raw chat transcripts.

## Source Register

- `SRC-000`: Bootstrap mission prompt supplied as a Codex attachment on 2026-08-13 by the project owner. Status: raw input extracted into canonical repository structure.
- `SRC-001`: Existing local codebase inspected on 2026-08-13. Status: current implementation evidence.
- `SRC-002`: Local verification on 2026-08-13: `python -m pytest` passed 14 tests; `python experiments/factory_io_mock_residual_baseline/run.py` produced the expected normal, missing-transition, and delayed-transition scenario split.
- `SRC-003`: Local verification on 2026-08-13 after chat ingestion: `python -m pytest` passed 15 tests; the Factory I/O mock baseline kept the expected scenario split; `python experiments/aemid_motor_active_diagnosis/run.py` showed `active_probe` lower average entropy than `passive_idle` with no safety violations.
- `SRC-004`: Sister Codex task "Build model-blame-mvp MVP" and local project at `C:\Users\sam10\Documents\Codex\2026-08-12\referenced-chatgpt-conversation-this-is-an`, read on 2026-08-13. Status: prior Candidate D motor MVP and everyday toy-case code/tests synthesized into this repo; old workspace not copied wholesale.
- `SRC-005`: Local verification on 2026-08-13 after toy-case synthesis: `python -m pytest` passed 20 tests; Factory I/O mock baseline, active motor diagnosis, and everyday toy-case experiment commands all completed with expected winners.
- `CHAT-001`: "AI Project Repository Prompt", https://chatgpt.com/share/6a7e394d-a2f0-83e8-b5ef-eb7cf30caa61. Status: complete accessible shared text extracted and reconciled on 2026-08-13; raw transcript not committed.
- `CHAT-002`: "MVP AI for Blame", https://chatgpt.com/share/6a7e395a-c344-83e8-92a4-a09b78208ea3. Status: complete accessible shared text extracted and reconciled on 2026-08-13; implementation requirements compared against current code.
- `CHAT-003`: "AI in Industrial Automation", https://chatgpt.com/share/6a7b878d-e51c-83e8-acda-a57baa1e9ab4. Status: complete accessible shared text extracted and reconciled on 2026-08-13; research claims treated as hypotheses unless separately verified.
- `CHAT-004`: "Machine Data Access Flow", https://chatgpt.com/share/6a7e36e3-3d3c-83ea-89d8-ec1a055d8435. Status: complete accessible shared text extracted and reconciled on 2026-08-13.
- `CHAT-005`: "AI in Industrial Automation", https://chatgpt.com/share/6a7e36c1-62f4-83ea-9afa-6eb9c7c2bb47. Status: complete accessible shared text extracted and reconciled on 2026-08-13.
- `SURV-001`: AGENTS.md standard, https://agents.md/.
- `SURV-002`: OpenAI Codex AGENTS.md docs, https://learn.chatgpt.com/docs/agent-configuration/agents-md.
- `SURV-003`: OpenAI ExecPlans article, https://developers.openai.com/cookbook/articles/codex_exec_plans.
- `SURV-004`: OpenAI/Agent Skills docs, https://learn.chatgpt.com/docs/build-skills and https://agentskills.io/specification.
- `SURV-005`: Claude Code memory docs, https://code.claude.com/docs/en/memory.
- `SURV-006`: Gemini CLI context docs, https://geminicli.com/docs/cli/gemini-md/.
- `SURV-007`: Cursor rules docs, https://cursor.com/docs/rules.
- `SURV-008`: GitHub Copilot custom-instruction docs, https://docs.github.com/en/copilot/reference/custom-instructions-support.
- `SURV-009`: Basic Memory docs and repository, https://github.com/basicmachines-co/basic-memory and https://docs.basicmemory.com/reference/technical-information.
- `SURV-010`: OpenSpec repository, https://github.com/Fission-AI/OpenSpec.
- `SURV-011`: GitHub Spec Kit docs, https://github.github.com/spec-kit/.
- `SURV-012`: MemoryCustodian repository, https://github.com/waittim/MemoryCustodian.
- `SURV-013`: projectmem repository, https://github.com/riponcm/projectmem.
- `SURV-014`: agentmemory repository, https://github.com/rohitg00/agentmemory.
- `IND-001`: NIST Digital Twins for Advanced Manufacturing, https://www.nist.gov/programs-projects/digital-twins-advanced-manufacturing. Status: primary source reviewed on 2026-08-13.
- `IND-002`: NIST credibility consideration for manufacturing digital twins, https://www.nist.gov/publications/credibility-consideration-digital-twins-manufacturing. Status: primary source reviewed on 2026-08-13.
- `IND-003`: OPC Foundation AAS/OPC UA companion specification overview and mapping, https://reference.opcfoundation.org/specs/OPC-30270/4 and https://reference.opcfoundation.org/specs/OPC-30270/5.1. Status: primary source reviewed on 2026-08-13.
- `IND-004`: Eclipse BaSyx overview, https://eclipse.dev/basyx/. Status: primary source reviewed on 2026-08-13.
- `IND-005`: FMI standard overview and documentation, https://fmi-standard.org/ and https://fmi-standard.org/docs/main/. Status: primary source reviewed on 2026-08-13.
- `IND-006`: Vendor market signals reviewed on 2026-08-13: Rockwell GuardianAI, https://www.rockwellautomation.com/en-in/products/software/factorytalk/maintenancesuite/factorytalk-analytics-guardianai.html; ABB asset health and monitoring, https://www.abb.com/global/en/areas/motion/services/asset-health-and-monitoring; Siemens Senseye Predictive Maintenance, https://www.siemens.com/en-us/products/industrial-digitalization-services/senseye-predictive-maintenance/.

## Product And Market Understanding

HYPOTHESIS: Factory simulation and commissioning teams need faster diagnosis when modeled behavior and observed line behavior diverge. This still needs customer validation. Sources: `CHAT-002`, `CHAT-003`.

ASSUMPTION: The first high-value workflow is not autonomous repair; it is evidence-backed triage that narrows which model assumption, tag mapping, sensor, actuator, physical process, or control behavior should be checked next. Sources: `CHAT-002`, `SRC-001`.

HYPOTHESIS: The strongest long-term positioning is active, uncertainty-aware machine understanding: the system should know when passive observation is ambiguous, separate physical changes from sensor/actuator/model failures, and propose safe discriminating experiments. Source: `CHAT-003`.

OBSERVATION: Everyday examples make the model-blame idea easier to explain before introducing industrial simulators: laptop temperature can blame hidden CPU load, phone battery drain can blame GPS activity, coffee cooling can blame heat-loss assumptions, and video-call latency can blame upload traffic. Source: `SRC-004`.

HYPOTHESIS: The differentiated buyer may be a simulation engineering lead, commissioning lead, controls engineering lead, digital-twin/model credibility owner, or controls R&D team rather than a generic maintenance buyer. Source: `CHAT-003`.

OBSERVATION: Predictive maintenance and asset-health messaging is already present in major industrial vendor offerings. This supports caution against positioning the project as generic predictive maintenance, but it is not a complete competitive analysis. Source: `IND-006`.

OPEN QUESTION: Which customer pain is strongest: model credibility, commissioning, simulator mismatch diagnosis, sensor trust, or plant-wide fault propagation?

OPEN QUESTION: Which simulator backend after Factory I/O would create the strongest evidence of generality: ROS2/Gazebo, FlexSim, Siemens Plant Simulation, Visual Components, Simulink, or another tool?

## Current Implementation Findings

FACT: The current MVP is a Python package named `model-blame-factoryio-mvp` requiring Python 3.10 or newer, Pydantic, and PyYAML. Optional extras cover Web API, OPC UA, Modbus, API server, and dev/test dependencies. Source: `SRC-001`.

FACT: SimIR is implemented as Pydantic models for simulator backend metadata, simulation runs, assets, tags, telemetry samples and batches, events, alarms, commands, fault injection specs, operation results, backend capabilities, residuals, and blame hypotheses. Source: `SRC-001`.

FACT: `MockFactoryIOAdapter` generates deterministic Factory I/O-style telemetry for three scenarios: `normal`, `missing_exit`, and `delayed_transition`. Source: `SRC-001`.

FACT: `FactoryIOAdapter` isolates live Factory I/O integration behind Web API, OPC UA, and Modbus transport client classes. Web API supports configured endpoints; OPC UA and Modbus clients are scaffolds that raise `NotImplementedError` on connect. Source: `SRC-001`.

FACT: The first expectation rule checks whether `conveyor_1.entry_sensor` is followed by `conveyor_1.exit_sensor` within 3 seconds. Missing or late transitions produce residuals. Source: `SRC-001`.

OBSERVATION: Baseline experiment verification on 2026-08-13 showed the expected scenario split: normal emitted no residuals, missing exit emitted `missing_transition`, and delayed exit emitted `delayed_transition`. Generated artifacts are reproducible outputs and are not canonical by themselves. Source: `SRC-002`.

FACT: `experiments/aemid_motor_active_diagnosis/` is a deterministic toy experiment that compares passive idle observation against a bounded active probe for a DC motor fault set. Latest verification showed lower average final entropy for the active probe and no safety-envelope violations. Sources: `SRC-001`, `SRC-003`.

FACT: `experiments/everyday_model_blame_toy_cases/` is a deterministic pure-Python experiment with four fake model-blame scenarios: laptop temperature/background CPU load, phone battery/GPS activity, coffee cooling/insulated mug, and video-call latency/cloud backup upload traffic. Sources: `SRC-004`, `SRC-005`.

GAP: Live Factory I/O is not validated; the Web API path assumes a configured/custom bridge, and OPC UA/Modbus remain placeholders. Source: `CHAT-002`, `SRC-001`.

GAP: The two-stream product thesis, real-world telemetry versus simulator/digital-twin telemetry, is not implemented yet. The current MVP diagnoses simulator telemetry against expectation rules. Source: `CHAT-002`, `SRC-001`.

GAP: Residual coverage is still narrow. Candidate future rules include actuator command with no effect, motor on with no motion/state change, counter/throughput mismatch, starved/blocked heuristics, and observed-vs-expected tag divergence thresholds. Source: `CHAT-002`.

## Industrial Data Architecture

FACT: Machine telemetry usually begins with sensors measuring values such as temperature, pressure, speed, current, position, vibration, flow, voltage, events, and alarms. Sources: `CHAT-004`, `CHAT-005`.

FACT: PLCs normally receive sensor signals and use current/live values for control; they should not be described as the main long-term historical store. Sources: `CHAT-004`, `CHAT-005`.

FACT: AI-facing software usually does not connect directly to physical sensors. It reads values exposed by PLCs, SCADA, historians/databases, edge gateways, APIs, or protocol clients. Sources: `CHAT-004`, `CHAT-005`.

FACT: There is no universal factory data chain. SCADA, historians, databases, MES, edge gateways, local files, cloud databases, APIs, and vendor platforms may appear in different combinations. Source: `CHAT-004`.

ASSUMPTION: Factory heterogeneity is a core product reason for keeping SimIR as the stable boundary. Source: `CHAT-004`.

ADAPTER IMPLICATION: PLC/protocol adapters should preserve raw address, unit, scaling, quality, timestamp source, and write capability when mapping OPC UA nodes, Modbus registers, or vendor tags into SimIR.

ADAPTER IMPLICATION: SCADA adapters should expect renamed or derived tags, deadbands, latency, and operator-facing alarms/events.

ADAPTER IMPLICATION: Historian/database adapters should support historical windows, original timestamps, sampling/compression metadata, stale/missing/interpolated quality, and replay-mode SimIR runs.

ADAPTER IMPLICATION: Edge gateway/MQTT adapters should preserve broker/topic, payload timestamp, QoS/retained status when relevant, gateway transform metadata, and disconnect/staleness behavior.

OPEN QUESTION: Which first real telemetry source is actually available: PLC OPC UA, Modbus TCP, SCADA API, historian/database, MQTT gateway, or Factory I/O-specific bridge?

OPEN QUESTION: Which timestamp is authoritative: PLC/device time, SCADA time, gateway publish time, database insert time, or adapter receive time?

OPEN QUESTION: Are writes/commands allowed at all for real factory sources, or should real-factory adapters always default to read-only?

## Standards And Research Direction

FACT: NIST manufacturing digital-twin work treats verification, validation, uncertainty quantification, and credibility as important digital-twin concerns. Sources: `IND-001`, `IND-002`.

FACT: OPC UA and AAS have a documented mapping path for Industrie 4.0-style digital-twin data, and Eclipse BaSyx positions AAS with OPC UA/MQTT integration patterns. Sources: `IND-003`, `IND-004`.

FACT: FMI is a standard for exchanging dynamic simulation models as FMUs with interface types such as co-simulation and model exchange. Source: `IND-005`.

DECISION: Do not invent a competing industrial ontology as the first move. Treat OPC UA/AAS as likely semantic/operational substrates and FMI as a likely simulation-model substrate where they fit.

HYPOTHESIS: SimIR should eventually extend from telemetry normalization into an epistemic experiment interface: observe, act, experiment, query capabilities, maintain hypothesis state, and emit next-best diagnostic probes. Source: `CHAT-003`.

HYPOTHESIS: Future model blame data structures may need named model components/equations, parameter posterior state, validity region, contradicting evidence, safety constraints, and proposed discriminating experiments. Source: `CHAT-003`.

OPEN QUESTION: Should the next implementation push remain live Factory I/O validation, or should it first deepen the controlled active-diagnosis experiment?

OPEN QUESTION: What safety model is sufficient for experiment selection: max current/speed/temp/acceleration/duration, explicit forbidden states, and read-only mode for real plants?

## Repository Operating Model

DECISION: Use plain Git plus Markdown as the authoritative project state. Do not install a memory system in the bootstrap step. Sources: `SRC-000`, `CHAT-001`, `SURV-001` through `SURV-014`.

DECISION: Use root `AGENTS.md` as the portable control plane. It routes agents to `README.md`, `PROJECT.md`, `KNOWLEDGE.md`, `EXECUTION.md`, source code, tests, experiments, or plans as needed. Source: `CHAT-001`.

DECISION: Use root `ORIENTATION.md` as the human-first directory map. Agents should update it when repository layout changes or when a directory's purpose changes. Source: current repository operating decision on 2026-08-13.

DECISION: AI chats and memory entries are inbox/evidence only until explicitly reconciled into Git-tracked docs, code, tests, specs, or experiments. Do not create one permanent summary file per chat. Sources: `CHAT-001`, `SRC-000`.

DECISION: Use thin vendor adapters only when they prevent duplication. Claude Code gets `CLAUDE.md` with `@AGENTS.md`; Gemini CLI gets `.gemini/settings.json` that includes `AGENTS.md` as a context filename. Cursor and GitHub Copilot adapters are deferred because current docs show AGENTS.md support in relevant agent contexts. Sources: `SURV-005` through `SURV-008`.

DECISION: Basic Memory is the strongest evaluated retrieval/indexing candidate, but it is deferred. It is local-first and file-first with a secondary SQLite index and MCP support, but its AGPL license, optional cloud route, and write-capable memory graph need an explicit governance decision before adoption. Source: `SURV-009`.

DECISION: OpenSpec and Spec Kit are deferred. OpenSpec is the lighter candidate for durable feature specs; Spec Kit is powerful but too heavyweight for the current MVP. Sources: `SURV-010`, `SURV-011`.

DECISION: Use ExecPlan-style living plans only for substantial multi-session work. Do not add permanent plan bureaucracy for small tasks. Source: `SURV-003`.

HYPOTHESIS: A project-specific `knowledge-consolidation` Agent Skill may be useful after a few more ingestion batches reveal a stable repeatable workflow. Source: `CHAT-001`.

## Security And Licensing

FACT: No secrets were found during the initial file inspection. Source: `SRC-001`.

ASSUMPTION: Factory I/O endpoint details, customer scenes, exported telemetry, and production plant data may be commercially sensitive and should not be sent to cloud memory or indexing tools without review.

OPEN QUESTION: The project itself does not currently declare a license. Decide before sharing or accepting external contributions.

OPEN QUESTION: If Basic Memory or another memory tool is adopted, decide whether AGPL obligations, cloud storage, telemetry, sync, and derived indexes are acceptable for business use.
