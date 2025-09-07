#!/usr/bin/env python3
"""
Minimal test server to verify the trip_id fix
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

app = FastAPI(title="Test Server", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripCreateRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    currency: str = "USD"
    travelers: Dict[str, int]

class TripResponse(BaseModel):
    trip_id: str
    status: str
    message: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Test Server Running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/trips")
@app.post("/api/v1/trips/")
async def create_trip(request: TripCreateRequest):
    """Test trip creation endpoint"""
    try:
        # Mock trip creation
        trip_id = f"trip-{hash(request.destination) % 10000}"
        
        return TripResponse(
            trip_id=trip_id,
            status="completed",
            message=f"Trip to {request.destination} created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trips")
@app.get("/api/v1/trips/")
async def list_trips():
    """Test trip listing endpoint"""
    return {
        "trips": [
            {
                "tripId": "test-trip-1",
                "metadata": {
                    "title": "Test Trip",
                    "destination": {"name": "Paris, France"},
                    "dates": {"startDate": "2025-06-01", "endDate": "2025-06-07"}
                },
                "status": "completed"
            }
        ],
        "total": 1
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
