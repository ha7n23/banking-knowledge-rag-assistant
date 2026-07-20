from pathlib import Path

from fastapi.staticfiles import StaticFiles

from banking_rag.api.frontend_routes import router as frontend_router
from fastapi import FastAPI

from banking_rag.api.routes import router
from banking_rag.core.config import APP_NAME

from fastapi.staticfiles import StaticFiles
from banking_rag.api.frontend_routes import router as frontend_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=APP_NAME,
        description=(
            "A Retrieval-Augmented Generation API for banking and fintech "
            "knowledge documents."
        ),
        version="0.1.0",
    )

    BASE_DIR = Path(__file__).resolve().parents[1]
    STATIC_DIR = BASE_DIR / "web" / "static"

    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )

    app.include_router(frontend_router)

    app.include_router(router)

    return app


app = create_app()