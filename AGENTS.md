# Agent Instructions — Local Agent Workspace

These instructions apply to the entire repository. Follow them when planning, implementing, reviewing, or documenting changes.

## Project and current scope

Local Agent Workspace is a public, open-source, single-user, local-first AI assistant for authorized local documents, structured data, and extensible tools. The application is under development; do not describe planned capabilities as implemented or verified.

Implement only the scope of the assigned GitHub issue. Prefer the smallest coherent, testable change over speculative infrastructure or abstractions. Ask for a design decision when a task conflicts with an accepted document or would materially change an architectural boundary.

## Authoritative project documents

Read the relevant documents **before designing or editing code**:

- `docs/requirements/product-requirements.md` — product goals and use cases.
- `docs/requirements/software-requirements.md` — requirement IDs and verification expectations.
- `docs/architecture/architecture-overview.md` — component responsibilities and trust boundaries.
- `docs/architecture/adr/` — accepted architectural decisions; in particular:
  - ADR-0001: LangGraph for agent orchestration.
  - ADR-0002: modular monolith.
  - ADR-0003: centralized tool authorization and policy enforcement.
  - ADR-0004: configurable model providers.
- `docs/security/threat-model.md` — threats, mitigations, and security testing priorities.
- `docs/project/development-roadmap.md` — milestones, release boundaries, and Definition of Done.

Treat accepted requirements and ADRs as the design baseline. If documents appear inconsistent, flag the discrepancy rather than silently choosing an interpretation. Distinguish **proposed**, **accepted**, **implemented**, and **verified**.

## Technology and repository conventions

- Python backend: FastAPI and Pydantic; LangGraph when agent orchestration is introduced.
- Frontend: React, TypeScript, and Vite when the frontend milestone begins.
- Python environments and dependencies: **uv** with the root `pyproject.toml` and committed `uv.lock`. Respect `.python-version` and `requires-python`; do not introduce pip/Poetry/Pipenv as parallel project managers.
- Documentation: Markdown and MkDocs Material; verify with `uv run mkdocs build --strict` after syncing the appropriate dependencies.
- Introduce directories and dependencies when a real feature requires them. Do not create unused scaffolding.

## Architecture and dependency boundaries

- Keep a **modular monolith**, not microservices. Organize packages by clear responsibility.
- Imports between Python subpackages are allowed where justified; they must follow deliberate dependency directions. Avoid circular imports and arbitrary cross-module access.
- HTTP/API code may call application services; application and domain logic must not depend on FastAPI request objects or transport-specific details.
- Prefer narrow, typed interfaces at meaningful boundaries (such as model providers, tools, and persistence). Introduce dependency inversion when it enables isolation and testing; avoid needless interface proliferation.
- Do not create a generic `common` or `utils` dumping ground.
- LangGraph controls workflow, **not authorization**. Model-generated requests must enter tools through the policy-enforcing gateway; no bypass via direct adapter execution.
- Do not add a second agent orchestration framework without a reviewed architectural decision.

## Security requirements

- Treat model output, retrieved documents, tool results, and MCP metadata as **untrusted data**. Never treat content or prompts as grants of permission.
- Enforce tool capabilities, resource scope, and run limits in deterministic application code. Fail closed when permissions or identities are unclear.
- Limit filesystem access to configured authorized roots; defend against traversal and symlink-based escapes.
- File writes require explicit approval bound to the **exact operation**; account for changed inputs, replay, retries, and resume semantics when implementing writes.
- Database tools must use a dedicated least-privilege read identity. MCP tools follow the same authorization policy as internal tools.
- External inference requires explicit opt-in; never silently fall back to a remote provider.
- Do not introduce unrestricted shell execution for agents. Do not commit secrets, personal documents, credentials, or sensitive example data. Minimize sensitive logging.
- Do not assume that binding to `localhost` alone secures an API.

## Implementation and verification workflow

1. Read the assigned issue, applicable requirement IDs, ADRs, and threat scenarios. Confirm scope and acceptance criteria.
2. Make a small, reviewable change on a feature branch. Preserve existing behavior unless change is explicitly requested.
3. Add or update deterministic tests for business rules, API contracts, and security boundaries. Include negative tests where authorization, input validation, or side effects are involved.
4. Prefer tests that do not require a live LLM, GPU, paid API, personal files, or internet connectivity. Clearly separate optional integration/evaluation tests.
5. Run relevant checks; for documentation changes run the strict MkDocs build and visually inspect modified Mermaid diagrams.
6. Update documentation, configuration examples, and dependency lockfiles whenever required by the change.
7. In the final implementation report, summarize changed files, requirement/issue coverage, checks **actually run** and their results, and any unverified behavior or remaining risks. Never claim tests passed unless executed.

Use GitHub issues and pull requests as the change record. Do not bypass required CI, branch protection, or review. Avoid unrelated refactoring, speculative features, or unrequested dependency upgrades.
