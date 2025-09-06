"""
API v1 Module

This module contains all v1 API routes and endpoints organized by domain.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    trips,
    ai, 
    collaboration,
    users,
    notifications,
    analytics,
    health
)

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["authentication"]
)

api_router.include_router(
    trips.router, 
    prefix="/trips", 
    tags=["trips"]
)

api_router.include_router(
    ai.router, 
    prefix="/ai", 
    tags=["ai"]
)

api_router.include_router(
    collaboration.router, 
    prefix="/collaboration", 
    tags=["collaboration"]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"]
)

api_router.include_router(
    notifications.router, 
    prefix="/notifications", 
    tags=["notifications"]
)

api_router.include_router(
    analytics.router, 
    prefix="/analytics", 
    tags=["analytics"]
)

api_router.include_router(
    health.router, 
    prefix="/health", 
    tags=["health"]
)
