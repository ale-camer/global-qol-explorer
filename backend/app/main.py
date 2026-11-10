# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
from contextlib import asynccontextmanager
import logging

# --- Third-party ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# --- Project ---
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import init_bq_client, close_bq_client

# =============================================================================
# CONFIGURATION
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_bq_client()
    try:
        yield
    finally:
        close_bq_client()


app = FastAPI(
    title="Global Quality of Life API",
    description="An API to explore life quality indicators.",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Global Quality of Life API! Docs available at /docs"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
