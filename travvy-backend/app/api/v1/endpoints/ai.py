"""
AI Service API Endpoints

This module handles AI-powered features including conversation processing,
image analysis, voice input, and trip generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import Dict, Any, Optional
import logging

from app.core.security import get_current_user
from app.services.ai_service import AIService
from app.models.schemas import (
    ConversationStartRequest,
    ConversationResponse,
    ImageAnalysisResponse,
    VoiceProcessingResponse,
    AITaskStatusResponse
)
from app.core.monitoring import monitor_endpoint
from app.tasks.ai_tasks import process_image_analysis, process_voice_input

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/conversation", response_model=ConversationResponse)
@monitor_endpoint("ai_conversation")
async def start_conversation(
    request: ConversationStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIService = Depends()
) -> ConversationResponse:
    """
    Start or continue AI conversation for trip planning.
    
    Args:
        request: Conversation request data
        current_user: Current authenticated user
        ai_service: AI service dependency
        
    Returns:
        AI conversation response
    """
    try:
        conversation = await ai_service.process_message(
            user_id=current_user["uid"],
            message=request.message,
            conversation_id=request.conversation_id,
            context=request.context or {}
        )
        
        logger.info(f"AI conversation processed for user {current_user['uid']}")
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            response=conversation.messages[-1].content.text,
            suggested_actions=conversation.ai_state.get("suggested_actions", []),
            context=conversation.context,
            confidence_score=conversation.ai_state.get("confidence", 0.8)
        )
        
    except Exception as e:
        logger.error(f"AI conversation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI conversation processing failed: {str(e)}"
        )


@router.post("/image-analysis", response_model=Dict[str, str])
@monitor_endpoint("ai_image_analysis")
async def analyze_image(
    image: UploadFile = File(...),
    prompt: str = Form("What destination does this image suggest?"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Analyze uploaded image for destination suggestions.
    
    Args:
        image: Uploaded image file
        prompt: Analysis prompt
        current_user: Current authenticated user
        
    Returns:
        Task ID for async processing
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size (10MB limit)
        content = await image.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image file too large (max 10MB)"
            )
        
        # Process image asynchronously
        task = process_image_analysis.delay(
            image_data=content,
            prompt=prompt,
            user_id=current_user["uid"],
            filename=image.filename
        )
        
        logger.info(f"Image analysis queued for user {current_user['uid']}")
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Image analysis started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image analysis failed"
        )


@router.post("/voice-input", response_model=Dict[str, str])
@monitor_endpoint("ai_voice_input")
async def process_voice(
    audio: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Process voice input for trip planning.
    
    Args:
        audio: Uploaded audio file
        current_user: Current authenticated user
        
    Returns:
        Task ID for async processing
    """
    try:
        # Validate audio file
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )
        
        # Check file size (5MB limit)
        content = await audio.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file too large (max 5MB)"
            )
        
        # Process voice asynchronously
        task = process_voice_input.delay(
            audio_data=content,
            user_id=current_user["uid"],
            filename=audio.filename
        )
        
        logger.info(f"Voice processing queued for user {current_user['uid']}")
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Voice processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice processing failed"
        )


@router.get("/task/{task_id}", response_model=AITaskStatusResponse)
@monitor_endpoint("ai_task_status")
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AITaskStatusResponse:
    """
    Get status of AI processing task.
    
    Args:
        task_id: Task ID to check
        current_user: Current authenticated user
        
    Returns:
        Task status and results
    """
    try:
        from celery.result import AsyncResult
        from app.core.celery import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            response = {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is waiting to be processed"
            }
        elif result.state == 'PROGRESS':
            response = {
                "task_id": task_id,
                "status": "processing",
                "progress": result.info,
                "message": "Task is being processed"
            }
        elif result.state == 'SUCCESS':
            response = {
                "task_id": task_id,
                "status": "completed",
                "result": result.result,
                "message": "Task completed successfully"
            }
        elif result.state == 'FAILURE':
            response = {
                "task_id": task_id,
                "status": "failed",
                "error": str(result.info),
                "message": "Task failed"
            }
        else:
            response = {
                "task_id": task_id,
                "status": result.state.lower(),
                "message": f"Task state: {result.state}"
            }
        
        return AITaskStatusResponse(**response)
        
    except Exception as e:
        logger.error(f"Failed to get task status {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status"
        )


@router.post("/suggestions")
@monitor_endpoint("ai_suggestions")
async def get_destination_suggestions(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIService = Depends()
) -> Dict[str, Any]:
    """
    Get AI-powered destination suggestions.
    
    Args:
        query: User query for destinations
        current_user: Current authenticated user
        ai_service: AI service dependency
        
    Returns:
        Destination suggestions
    """
    try:
        suggestions = await ai_service.get_destination_suggestions(
            query=query,
            user_id=current_user["uid"],
            user_preferences=current_user.get("preferences", {})
        )
        
        logger.info(f"Destination suggestions generated for user {current_user['uid']}")
        
        return {
            "suggestions": suggestions,
            "query": query,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get destination suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggestions"
        )


@router.post("/enhance-itinerary")
@monitor_endpoint("ai_enhance_itinerary")
async def enhance_itinerary(
    trip_id: str,
    enhancement_type: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    ai_service: AIService = Depends()
) -> Dict[str, str]:
    """
    Enhance existing itinerary with AI.
    
    Args:
        trip_id: Trip ID to enhance
        enhancement_type: Type of enhancement (activities, restaurants, etc.)
        current_user: Current authenticated user
        ai_service: AI service dependency
        
    Returns:
        Enhancement task status
    """
    try:
        # TODO: Check if user has access to trip
        
        # Queue enhancement task
        from app.tasks.ai_tasks import enhance_itinerary
        task = enhance_itinerary.delay(
            trip_id=trip_id,
            enhancement_type=enhancement_type,
            user_id=current_user["uid"]
        )
        
        logger.info(f"Itinerary enhancement queued for trip {trip_id}")
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": f"Itinerary {enhancement_type} enhancement started"
        }
        
    except Exception as e:
        logger.error(f"Itinerary enhancement failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start itinerary enhancement"
        )


@router.get("/models")
@monitor_endpoint("ai_models")
async def get_available_models(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get list of available AI models and their capabilities.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Available AI models information
    """
    try:
        models = {
            "text_models": [
                {
                    "name": "gemini-1.5-pro",
                    "description": "Advanced conversation and trip planning",
                    "capabilities": ["text_generation", "conversation", "planning"]
                }
            ],
            "vision_models": [
                {
                    "name": "gemini-pro-vision",
                    "description": "Image analysis and destination recognition",
                    "capabilities": ["image_analysis", "landmark_detection"]
                }
            ],
            "speech_models": [
                {
                    "name": "whisper-1",
                    "description": "Speech-to-text conversion",
                    "capabilities": ["transcription", "voice_commands"]
                }
            ]
        }
        
        return models
        
    except Exception as e:
        logger.error(f"Failed to get AI models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI models"
        )
