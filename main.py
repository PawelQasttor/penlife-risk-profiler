"""
PenLife Risk Profiler - Cloud Run Service
Main FastAPI application entry point
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from google.cloud import secretmanager

from app.api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fetch API key from Secret Manager on startup
def get_api_key() -> str:
    """Fetch API key from Google Secret Manager"""
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "penlife-associates")
        secret_name = f"projects/{project_id}/secrets/penlife-api-key/versions/latest"

        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": secret_name})
        api_key = response.payload.data.decode("UTF-8")
        logger.info("✅ API key loaded from Secret Manager")
        return api_key
    except Exception as e:
        logger.error(f"❌ Failed to load API key from Secret Manager: {e}")
        # Fallback for local development
        return os.environ.get("API_KEY", "")

# Load API key at startup
EXPECTED_API_KEY = get_api_key()

# Create FastAPI app
app = FastAPI(
    title="PenLife Risk Profiler API",
    description="Automated PDF processing service for PenLife risk questionnaires",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication Middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Verify API key for protected endpoints"""
    # Public endpoints (no auth required)
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]

    if request.url.path in public_paths:
        return await call_next(request)

    # Protected endpoints require X-API-Key header
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        logger.warning(f"❌ Missing API key for {request.url.path}")
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "message": "Missing X-API-Key header"
            }
        )

    if api_key != EXPECTED_API_KEY:
        logger.warning(f"❌ Invalid API key for {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Forbidden",
                "message": "Invalid API key"
            }
        )

    # API key is valid, proceed
    return await call_next(request)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response

# Include API routes
app.include_router(routes.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "penlife-risk-profiler"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "PenLife Risk Profiler API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred processing your request"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
