# Local Agent Workspace

Local Agent Workspace is an open-source, self-hosted AI assistant designed to work with local language models, authorized documents, structured data, and extensible tools. The project prioritizes local control, explicit permissions, observability, and verifiable behavior.

> **Project status:** Early development. A minimal FastAPI backend provides a health endpoint and OpenAPI schema. A React frontend displays its health status. The assistant, models, tools, and persistence are not yet implemented.

## Prerequisites

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package and environment manager)
- Python supported by the project's `requires-python` setting in `pyproject.toml`. uv can download a suitable Python version if necessary.
- [Node.js](https://nodejs.org/) 24.x with its bundled npm for the frontend. Python dependencies continue to use uv.

On Windows, run the commands below from PowerShell. On macOS or Linux, use your preferred terminal.

## Get started

Clone the repository and enter the project directory:

```shell
git clone https://github.com/Frallmeister/local-agent-workspace.git
cd local-agent-workspace
```

Install the backend, development tools, and documentation dependencies:

```shell
uv sync --locked --group docs
```

### Run and test the backend

Start the backend on loopback:

```shell
uv run --no-sync uvicorn local_agent_workspace.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://127.0.0.1:8000/api/health** to receive HTTP 200 with `{"status":"ok"}`. This is a liveness check, not a readiness check for models or databases. The contract is declared with a Pydantic response model and published at **http://127.0.0.1:8000/openapi.json**; interactive API documentation is at `/docs`.

Run the deterministic backend checks:

```shell
uv run --no-sync pytest tests/backend
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
```

Tests use an in-process client and require no model, database, credentials, or running server. The installed package uses `src/local_agent_workspace/`; `main.py` assembles the API and `api/routes/health.py` owns the health contract. Future application logic should remain independent of HTTP routing (ADR-0002).

Authentication and authorization are not implemented in this foundation. Loopback binding is a development default, not an authorization control; sensitive APIs require the protections described in the threat model before introduction. This increment covers M1-01 ([issue #4](https://github.com/Frallmeister/local-agent-workspace/issues/4)): FR-001 (backend foundation only), NFR-002, NFR-003, NFR-005, and SEC-008.

### Run the frontend with the backend

Keep the backend running with the command above. In a second terminal, from the repository root:

```shell
cd frontend
npm ci
npm run dev
```

On Windows, use `npm.cmd` instead of `npm` if PowerShell blocks the npm script. Node.js must be on your PATH; reopen the terminal after installation if necessary.

Open **http://127.0.0.1:5173/**. The page checks backend health, displays `ok` when connected, and offers **Check again** to retry. To check the error state, stop the backend and click **Check again**. Checks time out after five seconds; pending checks display a loading state.

The browser calls the relative URL `/api/health`. Vite proxies `/api` to **http://127.0.0.1:8000** during development, so no backend CORS change is needed. Both servers bind to loopback. The typed API client in `frontend/src/api/health.ts` validates the JSON response at runtime: it must be an object with `status` equal to `"ok"`. Non-success HTTP responses, invalid JSON, invalid response shapes, network failures, and timeouts lead to the error state. The health endpoint reports application liveness only.

Verify the frontend compilation and bundle:

```shell
npm run build
npm run test:api
```

The build performs TypeScript checking and writes the bundle to ignored `frontend/dist/`. The API tests use Node's built-in test runner with mocked fetch responses to check validation, HTTP/network failures, timeout, and cancellation without a backend. Production serving and proxy configuration are outside M1-02; the development proxy is not included in the bundle. Commit `frontend/package-lock.json` when dependencies change and use `npm ci` for reproducible installation.

The **Frontend tests** GitHub Actions job runs these API tests on pull requests to `main`, pushes to `main`, and manual dispatch. After its first successful run, select **Frontend tests** as a required status check in the branch ruleset. The workflow has no path filters, so it reports a result for every pull request to `main`.

M1-02 ([issue #6](https://github.com/Frallmeister/local-agent-workspace/issues/6)) covers FR-001 (interface foundation), NFR-002, NFR-003, and SEC-008, under ADR-0002 and threats T-07/T-11. Frontend component tests, ESLint, and broader CI checks are planned in M1-03; complete M1 setup verification is planned in M1-04. No secrets or configuration template are needed for this health-only integration.

### Work with the documentation

Start the live documentation server on a separate port:

```shell
uv run --no-sync mkdocs serve --dev-addr 127.0.0.1:8001
```

Open **http://127.0.0.1:8001/** in your browser. Changes to Markdown files are reflected automatically while the server is running. Stop either server with `Ctrl+C`.

To build and validate the documentation:

```shell
uv run --no-sync mkdocs build --strict
```

The generated website is written to `site/`. **Use `mkdocs serve` to browse it locally** rather than opening `site/index.html` directly: MkDocs' default directory-style links expect a web server.

`uv sync --locked` uses the committed `uv.lock` file; contributors should commit lockfile updates when dependency definitions change. uv manages `.venv` automatically, so manually activating a virtual environment is unnecessary.

## Documentation map

The documentation covers:

- **Product and software requirements:** `docs/requirements/`
- **Architecture and accepted decisions:** `docs/architecture/` and `docs/architecture/adr/`
- **Security threat model:** `docs/security/`
- **Development roadmap:** `docs/project/development-roadmap.md`

The accepted project documents are the baseline for design and implementation. A design decision marked *Accepted* does **not** mean its functionality is implemented or verified.

## Development and contributions

Development is organized around small GitHub issues, feature branches, and pull requests. Please check the [development roadmap](docs/project/development-roadmap.md) for the planned implementation sequence and acceptance criteria.

For documentation-only changes, run `uv run --no-sync mkdocs build --strict` after synchronizing dependencies, and visually inspect changed Mermaid diagrams in `mkdocs serve` (a successful build does not guarantee browser-side Mermaid rendering).

Assistant examples will be added when those capabilities are implemented. Do not treat proposed architectural components as working features.

## License

License information will be added when the repository's licensing decision is finalized.
