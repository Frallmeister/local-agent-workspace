# Development Roadmap

**Product:** Local Agent Workspace  
**Status:** Accepted — initial development roadmap  
**Scope:** Incremental implementation following the initial product definition (M0)  
**Sources:** [PRD](../requirements/product-requirements.md), [SRS](../requirements/software-requirements.md), [Architecture Overview](../architecture/architecture-overview.md), [Threat Model](../security/threat-model.md), and accepted [ADRs](../architecture/adr/)

## 1. Purpose and delivery principles

This roadmap defines **delivery order and acceptance evidence**, not a calendar commitment. The SRS describes the intended initial product; a requirement marked *Must* need not be delivered in the first increment. Every milestone should produce a coherent, locally demonstrable capability and be implemented through scoped GitHub issues and reviewable pull requests.

- **Local-first:** No paid API, cloud platform, or GPU is required for automated CI checks; Ollama integration is tested separately on a suitable local machine.
- **Security from the first feature:** Authorization, bounded execution, secret hygiene, and safe logging are implemented alongside the corresponding capability, not postponed until a security milestone.
- **Deterministic checks first:** Mocked model responses and controlled fixtures verify orchestration and tools. Real-model evaluations are separate and explicitly identified as potentially nondeterministic.
- **Simple architecture:** Maintain a modular monolith; introduce additional agents, storage, or integrations only when required.
- **Evidence over claims:** A feature is *implemented* when code exists and *verified* only when its acceptance checks have been executed with recorded results.

## 2. Release boundaries

**MVP (after M2):** A locally accessible web assistant running one bounded agent against a configured local model, able to invoke at least one **read-only, authorized** workspace tool. The UI shows the response and a minimal run/tool status. The MVP does **not** yet claim RAG, SQL, MCP, file modification, durable approvals, or multi-agent support.

**Initial product v1.0 (after M7):** The broader set of *Must* capabilities in the accepted SRS, including document retrieval and RAG, PostgreSQL reads, bounded multi-agent coordination, MCP client/server integration, approved file writes, persistence needed for approval recovery, cancellation, observability, and evaluation. The *Should* items (FR-015, NFR-009, NFR-010) may be deferred with an explicit record.

The first supported writable formats are **UTF-8 plain-text files**, including Markdown and JSON as text. Binary document editing (PDF, DOCX, etc.) is excluded from v1.0 unless a subsequent decision explicitly changes the scope. This release-scope decision refines the SRS without changing its stated requirements; implementation details remain subject to security review.

## 3. Milestones

### M0 — Project definition (documentation baseline)

**Deliverables:** Accepted PRD, SRS, Architecture Overview, ADR-0001–0004, initial Threat Model, this roadmap, and one reviewable documentation PR.

**Acceptance:** Documents are internally consistent; key security boundaries and remaining design questions are recorded; file links and diagrams render; no unimplemented capability is described as implemented. Squash merge to `main` only after review.

### M1 — Application foundation

**Deliverables:** Python package and FastAPI health endpoint; React/TypeScript/Vite shell; typed frontend–backend contract; dependency locking; configuration template; pytest, lint/type checks, frontend checks; GitHub Actions; MkDocs setup; development instructions (`AGENTS.md`).

**Acceptance:** A contributor can follow documented commands to start frontend and backend, see a health response in the UI, and run deterministic checks locally and in CI without model, database, or secrets. API rejects invalid inputs. Defaults bind application services to loopback; no credentials or personal files are committed.

**Requirements:** FR-001 (interface foundation), NFR-002, NFR-005, SEC-008.  
**Threats:** T-07, T-11.

### M2 — Single-agent core and secure read tool (**MVP**)

**Deliverables:** LangGraph single-agent loop, configured local model integration, model-provider capability checks, bounded run execution, Pydantic tool schemas, central tool gateway, restricted file listing/reading, minimal run/tool activity view; deterministic mock-provider path.

**Acceptance:** A controlled task reaches an allowed read tool and returns a result; unauthorized paths/tools fail closed; configured step/tool/time limits stop execution; CI passes without Ollama; a separately documented local Ollama smoke test records its observed result. External model calls never activate implicitly. MVP demonstration succeeds on authorized synthetic fixtures.

**Requirements:** FR-001–005 (FR-005 limited to local listing/reading), FR-011 (minimal), FR-014 (model/tools), NFR-003–005, NFR-007–008, SEC-001, SEC-003–005, SEC-007–008, SEC-011–012.  
**Threats:** T-01, T-02, T-06–08, T-11.

### M3 — Structured data and document retrieval

**Deliverables:** PostgreSQL with migrations and seeded synthetic tables, dedicated read-only query identity; local document ingestion and indexing, embeddings and pgvector retrieval; source references; controlled evaluation fixtures for SQL access and retrieval.

**Acceptance:** Known questions retrieve expected source passages; generated or mocked SQL accesses approved data but cannot mutate tables under the actual application role; retrieval and generation failures can be distinguished; reindexing produces traceable document provenance; deterministic integration tests run against test services.

**Requirements:** FR-005–007, NFR-006, SEC-004, SEC-006.  
**Threats:** T-04, T-10, T-11.

### M4 — Stateful orchestration and agent delegation

**Deliverables:** Specialist agent flows for documents, SQL and workspace; bounded routing/delegation; run-state transitions, checkpoint design and persistence where needed; user cancellation and richer execution status.

**Acceptance:** An integration scenario demonstrates appropriate delegation and combined results; step/tool/time budgets remain enforced across agents; cancellation prevents further tool dispatch; restart and failure scenarios do not cause unauthorized side effects; agent graph behavior can be tested with deterministic model stubs.

**Requirements:** FR-008, FR-011–012, NFR-004, NFR-007–008.  
**Threats:** T-01, T-08–09.

### M5 — Approved workspace mutations

**Deliverables:** Proposal/review/approve-or-reject workflow for UTF-8 file creation and modification; versioned operation identity and preconditions; backend policy enforcement and auditable result; persisted pending approvals and resumable execution.

**Acceptance:** An unapproved, rejected, changed, expired, replayed or out-of-scope operation cannot write; an approved unchanged proposal writes exactly as displayed; symlink/path and concurrent-change adversarial tests pass; restart/retry does not duplicate the side effect; user can inspect resulting status. The approval UI is not a security boundary.

**Requirements:** FR-010, FR-013, SEC-001–005, SEC-010.  
**Threats:** T-02–03, T-07, T-09.

### M6 — MCP integration

**Deliverables:** A minimal MCP server exposing explicitly scoped workspace tools and an MCP client connecting to an explicitly configured server through the existing tool gateway; server/tool allowlisting and error handling.

**Acceptance:** Tool contracts work across MCP client/server; unconfigured servers and forbidden capabilities are unavailable; malformed or malicious metadata and responses cannot bypass authorization; launched local MCP processes have documented permissions and resource exposure. No cloud document connector is required for v1.0.

**Requirements:** FR-009, SEC-003–004, SEC-009, NFR-003.  
**Threats:** T-01, T-05–06, T-08.

### M7 — Evaluation, hardening and v1.0 release

**Deliverables:** Versioned golden datasets and negative/security fixtures; repeatable evaluation runner and baseline results; end-to-end checks across UI/API/tools; structured traces with redaction tests; dependency/security checks; installation and troubleshooting docs; release checklist and version tag.

**Acceptance:** Every *Must* SRS requirement has linked verification evidence or an explicitly approved scope change; regression and adversarial suites run with documented results; local first-run procedure works on a clean environment; limitations, residual risks, evaluation conditions and compatible model capabilities are documented. Validate that the user-facing application meets its stated local-assistant use cases on representative synthetic data.

**Requirements:** All outstanding *Must* items, especially NFR-004–006, SEC-011; assess *Should* items separately.  
**Threats:** T-01–T-11, plus any newly discovered scenarios.

## 4. Cross-cutting Definition of Done

For each issue or pull request introducing or changing behavior:

1. **Scope:** Link the relevant SRS IDs and, where relevant, threat IDs and accepted ADRs. State what is out of scope.
2. **Design:** Respect accepted architecture and policy boundaries; record a new ADR only for a consequential architectural change.
3. **Implementation:** Include typed contracts, explicit errors, bounded resources, and least-privilege defaults as applicable.
4. **Verification:** Add appropriate positive and negative tests, execute applicable checks, and report results honestly. If a check cannot run locally, say so; CI status does not substitute for unrun hardware-dependent checks.
5. **Security and privacy:** Review new inputs, data flows, side effects, logs, secrets and threat-model triggers. Never treat model refusal alone as security enforcement.
6. **Documentation:** Update user/developer docs, examples and configuration when external behavior or setup changes.
7. **Review:** Complete PR review and required CI checks before squash merging. Avoid mixing unrelated tasks in one PR.

For documentation-only issues, only the applicable items above are required; no dummy test is necessary.

## 5. Suggested GitHub work management

- **Milestones:** M1–M7 after closing M0; use GitHub milestones for deliverable tracking rather than fixed dates.
- **Issues:** Small work items with goal, relevant requirement IDs, acceptance criteria, dependencies and verification plan. Start with one vertical slice, not separate disconnected frontend/backend skeletons.
- **Branches:** A feature branch per cohesive change, following the repository's naming convention. Squash merge preserves the reviewed PR as the long-lived change record.
- **PR template (later):** Summary, requirement links, verification results, security impact, documentation changes and unresolved limitations.
- **Traceability:** SRS ID → issue/PR → test/evaluation evidence. Do not create a heavy requirements database for this project.

## 6. Explicit future decisions and non-goals

Before implementing the affected features, settle the exact local API protection model; filesystem write atomicity and idempotency; checkpoint backend; MCP child-process containment; data retention; model capability policy; and objective evaluation baselines. These are **design tasks**, not implied completed controls.

Cloud platforms, Terraform, Kubernetes, unrestricted shell execution, scheduled background automation, and cloud document storage integrations remain outside the initial release. No architecture decision requires those capabilities.

## 7. M0 completion checklist

- [ ] PRD, SRS, architecture overview, four ADRs and threat model are present and mutually consistent.
- [ ] This roadmap has been reviewed and accepted.
- [ ] Fix stale references to ADR status/numbers and outdated document links before merge.
- [ ] Review Markdown navigation and Mermaid diagrams when MkDocs becomes available; validate links in the meantime.
- [ ] Open a PR from `docs/project-definition` to `main`; review the complete M0 changeset.
- [ ] Squash merge after review; close M0 and create the first implementation issue.

**No roadmap milestone is claimed as implemented or verified by this document.**
