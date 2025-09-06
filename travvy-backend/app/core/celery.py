"""
Celery Configuration for Background Task Processing

This module configures Celery for handling AI processing, notifications,
trip optimization, and other background tasks.
"""

from celery import Celery
from celery.schedules import crontab
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def create_celery_app() -> Celery:
    """
    Create and configure Celery application.
    
    Returns:
        Celery: Configured Celery application instance
    """
    celery_app = Celery(
        "ai_trip_planner",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            "app.tasks.ai_tasks",
            "app.tasks.trip_tasks", 
            "app.tasks.notification_tasks",
            "app.tasks.analytics_tasks",
            "app.tasks.maintenance_tasks"
        ]
    )
    
    # Celery configuration
    celery_app.conf.update(
        # Serialization
        task_serializer=settings.CELERY_TASK_SERIALIZER,
        accept_content=settings.CELERY_ACCEPT_CONTENT,
        result_serializer=settings.CELERY_RESULT_SERIALIZER,
        
        # Timezone
        timezone=settings.CELERY_TIMEZONE,
        enable_utc=True,
        
        # Task execution
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        
        # Worker configuration
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=False,
        
        # Result backend
        result_expires=3600,  # 1 hour
        result_persistent=True,
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
    )
    
    # Task routing configuration
    celery_app.conf.task_routes = {
        # AI processing tasks (high priority, dedicated queue)
        "app.tasks.ai_tasks.process_trip_generation": {
            "queue": "ai_processing_high"
        },
        "app.tasks.ai_tasks.process_image_analysis": {
            "queue": "ai_processing"
        },
        "app.tasks.ai_tasks.process_voice_input": {
            "queue": "ai_processing"
        },
        "app.tasks.ai_tasks.enhance_itinerary": {
            "queue": "ai_processing"
        },
        
        # Trip processing tasks
        "app.tasks.trip_tasks.optimize_trip_route": {
            "queue": "trip_processing"
        },
        "app.tasks.trip_tasks.sync_real_time_data": {
            "queue": "trip_processing"
        },
        "app.tasks.trip_tasks.validate_trip_data": {
            "queue": "trip_processing"
        },
        
        # Notification tasks (fast queue)
        "app.tasks.notification_tasks.send_trip_ready_notification": {
            "queue": "notifications"
        },
        "app.tasks.notification_tasks.send_collaboration_invitation": {
            "queue": "notifications"
        },
        "app.tasks.notification_tasks.send_push_notification": {
            "queue": "notifications"
        },
        "app.tasks.notification_tasks.send_email": {
            "queue": "notifications"
        },
        
        # Analytics tasks (low priority)
        "app.tasks.analytics_tasks.track_user_behavior": {
            "queue": "analytics"
        },
        "app.tasks.analytics_tasks.generate_trip_insights": {
            "queue": "analytics"
        },
        "app.tasks.analytics_tasks.update_recommendations": {
            "queue": "analytics"
        },
        
        # Maintenance tasks
        "app.tasks.maintenance_tasks.cleanup_expired_data": {
            "queue": "maintenance"
        },
        "app.tasks.maintenance_tasks.backup_data": {
            "queue": "maintenance"
        },
    }
    
    # Queue priorities
    celery_app.conf.task_queue_priorities = {
        "ai_processing_high": 10,
        "notifications": 8,
        "ai_processing": 6,
        "trip_processing": 5,
        "analytics": 3,
        "maintenance": 1,
    }
    
    # Periodic tasks (Celery Beat)
    celery_app.conf.beat_schedule = {
        # Daily tasks
        "process-daily-notifications": {
            "task": "app.tasks.notification_tasks.process_daily_notifications",
            "schedule": crontab(hour=9, minute=0),  # 9 AM UTC daily
        },
        
        "sync-real-time-data": {
            "task": "app.tasks.trip_tasks.sync_all_active_trips",
            "schedule": crontab(minute="*/30"),  # Every 30 minutes
        },
        
        "cleanup-expired-data": {
            "task": "app.tasks.maintenance_tasks.cleanup_expired_data",
            "schedule": crontab(hour=2, minute=0),  # 2 AM UTC daily
        },
        
        # Weekly tasks
        "generate-weekly-analytics": {
            "task": "app.tasks.analytics_tasks.generate_weekly_report",
            "schedule": crontab(hour=1, minute=0, day_of_week=1),  # Monday 1 AM
        },
        
        "backup-critical-data": {
            "task": "app.tasks.maintenance_tasks.backup_critical_data",
            "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
        },
        
        # Hourly tasks
        "update-place-data": {
            "task": "app.tasks.trip_tasks.update_place_information",
            "schedule": crontab(minute=0),  # Every hour
        },
    }
    
    # Error handling
    celery_app.conf.task_annotations = {
        "*": {
            "retry_policy": {
                "max_retries": 3,
                "interval_start": 0,
                "interval_step": 0.2,
                "interval_max": 0.2,
            }
        },
        # Special retry policy for AI tasks
        "app.tasks.ai_tasks.*": {
            "retry_policy": {
                "max_retries": 2,
                "interval_start": 60,
                "interval_step": 60,
                "interval_max": 300,
            }
        },
    }
    
    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()


# Task result status monitoring
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
    return f'Task executed successfully at {self.request.id}'


# Health check task
@celery_app.task
def health_check():
    """Health check task for monitoring."""
    import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "worker_id": health_check.request.id
    }


# Task monitoring utilities
class TaskMonitor:
    """Utility class for monitoring task execution."""
    
    @staticmethod
    def get_active_tasks():
        """Get list of active tasks."""
        inspect = celery_app.control.inspect()
        return inspect.active()
    
    @staticmethod
    def get_scheduled_tasks():
        """Get list of scheduled tasks."""
        inspect = celery_app.control.inspect()
        return inspect.scheduled()
    
    @staticmethod
    def get_reserved_tasks():
        """Get list of reserved tasks."""
        inspect = celery_app.control.inspect()
        return inspect.reserved()
    
    @staticmethod
    def get_stats():
        """Get worker statistics."""
        inspect = celery_app.control.inspect()
        return inspect.stats()
    
    @staticmethod
    def revoke_task(task_id: str, terminate=False):
        """
        Revoke a task by ID.
        
        Args:
            task_id: Task ID to revoke
            terminate: Whether to terminate if task is running
        """
        celery_app.control.revoke(task_id, terminate=terminate)
    
    @staticmethod
    def purge_queue(queue_name: str):
        """
        Purge all tasks from a queue.
        
        Args:
            queue_name: Name of queue to purge
        """
        celery_app.control.purge()


# Export the configured Celery app
__all__ = ["celery_app", "TaskMonitor", "create_celery_app"]
