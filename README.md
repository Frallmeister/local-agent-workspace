# Local Agent Workspace

Local Agent Workspace is an open-source, self-hosted AI assistant designed to work with local language models, authorized documents, structured data, and extensible tools. The project prioritizes local control, explicit permissions, observability, and verifiable behavior.

> **Project status:** Early development. A minimal FastAPI backend provides a health endpoint and OpenAPI schema. The assistant, frontend, models, tools, and persistence are not yet implemented.

## Prerequisites

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package and environment manager)
- Python supported by the project's `requires-python` setting in `pyproject.toml`. uv can download a suitable Python version if necessary.

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

Frontend setup and assistant examples will be added when those capabilities are implemented. Do not treat proposed architectural components as working features.

## License

License information will be added when the repository's licensing decision is finalized.
