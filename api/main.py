"""FastAPI application — main entrypoint for ArgosArt API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from core.config import get_settings
from core.logging import logger
from storage.database import close_db, init_db

from .routes import router
from .oauth import router as oauth_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(f"Starting {settings.project_name} API v{settings.project_version} ({settings.env})")

    await init_db()

    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)
    Path("./data/logs").mkdir(parents=True, exist_ok=True)

    logger.info(
        f"🎨 {settings.project_name} ready — {settings.api_host}:{settings.api_port} | "
        f"embedding: {settings.text_embedding_model} | "
        f"storage: {settings.storage_backend}"
    )

    try:
        from embeddings.vector_store import VectorStore
        vs = VectorStore()
        await vs.initialize()
        logger.info("Vector store initialized — Qdrant connected")
    except Exception as e:
        logger.warning(f"Vector store unavailable: {e}")

    yield

    logger.info(f"Shutting down {settings.project_name} API")
    await close_db()


app = FastAPI(
    title="ArgosArt RAG API",
    description="""🎨 Modular RAG system for creative portfolio ingestion,
    art collaboration semantic search, and encrypted archival storage.

    Built for the he.Art creative partnership.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(oauth_router, prefix="/api/auth")


@app.get("/", response_class=HTMLResponse)
async def serve_spa():
    spa_path = Path(__file__).resolve().parent.parent / "ui" / "spa.html"
    if spa_path.exists():
        return HTMLResponse(content=spa_path.read_text())
    return HTMLResponse(content="<h1>🎨 ArgosArt API</h1><p>SPA not found. Visit /docs for API.</p>")


@app.get("/api", tags=["System"])
async def root():
    return {
        "name": "ArgosArt",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }
