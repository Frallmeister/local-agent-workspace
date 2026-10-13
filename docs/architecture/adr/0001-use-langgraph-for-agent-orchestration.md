# ADR-0001: Use LangGraph for Agent Orchestration

- **Status:** Accepted
- **Date:** 2026-10-14
- **Decision owners:** Project maintainers
- **Related requirements:** FR-004, FR-008, FR-010–FR-013, NFR-005–NFR-008, SEC-002–SEC-004, SEC-009–SEC-010
- **Related architecture:** [Architecture Overview](../architecture-overview.md)

## Context

Local Agent Workspace is a single-user, local-first assistant that must support tool calling, bounded execution, specialist-agent delegation, inspection, cancellation, and pauses for user approval before file modification. The design must remain testable without a live LLM and allow compatible model providers to be changed through configuration.

An orchestration mechanism is required to model control flow and execution state. Introducing multiple overlapping agent frameworks would raise dependency and integration costs for a small, modular application. The orchestration framework must not become the enforcement boundary for filesystem, database, or MCP authorization.

## Decision

Use **LangGraph as the sole agent orchestration framework**, with ordinary Python and **Pydantic (not Pydantic AI)** for typed inputs, outputs, tool contracts, and validation.

- Express agent control flow, delegation, state transitions, and interrupt/resume behavior in LangGraph.
- Keep tool implementations, connectors, permission checks, and approval enforcement in framework-independent application services.
- Introduce specialist-agent graphs incrementally; a single agent and deterministic workflow remain preferred until there is a demonstrated need for delegation.
- Use a defined model-provider interface (or a thin integration boundary around supported LangChain model clients) so model choices are configuration-driven, subject to capability checks.
- Enforce execution budgets, tool permissions, and approval decisions in deterministic backend logic. Graph state or model instructions alone must not authorize sensitive actions.
- Use durable checkpoints when resumable workflows are implemented. The backing store and recovery protocol require separate design and verification.

## Considered alternatives

| Alternative | Advantages | Disadvantages / reason not selected |
| --- | --- | --- |
| **Pydantic AI only** | Python-first, typed tool interfaces, relatively little setup | Stateful branching, resumable approval flows, and explicit delegation would require further assessment and potentially application-specific orchestration; less aligned with the chosen graph-centric control model |
| **LangGraph only, plus Pydantic** | Explicit graph transitions, state, interrupts, checkpoint integrations; one orchestration framework | Graph lifecycle and replay semantics introduce conceptual and testing complexity; agent tooling may require more explicit assembly |
| **Pydantic AI + LangGraph** | Rich agent abstraction plus graph orchestration | Two overlapping frameworks, additional integration contracts, and more difficult diagnosis; no initial requirement justifies both |
| **Custom agent loop in Python** | Minimal dependencies and full control | Requires maintaining our own state, cancellation, resumability, routing, and recovery semantics; larger long-term maintenance burden |

## Consequences

### Positive

- Explicit, inspectable execution paths for bounded multi-step work.
- A single orchestration model for future specialization and approval flows.
- Deterministic tools and policy enforcement can be unit tested without LangGraph or an LLM.
- Graph checkpoints and interruption can support recovery of awaiting-approval runs.

### Costs and risks

- LangGraph becomes an architectural dependency; API upgrades require compatibility testing.
- Interrupt/resume may rerun code within nodes. Operations with side effects must be designed for safe replay, idempotency where feasible, and transactionally validated execution.
- The framework does **not** provide a security boundary. The tool gateway must authorize actual operations, including MCP tools, independently of agent decisions.
- Not all model providers support reliable tool calling or structured responses. Capability validation and targeted evaluation remain necessary.
- A multi-agent architecture may increase latency, cost, and failure modes; complexity must be introduced only for specific use cases and evaluated against a simpler baseline.

## Verification and acceptance criteria

This decision is considered implemented only after the relevant functionality exists and its tests provide evidence that:

1. A deterministic graph can run end-to-end with a mocked model, without Ollama or external APIs (NFR-005).
2. A tool invocation crosses the shared authorization boundary; unauthorized actions fail even when requested by the graph (SEC-003, SEC-009).
3. A write proposal suspends execution and cannot execute without approval bound to the exact operation (FR-010, SEC-002, SEC-010).
4. Interrupted work can be resumed or cancelled without unintended duplicate file writes (FR-012, FR-013).
5. Configured execution limits are enforced outside model instructions (NFR-007).
6. At least one evaluation compares a delegated workflow with a simpler single-agent or deterministic approach before declaring multi-agent orchestration beneficial.

## Follow-up decisions

- Checkpoint persistence and recovery semantics.
- Tool gateway and authorization enforcement, including MCP integration.
- Model-provider capabilities and configuration contract.
- Supported workspace file modification operations and approval protocol.

## References

- [Software Requirements Specification](../../requirements/software-requirements.md)
- [Product Requirements Document](../../requirements/product-requirements.md)
- [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)
