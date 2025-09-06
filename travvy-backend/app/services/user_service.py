"""
User Service

This service handles user management, authentication,
and user-related operations.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

from app.core.database import get_database, FirestoreService
from app.models.schemas import User, UserProfile

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db_service: FirestoreService = None):
        self.db_service = db_service
        self.collection_name = "users"
    
    async def get_db(self) -> FirestoreService:
        """Get database service instance."""
        if not self.db_service:
            self.db_service = await get_database()
        return self.db_service
    
    async def get_or_create_user_from_google(
        self, 
        google_user_info: Dict[str, Any]
    ) -> User:
        """Get or create user from Google OAuth info."""
        try:
            user_id = google_user_info["sub"]
            
            # Try to get existing user
            user = await self.get_user_by_id(user_id)
            
            if not user:
                # Create new user
                user_data = {
                    "uid": user_id,
                    "email": google_user_info["email"],
                    "displayName": google_user_info.get("name", ""),
                    "photoURL": google_user_info.get("picture", ""),
                    "profile": {
                        "firstName": google_user_info.get("given_name", ""),
                        "lastName": google_user_info.get("family_name", ""),
                        "dateOfBirth": None,
                        "nationality": None,
                        "languages": ["en"]
                    },
                    "preferences": {
                        "budgetRange": "moderate",
                        "travelStyle": [],
                        "accommodationType": [],
                        "activityTypes": [],
                        "dietaryRestrictions": [],
                        "accessibility": {
                            "mobility": False,
                            "vision": False,
                            "hearing": False
                        }
                    },
                    "travelHistory": {
                        "totalTrips": 0,
                        "countries": [],
                        "favoriteDestinations": [],
                        "averageBudget": 0,
                        "preferredSeasons": []
                    },
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow(),
                    "lastActiveAt": datetime.utcnow()
                }
                
                db = await self.get_db()
                await db.db.collection(self.collection_name).document(user_id).set(user_data)
                
                user = User(**user_data)
                logger.info(f"New user created from Google: {user.email}")
            else:
                # Update last active time
                await self.update_last_login(user_id)
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get/create user from Google: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            db = await self.get_db()
            user_data = await db.get_with_cache(
                collection=self.collection_name,
                doc_id=user_id,
                cache_ttl=600  # 10 minutes
            )
            
            if user_data:
                # Remove password_hash for security - don't include in User object
                user_data.pop('password_hash', None)
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            db = await self.get_db()
            
            if not db or not db.db:
                logger.error("Database connection is not available - check Firestore permissions")
                raise RuntimeError("Database connection failed - check Firestore IAM permissions for service account")
            
            # Query by email
            users_ref = db.db.collection(self.collection_name)
            query = users_ref.where("email", "==", email).limit(1)
            docs = query.stream()
            
            async for doc in docs:
                user_data = doc.to_dict()
                # Remove password_hash for security - don't include in User object
                user_data.pop('password_hash', None)
                return User(**user_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {str(e)}")
            raise
    
    async def verify_user_password(self, email: str, password: str) -> Optional[User]:
        """Verify user password and return user if valid."""
        try:
            db = await self.get_db()
            
            if not db or not db.db:
                logger.error("Database connection is not available - check Firestore permissions")
                raise RuntimeError("Database connection failed - check Firestore IAM permissions for service account")
            
            # Query by email
            users_ref = db.db.collection(self.collection_name)
            query = users_ref.where("email", "==", email).limit(1)
            docs = query.stream()
            
            async for doc in docs:
                user_data = doc.to_dict()
                password_hash = user_data.get('password_hash')
                
                if not password_hash:
                    return None
                
                # Import security service for password verification
                from app.core.security import security_service
                
                # Verify password
                if security_service.verify_password(password, password_hash):
                    # Remove password_hash for security
                    user_data.pop('password_hash', None)
                    return User(**user_data)
                else:
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to verify user password for {email}: {str(e)}")
            raise
    
    async def create_user(
        self,
        email: str,
        password: str,
        display_name: str,
        profile_data: Dict[str, Any] = None
    ) -> User:
        """Create a new user with email/password."""
        try:
            db = await self.get_db()
            
            if not db or not db.db:
                logger.error("Database connection is not available - check Firestore permissions")
                raise RuntimeError("Database connection failed - check Firestore IAM permissions for service account")
            
            user_id = str(uuid.uuid4())
            
            user_data = {
                "uid": user_id,
                "email": email,
                "password_hash": password,  # Should be hashed
                "displayName": display_name,
                "photoURL": None,
                "profile": profile_data.dict() if profile_data and hasattr(profile_data, 'dict') else {
                    "firstName": "",
                    "lastName": "",
                    "dateOfBirth": None,
                    "nationality": None,
                    "languages": ["en"]
                },
                "preferences": {
                    "budgetRange": "moderate",
                    "travelStyle": [],
                    "accommodationType": [],
                    "activityTypes": [],
                    "dietaryRestrictions": [],
                    "accessibility": {
                        "mobility": False,
                        "vision": False,
                        "hearing": False
                    }
                },
                "travelHistory": {
                    "totalTrips": 0,
                    "countries": [],
                    "favoriteDestinations": [],
                    "averageBudget": 0,
                    "preferredSeasons": []
                },
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "lastActiveAt": datetime.utcnow()
            }
            
            await db.db.collection(self.collection_name).document(user_id).set(user_data)
            
            logger.info(f"New user created: {email}")
            return User(**user_data)
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise
    
    async def update_user_profile(
        self, 
        user_id: str, 
        updates: Dict[str, Any]
    ) -> User:
        """Update user profile."""
        try:
            db = await self.get_db()
            
            updates["updatedAt"] = datetime.utcnow()
            await db.db.collection(self.collection_name).document(user_id).update(updates)
            
            # Invalidate cache
            await db.invalidate_cache(f"{self.collection_name}:{user_id}")
            
            updated_user = await self.get_user_by_id(user_id)
            return updated_user
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
            raise
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user travel preferences."""
        try:
            db = await self.get_db()
            
            updates = {
                "preferences": preferences,
                "updatedAt": datetime.utcnow()
            }
            
            await db.db.collection(self.collection_name).document(user_id).update(updates)
            await db.invalidate_cache(f"{self.collection_name}:{user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {str(e)}")
            raise
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login time."""
        try:
            db = await self.get_db()
            
            updates = {"lastActiveAt": datetime.utcnow()}
            await db.db.collection(self.collection_name).document(user_id).update(updates)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update last login: {str(e)}")
            return False
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user travel statistics."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return {}
            
            return {
                "total_trips": user.travelHistory.totalTrips,
                "countries_visited": len(user.travelHistory.countries),
                "favorite_destinations": user.travelHistory.favoriteDestinations,
                "average_budget": user.travelHistory.averageBudget,
                "account_created": user.createdAt,
                "last_active": user.lastActiveAt
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            raise
    
    async def delete_user_account(self, user_id: str) -> bool:
        """Soft delete user account."""
        try:
            db = await self.get_db()
            
            updates = {
                "deleted": True,
                "deletedAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            await db.db.collection(self.collection_name).document(user_id).update(updates)
            await db.invalidate_cache(f"{self.collection_name}:{user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user account: {str(e)}")
            raise
