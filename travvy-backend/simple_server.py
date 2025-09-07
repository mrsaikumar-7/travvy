#!/usr/bin/env python3
"""
Simplified FastAPI server for testing trip functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, date

from app.services.trip_service import TripService
from app.services.ai_service import AIService
from mock_db import get_mock_database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Travvy API - Simple Demo",
    description="Simplified trip planning API for testing",
    version="1.0.0-demo"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global services
trip_service = None
ai_service = AIService()

# Request/Response models
class TripCreateRequest(BaseModel):
    destination: str
    start_date: str  # ISO format date string
    end_date: str    # ISO format date string  
    budget: float
    currency: str = "USD"
    travelers: Dict[str, int]
    preferences: Optional[Dict[str, Any]] = {}
    conversation_context: Optional[Dict[str, Any]] = {}

class TripResponse(BaseModel):
    trip_id: str
    status: str
    message: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global trip_service
    logger.info("🚀 Starting Travvy API Demo...")
    
    # Initialize mock database
    mock_db = await get_mock_database()
    trip_service = TripService(db_service=mock_db)
    
    logger.info("✅ Services initialized successfully")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Travvy API Demo",
        "version": "1.0.0-demo",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "trip_service": "active",
            "ai_service": "active",
            "database": "mock"
        }
    }

@app.post("/api/v1/trips", response_model=TripResponse)
async def create_trip(trip_request: TripCreateRequest):
    """Create a new trip with AI generation"""
    try:
        logger.info(f"Creating trip to {trip_request.destination}")
        
        # Create the trip
        trip = await trip_service.create_trip(
            user_id="demo-user-123",
            destination=trip_request.destination,
            start_date=trip_request.start_date,
            end_date=trip_request.end_date,
            budget=trip_request.budget,
            currency=trip_request.currency,
            travelers=trip_request.travelers
        )
        
        # Generate AI content
        itinerary_data = await ai_service.generate_itinerary(
            conversation_context={
                "destination": trip_request.destination,
                "start_date": trip_request.start_date,
                "end_date": trip_request.end_date,
                "budget": trip_request.budget,
                "travelers": trip_request.travelers
            },
            user_preferences=trip_request.preferences
        )
        
        # Generate hotels
        hotels = await ai_service.generate_hotel_recommendations(
            destination=trip_request.destination,
            budget=trip_request.budget,
            preferences=trip_request.preferences
        )
        
        # Update trip with AI results
        await trip_service.update_trip_with_ai_results(
            trip_id=trip.tripId,
            itinerary_data=itinerary_data,
            hotel_data=hotels,
            ai_metadata={"generation_time": "2.5 seconds", "confidence": 0.9}
        )
        
        logger.info(f"✅ Trip created successfully: {trip.tripId}")
        
        return TripResponse(
            trip_id=trip.tripId,
            status="completed",
            message="Trip created and AI content generated successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to create trip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trips")
async def list_trips():
    """List all trips"""
    try:
        trips_result = await trip_service.get_user_trips(
            user_id="demo-user-123",
            limit=20,
            offset=0
        )
        
        return {
            "trips": [trip.dict() for trip in trips_result.trips],
            "total": trips_result.total,
            "has_more": trips_result.has_more
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list trips: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trips/{trip_id}")
async def get_trip(trip_id: str):
    """Get trip details"""
    try:
        trip = await trip_service.get_trip_by_id(trip_id)
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        return trip.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
