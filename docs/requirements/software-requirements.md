# Software Requirements Specification

**Product:** Local Agent Workspace  
**Status:** Accepted — initial requirements baseline  
**Source:** [Product Requirements Document](product-requirements.md)  
**Scope:** Initial product, delivered incrementally

## 1. Purpose and conventions

This specification defines verifiable functional, quality, and security requirements derived from the accepted PRD. It describes expected behavior without prescribing implementation technologies.

Prefixes **FR** (functional), **NFR** (quality/non-functional), and **SEC** (security) are project conventions, not standard-mandated identifiers. **Must** means required for the intended initial product release, not necessarily the first increment; **Should** means desirable and potentially deferrable. Increment boundaries will be defined in the roadmap.

## 2. Functional requirements

| ID | Requirement | Priority | PRD source |
| --- | --- | --- | --- |
| FR-001 | Users shall be able to submit requests and receive responses through a locally accessible web interface. | Must | UC-01–UC-06 |
| FR-002 | The system shall support configuring different compatible language models without modifying agent application logic. | Must | G3 |
| FR-003 | The system shall support locally hosted models without depending on external inference services. | Must | G2 |
| FR-004 | Agents shall be able to invoke registered tools with structured arguments and process tool results. | Must | UC-03 |
| FR-005 | The system shall support searching for and reading documents in configured local directories. | Must | UC-01 |
| FR-006 | The system shall support retrieval-augmented generation over indexed local documents. | Must | UC-01 |
| FR-007 | The system shall support discovering the schema of a configured PostgreSQL database and executing authorized read queries. | Must | UC-02 |
| FR-008 | The system shall support coordinating bounded tasks across specialized agents and combining their results. | Must | UC-03 |
| FR-009 | The system shall be able to expose defined tools through an MCP server and use tools from configured MCP servers. | Must | UC-04 |
| FR-010 | The system shall support proposing file creation or modification and obtaining user approval before execution. | Must | UC-05 |
| FR-011 | Users shall be able to inspect agent steps, tool invocations, failures, and execution status. | Must | UC-06 |
| FR-012 | Users shall be able to request cancellation of an active agent run. | Must | UC-06 |
| FR-013 | The system shall preserve execution state necessary to resume workflows awaiting user approval. | Must | UC-05 |
| FR-014 | The system shall provide configurable models, data sources, and available tools. | Must | G3 |
| FR-015 | The system should allow users to view and resume previous conversations. | Should | G1 |

## 3. Non-functional requirements

| ID | Requirement | Priority | PRD source |
| --- | --- | --- | --- |
| NFR-001 | Core application functionality shall operate on a single computer without commercial cloud infrastructure. | Must | G2 |
| NFR-002 | Installation and startup shall be possible through documented, reproducible procedures. | Must | G6 |
| NFR-003 | Model providers, document sources, and tools shall have documented integration contracts. | Must | G3 |
| NFR-004 | The system shall record structured information about agent runs, tool invocations, errors, and execution durations. | Must | G5 |
| NFR-005 | Automated verification of core deterministic functionality shall be possible without a running language model. | Must | G5 |
| NFR-006 | The system shall support repeatable evaluations using version-controlled test cases and configurations. | Must | G5 |
| NFR-007 | Agent runs shall have configurable limits on execution steps, tool calls, and elapsed time, enforced outside model instructions. | Must | G4 |
| NFR-008 | The system shall report failures so model, tool, and integration errors can be distinguished. | Must | G5 |
| NFR-009 | Changes to published API contracts should be detectable through automated checks. | Should | G6 |
| NFR-010 | The system should support reporting token usage and estimated inference costs when the provider supplies the needed information. | Should | G5 |

Performance targets will be established against a documented test environment and measured baseline rather than arbitrary response-time thresholds independent of hardware and model.

## 4. Security requirements

| ID | Requirement | Priority | PRD source |
| --- | --- | --- | --- |
| SEC-001 | Filesystem tools shall only access explicitly authorized directories and operations. | Must | G4, UC-05 |
| SEC-002 | File creation and modification shall require approval of the specific operation before execution. | Must | G4, UC-05 |
| SEC-003 | Permissions and execution limits shall be enforced by application controls, not solely through model instructions. | Must | G4 |
| SEC-004 | Retrieved documents, model-generated content, and external tool results shall be treated as untrusted inputs. | Must | G4 |
| SEC-005 | Path traversal and symbolic-link redirection shall not bypass configured filesystem authorization. | Must | G4, UC-05 |
| SEC-006 | Database query tools shall use a dedicated database identity with restricted permissions for permitted read operations. | Must | UC-02, G4 |
| SEC-007 | External model providers shall require explicit configuration and shall not activate as implicit fallbacks. | Must | G2 |
| SEC-008 | Secrets such as API keys and database credentials shall not be committed to version-controlled configuration files. | Must | G4, G6 |
| SEC-009 | MCP tools shall be subject to the same application authorization policies as internal tools. | Must | G4, UC-04 |
| SEC-010 | Approval shall be bound to the exact proposed operation, and shall not authorize a changed operation or be reusable without renewed authorization. | Must | G4, UC-05 |
| SEC-011 | Logs and traces shall exclude secrets and sensitive document content by default. | Must | G4, G5 |
| SEC-012 | Agents shall not have unrestricted host operating-system command execution in the initial application. | Must | G4 |

## 5. Verification and validation approach

Every **Must** requirement must be linked to verification evidence before the corresponding capability is considered complete. One test may cover several requirements. Agent answer quality requires representative evaluations in addition to deterministic tests.

| Requirement(s) | Verification method | Example evidence |
| --- | --- | --- |
| FR-001, FR-004 | End-to-end and integration tests | A request invokes an authorized tool and returns a visible result. |
| FR-002, FR-003 | Integration and system tests | A compatible model is swapped by configuration; local inference runs without external services. |
| FR-005, FR-006 | Integration and retrieval evaluation | Known passages are retrieved from controlled documents. |
| FR-007, SEC-006 | Database integration and negative tests | Allowed reads succeed; attempted writes using the application role fail. |
| FR-008 | Integration test | Bounded specialist-agent delegation produces a combined result. |
| FR-009, SEC-009 | MCP contract and authorization tests | Allowed tools succeed; unauthorized tools are denied. |
| FR-010, SEC-002, SEC-010 | Security integration tests | File changes are rejected without approval or after a change to the approved operation. |
| FR-012, FR-013 | State-transition and integration tests | Cancellation stops further work; pending approval survives restart. |
| NFR-005, NFR-006 | CI and reproducibility checks | Deterministic tests run without GPU; evaluations record dataset and configuration versions. |
| NFR-007 | Boundary tests | The agent terminates at configured limits. |
| SEC-001, SEC-005 | Adversarial filesystem tests | Traversal and symlink attacks cannot escape authorized directories. |
| SEC-007, SEC-008, SEC-011 | Configuration and security tests | No implicit external inference, committed secrets, or sensitive trace contents. |

Detailed acceptance thresholds and test-case IDs will be tracked alongside implementation and evaluation artifacts, linked to stable requirement IDs.

## 6. Open design and release questions

These are **not yet accepted decisions** and should be resolved in architecture, security design, or roadmap before affected features are implemented:

1. **Supported write formats:** Which file formats agents may create and modify in the first release (e.g., UTF-8 text rather than arbitrary binary files).
2. **Release boundaries:** Which Must requirements belong in the first minimal usable increment (MVP) versus the broader initial release.
3. **Agent architecture:** How multi-agent coordination is implemented, and what evidence justifies additional agents.
4. **Approval mechanics:** How proposed writes are identified, revalidated, recovered, and audited.
5. **MCP trust boundaries:** Which servers and capabilities may be enabled and how trust is established.

These decisions must preserve the PRD's security and user-control principles.

## 7. Related artifacts

- [Product Requirements Document](product-requirements.md)
- Architecture overview and ADRs (planned)
- Threat model and security policy (planned)
- Evaluation strategy (planned)
- Development roadmap (planned)
