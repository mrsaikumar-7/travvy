"""
Monitoring and Metrics

This module provides monitoring utilities, performance tracking,
and custom metrics for the application.
"""

import time
import logging
from functools import wraps
from typing import Any, Callable
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class MonitoringService:
    """Service for application monitoring and metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_api_latency(self, endpoint: str, method: str, latency_ms: float):
        """Record API endpoint latency."""
        # TODO: Implement metrics recording to Google Cloud Monitoring
        logger.info(
            "API latency recorded",
            endpoint=endpoint,
            method=method,
            latency_ms=latency_ms
        )
    
    def record_ai_request(self, model: str, tokens_used: int, latency_ms: float):
        """Record AI API usage metrics."""
        # TODO: Implement AI metrics recording
        logger.info(
            "AI request recorded",
            model=model,
            tokens_used=tokens_used,
            latency_ms=latency_ms
        )
    
    def increment_counter(self, metric_name: str, value: int = 1, tags: dict = None):
        """Increment a counter metric."""
        # TODO: Implement counter metrics
        logger.debug(
            "Counter incremented",
            metric=metric_name,
            value=value,
            tags=tags or {}
        )


# Global monitoring service instance
monitoring_service = MonitoringService()


def monitor_endpoint(endpoint_name: str):
    """
    Decorator for monitoring API endpoints.
    
    Args:
        endpoint_name: Name of the endpoint for metrics
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful request
                latency = (time.time() - start_time) * 1000
                monitoring_service.record_api_latency(
                    endpoint=endpoint_name,
                    method="SUCCESS",
                    latency_ms=latency
                )
                
                logger.info(
                    "API request completed",
                    endpoint=endpoint_name,
                    latency_ms=latency,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                # Record failed request
                latency = (time.time() - start_time) * 1000
                monitoring_service.record_api_latency(
                    endpoint=endpoint_name,
                    method="ERROR",
                    latency_ms=latency
                )
                
                logger.error(
                    "API request failed",
                    endpoint=endpoint_name,
                    latency_ms=latency,
                    error=str(e),
                    status="error"
                )
                
                raise
        
        return wrapper
    return decorator


def track_performance(operation_name: str):
    """
    Decorator for tracking operation performance.
    
    Args:
        operation_name: Name of the operation
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                latency = (time.time() - start_time) * 1000
                logger.info(
                    "Operation completed",
                    operation=operation_name,
                    latency_ms=latency,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                logger.error(
                    "Operation failed",
                    operation=operation_name,
                    latency_ms=latency,
                    error=str(e),
                    status="error"
                )
                
                raise
        
        return wrapper
    return decorator
