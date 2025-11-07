from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/api", tags=["weather"])

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

@router.get("/weather")
async def weather(city: str):
    async with httpx.AsyncClient(timeout=10) as client:
        # 1) Geocode city → coords
        g = await client.get(GEOCODE_URL, params={"name": city, "count": 1})
        g.raise_for_status()
        data = g.json()
        if not data.get("results"):
            raise HTTPException(status_code=404, detail="City not found")
        r0 = data["results"][0]
        lat, lon = r0["latitude"], r0["longitude"]

        # 2) 7-day daily forecast
        f = await client.get(FORECAST_URL, params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "forecast_days": 7,
            "timezone": "auto",
        })
        f.raise_for_status()
        return f.json()