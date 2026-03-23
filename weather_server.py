import os
from dotenv import load_dotenv
import requests
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("weather-server")

WEATHER_API_KEY = os.getenv("WEATHERAPI_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@mcp.tool()
def get_weather(city: str):
    """Get live weather data for a city"""
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}")
    data = response.json()
    return data

@mcp.tool()
def tavily_search(query: str):
    """Search the web using Tavily"""
    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": 5
        }
    )
    data = response.json()
    return data

if __name__ == "__main__":
    mcp.run()