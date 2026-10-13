# Initial Threat Model

**Product:** Local Agent Workspace  
**Status:** Accepted — initial design-time threat baseline  
**Scope:** Initial single-user, local-first release  
**Basis:** [Product Requirements](../requirements/product-requirements.md), [Software Requirements](../requirements/software-requirements.md), [Architecture Overview](../architecture/architecture-overview.md), and ADR-0003 (central tool authorization)

## 1. Purpose and method

Identify realistic abuse cases against a local AI assistant that reads personal files, queries PostgreSQL, and invokes internal or MCP tools. This is a **design-time assessment**, not evidence that mitigations have been implemented or tested. Apply STRIDE as a checklist (spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege), with additional focus on LLM prompt injection and tool misuse. Reassess as new capabilities or trust boundaries are introduced.

### Assumptions and limits

- One local user; the web API is intended for loopback access, not public internet exposure. Other processes and websites on the machine are **not** assumed trustworthy.
- Local inference is the default. Remote model providers are optional and explicitly configured.
- Only authorized filesystem roots are in scope. PostgreSQL access for agent-generated queries is read-only with a restricted database identity.
- File mutations require explicit, operation-specific approval; unrestricted shell execution is excluded.
- MCP servers and retrieved documents may be malicious, even when hosted locally.
- The threat model does not claim to defend against a fully compromised operating system or a malicious user with administrator privileges on the host.

## 2. Assets and security objectives

| Asset | Objective |
| --- | --- |
| Local documents and file metadata | Prevent unauthorized disclosure, modification, and deletion |
| PostgreSQL data and credentials | Enforce least-privilege reads; prevent writes and credential exposure |
| Tool registry, permissions, and approvals | Prevent unapproved operations and privilege escalation |
| Model prompts, retrieved context, and conversation/run state | Protect private content; prevent untrusted instructions from acquiring authority |
| MCP configuration and remote tool responses | Restrict capabilities; limit untrusted integration behavior |
| Audit events, traces, and evaluation results | Preserve meaningful evidence without leaking sensitive content |
| Local application availability | Bound resource usage and allow cancellation and recovery |

## 3. Trust boundaries and entry points

| Boundary / entry point | Untrusted input | Enforcement location |
| --- | --- | --- |
| Browser / other local clients → FastAPI | Requests, approval decisions, identifiers | API validation, local access protections, application authorization |
| LLM / agent state → tool gateway | Generated tool names, arguments and plans | Typed schemas, policy checks, execution budgets |
| Documents / SQL results → model context | Retrieved content containing attacker instructions | Context isolation and tool authorization independent of content |
| Backend → filesystem | Paths, file contents, mutations | Scoped filesystem adapter and operation-specific authorization |
| Backend → PostgreSQL | Generated SQL, identifiers | Read-only database role, query safeguards and resource limits |
| Backend → MCP server | Tool descriptions, inputs and outputs | Explicitly approved servers/tools, controlled invocation |
| Backend → remote model provider (optional) | Prompt/context payloads | Explicit opt-in, egress controls and sensitive-data policy |
| Application → logs / persistent state | Tokens, prompts, tool inputs/outputs | Data minimization, redaction and access restrictions |

Localhost is a network location, **not** an authentication or authorization mechanism by itself. Browser-originated requests and requests from other local processes require separate consideration.

## 4. Prioritized threat scenarios

Qualitative priority is based on potential impact and plausible exposure in the proposed product, **not a quantified likelihood assessment**. Risk remains provisional until mitigations and threat assumptions are verified.

| ID | STRIDE / threat scenario | Priority | Mitigation direction | Related requirements |
| --- | --- | --- | --- | --- |
| T-01 | **Elevation of privilege / prompt injection:** A document or MCP response instructs the agent to bypass policies or disclose information. | High | Treat retrieved content as untrusted data; enforce tool permissions outside the model; test adversarial fixtures. | SEC-003, SEC-004, SEC-009 |
| T-02 | **Tampering:** Path traversal, symlink replacement, or race conditions cause reads/writes outside authorized roots. | High | Canonicalization alone is insufficient; use race-aware filesystem access, confined roots, and negative tests. | SEC-001, SEC-005 |
| T-03 | **Tampering / spoofing:** A forged, replayed, stale, or altered approval authorizes an unintended file write. | High | Persist exact operation identity and preconditions, tie authorization to that operation, expire/consume approvals, revalidate before execution. | SEC-002, SEC-010, FR-013 |
| T-04 | **Elevation of privilege:** Generated SQL or a tool bypass writes to the database or accesses prohibited relations. | High | Dedicated least-privilege database role, constrained query surface, timeouts and adversarial database tests. | SEC-006, FR-007 |
| T-05 | **Elevation of privilege / information disclosure:** Untrusted MCP server exposes extra tools, returns malicious instructions or accesses host resources outside approved scope. | High | Explicit server/tool allowlists; policy-gated calls; limit child-process privileges and credentials; do not trust MCP metadata. | SEC-004, SEC-009 |
| T-06 | **Information disclosure:** Private document excerpts, credentials or tool results leak to external inference endpoints or telemetry. | High | Local provider default; explicit external opt-in; restricted data egress; sanitized logs/traces; secret handling. | SEC-007, SEC-008, SEC-011 |
| T-07 | **Spoofing / request forgery:** A malicious website or local process targets a localhost API and submits actions or approvals. | High | Bind to loopback, verify Origin/CSRF where applicable, protect sensitive endpoints with suitable session/authentication controls; never assume CORS is sufficient. | SEC-002, SEC-003, SEC-010 |
| T-08 | **Denial of service:** Agent loops, model calls, expensive SQL or oversized ingestion exhaust CPU, GPU, storage or memory. | Medium | Enforced step/tool/time budgets, query timeouts, input limits, bounded concurrency, cancellation. | NFR-007, FR-012 |
| T-09 | **Tampering / repudiation:** Checkpoint replay or a failed retry repeats a side effect, while incomplete logs obscure what happened. | High | Idempotency/operation IDs, atomic state transitions where feasible, durable approval records and sanitized audit events. | FR-013, SEC-010, NFR-004 |
| T-10 | **Information disclosure / tampering:** Poisoned or misleading retrieved material causes ungrounded answers or poisoned index results. | Medium | Retain provenance, separate retrieval from generation, evaluate retrieval against known sources; do not treat generated answers as authoritative. | FR-006, NFR-006, SEC-004 |
| T-11 | **Information disclosure:** Sensitive files, secrets or local runtime state accidentally enter the public repository or test fixtures. | Medium | Ignore user data and local secrets, example-only configuration, secret scanning, synthetic fixtures. | SEC-008, NFR-002 |

## 5. Security controls and verification evidence

| Control / verification theme | Initial check or test | Threat coverage |
| --- | --- | --- |
| Tool authorization | Invoke forbidden internal and MCP tools with valid and malformed arguments; all must fail closed. | T-01, T-05 |
| Filesystem confinement | Attempt `../`, absolute paths, symlink swaps and other escape paths in read/write tools. | T-02 |
| Write approval integrity | Modify file contents or operation arguments after approval; replay or expire an approval; verify no unintended write. | T-03, T-09 |
| SQL least privilege | Attempt INSERT/UPDATE/DELETE/DDL and forbidden table access as the actual application database role. | T-04 |
| Prompt-injection resistance | Place malicious instructions in controlled test documents/tool outputs; verify permissions remain enforced. | T-01, T-05, T-10 |
| Local API boundary | Simulate cross-origin browser requests and unauthorized local clients against sensitive endpoints. | T-07 |
| Data egress / logging | Inspect requests to configured providers and resulting traces; ensure no implicit egress or default sensitive payload capture. | T-06, T-11 |
| Resource limits / replay | Exhaust configured run limits; cancel runs; restart during pending approval or execution. | T-08, T-09 |

A security requirement is **not verified** merely because an agent refuses a malicious prompt. Tests must exercise the enforcing code or underlying platform permission.

## 6. Decisions and residual risks to revisit

1. **Local API protection:** Select a concrete approach appropriate for a single-user browser UI, including CSRF/origin controls and defenses against unwanted local clients.
2. **Safe write implementation:** Decide supported writable formats and how operation binding, atomicity, symlink races and idempotency are addressed.
3. **MCP isolation:** Establish constraints for local MCP processes and handling of any future remotely hosted servers.
4. **Persistent state and privacy:** Define sensitive-data retention, cleanup, backups and checkpoint consistency.
5. **Availability limits:** Choose realistic resource ceilings for the target development hardware and validate them by measurement.
6. **Third-party supply chain:** Define dependency review, pinning, vulnerability checks and update procedures before distribution.

These are open design and verification tasks, not accepted mitigations. They should become tracked work items when their corresponding capability is implemented.

## 7. Review triggers

Review this threat model when introducing a new tool capability, external provider, writable format, MCP server transport, exposure beyond localhost, persistence mechanism, or authentication model; and after meaningful security incidents or findings.

## 8. References within the project

- [Product Requirements Document](../requirements/product-requirements.md)
- [Software Requirements Specification](../requirements/software-requirements.md)
- [Architecture Overview](../architecture/architecture-overview.md)
- [ADR-0003: Centralize Tool Authorization](../architecture/adr/0003-centralize-tool-authorization.md)
