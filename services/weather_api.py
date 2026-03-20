import json
from dotenv import load_dotenv
from pathlib import Path
import os
import requests

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = os.getenv("WEATHER_API_KEY")
SETTINGS_PATH = Path(__file__).parent.parent / "data" / "settings.json"

def get_city():
    if not SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "w") as f:
            json.dump({"city": "london"}, f, indent=2)
        return "london"
    with open(SETTINGS_PATH) as f:
        return json.load(f)["city"]

def get_data():
    url = BASE_URL + "appid=" + API_KEY + "&q=" + get_city() + "&units=metric"
    response = requests.get(url)
    response.raise_for_status()     
    return response.json()

def get_location(data):
    return data["name"], data["sys"]["country"]

def get_temperature(data) -> int:
    return int(data["main"]["temp"])

def get_temperature_feels_like(data) -> int:
    return int(data["main"]["feels_like"])

def get_humidity(data) -> int:
    return int(data["main"]["humidity"])

def get_rain_chance(data):
    return data.get("rain", {}).get("1h", 0)
