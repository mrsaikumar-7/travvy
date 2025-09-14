import asyncio
import json
import logging
import sys
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (important: NOT stdout!)
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Import your service functions (these call RTT API)
from trains import (
    get_station_live_status,
    get_train_details,
    get_trains_between_stations,
    get_train_route,
    get_trains_on_date,
    get_pnr_status,
)

# Initialize MCP server
server = FastMCP("indian-railways-mcp")


# ---------------------------
# Tools
# ---------------------------

@server.tool()
async def get_station_live_status_tool(stationCode: str):
    """Get live station status"""
    try:
        station_code = stationCode.upper()
        resp = await get_station_live_status(station_code)
        return {"content": [{"type": "text", "text": json.dumps(resp)}]}
    except Exception as e:
        logging.error(f"Station status error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


@server.tool()
async def get_train_details_tool(trainNumber: str):
    """Get train details by train number"""
    try:
        resp = await get_train_details(trainNumber)
        return {"content": [{"type": "text", "text": json.dumps(resp)}]}
    except Exception as e:
        logging.error(f"Train details error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


@server.tool()
async def get_trains_between_stations_tool(from_: str, to: str):
    """Get trains between two stations"""
    try:
        resp = await get_trains_between_stations(from_, to)
        return {"content": [{"type": "text", "text": json.dumps(resp)}]}
    except Exception as e:
        logging.error(f"Between stations error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


@server.tool()
async def get_train_route_tool(trainNumber: str):
    """Get train route by train number"""
    try:
        resp = await get_train_route(trainNumber)
        return {"content": [{"type": "text", "text": json.dumps(resp)}]}
    except Exception as e:
        logging.error(f"Train route error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


@server.tool()
async def get_trains_on_date_tool(from_: str, to: str, date: str):
    """Get trains between two stations on a specific date"""
    try:
        resp = await get_trains_on_date(from_, to, date)
        return {"content": [{"type": "text", "text": json.dumps(resp)}]}
    except Exception as e:
        logging.error(f"Trains on date error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


@server.tool()
async def get_pnr_status_tool(pnrNumber: str):
    """Get PNR status by PNR number"""
    try:
        resp = await get_pnr_status(pnrNumber)
        return {"content": [{"type": "text", "text": json.dumps(resp)}]}
    except Exception as e:
        logging.error(f"PNR status error: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
