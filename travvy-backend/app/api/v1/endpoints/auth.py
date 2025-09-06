"""
Authentication API Endpoints

This module handles user authentication including Google OAuth,
JWT token management, and session handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any
import logging

from app.core.security import security_service, get_current_user
from app.dependencies import get_user_service
from app.services.user_service import UserService
from app.models.schemas import (
    GoogleTokenRequest,
    AuthResponse,
    TokenRefreshRequest,
    UserLoginRequest,
    UserRegistrationRequest
)
from app.core.monitoring import monitor_endpoint

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/google", response_model=AuthResponse)
@monitor_endpoint("auth_google")
async def authenticate_with_google(
    request: GoogleTokenRequest,
    user_service = Depends(get_user_service)
) -> AuthResponse:
    """
    Authenticate user with Google OAuth token.
    
    Args:
        request: Google token request containing ID token
        user_service: User service dependency
        
    Returns:
        Authentication response with JWT tokens
    """
    try:
        # Verify Google token
        google_user_info = await security_service.verify_google_token(request.id_token)
        
        # Get or create user
        user = await user_service.get_or_create_user_from_google(
            google_user_info=google_user_info
        )
        
        # Generate JWT tokens
        access_token = security_service.create_access_token(
            user_id=user.uid,
            additional_claims={"email": user.email}
        )
        
        refresh_token = security_service.create_refresh_token(user.uid)
        
        logger.info(f"User authenticated successfully: {user.email}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user
        )
        
    except Exception as e:
        logger.error(f"Google authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed"
        )


@router.post("/refresh", response_model=Dict[str, str])
@monitor_endpoint("auth_refresh")
async def refresh_access_token(
    request: TokenRefreshRequest
) -> Dict[str, str]:
    """
    Refresh access token using refresh token.
    
    Args:
        request: Token refresh request
        
    Returns:
        New access token
    """
    try:
        # Verify refresh token
        user_id = security_service.verify_refresh_token(request.refresh_token)
        
        # Generate new access token
        access_token = security_service.create_access_token(user_id)
        
        logger.info(f"Access token refreshed for user: {user_id}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
@monitor_endpoint("auth_logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout current user (invalidate tokens).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Logout confirmation
    """
    try:
        # TODO: Implement token blacklisting in Redis
        # For now, just log the logout
        logger.info(f"User logged out: {current_user.get('uid')}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me")
@monitor_endpoint("auth_profile")
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_service = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Get current user profile information.
    
    Args:
        current_user: Current authenticated user
        user_service: User service dependency
        
    Returns:
        User profile information
    """
    try:
        user = await user_service.get_user_by_id(current_user["uid"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/register", response_model=AuthResponse)
@monitor_endpoint("auth_register")
async def register_user(
    request: UserRegistrationRequest,
    user_service = Depends(get_user_service)
) -> AuthResponse:
    """
    Register a new user with email and password.
    
    Args:
        request: User registration data
        user_service: User service dependency
        
    Returns:
        Authentication response with JWT tokens
    """
    try:
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = security_service.hash_password(request.password)
        
        # Create user
        user = await user_service.create_user(
            email=request.email,
            password=hashed_password,
            display_name=request.display_name,
            profile_data=request.profile
        )
        
        # Generate tokens
        access_token = security_service.create_access_token(
            user_id=user.uid,
            additional_claims={"email": user.email}
        )
        
        refresh_token = security_service.create_refresh_token(user.uid)
        
        logger.info(f"New user registered: {user.email}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
@monitor_endpoint("auth_login")
async def login_user(
    request: UserLoginRequest,
    user_service = Depends(get_user_service)
) -> AuthResponse:
    """
    Login user with email and password.
    
    Args:
        request: User login credentials
        user_service: User service dependency
        
    Returns:
        Authentication response with JWT tokens
    """
    try:
        # Verify user credentials (email + password)
        user = await user_service.verify_user_password(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate tokens
        access_token = security_service.create_access_token(
            user_id=user.uid,
            additional_claims={"email": user.email}
        )
        
        refresh_token = security_service.create_refresh_token(user.uid)
        
        # Update last login
        await user_service.update_last_login(user.uid)
        
        logger.info(f"User logged in: {user.email}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
