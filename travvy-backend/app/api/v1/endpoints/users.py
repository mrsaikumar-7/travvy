"""
User Management API Endpoints

This module handles user profile management, preferences,
and user-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import logging

from app.core.security import get_current_user
from app.services.user_service import UserService
from app.dependencies import get_user_service
from app.models.schemas import (
    UserProfile,
    UserPreferencesUpdate,
    UserProfileUpdate
)
from app.core.monitoring import monitor_endpoint

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserProfile)
@monitor_endpoint("get_user_profile")
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
) -> UserProfile:
    """Get current user profile."""
    try:
        user = await user_service.get_user_by_id(current_user["uid"])
        return user
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/me", response_model=UserProfile)
@monitor_endpoint("update_user_profile")
async def update_user_profile(
    updates: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
) -> UserProfile:
    """Update current user profile."""
    try:
        updated_user = await user_service.update_user_profile(
            user_id=current_user["uid"],
            updates=updates.dict(exclude_unset=True)
        )
        return updated_user
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.put("/me/preferences")
@monitor_endpoint("update_user_preferences")
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
) -> Dict[str, str]:
    """Update user travel preferences."""
    try:
        await user_service.update_user_preferences(
            user_id=current_user["uid"],
            preferences=preferences.dict()
        )
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.get("/me/stats")
@monitor_endpoint("get_user_stats")
async def get_user_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
) -> Dict[str, Any]:
    """Get user travel statistics."""
    try:
        stats = await user_service.get_user_statistics(current_user["uid"])
        return stats
    except Exception as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


@router.delete("/me")
@monitor_endpoint("delete_user_account")
async def delete_user_account(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
) -> Dict[str, str]:
    """Delete user account (soft delete)."""
    try:
        await user_service.delete_user_account(current_user["uid"])
        return {"message": "Account deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete user account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
