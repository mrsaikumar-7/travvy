"""
Trip Management API Endpoints

This module handles all trip-related operations including creation,
retrieval, updates, and AI-powered trip generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
import logging

from app.core.security import get_current_user, get_current_user_optional, require_permission, Permissions
from app.services.trip_service import TripService
from app.services.ai_service import AIService
from app.models.schemas import (
    TripCreateRequest,
    TripUpdateRequest,
    TripResponse,
    TripDetail,
    TripListResponse,
    TripOptimizationRequest
)
from app.dependencies import get_trip_service, get_ai_service
from app.core.celery import celery_app
from app.core.monitoring import monitor_endpoint
# from app.tasks.trip_tasks import process_trip_generation  # TODO: Implement this task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=TripResponse)
@router.post("", response_model=TripResponse)  # Handle both with and without trailing slash
@monitor_endpoint("create_trip")
async def create_trip(
    trip_request: TripCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service),
    ai_service: AIService = Depends(get_ai_service)
) -> TripResponse:
    """
    Create a new trip with AI generation.
    
    Args:
        trip_request: Trip creation data
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        trip_service: Trip service dependency
        ai_service: AI service dependency
        
    Returns:
        Trip response with generation status
    """
    try:
        # Create initial trip document with status="generating"
        trip = await trip_service.create_trip(
            user_id=current_user["uid"],
            **trip_request.dict()
        )
        
        logger.info(f"Created trip with status 'generating': {trip.tripId}")
        
        # Import here to avoid circular imports
        from app.tasks.ai_tasks import process_trip_generation
        
        # Trigger Celery task for AI generation
        conversation_context = {
            "destination": trip_request.destination,
            "start_date": trip_request.start_date,
            "end_date": trip_request.end_date,
            "budget": trip_request.budget,
            "travelers": trip_request.travelers
        }
        
        task = process_trip_generation.delay(
            trip_id=trip.tripId,
            user_preferences=current_user.get("preferences", {}),
            conversation_context=conversation_context
        )
        
        logger.info(f"Started AI generation task {task.id} for trip {trip.tripId}")
        
        return TripResponse(
            trip_id=trip.tripId,
            status="generating",
            message="Trip created, AI is generating your itinerary",
            task_id=task.id
        )
        
    except Exception as e:
        logger.error(f"Trip creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trip: {str(e)}"
        )


@router.get("/", response_model=TripListResponse)
@router.get("", response_model=TripListResponse)  # Handle both with and without trailing slash
@monitor_endpoint("list_trips")
async def list_user_trips(
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
) -> TripListResponse:
    """
    Get list of user's trips with pagination and filtering.
    
    Args:
        current_user: Current authenticated user
        trip_service: Trip service dependency
        limit: Maximum number of trips to return
        offset: Number of trips to skip
        status_filter: Filter by trip status
        search: Search query for trip names/destinations
        
    Returns:
        Paginated list of user trips
    """
    try:
        trips = await trip_service.get_user_trips(
            user_id=current_user["uid"],
            limit=limit,
            offset=offset,
            status_filter=status_filter,
            search_query=search
        )
        
        return trips
        
    except Exception as e:
        logger.error(f"Failed to list trips: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trips"
        )


@router.get("/{trip_id}", response_model=TripDetail)
@monitor_endpoint("get_trip")
async def get_trip(
    trip_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service)
) -> TripDetail:
    """
    Get detailed trip information.
    
    Args:
        trip_id: Trip ID
        current_user: Current authenticated user
        trip_service: Trip service dependency
        
    Returns:
        Detailed trip information
    """
    try:
        # Check if user has access to this trip
        if not await trip_service.has_access(trip_id, current_user["uid"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this trip"
            )
        
        trip = await trip_service.get_trip_by_id(trip_id)
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        return trip
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trip {trip_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trip"
        )


@router.put("/{trip_id}", response_model=TripDetail)
@monitor_endpoint("update_trip")
async def update_trip(
    trip_id: str,
    updates: TripUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service)
) -> TripDetail:
    """
    Update trip with optimistic locking.
    
    Args:
        trip_id: Trip ID to update
        updates: Trip update data
        current_user: Current authenticated user
        trip_service: Trip service dependency
        
    Returns:
        Updated trip information
    """
    try:
        # Check if user has edit access
        if not await trip_service.has_edit_access(trip_id, current_user["uid"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No edit permission for this trip"
            )
        
        updated_trip = await trip_service.update_trip(
            trip_id=trip_id,
            updates=updates.dict(exclude_unset=True),
            user_id=current_user["uid"],
            version=updates.version
        )
        
        logger.info(f"Trip updated: {trip_id} by user {current_user['uid']}")
        
        return updated_trip
        
    except trip_service.OptimisticLockException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Trip was modified by another user. Please refresh and try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update trip {trip_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update trip"
        )


@router.delete("/{trip_id}")
@monitor_endpoint("delete_trip")
async def delete_trip(
    trip_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service)
) -> Dict[str, str]:
    """
    Delete a trip (soft delete).
    
    Args:
        trip_id: Trip ID to delete
        current_user: Current authenticated user
        trip_service: Trip service dependency
        
    Returns:
        Deletion confirmation
    """
    try:
        # Check if user owns this trip
        trip = await trip_service.get_trip_by_id(trip_id)
        if not trip or trip.created_by != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only trip owner can delete the trip"
            )
        
        await trip_service.delete_trip(trip_id, current_user["uid"])
        
        logger.info(f"Trip deleted: {trip_id} by user {current_user['uid']}")
        
        return {"message": "Trip deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete trip {trip_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete trip"
        )


@router.post("/{trip_id}/optimize")
@monitor_endpoint("optimize_trip")
async def optimize_trip_route(
    trip_id: str,
    optimization_request: TripOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service)
) -> Dict[str, str]:
    """
    Optimize trip route for time/cost efficiency.
    
    Args:
        trip_id: Trip ID to optimize
        optimization_request: Optimization parameters
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        trip_service: Trip service dependency
        
    Returns:
        Optimization task status
    """
    try:
        # Check access
        if not await trip_service.has_access(trip_id, current_user["uid"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this trip"
            )
        
        # Queue optimization task
        from app.tasks.trip_tasks import optimize_trip_route
        task = optimize_trip_route.delay(
            trip_id=trip_id,
            preferences=optimization_request.dict()
        )
        
        logger.info(f"Trip optimization queued: {trip_id}")
        
        return {
            "message": "Trip optimization started",
            "task_id": task.id,
            "estimated_completion": "1-2 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize trip {trip_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start trip optimization"
        )


@router.get("/{trip_id}/status")
@monitor_endpoint("get_trip_status")
async def get_trip_status(
    trip_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service)
) -> Dict[str, Any]:
    """
    Get trip generation/processing status.
    
    Args:
        trip_id: Trip ID
        current_user: Current authenticated user
        trip_service: Trip service dependency
        
    Returns:
        Trip status information
    """
    try:
        # Check access
        if not await trip_service.has_access(trip_id, current_user["uid"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this trip"
            )
        
        status_info = await trip_service.get_trip_status(trip_id)
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trip status {trip_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trip status"
        )


@router.post("/{trip_id}/duplicate")
@monitor_endpoint("duplicate_trip")
async def duplicate_trip(
    trip_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_optional),
    trip_service: TripService = Depends(get_trip_service)
) -> TripResponse:
    """
    Duplicate an existing trip.
    
    Args:
        trip_id: Trip ID to duplicate
        current_user: Current authenticated user
        trip_service: Trip service dependency
        
    Returns:
        New trip information
    """
    try:
        # Check access
        if not await trip_service.has_access(trip_id, current_user["uid"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this trip"
            )
        
        new_trip = await trip_service.duplicate_trip(
            original_trip_id=trip_id,
            user_id=current_user["uid"]
        )
        
        logger.info(f"Trip duplicated: {trip_id} -> {new_trip.tripId}")
        
        return TripResponse(
            trip_id=new_trip.tripId,
            status="completed",
            message="Trip duplicated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to duplicate trip {trip_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate trip"
        )
