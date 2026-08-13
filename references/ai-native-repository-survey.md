# AI-Native Repository Survey

Survey date: 2026-08-13.

This survey supports the bootstrap decision for the Factory I/O model-blame MVP. It favors primary project documentation, official product docs, package registries, and GitHub repository metadata. Searches also checked GitLab, Codeberg, Forgejo-style and package-registry surfaces for stronger current candidates; no alternative justified adding infrastructure during bootstrap.

## Summary Recommendation

Use plain Git plus Markdown as the canonical project state. Adopt root `AGENTS.md`, a tiny `CLAUDE.md` import adapter, and Gemini CLI project settings that load `AGENTS.md`. Borrow memory and spec-system ideas, but do not install Basic Memory, projectmem, MemoryCustodian, OpenSpec, Spec Kit, or agentmemory yet.

## Candidate Decisions

| System | Current fit | Decision |
| --- | --- | --- |
| AGENTS.md | Portable, readable project instruction surface. Broad agent ecosystem support. | ADOPT |
| OpenAI Codex AGENTS.md | Codex reads root and nested AGENTS files with precedence and size limits. | ADOPT |
| Claude Code CLAUDE.md | Claude reads `CLAUDE.md`, not `AGENTS.md`, but supports `@AGENTS.md` imports. | ADOPT THIN ADAPTER |
| Gemini CLI context files | Gemini defaults to `GEMINI.md`, but project settings can configure `context.fileName` to include `AGENTS.md`. | ADOPT CONFIG |
| Cursor rules | Cursor supports root and nested `AGENTS.md`; `.cursor/rules` is useful only for scoped metadata rules. | DEFER |
| GitHub Copilot instructions | Copilot supports `.github/copilot-instructions.md` broadly and `AGENTS.md` in agent contexts. | DEFER |
| Agent Skills / SKILL.md | Good for repeatable procedures with progressive disclosure. | BORROW DESIGN |
| OpenAI ExecPlans | Good for substantial multi-session work. | BORROW DESIGN |
| Basic Memory | Strong local-first Markdown plus SQLite index plus MCP retrieval. AGPL and write-capable memory need governance. | ADOPT PARTIALLY LATER |
| MemoryCustodian | Repo-native Markdown memory with minimal-context routing, but small and young. | BORROW DESIGN |
| projectmem | Local `.projectmem/`, MCP, event log, and repeat-failure warnings. Useful but adds another state layer. | BORROW DESIGN |
| OpenSpec | Lightweight spec workflow for brownfield changes. | DEFER |
| GitHub Spec Kit | Large, mature, extensible spec-driven toolkit. Too much process for this MVP now. | DEFER |
| agentmemory | Active, multi-agent MCP/hook memory server with benchmarks. Too much machinery for bootstrap. | WATCH |

## Repository Metadata Snapshot

GitHub API snapshot on 2026-08-13:

| Repository | License | Stars | Last pushed | Notes |
| --- | --- | ---: | --- | --- |
| `agentsmd/agents.md` | MIT | 23625 | 2026-03-12 | Open AGENTS.md format site. |
| `basicmachines-co/basic-memory` | AGPL-3.0 | 3654 | 2026-08-13 | Local-first/cloud optional Markdown memory system. |
| `Fission-AI/OpenSpec` | MIT | 64787 | 2026-08-13 | Lightweight spec-driven development framework. |
| `github/spec-kit` | MIT | 127341 | 2026-08-13 | Broad spec-driven toolkit and CLI. |
| `waittim/MemoryCustodian` | MIT | 20 | 2026-07-30 | Small repo-native memory governance project. |
| `riponcm/projectmem` | MIT | 654 | 2026-08-06 | Local-first event-sourced memory layer. |
| `rohitg00/agentmemory` | Apache-2.0 | 26965 | 2026-08-10 | MCP/hook memory server with auto-capture. |

Package registry snapshot on 2026-08-13:

| Package | Registry | Version | License | Notes |
| --- | --- | --- | --- | --- |
| `basic-memory` | PyPI | 0.22.1 | AGPL-3.0-or-later | Local-first knowledge management. |
| `projectmem` | PyPI | 0.2.0 | MIT | Memory plus judgment layer for coding agents. |
| `memory-custodian` | PyPI | not found | n/a | GitHub repo exists; no PyPI package found. |
| `specify-cli` | PyPI | 0.16.3 | not declared in registry metadata | Spec Kit CLI. |
| `@fission-ai/openspec` | npm | 1.9.0 | MIT | OpenSpec CLI package. |

## Source Notes

- AGENTS.md standard: https://agents.md/ describes AGENTS.md as a predictable README-like file for coding agents and lists broad ecosystem compatibility.
- OpenAI Codex AGENTS.md docs: https://learn.chatgpt.com/docs/agent-configuration/agents-md documents Codex discovery, precedence, nested files, and default project instruction size limits.
- OpenAI ExecPlans: https://developers.openai.com/cookbook/articles/codex_exec_plans recommends self-contained living plans for complex features and significant refactors.
- Agent Skills: https://learn.chatgpt.com/docs/build-skills and https://agentskills.io/specification describe `SKILL.md`, progressive disclosure, optional scripts/references/assets, and validation.
- Claude Code: https://code.claude.com/docs/en/memory says Claude reads `CLAUDE.md`, supports `@AGENTS.md` imports, and loads CLAUDE files at session start.
- Gemini CLI: https://geminicli.com/docs/cli/gemini-md/ says `GEMINI.md` is the default context file and `context.fileName` can include `AGENTS.md`.
- Cursor: https://cursor.com/docs/rules says AGENTS.md is a simple alternative to `.cursor/rules` and supports root and nested AGENTS files.
- GitHub Copilot: https://docs.github.com/en/copilot/reference/custom-instructions-support documents which Copilot surfaces support `.github/copilot-instructions.md`, path-specific instructions, and AGENTS.md.
- Basic Memory: https://github.com/basicmachines-co/basic-memory and https://docs.basicmemory.com/reference/technical-information describe file-first Markdown storage, secondary database indexing, MCP, local/cloud modes, and AGPL licensing.
- OpenSpec: https://github.com/Fission-AI/OpenSpec positions itself as a lightweight, brownfield-friendly spec layer with per-change folders.
- Spec Kit: https://github.github.com/spec-kit/ describes an extensible intent-driven harness with Spec -> Plan -> Tasks -> Implement phases and many integrations.
- MemoryCustodian: https://github.com/waittim/MemoryCustodian describes repo-native plain Markdown project memory loaded only as needed.
- projectmem: https://github.com/riponcm/projectmem describes local `.projectmem/` memory, no cloud/telemetry, MCP tools, event log, and repeat-failure warnings.
- agentmemory: https://github.com/rohitg00/agentmemory describes a memory server with MCP, hooks, plugins, auto-capture, and multi-agent compatibility.

## Architecture Implications

- Keep `AGENTS.md` concise and route to canonical files rather than duplicating project truth.
- Keep memory systems derived from, or subordinate to, Git-tracked state.
- Prefer source-linked claims in `KNOWLEDGE.md` over AI recollections.
- Use experiment README files for executable questions and observed results.
- Use living plans only when work spans several files, sessions, or unresolved design questions.
- Avoid tool-specific duplicates unless the target tool cannot read or import the shared guidance.

## Deferred Adoption Criteria

Adopt a memory/indexing layer only if at least one of these becomes true:

- Incoming chats or research batches become large enough that manual routing is inefficient.
- Agents repeatedly miss durable context that is already present in canonical docs.
- Retrieval needs are task-specific enough that loading `KNOWLEDGE.md` is wasteful.
- The team accepts the license, storage, cloud, telemetry, and write-governance implications.

Adopt a spec system only if a feature requires durable behavioral agreement across multiple implementation sessions, contributors, or agent tools.
