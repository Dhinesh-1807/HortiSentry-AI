import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import sys
from pathlib import Path

from app.core.config import settings, BASE_DIR
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.init_db import init_db
from app.api import health, crops, observations, expert, predict, ai_review, evidence_status, auth, notifications, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hortisentry")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing HortiSentry Backend Core...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    try:
        init_db()
        logger.info("Database & Seed Data initialization verified.")
    except Exception as e:
        logger.error(f"Error initializing database during startup: {e}")
    yield
    # Shutdown sequence
    logger.info("HortiSentry Backend Core shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "HortiSentry is an AI-powered horticultural disease observation platform that combines "
        "instant image analysis with structured expert escalation workflows to protect horticultural crop yields."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploaded media directory securely
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/api/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="api_uploads")

# Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please consult server logs."}
    )

# Include Routers
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(crops.router, prefix="/api")
app.include_router(observations.router, prefix="/api")
app.include_router(expert.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(ai_review.router, prefix="/api")
app.include_router(evidence_status.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/", include_in_schema=False)
def root():
    return {
        "title": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }
