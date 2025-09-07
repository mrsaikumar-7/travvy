"""
AI Service

This service handles all AI-powered features including
conversation processing, image analysis, and trip generation using Google Gemini AI.
"""

from typing import Dict, Any, List, Optional
import logging
import json
import asyncio
from datetime import datetime, timedelta
import google.generativeai as genai
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AIService:
    """Service class for AI operations using Google Gemini AI."""
    
    def __init__(self):
        """Initialize Google Gemini AI client."""
        self.settings = get_settings()
        
        # Configure Gemini AI
        if self.settings.GOOGLE_AI_API_KEY:
            genai.configure(api_key=self.settings.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(self.settings.AI_MODEL_NAME)
            logger.info(f"✅ Initialized Google Gemini AI model: {self.settings.AI_MODEL_NAME}")
        else:
            logger.error("❌ GOOGLE_AI_API_KEY not found in environment variables")
            raise ValueError("Google AI API key is required for AI service")
        
        # For fallback reference only - not used in AI generation
        self.destinations_data = {
            "Paris": {
                "country": "France",
                "best_time": "Spring (April-June) or Fall (September-November)",
                "currency": "EUR",
                "activities": ["Eiffel Tower", "Louvre Museum", "Notre-Dame", "Montmartre", "Seine River Cruise"],
                "daily_budget": {"budget": 80, "moderate": 150, "luxury": 300}
            },
            "Tokyo": {
                "country": "Japan", 
                "best_time": "Spring (March-May) or Fall (September-November)",
                "currency": "JPY",
                "activities": ["Sensoji Temple", "Shibuya Crossing", "Tokyo Skytree", "Tsukiji Market", "Meiji Shrine"],
                "daily_budget": {"budget": 60, "moderate": 120, "luxury": 250}
            },
            "Bali": {
                "country": "Indonesia",
                "best_time": "Dry season (April-October)",
                "currency": "IDR", 
                "activities": ["Ubud Rice Terraces", "Tanah Lot Temple", "Mount Batur", "Seminyak Beach", "Monkey Forest"],
                "daily_budget": {"budget": 40, "moderate": 80, "luxury": 180}
            },
            "London": {
                "country": "United Kingdom",
                "best_time": "Late Spring to Early Fall (May-September)",
                "currency": "GBP",
                "activities": ["Big Ben", "London Eye", "British Museum", "Tower Bridge", "Hyde Park"],
                "daily_budget": {"budget": 70, "moderate": 140, "luxury": 280}
            }
        }
        pass
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process AI conversation message."""
        try:
            # TODO: Implement AI conversation processing
            return {
                "conversation_id": conversation_id or "conv_123",
                "messages": [
                    {
                        "content": {"text": "I'd be happy to help you plan your trip!"},
                        "type": "text"
                    }
                ],
                "ai_state": {
                    "suggested_actions": ["set_destination", "set_dates"],
                    "confidence": 0.8
                },
                "context": context or {}
            }
        except Exception as e:
            logger.error(f"AI message processing failed: {str(e)}")
            raise
    
    async def generate_itinerary(
        self,
        conversation_context: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate trip itinerary using Google Gemini AI."""
        try:
            destination = conversation_context.get("destination", "Paris")
            start_date = conversation_context.get("start_date", "2024-06-01")
            end_date = conversation_context.get("end_date", "2024-06-07")
            budget = float(conversation_context.get("budget", 2000))
            travelers = conversation_context.get("travelers", {"adults": 2, "children": 0, "infants": 0})
            
            # Calculate trip duration
            start = datetime.strptime(str(start_date)[:10], "%Y-%m-%d") if isinstance(start_date, str) else start_date
            end = datetime.strptime(str(end_date)[:10], "%Y-%m-%d") if isinstance(end_date, str) else end_date
            duration = (end - start).days
            
            logger.info(f"🤖 Generating AI itinerary for {destination}, {duration} days, budget ${budget}")
            
            # Create simplified prompt for Gemini
            prompt = f"""Create a {duration}-day travel itinerary for {destination} with ${budget} budget for {travelers.get('adults', 2)} adults.

Return only valid JSON in this structure:
{{
  "destination_overview": {{
    "name": "{destination}",
    "best_time_to_visit": "Best time to visit",
    "currency_info": {{"currency": "EUR", "exchange_rate": "Current rate"}},
    "local_culture_tips": ["Tip 1", "Tip 2"],
    "safety_considerations": ["Stay aware of surroundings", "Keep valuables secure"]
  }},
  "itinerary": [
    {{
      "day": 1,
      "date": "{start_date}T00:00:00",
      "theme": "Explore {destination}",
      "activities": [
        {{
          "activityId": "act_0_0",
          "name": "Famous Attraction",
          "description": "Description of activity",
          "location": {{
            "name": "Location Name",
            "placeId": "",
            "coordinates": {{"lat": 41.4036, "lng": 2.1744}},
            "address": "Address",
            "city": "{destination.split(',')[0]}",
            "country": "Country"
          }},
          "timing": {{"start": "09:00", "end": "12:00", "duration": 180}},
          "pricing": {{"adult": 25, "currency": "USD"}},
          "category": "sightseeing",
          "rating": 4.5,
          "images": [],
          "bookingInfo": null,
          "accessibility": {{"mobility": false, "vision": false, "hearing": false}},
          "tags": []
        }}
      ],
      "meals": [
        {{
          "type": "lunch", 
          "restaurant": "Restaurant Name", 
          "cuisine": "Local",
          "budgetRange": "moderate",
          "location": {{"name": "Area Name", "placeId": "", "coordinates": null, "address": "", "country": "", "city": ""}},
          "specialties": ["specialty1", "specialty2"]
        }}
      ],
      "transportation": [
        {{
          "fromLocation": "Hotel",
          "toLocation": "First attraction",
          "method": "Metro",
          "cost": 5.0,
          "durationMinutes": 20,
          "bookingInfo": null
        }}
      ],
      "accommodation": {{
        "name": "Central Hotel Example",
        "type": "hotel",
        "rating": 4.2,
        "priceRange": "moderate",
        "location": {{
          "name": "City Center",
          "placeId": "",
          "coordinates": {{"lat": 41.4036, "lng": 2.1744}},
          "address": "123 Main Street",
          "city": "{destination.split(',')[0]}",
          "country": "Country"
        }},
        "amenities": ["WiFi", "Breakfast", "Air Conditioning"],
        "bookingInfo": null
      }},
      "totalBudget": 120.0,
      "notes": "Day exploring {destination}"
    }}
  ],
  "budget_summary": {{
    "total": {budget},
    "breakdown": {{
      "accommodation": {budget * 0.4},
      "transportation": {budget * 0.2},
      "food": {budget * 0.3},
      "activities": {budget * 0.1}
    }},
    "daily_average": {budget // duration if duration > 0 else budget},
    "cost_optimization_tips": ["Book in advance", "Use public transport", "Eat at local places"]
  }},
  "packing_suggestions": {{
    "essential": ["Passport", "Comfortable shoes", "Camera"],
    "weather_specific": ["Light jacket", "Sunscreen"],
    "activity_specific": ["Walking shoes", "Day pack"]
  }}
}}

IMPORTANT:
- Use real {destination} attractions and accurate coordinates
- Set bookingInfo to null (not a string)
- Include realistic pricing and ratings
- Make all coordinates accurate for the real locations
- For accommodation: Include hotel details for first day (arrival) and special stays. Set to null for regular touring days
- Use proper accommodation object format with name, type, rating, priceRange, location, amenities"""
            
            # Generate with Gemini AI
            logger.info("🔄 Sending request to Gemini AI...")
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.settings.AI_TEMPERATURE,
                    max_output_tokens=8192  # Increased for longer itineraries
                )
            )
            
            logger.info("✅ Received response from Gemini AI")
            
            # Parse the JSON response - handle markdown wrapped responses
            try:
                response_text = response.text.strip()
                logger.info(f"📄 Raw response length: {len(response_text)} characters")
                
                # More robust JSON extraction from markdown blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_end != -1:
                        extracted_json = response_text[json_start:json_end].strip()
                        if extracted_json:  # Ensure we have content
                            response_text = extracted_json
                            logger.info("🔧 Extracted JSON from markdown block")
                        else:
                            logger.warning("⚠️ Empty content in markdown block, using full response")
                elif response_text.startswith("```") and response_text.endswith("```"):
                    # Handle generic code blocks
                    extracted_content = response_text[3:-3].strip()
                    if extracted_content:  # Ensure we have content
                        response_text = extracted_content
                        logger.info("🔧 Extracted content from generic code block")
                    else:
                        logger.warning("⚠️ Empty content in generic code block")
                        
                # Additional cleanup - remove any remaining backticks or markdown
                response_text = response_text.strip('`').strip()
                
                # Check if response starts with '{' as expected for JSON
                if not response_text.startswith('{'):
                    # Try to find JSON object start
                    json_start_idx = response_text.find('{')
                    if json_start_idx != -1:
                        response_text = response_text[json_start_idx:]
                        logger.info(f"🔧 Found JSON start at position {json_start_idx}")
                
                logger.info(f"📄 Processing response: {len(response_text)} characters")
                
                if not response_text:
                    raise ValueError("Empty response after processing")
                
                itinerary_data = json.loads(response_text)
                logger.info(f"✅ Successfully generated {len(itinerary_data.get('itinerary', []))} day itinerary")
                return itinerary_data
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI response as JSON: {e}")
                logger.error(f"📄 First 500 chars: {response_text[:500]}...")
                logger.error(f"📄 Last 500 chars: {response_text[-500:]}")
                raise ValueError(f"AI response is not valid JSON: {e}")
                
        except Exception as e:
            logger.error(f"❌ AI itinerary generation failed: {str(e)}")
            raise
    
    async def enhance_with_places_data(
        self, 
        base_itinerary: Dict[str, Any],
        trip_id: str
    ) -> Dict[str, Any]:
        """Enhance itinerary with Google Places data."""
        try:
            # TODO: Integrate with Google Places API
            return base_itinerary
        except Exception as e:
            logger.error(f"Places data enhancement failed: {str(e)}")
            raise
    
    async def generate_hotel_recommendations(
        self,
        destination: str,
        budget: float,
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate hotel recommendations using Google Gemini AI."""
        try:
            logger.info(f"🏨 Generating AI hotel recommendations for {destination}, budget ${budget}")
            
            # Determine budget level for hotels
            daily_budget = budget / 7  # Assume 7 days for budget calculation
            accommodation_budget = daily_budget * 0.4  # 40% of daily budget for accommodation
            
            budget_level = "budget" if accommodation_budget < 100 else ("moderate" if accommodation_budget < 200 else "luxury")
            
            # Create detailed prompt for hotel recommendations
            prompt = f"""
You are a hotel booking expert. Recommend 3 hotels in {destination} for a budget of ${accommodation_budget:.2f} per night.

REQUIREMENTS:
- Destination: {destination}
- Budget per night: ${accommodation_budget:.2f}
- Budget level: {budget_level}
- Preferences: {json.dumps(preferences)}
- Return 3 diverse hotel options (different price ranges and styles)

Provide a JSON array with this EXACT structure:
[
  {{
    "hotelId": "unique_hotel_id",
    "name": "Real Hotel Name",
    "description": "Detailed description of the hotel and its unique features",
    "location": {{
      "name": "Neighborhood, {destination}",
      "placeId": "place_id_if_available",
      "coordinates": {{"lat": 0.0, "lng": 0.0}},
      "address": "Real street address",
      "city": "{destination.split(',')[0]}",
      "country": "Country name"
    }},
    "rating": 4.2,
    "pricePerNight": 120.00,
    "amenities": ["Free WiFi", "24/7 Reception", "Air Conditioning", "Restaurant"],
    "images": ["image_url_1", "image_url_2", "image_url_3"],
    "bookingUrl": "https://booking.example.com/hotel",
    "totalPrice": 840.00,
    "cancellationPolicy": "Cancellation policy details"
  }}
]

REQUIREMENTS:
1. Use real hotel names that exist in {destination}
2. Provide accurate coordinates for the city
3. Include realistic amenities for each budget level
4. Price the first hotel below budget, second at budget, third slightly above
5. Include diverse neighborhoods/areas
6. Provide realistic ratings (3.5-5.0)
7. Make descriptions informative and appealing
8. Total price should be for 7 nights
9. Ensure JSON is valid
10. Use actual addresses and locations

Focus on well-known, highly-rated hotels in {destination}!
"""
            
            # Generate with Gemini AI
            logger.info("🔄 Sending hotel request to Gemini AI...")
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.settings.AI_TEMPERATURE,
                    max_output_tokens=2048
                )
            )
            
            logger.info("✅ Received hotel response from Gemini AI")
            
            # Parse the JSON response - handle markdown wrapped responses
            try:
                response_text = response.text.strip()
                logger.info(f"🏨 Raw hotel response length: {len(response_text)} characters")
                
                # More robust JSON extraction from markdown blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_end != -1:
                        extracted_json = response_text[json_start:json_end].strip()
                        if extracted_json:  # Ensure we have content
                            response_text = extracted_json
                            logger.info("🔧 Extracted hotel JSON from markdown block")
                        else:
                            logger.warning("⚠️ Empty hotel content in markdown block, using full response")
                elif response_text.startswith("```") and response_text.endswith("```"):
                    # Handle generic code blocks
                    extracted_content = response_text[3:-3].strip()
                    if extracted_content:  # Ensure we have content
                        response_text = extracted_content
                        logger.info("🔧 Extracted hotel content from generic code block")
                    else:
                        logger.warning("⚠️ Empty hotel content in generic code block")
                        
                # Additional cleanup - remove any remaining backticks or markdown
                response_text = response_text.strip('`').strip()
                
                # Check if response starts with '[' (for array) or '{' as expected for JSON
                if not (response_text.startswith('[') or response_text.startswith('{')):
                    # Try to find JSON start
                    json_start_idx = max(response_text.find('['), response_text.find('{'))
                    if json_start_idx != -1:
                        response_text = response_text[json_start_idx:]
                        logger.info(f"🔧 Found hotel JSON start at position {json_start_idx}")
                
                if not response_text:
                    raise ValueError("Empty hotel response after processing")
                
                hotels_data = json.loads(response_text)
                if isinstance(hotels_data, list):
                    logger.info(f"✅ Successfully generated {len(hotels_data)} hotel recommendations")
                    return hotels_data
                else:
                    logger.error(f"❌ Expected list, got: {type(hotels_data)}")
                    raise ValueError("AI response should be a list of hotels")
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse hotel AI response as JSON: {e}")
                logger.error(f"🏨 First 500 chars: {response_text[:500]}...")
                logger.error(f"🏨 Last 500 chars: {response_text[-500:]}")
                raise ValueError(f"AI hotel response is not valid JSON: {e}")
                
        except Exception as e:
            logger.error(f"❌ AI hotel recommendation failed: {str(e)}")
            raise
    
    async def optimize_trip(
        self,
        itinerary: List[Dict[str, Any]],
        hotels: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize trip for efficiency."""
        try:
            # TODO: Implement trip optimization
            return {
                "itinerary": itinerary,
                "hotels": hotels,
                "metadata": {
                    "generation_time": "2.5 seconds",
                    "confidence": 0.85
                }
            }
        except Exception as e:
            logger.error(f"Trip optimization failed: {str(e)}")
            raise
    
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str
    ) -> Dict[str, Any]:
        """Analyze image for travel insights."""
        try:
            # TODO: Implement image analysis with Vision API
            return {
                "landmarks": [],
                "suggestions": [],
                "confidence": 0.0
            }
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise
    
    async def process_voice_intent(
        self,
        transcription: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process voice input for travel intent."""
        try:
            # TODO: Implement voice intent processing
            return {
                "intent": "plan_trip",
                "entities": {},
                "confidence": 0.0,
                "suggested_response": "I heard you want to plan a trip. Where would you like to go?",
                "follow_up_questions": []
            }
        except Exception as e:
            logger.error(f"Voice intent processing failed: {str(e)}")
            raise
    
    async def get_destination_suggestions(
        self,
        query: str,
        user_id: str,
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get AI-powered destination suggestions."""
        try:
            # TODO: Implement destination suggestion logic
            return [
                {
                    "name": "Paris, France",
                    "description": "City of lights with rich culture",
                    "best_time": "Spring/Fall",
                    "estimated_budget": 2000,
                    "match_score": 0.9
                }
            ]
        except Exception as e:
            logger.error(f"Destination suggestions failed: {str(e)}")
            raise
