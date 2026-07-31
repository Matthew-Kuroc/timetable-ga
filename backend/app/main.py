from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.datasets import router as datasets_router
from backend.app.api.batches import router as batches_router
from backend.app.api.ga import router as ga_router
from backend.app.api.imports import router as imports_router
from backend.app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(datasets_router)
    app.include_router(batches_router)
    app.include_router(imports_router)
    app.include_router(ga_router)

    frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
    if (frontend_dir / "index.html").exists():
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

        @app.get("/")
        def frontend_index() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
