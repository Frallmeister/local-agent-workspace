# M1 application foundation verification

**Review date:** 2026-10-15 (Europe/Stockholm)  
**Issue:** [M1-04, #8](https://github.com/Frallmeister/local-agent-workspace/issues/8)  
**Application baseline:** `17e20463cee402aa6781c5315119c51a7fb931eb`  
**Scope:** M1 foundation only; this is not verification of the M2 MVP or full FR-001 assistant behavior.

## Environment and procedure

Reviewed README, AGENTS.md, dependency manifests/locks, CI workflows, tracked artifacts, the M1 roadmap criteria, and applicable architecture/security boundaries. Tested a clean `git archive HEAD` export in a temporary directory with initially absent `.venv` and `node_modules`, rather than reusing the working checkout's environment. Package caches and existing system tool installations were available; this was not a fresh operating-system installation.

Observed Windows tool versions: Python 3.14.7, uv 0.12.5, Node.js 24.22.0, npm 11.19.1. Python matches `.python-version` and `requires-python`; Node matches the frontend's 24.x requirement. The shell required adding the installed Node directory to PATH. uv used `--system-certs` and npm used `NODE_OPTIONS=--use-system-ca` to trust the machine's certificate store; certificate verification remained enabled. These were local environment adjustments, not application settings.

## Acceptance evidence

| M1 acceptance / requirement | Evidence and result |
| --- | --- |
| Reproducible dependency setup (NFR-002) | `uv sync --locked --group docs` (with the certificate flag above) and `npm ci` completed in the clean export. Both lockfiles are committed. |
| Documented local startup (NFR-002) | Started the README's Uvicorn command with reload and `npm run dev` from the clean export. Frontend HTML and proxied API returned HTTP 200. |
| Health displayed in UI (FR-001 foundation) | Live Vite `/api/health` returned `{"status":"ok"}`. The maintainer confirmed in this review that the browser displays “Backend connected” and “Health status: ok”, and displays an error after stopping FastAPI and clicking “Check again”. This browser observation is maintainer-reported; agent browser automation was unavailable. |
| Deterministic backend checks (NFR-005) | `uv run --no-sync pytest tests/backend`: 6 passed. Ruff lint and format checks passed. No model, database, or credentials required. |
| Invalid inputs / response contracts | Backend tests reject unsupported POST with HTTP 405 and invalid Pydantic health statuses; OpenAPI declares the response contract. The GET endpoint accepts no application input body. Frontend boundary tests reject malformed JSON, invalid shapes/statuses, and HTTP failures. This is the M1 health-only validation scope. |
| Deterministic frontend checks (NFR-005) | `npm run typecheck`, `npm run lint`, and `npm run build` passed. `npm run test:api`: 12 passed. `npm test`: 5 component tests passed, including pending, success, failure, retry, and cancellation behavior. |
| Loopback development defaults (T-07) | Observed both actual listeners at `127.0.0.1`, ports 8000 and 5173. No wildcard CORS added. When FastAPI stopped, the live proxy returned HTTP 500 as expected; temporary servers were then stopped. |
| Secret / artifact hygiene (SEC-008, T-11) | Reviewed tracked files; no credentials or personal documents identified. Targeted private-key/token/credential-URL pattern checks found no matches in the baseline. Environment, dependencies, build output, and documentation output are ignored; this review extends ignores to `.env.*`, retaining a safe `.env.example` exception. This is a scoped review, not proof that arbitrary secrets can never exist. |
| Documentation | `uv run --no-sync mkdocs build --strict` passed in the clean export. No Mermaid diagrams were changed. README documents both servers and all checks; AGENTS.md is updated with the implemented workflow. |
| Configuration template | Not applicable yet: the application consumes no environment settings. Current host/port/proxy settings are documented CLI arguments and Vite configuration. M1-04 explicitly limits templates to settings actually used; no unused template was added. |

## CI evidence

The following GitHub runs completed successfully at the application baseline above:

- [Frontend: type/lint/build/API/component checks](https://github.com/Frallmeister/local-agent-workspace/actions/runs/38644528587)
- [Backend tests and Ruff](https://github.com/Frallmeister/local-agent-workspace/actions/runs/38644528447)
- [Strict documentation build](https://github.com/Frallmeister/local-agent-workspace/actions/runs/38644528338)

These runs verify the merged application baseline, not the subsequent documentation/ignore-file changes in this review. Branch-ruleset enforcement was not independently inspected.

## Limitations and closeout

- Clean setup was verified on Windows with existing tools and caches; GitHub CI provides Linux check evidence. No clean macOS setup was tested.
- Browser success/error behavior was confirmed by the maintainer, not an automated real-browser end-to-end test. Component tests use jsdom and mocked fetch.
- Authentication, CSRF/session controls, tools, inference, persistence, and production deployment are outside M1. Loopback alone is not authorization; revisit T-07 before adding sensitive APIs.
- Backend tests emit an upstream Starlette deprecation warning for HTTPX. npm reports an unapproved esbuild install script, but the build succeeds with the platform binary installed. Neither warning failed verification; no dependency upgrade was introduced for this review.
- No runtime configuration template or new application feature is justified by this review.

M1's scoped acceptance evidence is complete with the maintainer's UI confirmation. The small documentation and ignore-file corrections should be reviewed and merged before closing M1-04 and the milestone; GitHub issue/milestone state has not been changed by this review.
