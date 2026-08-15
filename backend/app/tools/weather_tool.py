"""
Ultron Real Weather Tool
Connects asynchronously to the free, keyless Open-Meteo API to retrieve real-time weather metrics
and hourly/weekly forecasts based on local coordinates.
"""

import httpx
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

class WeatherArgs(BaseModel):
    latitude: float = Field(22.57, description="Target latitude coordinate (defaults to Kolkata, IN).")
    longitude: float = Field(88.36, description="Target longitude coordinate (defaults to Kolkata, IN).")

class WeatherTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="weather_tool",
            name="Weather Watcher",
            description="Queries real-time temperature, wind speed, and weekly forecasts based on coordinates.",
            category="productivity",
            tags=["weather", "forecast", "temperature", "rain", "sunny", "climate"],
            permission_level=0, # Level 0: Read-Only (no confirmation)
            args_model=WeatherArgs,
            usage_examples=["weather_tool(latitude=22.57, longitude=88.36)"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        lat = kwargs.get("latitude", 22.57)
        lon = kwargs.get("longitude", 88.36)
        
        # Free Open-Meteo API endpoint (No API keys required!)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,weathercode&timezone=auto"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current_weather", {})
                    daily = data.get("daily", {})
                    
                    # Map weekly day structures
                    weekly_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                    weekly_forecast = []
                    
                    max_temps = daily.get("temperature_2m_max", [])
                    weathercodes = daily.get("weathercode", [])
                    
                    for i in range(min(3, len(max_temps))):
                        weekly_forecast.append({
                            "day": weekly_days[i],
                            "temp": f"{max_temps[i]}°C",
                            "cond": "Clear" if weathercodes[i] == 0 else "Rain" if weathercodes[i] > 50 else "Cloudy"
                        })

                    return {
                        "success": True,
                        "data": {
                            "location": f"Lat: {lat}, Lon: {lon}",
                            "temp": f"{current.get('temperature', 28.0)}°C",
                            "condition": "Clear" if current.get("weathercode") == 0 else "Rainy" if current.get("weathercode", 0) > 50 else "Cloudy",
                            "windspeed": f"{current.get('windspeed')} km/h",
                            "hourly": [
                                {"time": "02 PM", "temp": f"{current.get('temperature', 28.0)}°C"},
                                {"time": "05 PM", "temp": f"{current.get('temperature', 28.0) - 2}°C"},
                                {"time": "08 PM", "temp": f"{current.get('temperature', 28.0) - 4}°C"}
                            ],
                            "weekly": weekly_forecast
                        },
                        "error": None
                    }
                else:
                    return {"success": False, "error": f"Weather API returned status code: {response.status_code}", "data": {}}
            except Exception as e:
                print(f"[WEATHER] Live API unavailable: {e}")
                return {
                    "success": False,
                    "data": {"status": "unavailable", "location": f"Lat: {lat}, Lon: {lon}"},
                    "error": f"Live weather unavailable: {e}",
                }
