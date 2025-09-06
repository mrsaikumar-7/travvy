"""
Test cases for the main application.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Travvy API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_docs():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_google_auth_endpoint_exists(self):
        """Test that Google auth endpoint exists."""
        response = client.post("/api/v1/auth/google", json={"id_token": "invalid_token"})
        # Should return 401 for invalid token, not 404
        assert response.status_code != 404


class TestTrips:
    """Test trip-related endpoints."""
    
    def test_create_trip_requires_auth(self):
        """Test that creating a trip requires authentication."""
        trip_data = {
            "destination": "Paris, France",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "budget": 2000,
            "currency": "USD",
            "travelers": {"adults": 2, "children": 0}
        }
        response = client.post("/api/v1/trips/", json=trip_data)
        assert response.status_code == 401  # Unauthorized


class TestAI:
    """Test AI-related endpoints."""
    
    def test_ai_conversation_requires_auth(self):
        """Test that AI conversation requires authentication."""
        conversation_data = {
            "message": "I want to plan a trip to Tokyo",
            "context": {}
        }
        response = client.post("/api/v1/ai/conversation", json=conversation_data)
        assert response.status_code == 401  # Unauthorized
