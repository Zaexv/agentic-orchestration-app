"""
Weather tools for agents.

Provides weather information using free weather APIs.
"""

import requests
from typing import Optional, Dict, Any
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool
def get_weather(location: str) -> str:
    """
    Get current weather information for a location.
    
    Args:
        location: City name, address, or location (e.g., "London", "New York", "Tokyo")
    
    Returns:
        Weather information including temperature, conditions, and forecast
    
    Example:
        >>> get_weather("London")
        "Weather in London: 15°C, Partly cloudy, Humidity: 65%, Wind: 10 km/h"
    """
    try:
        # Use wttr.in API - free, no API key required
        url = f"https://wttr.in/{location}?format=j1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract current conditions
        current = data.get("current_condition", [{}])[0]
        location_name = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", location)
        
        # Build weather report
        temp_c = current.get("temp_C", "N/A")
        temp_f = current.get("temp_F", "N/A")
        feels_like_c = current.get("FeelsLikeC", "N/A")
        condition = current.get("weatherDesc", [{}])[0].get("value", "N/A")
        humidity = current.get("humidity", "N/A")
        wind_speed = current.get("windspeedKmph", "N/A")
        wind_dir = current.get("winddir16Point", "N/A")
        precip = current.get("precipMM", "N/A")
        
        weather_report = f"""Weather in {location_name}:
🌡️ Temperature: {temp_c}°C ({temp_f}°F)
🤔 Feels like: {feels_like_c}°C
☁️ Conditions: {condition}
💧 Humidity: {humidity}%
🌬️ Wind: {wind_speed} km/h {wind_dir}
🌧️ Precipitation: {precip} mm"""
        
        # Add forecast if available
        if "weather" in data and len(data["weather"]) > 0:
            tomorrow = data["weather"][0]
            max_temp = tomorrow.get("maxtempC", "N/A")
            min_temp = tomorrow.get("mintempC", "N/A")
            weather_report += f"\n\n📅 Forecast: High {max_temp}°C, Low {min_temp}°C"
        
        logger.info(f"Weather fetched successfully for: {location}")
        return weather_report
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching weather for {location}: {str(e)}"
        logger.error(error_msg)
        return f"Sorry, I couldn't fetch the weather for {location}. Please check the location name and try again."
    except (KeyError, IndexError, TypeError) as e:
        error_msg = f"Error parsing weather data for {location}: {str(e)}"
        logger.error(error_msg)
        return f"Sorry, I received unexpected data from the weather service for {location}."


@tool
def get_weather_forecast(location: str, days: int = 3) -> str:
    """
    Get weather forecast for upcoming days.
    
    Args:
        location: City name or location
        days: Number of days to forecast (1-3, default 3)
    
    Returns:
        Multi-day weather forecast
    
    Example:
        >>> get_weather_forecast("Paris", days=2)
        "2-day forecast for Paris: ..."
    """
    try:
        # Limit days to 3 (free API limit)
        days = min(max(1, days), 3)
        
        url = f"https://wttr.in/{location}?format=j1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        location_name = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", location)
        
        forecast_report = f"📅 {days}-day forecast for {location_name}:\n\n"
        
        weather_data = data.get("weather", [])[:days]
        
        for day_data in weather_data:
            date = day_data.get("date", "N/A")
            max_temp = day_data.get("maxtempC", "N/A")
            min_temp = day_data.get("mintempC", "N/A")
            condition = day_data.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", "N/A")
            
            forecast_report += f"📆 {date}:\n"
            forecast_report += f"   🌡️ {min_temp}°C - {max_temp}°C\n"
            forecast_report += f"   ☁️ {condition}\n\n"
        
        logger.info(f"Forecast fetched successfully for: {location}")
        return forecast_report
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching forecast for {location}: {str(e)}"
        logger.error(error_msg)
        return f"Sorry, I couldn't fetch the forecast for {location}."
    except (KeyError, IndexError, TypeError) as e:
        error_msg = f"Error parsing forecast data for {location}: {str(e)}"
        logger.error(error_msg)
        return f"Sorry, I received unexpected data from the weather service."


# Export tools list for easy integration
weather_tools = [get_weather, get_weather_forecast]
