import asyncio
import logging
import os
import httpx
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from fastmcp import FastMCP

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Hotel MCP Server 🏨🏩🏨")

# Constants for RapidAPI
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "booking-com15.p.rapidapi.com")

# Validate required environment variables
if not RAPIDAPI_KEY:
    logger.warning("RAPIDAPI_KEY environment variable is not set. Live hotel data will not be available.")

async def make_rapidapi_request(endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Make a request to the RapidAPI with proper error handling."""
    if not RAPIDAPI_KEY:
        return {"error": "API key not configured"}
        
    url = f"https://{RAPIDAPI_HOST}{endpoint}"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    logger.info(f">>> 🌐 Making API request to {endpoint} with params: {params}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            logger.info(f">>> ✅ API request to {endpoint} successful")
            return response.json()
        except Exception as e:
            logger.error(f">>> ❌ API request to {endpoint} failed: {str(e)}")
            return {"error": str(e)}

@mcp.tool()
async def search_destinations(query: str) -> List[Dict[str, Any]]:
    """
    Search for hotel destinations by name using live data.
    Can be used to find destination IDs needed for hotel searches.

    Args:
        query: The destination to search for (e.g., "Paris", "New York", "Tokyo")

    Returns:
        A list of destination dictionaries with details like name, type, city_id, region, country, and coordinates.
    """
    logger.info(f">>> 🛠️ Tool: 'search_destinations' called for '{query}'")
    endpoint = "/api/v1/hotels/searchDestination"
    params = {"query": query}
    
    result = await make_rapidapi_request(endpoint, params)
    
    if "error" in result:
        logger.error(f">>> ❌ Error in search_destinations: {result['error']}")
        return [{"error": f"Error fetching destinations: {result['error']}"}]
    
    destinations = []
    if "data" in result and isinstance(result["data"], list):
        destinations_count = len(result["data"])
        logger.info(f">>> 📍 Found {destinations_count} destinations for query: {query}")
        for destination in result["data"]:
            dest_info = {
                "name": destination.get('name', 'Unknown'),
                "type": destination.get('dest_type', 'Unknown'),
                "city_id": destination.get('city_ufi', 'N/A'),
                "region": destination.get('region', 'Unknown'),
                "country": destination.get('country', 'Unknown'),
                "coordinates": {
                    "lat": destination.get('latitude', 'N/A'),
                    "lng": destination.get('longitude', 'N/A')
                }
            }
            destinations.append(dest_info)
    
    return destinations if destinations else [{"message": "No destinations found matching your query"}]

@mcp.tool()
async def get_hotels(destination_id: str, checkin_date: str, checkout_date: str, adults: int = 2) -> List[Dict[str, Any]]:
    """
    Get live hotels data for a specific destination using real booking API.
    
    Args:
        destination_id: The destination ID (city_ufi from search_destinations)
        checkin_date: Check-in date in YYYY-MM-DD format
        checkout_date: Check-out date in YYYY-MM-DD format
        adults: Number of adults (default: 2)

    Returns:
        A list of hotel dictionaries with live pricing, availability, and details.
    """
    logger.info(f">>> 🛠️ Tool: 'get_hotels' called for destination_id: {destination_id}, checkin: {checkin_date}, checkout: {checkout_date}, adults: {adults}")
    endpoint = "/api/v1/hotels/searchHotels"
    params = {
        "dest_id": destination_id,
        "search_type": "CITY",
        "arrival_date": checkin_date,
        "departure_date": checkout_date,
        "adults": str(adults)
    }
    
    result = await make_rapidapi_request(endpoint, params)
    
    if "error" in result:
        logger.error(f">>> ❌ Error in get_hotels: {result['error']}")
        return [{"error": f"Error fetching hotels: {result['error']}"}]
    
    hotels = []
    if "data" in result and "hotels" in result["data"] and isinstance(result["data"]["hotels"], list):
        hotels_count = len(result["data"]["hotels"])
        logger.info(f">>> 🏨 Found {hotels_count} hotels for destination: {destination_id}")
        hotel_list = result["data"]["hotels"]
        
        for hotel_entry in hotel_list[:10]:  # Limit to 10 hotels for performance
            if "property" in hotel_entry:
                property_data = hotel_entry["property"]
                
                # Parse accessibility label for room info
                room_info = "Not available"
                accessibility_label = hotel_entry.get("accessibilityLabel", "")
                if accessibility_label:
                    room_match = re.search(r'(Hotel room|Entire villa|Private suite|Private room)[^\.]*', accessibility_label)
                    if room_match:
                        room_info = room_match.group(0).strip()
                
                hotel_info = {
                    "name": property_data.get('name', 'Unknown'),
                    "location": property_data.get('wishlistName', 'Unknown'),
                    "rating": property_data.get('reviewScore', 'N/A'),
                    "review_count": property_data.get('reviewCount', 'N/A'),
                    "review_word": property_data.get('reviewScoreWord', 'N/A'),
                    "room_type": room_info,
                    "coordinates": {
                        "lat": property_data.get('latitude', 'N/A'),
                        "lng": property_data.get('longitude', 'N/A')
                    },
                    "stars": property_data.get('propertyClass', 'N/A'),
                    "photo_url": property_data.get('photoUrls', [None])[0],
                    "checkin_times": property_data.get('checkin', {}),
                    "checkout_times": property_data.get('checkout', {})
                }
                
                # Add pricing info if available
                if "priceBreakdown" in property_data and "grossPrice" in property_data["priceBreakdown"]:
                    price_data = property_data["priceBreakdown"]["grossPrice"]
                    hotel_info["price"] = {
                        "currency": price_data.get('currency', '$'),
                        "amount": price_data.get('value', 'N/A')
                    }
                    
                    # Add discount information if available
                    if "strikethroughPrice" in property_data["priceBreakdown"]:
                        original_price = property_data["priceBreakdown"]["strikethroughPrice"].get("value", "N/A")
                        if original_price != "N/A":
                            try:
                                current = float(price_data.get('value', 0))
                                original = float(original_price)
                                if original > 0:
                                    discount_pct = round((1 - current/original) * 100)
                                    hotel_info["discount_percentage"] = discount_pct
                            except (ValueError, TypeError):
                                pass
                else:
                    hotel_info["price"] = {"currency": "N/A", "amount": "Not available"}
                
                hotels.append(hotel_info)
    
    return hotels if hotels else [{"message": "No hotels found for this destination and dates"}]

@mcp.tool()
async def search_hotels_by_location(location: str, checkin_date: str, checkout_date: str, adults: int = 2) -> List[Dict[str, Any]]:
    """
    Convenience function to search hotels by location name (combines destination search + hotel search).
    
    Args:
        location: The location name (e.g., "Paris", "New York", "Tokyo")
        checkin_date: Check-in date in YYYY-MM-DD format
        checkout_date: Check-out date in YYYY-MM-DD format
        adults: Number of adults (default: 2)

    Returns:
        A list of hotel dictionaries with live data for the specified location.
    """
    logger.info(f">>> 🛠️ Tool: 'search_hotels_by_location' called for location: '{location}', checkin: {checkin_date}, checkout: {checkout_date}")
    
    # First, search for destinations
    destinations = await search_destinations(location)
    
    if not destinations or "error" in destinations[0]:
        return destinations
    
    # Use the first destination found
    destination_id = destinations[0].get("city_id")
    if destination_id == "N/A":
        return [{"error": "Could not find destination ID for the specified location"}]
    
    # Search for hotels in that destination
    return await get_hotels(destination_id, checkin_date, checkout_date, adults)
