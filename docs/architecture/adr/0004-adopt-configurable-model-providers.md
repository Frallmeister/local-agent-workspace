# ADR-0004: Adopt Configurable Model Providers

- **Status:** Accepted
- **Date:** 2026-10-14
- **Decision owners:** Project maintainers
- **Related requirements:** FR-002–FR-004, FR-014, NFR-001, NFR-003, NFR-005–NFR-008, SEC-007–SEC-008, SEC-011
- **Related architecture:** [Architecture Overview](../architecture-overview.md)

## Context

The assistant must run locally on modest hardware yet remain useful on future computers with different GPUs and model sizes. It may optionally support externally hosted inference, without silently sending local data off-device. Providers differ in tool-calling behavior, structured output support, context size, response metadata, and error handling. A single fixed model would restrict use and make evaluation less informative.

## Decision

Provide a **configuration-driven model integration boundary**, using LangChain model integrations where appropriate rather than developing a full inference SDK.

- **Local inference via Ollama is the default.** External model providers require explicit user configuration and are disabled unless selected.
- Resolve the model at application configuration / agent construction boundaries; keep domain tools and authorization logic independent of provider-specific APIs.
- Validate required provider capabilities (including tool calling and structured outputs when applicable) and report an explicit unsupported-capability error rather than silently degrading or switching providers.
- Never implicitly fall back from local to remote inference. Define whether a configured provider can access document excerpts or tool outputs and make that flow visible in configuration and UI.
- Keep provider credentials out of committed files; redact secrets and sensitive payloads in telemetry.
- Provide a mock/fake model implementation for deterministic tests. Use a small, versioned evaluation set to compare behavior when switching real models.
- Record provider/model identifier, relevant generation parameters, and evaluation configuration so findings can be reproduced; do not treat identical outputs across providers as a requirement.

This ADR establishes a replaceable **model provider**, not a blanket promise that every model supports every workflow. Embedding models may require their own separately configurable integration when retrieval is implemented.

## Considered alternatives

| Alternative | Trade-off |
| --- | --- |
| **Hard-code Ollama in every agent** | Simple initially, but couples agent code to one transport and limits testing/reconfiguration. |
| **Implement a custom universal LLM abstraction** | Maximum apparent control, but large maintenance burden and risk of obscuring provider-specific capabilities. |
| **Thin configurable boundary over existing integrations (selected)** | Small amount of application-specific logic, with explicit capability and compatibility checks. |

## Consequences

- Runtime configuration is the primary way to change compatible models; no agent business-logic edit is needed for ordinary model changes.
- Agent outcomes and tool-call reliability may vary with model choice. Acceptance tests and evaluations must distinguish model weaknesses from orchestration defects.
- A local model with inadequate capabilities may block a workflow; this is preferable to unsafe or misleading fallback behavior.
- Provider-specific usage/cost metrics may be missing; report only measured or reliably available values.
- Data sent to remote providers crosses a trust boundary and requires a separate user-controlled setting.

## Verification

1. The same deterministic tool workflow can be exercised with a fake model in CI without GPU or network calls (NFR-005).
2. A supported alternate model can be chosen by configuration without changes to tool or orchestration logic (FR-002).
3. Missing required model capabilities produce a clear failure rather than silent fallback (NFR-008).
4. Local-only configuration does not call an external inference provider (FR-003, SEC-007).
5. Provider credentials and sensitive tool/document data are omitted from committed configuration and default tracing (SEC-008, SEC-011).
6. Model/configuration metadata is captured for evaluation comparisons (NFR-006).

## Follow-up decisions

- Per-workflow minimum capability declarations and validation method.
- Embedding model selection and indexing compatibility.
- Configuration schema and secret-loading mechanism.

## References

- [Product Requirements Document](../../requirements/product-requirements.md)
- [Software Requirements Specification](../../requirements/software-requirements.md)
