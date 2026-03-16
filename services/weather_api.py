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

def getData():
    url = BASE_URL + "appid=" + API_KEY + "&q=" + get_city() + "&units=metric"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def getLocation(data):
    return data["name"], data["sys"]["country"]

def getTemperature(data):
    return data["main"]["temp"], data["main"]["feels_like"]

def getHumidity(data):
    return data["main"]["humidity"]

def getRainChance(data):
    return data.get("rain", {}).get("1h", 0)

def getWeatherIcon(data):
    icon_code = data["weather"][0]["icon"]
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
