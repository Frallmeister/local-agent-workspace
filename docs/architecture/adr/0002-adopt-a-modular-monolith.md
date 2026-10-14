# ADR-0002: Adopt a Modular Monolith

- **Status:** Accepted
- **Date:** 2026-10-14
- **Decision owners:** Project maintainers
- **Related requirements:** FR-001, FR-014, NFR-001–NFR-005, SEC-003
- **Related architecture:** [Architecture Overview](../architecture-overview.md)

## Context

Local Agent Workspace is a single-user, self-hosted application with a web UI, API, agent orchestration, tool execution, connectors, and persistence. Its first implementation must be understandable, testable, and runnable on a development laptop. Service boundaries would add deployment and operational costs before independent scaling or organizational ownership is needed.

## Decision

Use a **modular Python backend deployed as a single application process** (with PostgreSQL and the LLM runtime as separately managed dependencies) and a **separate React/TypeScript frontend**.

- Organize backend code by responsibilities: API, orchestration, model integration, tool execution, policy, retrieval, and connectors.
- Make dependencies explicit; avoid circular imports and cross-module access to implementation internals.
- Expose typed service contracts at boundaries, but introduce abstractions only where multiple implementations or testing justify them.
- Keep HTTP handlers thin; deterministic domain logic and authorization must not depend on FastAPI routes or LangGraph nodes.
- Use Docker Compose for local supporting services where useful; do not require Kubernetes or cloud provisioning.
- Package and run the frontend and backend through documented local development and release procedures. Their exact production serving arrangement remains an implementation choice.

## Considered alternatives

| Alternative | Trade-off |
| --- | --- |
| **Microservices for each agent/integration** | Independent processes and scaling, but excessive network, deployment, tracing, and failure-handling complexity for a single-user product. |
| **Unstructured monolith** | Fast initial coding, but weak boundaries make policy enforcement, testing, and later extensions harder. |
| **Modular monolith (selected)** | Clear code ownership and easier local deployment, with the trade-off that modules are not independently deployable. |

## Consequences

- All tool adapters are invoked behind application interfaces, whether implemented locally or through MCP.
- PostgreSQL may host both application data and vector retrieval, but data ownership and privileges must be distinguished logically.
- We do not promise arbitrary database-engine interchangeability: pgvector-specific behavior may be isolated, but replacing PostgreSQL would be a separate migration decision.
- Future service extraction is possible when justified by actual operational needs, not a present requirement.

## Verification

1. Backend unit tests can exercise policy, tools, and connectors without starting the web server or a real LLM (NFR-005).
2. A documented local startup path reaches a working API and frontend without external cloud infrastructure (FR-001, NFR-001–NFR-002).
3. Contract tests detect incompatible changes at key module/API boundaries (NFR-003; NFR-009 where implemented).

## References

- [Product Requirements Document](../../requirements/product-requirements.md)
- [Software Requirements Specification](../../requirements/software-requirements.md)
