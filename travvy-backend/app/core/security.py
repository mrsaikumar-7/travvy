"""
Security and Authentication Module

This module handles JWT token management, Google OAuth integration,
and user authentication/authorization for the API.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from app.core.config import get_settings
from app.models.schemas import User

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()


class SecurityService:
    """
    Security service for handling authentication and authorization.
    """
    
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_hours = settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google OAuth token and extract user information.
        
        Args:
            token: Google OAuth ID token
            
        Returns:
            Dict containing user information from Google
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.google_client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            logger.info(f"Google token verified for user: {idinfo.get('email')}")
            return idinfo
            
        except ValueError as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
    
    def create_access_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """
        Create JWT access token.
        
        Args:
            user_id: User ID to include in token
            additional_claims: Additional claims to include
            
        Returns:
            JWT access token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.access_token_expire_hours),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        logger.info(f"Access token created for user: {user_id}")
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create JWT refresh token.
        
        Args:
            user_id: User ID to include in token
            
        Returns:
            JWT refresh token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        logger.info(f"Refresh token created for user: {user_id}")
        return token
    
    def verify_access_token(self, token: str) -> str:
        """
        Verify JWT access token and extract user ID.
        
        Args:
            token: JWT access token
            
        Returns:
            User ID from token
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            
            user_id: str = payload.get("user_id")
            token_type: str = payload.get("type")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            if token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return user_id
            
        except jwt.ExpiredSignatureError:
            logger.warning("Access token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def verify_refresh_token(self, token: str) -> str:
        """
        Verify JWT refresh token and extract user ID.
        
        Args:
            token: JWT refresh token
            
        Returns:
            User ID from token
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            
            user_id: str = payload.get("user_id")
            token_type: str = payload.get("type")
            
            if user_id is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            return user_id
            
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        except jwt.JWTError as e:
            logger.error(f"Refresh token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)


# Global security service instance
security_service = SecurityService()


class PermissionChecker:
    """Check user permissions for resources."""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    async def __call__(self, current_user: User = Depends("get_current_user")):
        """Check if user has required permission."""
        # TODO: Implement permission checking logic
        # This would check user roles and permissions
        if not hasattr(current_user, 'permissions'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        if self.required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.required_permission}' required"
            )
        
        return current_user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency for getting current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify the token
        user_id = security_service.verify_access_token(credentials.credentials)
        
        # TODO: Get user from database
        # For now, return basic user info
        user_info = {
            "uid": user_id,
            "authenticated": True
        }
        
        logger.debug(f"User authenticated: {user_id}")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current active user (not disabled).
    
    Args:
        current_user: Current user from authentication
        
    Returns:
        Active user information
    """
    # TODO: Check if user is active/not disabled
    if current_user.get("is_active", True) is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


# Permission decorators
def require_permission(permission: str):
    """Decorator to require specific permission."""
    return PermissionChecker(permission)


# Common permissions
class Permissions:
    """Common permission constants."""
    
    # Trip permissions
    CREATE_TRIP = "trips:create"
    READ_TRIP = "trips:read"
    UPDATE_TRIP = "trips:update"
    DELETE_TRIP = "trips:delete"
    COLLABORATE_TRIP = "trips:collaborate"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_TRIPS = "admin:trips"
    ADMIN_SYSTEM = "admin:system"
    
    # AI permissions
    USE_AI_PREMIUM = "ai:premium"
    USE_AI_VOICE = "ai:voice"
    USE_AI_IMAGE = "ai:image"
