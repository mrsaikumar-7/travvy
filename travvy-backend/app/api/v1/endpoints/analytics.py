"""
Analytics API Endpoints

This module provides analytics and insights about user behavior,
trip patterns, and system performance.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
import logging

from app.core.security import get_current_user, require_permission, Permissions
from app.services.analytics_service import AnalyticsService
from app.dependencies import get_analytics_service
from app.core.monitoring import monitor_endpoint

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/user")
@monitor_endpoint("get_user_analytics")
async def get_user_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service),
    period: str = Query("30d", pattern="^(7d|30d|90d|1y)$")
) -> Dict[str, Any]:
    """Get user-specific analytics."""
    try:
        analytics = await analytics_service.get_user_analytics(
            user_id=current_user["uid"],
            period=period
        )
        return analytics
    except Exception as e:
        logger.error(f"Failed to get user analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user analytics"
        )


@router.get("/system")
@monitor_endpoint("get_system_analytics")
# @require_permission(Permissions.ADMIN_SYSTEM)  # TODO: Fix permission system
async def get_system_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service),
    period: str = Query("7d")
) -> Dict[str, Any]:
    """Get system-wide analytics (admin only)."""
    try:
        analytics = await analytics_service.get_system_analytics(period)
        return analytics
    except Exception as e:
        logger.error(f"Failed to get system analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system analytics"
        )
