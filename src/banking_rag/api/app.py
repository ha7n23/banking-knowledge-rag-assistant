from fastapi import FastAPI

from banking_rag.api.routes import router
from banking_rag.core.config import APP_NAME


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

    app.include_router(router)

    return app


app = create_app()