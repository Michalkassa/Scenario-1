import json
from pathlib import Path
import requests

SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"

# City name to (latitude, longitude, country) mapping
CITY_COORDS = {
    "london": (51.5085, -0.1257, "UK"),
    "new york": (40.7128, -74.0060, "USA"),
    "paris": (48.8566, 2.3522, "France"),
    "tokyo": (35.6762, 139.6503, "Japan"),
    "sydney": (-33.8688, 151.2093, "Australia"),
    "dubai": (25.2048, 55.2708, "UAE"),
}

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_city():
    if not SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "w") as f:
            json.dump({"city": "london"}, f, indent=2)
        return "london"
    with open(SETTINGS_PATH) as f:
        data = json.load(f)
        city = str(data.get("city", "london")).strip().lower()
        return city or "london"


def _request_weather(city):
    """Request weather from Open-Meteo API (no API key needed)"""
    if city.lower() not in CITY_COORDS:
        city = "london"
    
    coords = CITY_COORDS[city.lower()]
    lat, lon, country = coords
    
    response = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m"],
            "temperature_unit": "celsius",
        },
        timeout=6,
    )
    response.raise_for_status()
    data = response.json()
    data["_city"] = city.title()
    data["_country"] = country
    return data


def get_data():
    """Fetch weather data from Open-Meteo (no API key required)"""
    primary_city = get_city()
    for candidate in (primary_city, "london"):
        try:
            return _request_weather(candidate)
        except requests.RequestException:
            continue
    return None


def get_location(data):
    """Extract location from Open-Meteo response"""
    if data is None:
        return "Unknown", "UK"
    return data.get("_city", "Unknown"), data.get("_country", "UK")


def get_temperature(data) -> int:
    """Extract current temperature in Celsius"""
    return int(data["current"]["temperature_2m"])


def get_temperature_feels_like(data) -> int:
    """Extract feels-like temperature (approximate using humidity)"""
    # Open-Meteo doesn't provide feels_like directly, so we'll use actual temp
    return int(data["current"]["temperature_2m"])


def get_humidity(data) -> int:
    """Extract relative humidity percentage"""
    return int(data["current"]["relative_humidity_2m"])


def get_rain_chance(data):
    """Extract rain/precipitation data"""
    # Open-Meteo doesn't return rain chance in current weather
    # Return 0 or could be extended with hourly data
    return 0
