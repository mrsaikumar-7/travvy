#!/usr/bin/env python3
import os
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP 
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Load API Key from environment
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("❌ GOOGLE_MAPS_API_KEY environment variable not set.")

# Initialize MCP server
maps_server = FastMCP("google-maps")

# ----------------------
# Tool Implementations
# ----------------------

@maps_server.tool()
async def maps_geocode(address: str) -> dict:
    """Convert an address into geographic coordinates."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"address": address, "key": GOOGLE_MAPS_API_KEY})
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    result = data["results"][0]
    return {
        "location": result["geometry"]["location"],
        "formatted_address": result["formatted_address"],
        "place_id": result["place_id"],
    }

@maps_server.tool()
async def maps_reverse_geocode(latitude: float, longitude: float) -> dict:
    """Convert coordinates into an address."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"latlng": f"{latitude},{longitude}", "key": GOOGLE_MAPS_API_KEY})
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    result = data["results"][0]
    return {
        "formatted_address": result["formatted_address"],
        "place_id": result["place_id"],
        "address_components": result["address_components"],
    }

@maps_server.tool()
async def maps_search_places(query: str, latitude: float = None, longitude: float = None, radius: int = None) -> dict:
    """Search for places using Google Places API."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_MAPS_API_KEY}
    if latitude and longitude:
        params["location"] = f"{latitude},{longitude}"
    if radius:
        params["radius"] = str(radius)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    return {
        "places": [
            {
                "name": p["name"],
                "formatted_address": p.get("formatted_address"),
                "location": p["geometry"]["location"],
                "place_id": p["place_id"],
                "rating": p.get("rating"),
                "types": p.get("types", []),
            }
            for p in data["results"]
        ]
    }

@maps_server.tool()
async def maps_place_details(place_id: str) -> dict:
    """Get detailed information about a specific place."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"place_id": place_id, "key": GOOGLE_MAPS_API_KEY})
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    return data["result"]

@maps_server.tool()
async def maps_distance_matrix(origins: list[str], destinations: list[str], mode: str = "driving") -> dict:
    """Calculate travel distance and time between origins and destinations."""
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": mode,
            "key": GOOGLE_MAPS_API_KEY,
        })
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    return data

@maps_server.tool()
async def maps_elevation(locations: list[dict]) -> dict:
    """Get elevation data for given coordinates."""
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    loc_str = "|".join([f"{loc['latitude']},{loc['longitude']}" for loc in locations])
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"locations": loc_str, "key": GOOGLE_MAPS_API_KEY})
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    return {"results": data["results"]}

@maps_server.tool()
async def maps_directions(origin: str, destination: str, mode: str = "driving") -> dict:
    """Get directions between two points."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": GOOGLE_MAPS_API_KEY,
        })
    data = resp.json()
    if data["status"] != "OK":
        return {"error": data.get("error_message", data["status"])}
    return {"routes": data["routes"]}

# ----------------------
# Run the server
# ----------------------
if __name__ == "__main__":
    print("started")
    asyncio.run(maps_server.run())
