"""
FastAPI Dependencies

This module contains dependency functions for service classes.
"""

from app.services.trip_service import TripService
from app.services.user_service import UserService
from app.services.ai_service import AIService
from app.services.collaboration_service import CollaborationService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService


def get_trip_service() -> TripService:
    """Get TripService instance."""
    return TripService()


def get_user_service() -> UserService:
    """Get UserService instance."""
    return UserService()


def get_ai_service() -> AIService:
    """Get AIService instance."""
    return AIService()


def get_collaboration_service() -> CollaborationService:
    """Get CollaborationService instance."""
    return CollaborationService()


def get_notification_service() -> NotificationService:
    """Get NotificationService instance."""
    return NotificationService()


def get_analytics_service() -> AnalyticsService:
    """Get AnalyticsService instance."""
    return AnalyticsService()
