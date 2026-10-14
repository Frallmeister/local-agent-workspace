# Local Agent Workspace

Local Agent Workspace is an open-source, self-hosted AI assistant for interacting with local documents, structured data, and extensible tools.

The project is in **early implementation**. A minimal FastAPI backend exposes `GET /api/health` and its OpenAPI contract. See the [repository README](https://github.com/Frallmeister/local-agent-workspace#run-and-test-the-backend) for installation, startup, and test commands. The assistant and frontend are not yet implemented; the documents below describe the broader intended capabilities.

## Project definition

- [Product requirements](requirements/product-requirements.md)
- [Software requirements](requirements/software-requirements.md)
- [Development roadmap](project/development-roadmap.md)
- [Architecture overview](architecture/architecture-overview.md)
- [Architecture decision records](architecture/adr/0001-use-langgraph-for-agent-orchestration.md)
- [Initial threat model](security/threat-model.md)

## Development principles

The application is designed to be local-first, modular, secure by default, and verifiable. Refer to the accepted requirements and architecture decision records for authoritative project decisions.
