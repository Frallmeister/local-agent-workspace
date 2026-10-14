# Local Agent Workspace

Local Agent Workspace is an open-source, self-hosted AI assistant designed to work with local language models, authorized documents, structured data, and extensible tools. The project prioritizes local control, explicit permissions, observability, and verifiable behavior.

> **Project status:** Early development. The requirements, architecture decisions, threat model, and development roadmap are documented, but the assistant application is not yet available to run. The instructions below are for working with the **documentation**, not for launching an AI assistant.

## Prerequisites

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package and environment manager)
- Python supported by the project's `requires-python` setting in `pyproject.toml`. uv can download a suitable Python version if necessary.

On Windows, run the commands below from PowerShell. On macOS or Linux, use your preferred terminal.

## Get started with the documentation

Clone the repository and enter the project directory:

```shell
git clone https://github.com/Frallmeister/local-agent-workspace.git
cd local-agent-workspace
```

Install the documentation dependencies into a project-managed virtual environment:

```shell
uv sync --locked --only-group docs
```

Start the live documentation server:

```shell
uv run --no-sync mkdocs serve
```

Open **http://127.0.0.1:8000/** in your browser. Changes to Markdown files are reflected automatically while the server is running. Stop the server with `Ctrl+C`.

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

Application setup, backend/frontend development commands, and runnable examples will be added when the corresponding capabilities are implemented. Do not treat proposed architectural components as working features.

## License

License information will be added when the repository's licensing decision is finalized.
