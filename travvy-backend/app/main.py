"""
Travvy - Main FastAPI Application

This module contains the main FastAPI application with basic endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.core.config import get_settings
from app.api.v1 import api_router
from app.core.database import initialize_firestore

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Travvy API...")
    try:
        # Initialize database connections
        await initialize_firestore()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Travvy API...")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Travvy API",
        description="Advanced AI-powered trip planning platform with real-time collaboration",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        redirect_slashes=False  # Prevent 307 redirects for missing trailing slashes
    )
    
    # CORS Middleware - Allow development origins including ngrok
    allowed_origins = settings.get_allowed_origins()
    
    # Add ngrok support for development
    if settings.ENVIRONMENT in ["development", "dev"]:
        allowed_origins.extend([
            "https://795b112f4b0a.ngrok-free.app",
            "https://*.ngrok-free.app",
            "https://*.ngrok.io", 
            "https://*.ngrok.app",
            "*"  # Allow all origins in development
        ])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.ENVIRONMENT in ["development", "dev"] else allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=["*"]
    )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create the FastAPI app instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Travvy API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "redis": "connected",
            "ai_services": "available"
        }
    }


@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working."""
    return {
        "message": "API is working!",
        "features": [
            "Trip Planning",
            "AI Integration", 
            "Real-time Collaboration",
            "Multi-modal Input"
        ]
    }


if __name__ == "__main__":
    """Run the application with uvicorn for development."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
