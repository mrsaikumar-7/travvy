from mcps.accomadation import mcp as accomadation_mcp
from mcps.flights import mcp as flights_mcp
from mcps.weather_server import mcp as weather_mcp
from mcps.maps_server import maps_server as maps_mcp
from mcps.train_server import server as train_mcp
from multiprocessing import Process
import asyncio
import os

def run_trains_server():
    print("Starting Trains Server...")
    asyncio.run(train_mcp.run())


def run_maps_server():
    print("Starting Maps Server...")
    asyncio.run(maps_mcp.run())

def run_weather_server():
    print("Starting Weather Server...")
    weather_mcp.run(transport='stdio')

def run_accomadation_server():
    print("Starting Accomodations Server...")
    asyncio.run(
        accomadation_mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=os.getenv("PORT", 8080),
        )
    )

def run_flights_server():
    print("Starting Flights Server...")
    flights_mcp.run(transport='stdio')


if __name__ == "__main__":
    # Start maps_server in a separate process
    processes = []

    # Add each server's process
    processes.append(Process(target=run_trains_server))
    processes.append(Process(target=run_maps_server))
    processes.append(Process(target=run_weather_server))
    processes.append(Process(target=run_accomadation_server))
    processes.append(Process(target=run_flights_server))

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()
