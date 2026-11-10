# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
from contextlib import asynccontextmanager

# --- Third-party ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Project ---
from app.api.v1.api import api_router
from app.db.session import init_bq_client, close_bq_client

# =============================================================================
# CONFIGURATION
# =============================================================================
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
origins = [
    "http://localhost:5173",
    "http://1.bp.blogspot.com",
    "https://storage.googleapis.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Global Quality of Life API! Docs available at /docs"}
