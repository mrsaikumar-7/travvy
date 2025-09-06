"""
Notification API Endpoints

This module handles notification management including
push notifications, email notifications, and preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from app.core.security import get_current_user
from app.services.notification_service import NotificationService
from app.models.schemas import NotificationPreferences
from app.core.monitoring import monitor_endpoint

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
@monitor_endpoint("get_notifications")
async def get_user_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user),
    notification_service: NotificationService = Depends()
) -> List[Dict[str, Any]]:
    """Get user notifications."""
    try:
        notifications = await notification_service.get_user_notifications(
            current_user["uid"]
        )
        return notifications
    except Exception as e:
        logger.error(f"Failed to get notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.put("/preferences")
@monitor_endpoint("update_notification_preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: Dict[str, Any] = Depends(get_current_user),
    notification_service: NotificationService = Depends()
) -> Dict[str, str]:
    """Update notification preferences."""
    try:
        await notification_service.update_preferences(
            user_id=current_user["uid"],
            preferences=preferences.dict()
        )
        return {"message": "Notification preferences updated"}
    except Exception as e:
        logger.error(f"Failed to update notification preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.post("/{notification_id}/mark-read")
@monitor_endpoint("mark_notification_read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    notification_service: NotificationService = Depends()
) -> Dict[str, str]:
    """Mark notification as read."""
    try:
        await notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user["uid"]
        )
        return {"message": "Notification marked as read"}
    except Exception as e:
        logger.error(f"Failed to mark notification read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )
