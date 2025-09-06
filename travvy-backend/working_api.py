"""
Working AI Trip Planner API - Clean Implementation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn

app = FastAPI(
    title="AI Trip Planner API",
    description="Advanced AI-powered trip planning platform",
    version="1.0.0"
)

# CORS Middleware with comprehensive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "https://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language", 
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"]
)

# Pydantic Models
class User(BaseModel):
    uid: str
    email: str
    display_name: str
    photo_url: Optional[str] = None
    created_at: str

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = "New User"

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User

class TripCreateRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    currency: str = "USD"
    travelers: Dict[str, int] = {"adults": 2, "children": 0}
    preferences: Optional[Dict[str, Any]] = {}

class TripResponse(BaseModel):
    trip_id: str
    status: str
    message: str

class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    suggested_actions: List[str] = []

# Mock Data Storage
mock_users = {}
mock_trips = {}
mock_conversations = {}

# Add some default demo users for easy testing
default_demo_users = [
    {"email": "demo@Travvy.com", "password": "demo123", "name": "Demo User"},
    {"email": "test@example.com", "password": "test123", "name": "Test User"},
    {"email": "user@travel.com", "password": "password", "name": "Travel User"}
]

# Initialize demo users
for demo_user in default_demo_users:
    user_id = f"demo_user_{demo_user['email'].replace('@', '_').replace('.', '_')}"
    user = User(
        uid=user_id,
        email=demo_user["email"],
        display_name=demo_user["name"],
        created_at=datetime.utcnow().isoformat()
    )
    mock_users[demo_user["email"]] = {
        "user": user,
        "password": demo_user["password"]
    }

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "AI Trip Planner API",
        "version": "1.0.0", 
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected", 
            "redis": "connected",
            "ai_services": "available"
        }
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "API is working!",
        "features": [
            "Trip Planning",
            "AI Integration",
            "Real-time Collaboration",
            "Multi-modal Input"
        ],
        "endpoints": [
            "/api/v1/auth/register",
            "/api/v1/auth/login", 
            "/api/v1/trips",
            "/api/v1/ai/conversation"
        ]
    }

# Authentication endpoints
@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user profile - simplified version for testing"""
    # For now, return a simple success for any authenticated request
    # In a real app, you would validate the JWT token and return user info
    # For demo purposes, return a consistent mock user
    return {
        "uid": "demo_user_authenticated",
        "email": "demo@Travvy.com", 
        "display_name": "Demo User",
        "photo_url": None,
        "created_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/auth/logout")
async def logout_user():
    """Logout user - invalidate token"""
    return {"message": "Successfully logged out"}

@app.post("/api/v1/auth/google", response_model=AuthResponse)
async def google_auth(request: dict):
    """Google OAuth authentication"""
    # For demo purposes, create a Google user
    user_id = f"google_user_{int(datetime.utcnow().timestamp())}"
    user = User(
        uid=user_id,
        email="google@user.com",
        display_name="Google User",
        created_at=datetime.utcnow().isoformat()
    )
    
    access_token = f"google_access_token_{user_id}"
    refresh_token = f"google_refresh_token_{user_id}"
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@app.post("/api/v1/auth/refresh")
async def refresh_token(request: dict):
    """Refresh access token"""
    # For demo purposes, just return a new token
    new_token = f"refreshed_token_{int(datetime.utcnow().timestamp())}"
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """Register a new user"""
    
    # Check if user already exists
    if request.email in mock_users:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user_id = f"user_{len(mock_users) + 1}_{int(datetime.utcnow().timestamp())}"
    user = User(
        uid=user_id,
        email=request.email,
        display_name=request.display_name,
        created_at=datetime.utcnow().isoformat()
    )
    
    # Store user
    mock_users[request.email] = {
        "user": user,
        "password": request.password  # In real app, this would be hashed
    }
    
    # Generate tokens
    access_token = f"access_token_{user_id}_{int(datetime.utcnow().timestamp())}"
    refresh_token = f"refresh_token_{user_id}"
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token, 
        user=user
    )

@app.post("/api/v1/auth/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """Login user with email and password - flexible for demo"""
    
    # Check if user exists in mock_users
    if request.email in mock_users:
        stored_user = mock_users[request.email]
        if stored_user["password"] != request.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = stored_user["user"]
    else:
        # For demo purposes, create a new user on-the-fly for any login attempt
        # This allows frontend fallback authentication to work seamlessly
        user_id = f"user_{len(mock_users) + 1}_{int(datetime.utcnow().timestamp())}"
        user = User(
            uid=user_id,
            email=request.email,
            display_name=request.email.split('@')[0].title(),
            created_at=datetime.utcnow().isoformat()
        )
        
        # Store the new user for future logins
        mock_users[request.email] = {
            "user": user,
            "password": request.password
        }
    
    # Generate new tokens
    access_token = f"access_token_{user.uid}_{int(datetime.utcnow().timestamp())}"
    refresh_token = f"refresh_token_{user.uid}"
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

# Trip endpoints
@app.post("/api/v1/trips", response_model=TripResponse)
async def create_trip(request: TripCreateRequest):
    """Create a new trip"""
    
    trip_id = f"trip_{len(mock_trips) + 1}_{int(datetime.utcnow().timestamp())}"
    
    # Store trip
    mock_trips[trip_id] = {
        "trip_id": trip_id,
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "budget": request.budget,
        "currency": request.currency,
        "travelers": request.travelers,
        "preferences": request.preferences,
        "status": "planning",
        "created_at": datetime.utcnow().isoformat()
    }
    
    return TripResponse(
        trip_id=trip_id,
        status="created",
        message=f"Trip to {request.destination} created successfully!"
    )

@app.get("/api/v1/trips")
async def list_trips():
    """Get list of all trips"""
    return {
        "trips": list(mock_trips.values()),
        "total": len(mock_trips)
    }

@app.get("/api/v1/trips/{trip_id}")
async def get_trip(trip_id: str):
    """Get specific trip details"""
    if trip_id not in mock_trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return mock_trips[trip_id]

@app.put("/api/v1/trips/{trip_id}")
async def update_trip(trip_id: str, request: TripCreateRequest):
    """Update trip details"""
    if trip_id not in mock_trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Update the trip
    mock_trips[trip_id].update({
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "budget": request.budget,
        "currency": request.currency,
        "travelers": request.travelers,
        "preferences": request.preferences,
        "updated_at": datetime.utcnow().isoformat()
    })
    
    return mock_trips[trip_id]

@app.delete("/api/v1/trips/{trip_id}")
async def delete_trip(trip_id: str):
    """Delete a trip"""
    if trip_id not in mock_trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    del mock_trips[trip_id]
    return {"message": "Trip deleted successfully"}

@app.post("/api/v1/trips/{trip_id}/duplicate")
async def duplicate_trip(trip_id: str):
    """Duplicate a trip"""
    if trip_id not in mock_trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Create a new trip ID
    new_trip_id = f"trip_{len(mock_trips) + 1}_{int(datetime.utcnow().timestamp())}"
    
    # Copy the original trip
    original_trip = mock_trips[trip_id].copy()
    original_trip["trip_id"] = new_trip_id
    original_trip["created_at"] = datetime.utcnow().isoformat()
    original_trip["status"] = "planning"
    
    mock_trips[new_trip_id] = original_trip
    
    return {"trip_id": new_trip_id, "message": "Trip duplicated successfully"}

@app.post("/api/v1/trips/{trip_id}/optimize")
async def optimize_trip(trip_id: str, request: dict):
    """Optimize trip for better route/cost"""
    if trip_id not in mock_trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return {
        "message": "Trip optimization completed",
        "improvements": {
            "cost_saved": 150,
            "time_saved": "2 hours",
            "route_optimized": True
        }
    }

@app.get("/api/v1/trips/{trip_id}/status")
async def get_trip_status(trip_id: str):
    """Get trip generation/processing status"""
    if trip_id not in mock_trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return {
        "trip_id": trip_id,
        "status": mock_trips[trip_id].get("status", "completed"),
        "progress": 100,
        "message": "Trip ready"
    }

# AI endpoints
@app.post("/api/v1/ai/conversation", response_model=ConversationResponse)
async def ai_conversation(request: ConversationRequest):
    """Start or continue AI conversation"""
    
    conversation_id = request.conversation_id or f"conv_{int(datetime.utcnow().timestamp())}"
    
    # Simple AI response logic
    message = request.message.lower()
    
    if "paris" in message:
        response = "🗼 Paris is an amazing choice! The City of Light offers incredible art, cuisine, and romance. When are you planning to visit?"
        suggestions = ["5-day Paris itinerary", "Best time to visit Paris", "Paris budget guide"]
    elif "beach" in message or "ocean" in message:
        response = "🏖️ Beach destinations are perfect! Consider Maldives, Bali, Santorini, or Hawaii. What type of beach experience interests you?"
        suggestions = ["Tropical paradise", "Greek islands", "Budget beach destinations"]
    elif "adventure" in message or "mountain" in message:
        response = "⛰️ Adventure awaits! Nepal, New Zealand, Costa Rica, and Iceland offer amazing experiences. What activities do you enjoy?"
        suggestions = ["Mountain trekking", "Extreme sports", "Wildlife adventures"]
    else:
        response = f"That's interesting! I'd love to help you plan something amazing based on '{request.message}'. What type of experience are you looking for?"
        suggestions = ["Relaxation trip", "Adventure vacation", "Cultural experience", "Food & wine tour"]
    
    # Store conversation
    mock_conversations[conversation_id] = {
        "conversation_id": conversation_id,
        "messages": [
            {"user": request.message, "ai": response}
        ],
        "context": request.context,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    return ConversationResponse(
        conversation_id=conversation_id,
        response=response,
        suggested_actions=suggestions
    )

# Image analysis endpoint
@app.post("/api/v1/ai/image-analysis")
async def analyze_image():
    """Analyze uploaded image for destination suggestions"""
    return {
        "message": "Image analysis feature coming soon!",
        "suggestions": [
            "Upload images of places you'd like to visit",
            "Get AI-powered destination recommendations",
            "Analyze travel photos for inspiration"
        ]
    }

# Voice processing endpoint  
@app.post("/api/v1/ai/voice-input")
async def process_voice():
    """Process voice input for trip planning"""
    return {
        "message": "Voice processing feature coming soon!",
        "capabilities": [
            "Speech-to-text conversion",
            "Natural language understanding",
            "Voice-based trip planning"
        ]
    }

@app.get("/api/v1/ai/task/{task_id}")
async def get_ai_task_status(task_id: str):
    """Get AI task processing status"""
    # For demo purposes, return completed status
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "result": {
            "message": "AI processing completed successfully",
            "data": "Task result data"
        }
    }

# Health and status endpoints
@app.get("/api/v1/status")
async def api_status():
    """Get detailed API status"""
    return {
        "api_version": "1.0.0",
        "status": "operational", 
        "uptime": "running",
        "endpoints": {
            "authentication": "working",
            "trip_management": "working", 
            "ai_chat": "working",
            "image_analysis": "planned",
            "voice_processing": "planned"
        },
        "mock_data": {
            "users": len(mock_users),
            "trips": len(mock_trips),
            "conversations": len(mock_conversations)
        }
    }

# OPTIONS handlers for CORS preflight
@app.options("/api/v1/auth/register")
@app.options("/api/v1/auth/login") 
@app.options("/api/v1/auth/logout")
@app.options("/api/v1/auth/me")
@app.options("/api/v1/auth/google")
@app.options("/api/v1/auth/refresh")
@app.options("/api/v1/trips")
@app.options("/api/v1/trips/{trip_id}")
@app.options("/api/v1/trips/{trip_id}/duplicate")
@app.options("/api/v1/trips/{trip_id}/optimize") 
@app.options("/api/v1/trips/{trip_id}/status")
@app.options("/api/v1/ai/conversation")
@app.options("/api/v1/ai/image-analysis")
@app.options("/api/v1/ai/voice-input")
@app.options("/api/v1/ai/task/{task_id}")
async def handle_options():
    """Handle CORS preflight requests"""
    return {"message": "OK"}

if __name__ == "__main__":
    print("🚀 Starting AI Trip Planner API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        reload=True
    )
