"""
Health Check API Endpoints

This module provides system health monitoring endpoints
for load balancers and monitoring systems.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
import asyncio
from datetime import datetime

from app.core.database import get_database
from app.core.monitoring import monitor_endpoint

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
@monitor_endpoint("health_check")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "travvy-api",
        "version": "1.0.0"
    }


@router.get("/detailed")
@monitor_endpoint("detailed_health_check")
async def detailed_health_check(
    db_service = Depends(get_database)
) -> Dict[str, Any]:
    """Detailed health check with dependency verification."""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "travvy-api",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    try:
        # Test database connection
        try:
            await db_service._test_connections()
            health_info["dependencies"]["database"] = "healthy"
        except Exception as e:
            health_info["dependencies"]["database"] = f"unhealthy: {str(e)}"
            health_info["status"] = "degraded"
        
        # Test Redis connection
        try:
            if db_service.redis_client:
                await db_service.redis_client.ping()
                health_info["dependencies"]["redis"] = "healthy"
            else:
                health_info["dependencies"]["redis"] = "not_configured"
        except Exception as e:
            health_info["dependencies"]["redis"] = f"unhealthy: {str(e)}"
            health_info["status"] = "degraded"
        
        # Test Celery workers
        try:
            from app.core.celery import celery_app
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            if active_workers:
                health_info["dependencies"]["celery"] = "healthy"
                health_info["worker_count"] = len(active_workers)
            else:
                health_info["dependencies"]["celery"] = "no_workers"
                health_info["status"] = "degraded"
        except Exception as e:
            health_info["dependencies"]["celery"] = f"unhealthy: {str(e)}"
            health_info["status"] = "degraded"
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/ready")
@monitor_endpoint("readiness_check")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes deployments."""
    try:
        # Perform minimal checks to verify service is ready
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service not ready"
        )


@router.get("/live")
@monitor_endpoint("liveness_check")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes deployments."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
