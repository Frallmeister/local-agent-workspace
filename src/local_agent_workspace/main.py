"""ASGI application entry point."""

from fastapi import FastAPI

from local_agent_workspace.api.routes.health import router as health_router

app = FastAPI(title="Local Agent Workspace", version="0.1.0")
app.include_router(health_router)
