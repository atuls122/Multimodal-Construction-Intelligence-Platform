"""Epic 4 (part) - Weather-aware daily guidance using free Open-Meteo APIs (no key needed)."""
import requests

from .gemini_client import ask_text

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def geocode(city: str) -> dict | None:
    r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    top = results[0]
    return {"name": f"{top['name']}, {top.get('country', '')}", "lat": top["latitude"], "lon": top["longitude"]}


def get_forecast(lat: float, lon: float, days: int = 3) -> list[dict]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": days,
    }
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    d = r.json()["daily"]
    return [
        {
            "date": d["time"][i],
            "temp_max_c": d["temperature_2m_max"][i],
            "temp_min_c": d["temperature_2m_min"][i],
            "rain_mm": d["precipitation_sum"][i],
            "wind_kmh": d["wind_speed_10m_max"][i],
        }
        for i in range(len(d["time"]))
    ]


def daily_guidance(client, city: str, forecast: list[dict], activities: str) -> str:
    prompt = f"""You are a construction site planner. Location: {city}.
Planned activities: {activities}

Forecast (next days):
{forecast}

For each day give: a go / caution / avoid rating for the planned work, the reason,
and 2-3 practical actions (e.g. concrete pouring and curing in rain or heat, crane use in wind,
worker hydration, covering materials). Keep it concise and use a heading per day."""
    return ask_text(client, prompt)
