import os
from dotenv import load_dotenv
import requests
from mcp.server.fastmcp import FastMCP
load_dotenv()
mcp = FastMCP("weather-server")
API_KEY=os.getenv("WEATHERAPI_KEY")
@mcp.tool()
def get_weather(city: str):
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}")
    data = response.json()
    return data

if __name__ == "__main__":
    mcp.run()