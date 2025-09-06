"""
Super Simple CORS Test API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str = "Test User"

@app.get("/health")
async def health():
    return {"status": "ok", "message": "CORS test API working!"}

@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest):
    return {
        "access_token": f"test-token-{request.email}",
        "refresh_token": "test-refresh-token", 
        "token_type": "bearer",
        "user": {
            "uid": "test-123",
            "email": request.email,
            "display_name": request.display_name,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }

@app.post("/api/v1/auth/login")
async def login(request: RegisterRequest):
    return {
        "access_token": f"test-token-{request.email}",
        "refresh_token": "test-refresh-token",
        "token_type": "bearer", 
        "user": {
            "uid": "test-456",
            "email": request.email,
            "display_name": request.display_name,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
