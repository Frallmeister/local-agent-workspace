# ADR-0003: Centralize Tool Authorization and Policy Enforcement

- **Status:** Accepted
- **Date:** 2026-10-14
- **Decision owners:** Project maintainers
- **Related requirements:** FR-004, FR-009–FR-013, SEC-001–SEC-006, SEC-009–SEC-012
- **Related architecture:** [Architecture Overview](../architecture-overview.md)

## Context

Language models select and construct tool calls using probabilistic behavior. Instructions, retrieved documents, and MCP tool descriptions cannot safely act as an authorization mechanism. The application needs a consistent trust boundary for filesystem, database, and MCP capabilities. A local single-user deployment still needs to protect against prompt injection, unexpected tool arguments, path traversal, and accidental changes.

## Decision

All agent-initiated operations pass through a **backend-owned tool execution boundary** that validates arguments and enforces authorization before dispatching to any local or MCP tool.

- Default-deny capabilities: expose only explicitly registered and enabled tools, scoped to the running task and configured resources.
- Represent tool inputs and results using typed contracts. Validate inputs before policy evaluation and check operation-specific preconditions at execution time.
- Treat document text, MCP responses, and LLM output as untrusted data; they must not grant privileges or alter configured policy.
- Route state-changing file operations through a **proposal → user review → operation-specific approval → revalidation → execution** workflow. An approval authorizes exactly the reviewed operation, not a class of future actions. Preserve sufficient evidence for audit and replay protection.
- Enforce bounded run budgets, cancellation checks, and tool-level timeouts in backend execution logic, not exclusively inside graph prompts or state.
- Apply equivalent authorization to MCP tools; registering an MCP server does not implicitly authorize all its capabilities.
- For PostgreSQL read queries, use a restricted database role and database-enforced permissions as defense in depth. Application checks alone are insufficient.
- Prevent authorization bypass through alternate code paths by keeping tool execution entry points internal and testing all available routes.
- Exclude unrestricted shell execution from the initial product.

**Important:** This ADR establishes the enforcement boundary, not the complete approval-token, filesystem race-safety, or MCP trust protocol. Those details are specified and tested before enabling write-capable tools. A UI confirmation alone is not sufficient security enforcement.

## Considered alternatives

| Alternative | Trade-off |
| --- | --- |
| **Prompt instructions and agent-level guardrails** | Easy to implement, but can be bypassed by model errors or prompt injection; not a security boundary. |
| **Authorization independently embedded in each tool** | May provide localized checks but invites inconsistent rules and bypasses without a shared entry point. |
| **Central gateway with defense in depth (selected)** | Auditable, consistent policy path; requires careful routing and verification that tools cannot be invoked outside it. |

## Consequences

- A policy decision is distinct from the model's requested tool action and from the tool's actual side effect.
- Authorization decisions and approval outcomes require structured, privacy-conscious audit records.
- Durable approvals require explicit replay and time-of-check/time-of-use handling. For writes, implement safe file operations with operation binding and revalidation; don't treat a pathname check alone as adequate.
- MCP integrations are not a privileged shortcut. Tool discovery and trust configuration require explicit control.
- Security tests must include denied operations, path traversal, symlinks, prompt-injection attempts, changed proposals, and repeated approvals.

## Verification

1. Requests without a registered capability fail before tool execution (SEC-001, SEC-003, SEC-009).
2. File writes without exact approval, with altered content/target, or with replayed approval are denied (SEC-002, SEC-010).
3. Traversal and symlink attempts cannot escape granted filesystem bounds (SEC-005).
4. Read-only database credentials cannot modify protected tables even if the model requests a write (SEC-006).
5. Untrusted document and MCP content cannot change effective tool permissions (SEC-004, SEC-009).
6. Tool auditing omits secrets and sensitive document content by default (SEC-011).

## Follow-up designs

- Operation identity and approval persistence; transactional execution and recovery.
- Filesystem containment and race-safe writes on supported operating systems.
- MCP server allowlisting, transport, and consent UX.
- Threat model and security test fixtures.

## References

- [Product Requirements Document](../../requirements/product-requirements.md)
- [Software Requirements Specification](../../requirements/software-requirements.md)
