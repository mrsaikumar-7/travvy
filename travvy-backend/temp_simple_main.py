"""
Temporary Simple FastAPI Main - For CORS Testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="AI Trip Planner API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000"
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

class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None
    profile: Optional[dict] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

@app.get("/")
async def root():
    return {
        "message": "AI Trip Planner API",
        "version": "1.0.0", 
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
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
        "features": ["Trip Planning", "AI Integration"]
    }

@app.post("/api/v1/auth/register")
async def register_user(request: RegisterRequest):
    """Simplified registration for CORS testing."""
    
    # Mock user creation for testing
    mock_user = {
        "uid": "test-user-123",
        "email": request.email,
        "display_name": request.display_name or "Test User",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    mock_token = "mock-jwt-token-" + request.email.replace("@", "-at-")
    
    return AuthResponse(
        access_token=mock_token,
        refresh_token="mock-refresh-token",
        token_type="bearer",
        user=mock_user
    )

@app.post("/api/v1/auth/login")
async def login_user(request: LoginRequest):
    """Simplified login for CORS testing."""
    
    # Demo login check
    if request.email == "demo@Travvy.com" and request.password == "demo123":
        mock_user = {
            "uid": "demo-user-123",
            "email": "demo@Travvy.com",
            "display_name": "Demo User",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        return AuthResponse(
            access_token="demo-jwt-token-123",
            refresh_token="demo-refresh-token",
            token_type="bearer",
            user=mock_user
        )
    
    # For other users, create mock response
    mock_user = {
        "uid": "test-user-456", 
        "email": request.email,
        "display_name": "Test User",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    return AuthResponse(
        access_token=f"mock-jwt-{request.email.replace('@', '-')}",
        refresh_token="mock-refresh-token",
        token_type="bearer", 
        user=mock_user
    )

@app.options("/api/v1/auth/register")
async def options_register():
    """Handle CORS preflight for register."""
    return {"message": "OK"}

@app.options("/api/v1/auth/login") 
async def options_login():
    """Handle CORS preflight for login."""
    return {"message": "OK"}

if __name__ == "__main__":
    uvicorn.run("temp_simple_main:app", host="0.0.0.0", port=8000, reload=True)
