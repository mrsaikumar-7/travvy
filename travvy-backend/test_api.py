#!/usr/bin/env python3
"""
Simple API test script to verify trip creation functionality
"""

import asyncio
import json
from datetime import datetime, date
from app.services.trip_service import TripService
from app.services.ai_service import AIService
from mock_db import get_mock_database

async def test_trip_creation():
    """Test trip creation functionality"""
    try:
        print("Testing trip creation...")
        
        # Create mock database and trip service  
        mock_db = await get_mock_database()
        trip_service = TripService(db_service=mock_db)
        
        # Test data
        test_data = {
            "destination": "Paris, France",
            "start_date": "2025-06-01",
            "end_date": "2025-06-07",
            "budget": 2000.0,
            "currency": "USD",
            "travelers": {"adults": 2, "children": 0, "infants": 0}
        }
        
        # Create trip
        trip = await trip_service.create_trip(
            user_id="test-user-123",
            **test_data
        )
        
        print(f"✅ Trip created successfully: {trip.tripId}")
        print(f"   Destination: {trip.metadata.destination.name}")
        print(f"   Duration: {trip.metadata.dates.duration} days")
        
        # Test AI service
        print("\nTesting AI service...")
        ai_service = AIService()
        
        itinerary = await ai_service.generate_itinerary(
            conversation_context={
                "destination": test_data["destination"],
                "start_date": test_data["start_date"], 
                "end_date": test_data["end_date"],
                "budget": test_data["budget"],
                "travelers": test_data["travelers"]
            },
            user_preferences={}
        )
        
        print(f"✅ AI itinerary generated")
        print(f"   Days planned: {len(itinerary['itinerary'])}")
        print(f"   Budget summary: {itinerary['budget_summary']['total']}")
        
        # Test hotel recommendations
        hotels = await ai_service.generate_hotel_recommendations(
            destination=test_data["destination"],
            budget=test_data["budget"],
            preferences={}
        )
        
        print(f"✅ Hotel recommendations generated")
        print(f"   Hotels found: {len(hotels)}")
        if hotels:
            print(f"   Example: {hotels[0]['name']} - ${hotels[0]['pricePerNight']}/night")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_trip_creation())
    exit(0 if success else 1)
