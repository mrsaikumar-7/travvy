"""
Trip Service

This service handles all trip-related business logic including
CRUD operations, access control, and trip management.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

from app.core.database import get_database, FirestoreService
from app.models.schemas import Trip, TripCreateRequest, TripListResponse

logger = logging.getLogger(__name__)


class OptimisticLockException(Exception):
    """Exception raised when optimistic locking fails."""
    pass


class TripService:
    """
    Service class for trip management operations.
    """
    
    def __init__(self, db_service: FirestoreService = None):
        self.db_service = db_service
        self.collection_name = "trips"
    
    async def get_db(self) -> FirestoreService:
        """Get database service instance."""
        if not self.db_service:
            self.db_service = await get_database()
        return self.db_service
    
    async def create_trip(
        self,
        user_id: str,
        destination: str,
        start_date: str,
        end_date: str,
        budget: float,
        currency: str,
        travelers: Dict[str, int],
        **kwargs
    ) -> Trip:
        """
        Create a new trip.
        
        Args:
            user_id: ID of the user creating the trip
            destination: Trip destination
            start_date: Start date
            end_date: End date
            budget: Trip budget
            currency: Currency code
            travelers: Traveler information
            **kwargs: Additional trip data
            
        Returns:
            Created trip object
        """
        try:
            db = await self.get_db()
            
            # Generate trip ID
            trip_id = str(uuid.uuid4())
            
            # Create trip data
            trip_data = {
                "tripId": trip_id,
                "createdBy": user_id,
                "collaborators": {
                    user_id: {
                        "role": "owner",
                        "joinedAt": datetime.utcnow(),
                        "permissions": ["read", "write", "delete", "collaborate"]
                    }
                },
                "metadata": {
                    "title": f"Trip to {destination}",
                    "destination": {
                        "name": destination,
                        "placeId": "",  # Will be populated by AI service
                        "coordinates": None,
                        "country": "",
                        "city": ""
                    },
                    "dates": {
                        "startDate": start_date,
                        "endDate": end_date,
                        "duration": 0,  # Calculate duration
                        "flexible": False
                    },
                    "travelers": {
                        **travelers,
                        "totalCount": sum(travelers.values())
                    },
                    "budget": {
                        "currency": currency,
                        "total": budget,
                        "breakdown": {
                            "accommodation": 0,
                            "transportation": 0,
                            "food": 0,
                            "activities": 0,
                            "miscellaneous": 0
                        }
                    }
                },
                "aiGeneration": {
                    "conversationId": "",
                    "prompts": [],
                    "generatedAt": None,
                    "model": "",
                    "confidence": 0.0,
                    "userFeedback": None
                },
                "itinerary": [],
                "hotels": [],
                "status": "planning",
                "version": 1,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            # Save to database
            await db.db.collection(self.collection_name).document(trip_id).set(trip_data)
            
            logger.info(f"Trip created: {trip_id} by user {user_id}")
            
            # Convert to Trip model (mock for now)
            trip = Trip(**trip_data)
            return trip
            
        except Exception as e:
            logger.error(f"Failed to create trip: {str(e)}")
            raise
    
    async def get_trip_by_id(self, trip_id: str) -> Optional[Trip]:
        """
        Get trip by ID with caching.
        
        Args:
            trip_id: Trip ID
            
        Returns:
            Trip object or None if not found
        """
        try:
            db = await self.get_db()
            
            # Get with cache
            trip_data = await db.get_with_cache(
                collection=self.collection_name,
                doc_id=trip_id,
                cache_ttl=300  # 5 minutes
            )
            
            if trip_data:
                return Trip(**trip_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get trip {trip_id}: {str(e)}")
            raise
    
    async def get_user_trips(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> TripListResponse:
        """
        Get user's trips with pagination and filtering.
        
        Args:
            user_id: User ID
            limit: Maximum results
            offset: Results offset
            status_filter: Filter by status
            search_query: Search query
            
        Returns:
            Paginated trip list
        """
        try:
            db = await self.get_db()
            
            # Build filters
            filters = [("createdBy", "==", user_id)]
            
            if status_filter:
                filters.append(("status", "==", status_filter))
            
            # Get paginated results
            result = await db.paginated_query(
                collection=self.collection_name,
                filters=filters,
                order_by="createdAt",
                limit=limit,
                start_after=None  # TODO: Implement proper pagination
            )
            
            # Convert to Trip objects
            trips = [Trip(**item["data"]) for item in result["results"]]
            
            return TripListResponse(
                trips=trips,
                total=len(trips),
                has_more=result["has_more"],
                offset=offset,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get user trips: {str(e)}")
            raise
    
    async def has_access(self, trip_id: str, user_id: str) -> bool:
        """
        Check if user has access to trip.
        
        Args:
            trip_id: Trip ID
            user_id: User ID
            
        Returns:
            True if user has access
        """
        try:
            trip = await self.get_trip_by_id(trip_id)
            
            if not trip:
                return False
            
            # Check if user is in collaborators
            return user_id in trip.collaborators
            
        except Exception as e:
            logger.error(f"Access check failed for trip {trip_id}: {str(e)}")
            return False
    
    async def has_edit_access(self, trip_id: str, user_id: str) -> bool:
        """
        Check if user has edit access to trip.
        
        Args:
            trip_id: Trip ID
            user_id: User ID
            
        Returns:
            True if user has edit access
        """
        try:
            trip = await self.get_trip_by_id(trip_id)
            
            if not trip:
                return False
            
            # Check if user has edit permissions
            collaborator = trip.collaborators.get(user_id)
            if not collaborator:
                return False
            
            return "write" in collaborator.get("permissions", [])
            
        except Exception as e:
            logger.error(f"Edit access check failed for trip {trip_id}: {str(e)}")
            return False
    
    async def update_trip(
        self,
        trip_id: str,
        updates: Dict[str, Any],
        user_id: str,
        version: int
    ) -> Trip:
        """
        Update trip with optimistic locking.
        
        Args:
            trip_id: Trip ID
            updates: Updates to apply
            user_id: User making the update
            version: Expected version for optimistic locking
            
        Returns:
            Updated trip object
            
        Raises:
            OptimisticLockException: If version mismatch
        """
        try:
            db = await self.get_db()
            
            # Get current trip
            current_trip = await self.get_trip_by_id(trip_id)
            if not current_trip:
                raise ValueError("Trip not found")
            
            # Check version for optimistic locking
            if current_trip.version != version:
                raise OptimisticLockException("Trip was modified by another user")
            
            # Prepare updates
            updates["version"] = version + 1
            updates["updatedAt"] = datetime.utcnow()
            
            # Update in database
            await db.db.collection(self.collection_name).document(trip_id).update(updates)
            
            # Invalidate cache
            await db.invalidate_cache(f"{self.collection_name}:{trip_id}")
            
            # Return updated trip
            updated_trip = await self.get_trip_by_id(trip_id)
            
            logger.info(f"Trip updated: {trip_id} by user {user_id}")
            
            return updated_trip
            
        except OptimisticLockException:
            raise
        except Exception as e:
            logger.error(f"Failed to update trip {trip_id}: {str(e)}")
            raise
    
    async def delete_trip(self, trip_id: str, user_id: str) -> bool:
        """
        Soft delete a trip.
        
        Args:
            trip_id: Trip ID
            user_id: User requesting deletion
            
        Returns:
            True if successful
        """
        try:
            db = await self.get_db()
            
            # Mark as deleted
            updates = {
                "status": "deleted",
                "deletedAt": datetime.utcnow(),
                "deletedBy": user_id,
                "updatedAt": datetime.utcnow()
            }
            
            await db.db.collection(self.collection_name).document(trip_id).update(updates)
            
            # Invalidate cache
            await db.invalidate_cache(f"{self.collection_name}:{trip_id}")
            
            logger.info(f"Trip deleted: {trip_id} by user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete trip {trip_id}: {str(e)}")
            raise
    
    async def get_trip_status(self, trip_id: str) -> Dict[str, Any]:
        """
        Get trip generation/processing status.
        
        Args:
            trip_id: Trip ID
            
        Returns:
            Status information
        """
        try:
            trip = await self.get_trip_by_id(trip_id)
            
            if not trip:
                return {"status": "not_found"}
            
            return {
                "status": trip.status,
                "version": trip.version,
                "last_updated": trip.updatedAt,
                "ai_generation": trip.aiGeneration
            }
            
        except Exception as e:
            logger.error(f"Failed to get trip status {trip_id}: {str(e)}")
            raise
    
    async def duplicate_trip(self, original_trip_id: str, user_id: str) -> Trip:
        """
        Duplicate an existing trip.
        
        Args:
            original_trip_id: Original trip ID
            user_id: User creating the duplicate
            
        Returns:
            New trip object
        """
        try:
            # Get original trip
            original_trip = await self.get_trip_by_id(original_trip_id)
            if not original_trip:
                raise ValueError("Original trip not found")
            
            # Create new trip data
            new_trip_data = original_trip.dict()
            new_trip_data["tripId"] = str(uuid.uuid4())
            new_trip_data["createdBy"] = user_id
            new_trip_data["collaborators"] = {
                user_id: {
                    "role": "owner",
                    "joinedAt": datetime.utcnow(),
                    "permissions": ["read", "write", "delete", "collaborate"]
                }
            }
            new_trip_data["metadata"]["title"] = f"Copy of {original_trip.metadata.title}"
            new_trip_data["status"] = "planning"
            new_trip_data["version"] = 1
            new_trip_data["createdAt"] = datetime.utcnow()
            new_trip_data["updatedAt"] = datetime.utcnow()
            
            # Save to database
            db = await self.get_db()
            await db.db.collection(self.collection_name).document(
                new_trip_data["tripId"]
            ).set(new_trip_data)
            
            logger.info(f"Trip duplicated: {original_trip_id} -> {new_trip_data['tripId']}")
            
            return Trip(**new_trip_data)
            
        except Exception as e:
            logger.error(f"Failed to duplicate trip {original_trip_id}: {str(e)}")
            raise
