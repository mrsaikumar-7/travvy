"""
Collaboration API Endpoints

This module handles real-time collaboration features including
invitations, voting, and shared trip editing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from app.core.security import get_current_user
from app.services.collaboration_service import CollaborationService
from app.models.schemas import (
    CollaborationInvite,
    VoteCreateRequest,
    VoteCastRequest,
    CollaborationSession
)
from app.core.monitoring import monitor_endpoint

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/trips/{trip_id}/invite")
@monitor_endpoint("collaboration_invite")
async def invite_collaborator(
    trip_id: str,
    invitation: CollaborationInvite,
    current_user: Dict[str, Any] = Depends(get_current_user),
    collab_service: CollaborationService = Depends()
) -> Dict[str, str]:
    """
    Invite user to collaborate on trip.
    
    Args:
        trip_id: Trip ID to collaborate on
        invitation: Invitation details
        current_user: Current authenticated user
        collab_service: Collaboration service dependency
        
    Returns:
        Invitation status
    """
    try:
        await collab_service.send_invitation(
            trip_id=trip_id,
            inviter_id=current_user["uid"],
            invitee_email=invitation.email,
            role=invitation.role,
            message=invitation.message
        )
        
        logger.info(f"Collaboration invitation sent for trip {trip_id}")
        
        return {"status": "invitation_sent", "message": "Invitation sent successfully"}
        
    except Exception as e:
        logger.error(f"Collaboration invitation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send collaboration invitation"
        )


@router.post("/trips/{trip_id}/vote")
@monitor_endpoint("create_vote")
async def create_vote(
    trip_id: str,
    vote_request: VoteCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    collab_service: CollaborationService = Depends()
) -> Dict[str, Any]:
    """
    Create a vote for group decision.
    
    Args:
        trip_id: Trip ID for the vote
        vote_request: Vote details
        current_user: Current authenticated user
        collab_service: Collaboration service dependency
        
    Returns:
        Created vote information
    """
    try:
        vote = await collab_service.create_vote(
            trip_id=trip_id,
            creator_id=current_user["uid"],
            **vote_request.dict()
        )
        
        logger.info(f"Vote created for trip {trip_id}")
        
        return vote
        
    except Exception as e:
        logger.error(f"Vote creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vote"
        )


@router.post("/trips/{trip_id}/votes/{vote_id}/cast")
@monitor_endpoint("cast_vote")
async def cast_vote(
    trip_id: str,
    vote_id: str,
    vote_cast: VoteCastRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    collab_service: CollaborationService = Depends()
) -> Dict[str, Any]:
    """
    Cast vote in group decision.
    
    Args:
        trip_id: Trip ID
        vote_id: Vote ID
        vote_cast: Vote casting data
        current_user: Current authenticated user
        collab_service: Collaboration service dependency
        
    Returns:
        Vote result information
    """
    try:
        result = await collab_service.cast_vote(
            trip_id=trip_id,
            vote_id=vote_id,
            user_id=current_user["uid"],
            selections=vote_cast.selections
        )
        
        logger.info(f"Vote cast for trip {trip_id}, vote {vote_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Vote casting failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cast vote"
        )


@router.get("/trips/{trip_id}/session")
@monitor_endpoint("get_collaboration_session")
async def get_collaboration_session(
    trip_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    collab_service: CollaborationService = Depends()
) -> CollaborationSession:
    """
    Get current collaboration session for trip.
    
    Args:
        trip_id: Trip ID
        current_user: Current authenticated user
        collab_service: Collaboration service dependency
        
    Returns:
        Collaboration session information
    """
    try:
        session = await collab_service.get_session(trip_id, current_user["uid"])
        return session
        
    except Exception as e:
        logger.error(f"Failed to get collaboration session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collaboration session"
        )


@router.post("/trips/{trip_id}/join")
@monitor_endpoint("join_collaboration")
async def join_collaboration(
    trip_id: str,
    invitation_token: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    collab_service: CollaborationService = Depends()
) -> Dict[str, str]:
    """
    Join collaboration session via invitation token.
    
    Args:
        trip_id: Trip ID to join
        invitation_token: Invitation token
        current_user: Current authenticated user
        collab_service: Collaboration service dependency
        
    Returns:
        Join confirmation
    """
    try:
        await collab_service.join_collaboration(
            trip_id=trip_id,
            user_id=current_user["uid"],
            invitation_token=invitation_token
        )
        
        logger.info(f"User joined collaboration for trip {trip_id}")
        
        return {"status": "joined", "message": "Successfully joined collaboration"}
        
    except Exception as e:
        logger.error(f"Collaboration join failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to join collaboration"
        )
