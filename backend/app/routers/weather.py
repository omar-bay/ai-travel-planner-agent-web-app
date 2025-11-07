# backend/app/routers/weather.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, List

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["weather"])

# ---- Open-Meteo endpoints
GEOCODING_BASE = "https://geocoding-api.open-meteo.com/v1"
FORECAST_BASE  = "https://api.open-meteo.com/v1/forecast"
AIR_BASE       = "https://air-quality-api.open-meteo.com/v1/air-quality"
MARINE_BASE    = "https://marine-api.open-meteo.com/v1/marine"
ELEVATION_URL  = "https://api.open-meteo.com/v1/elevation"

UA = {"User-Agent": "ai-travel-planner/1.0 (+https://example.com/)"}

# Weather code → plain text
WCODE = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Heavy freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Violent showers",
    85: "Light snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm (light hail)", 99: "Thunderstorm (heavy hail)",
}

def wind_text(ms: Optional[float]) -> str:
    if ms is None: return "—"
    if ms < 3:  return "calm"
    if ms < 8:  return "light breeze"
    if ms < 14: return "moderate breeze"
    if ms < 21: return "fresh breeze"
    if ms < 27: return "strong wind"
    return "gale"

def aqi_category(us_aqi: Optional[float]) -> str:
    if us_aqi is None: return "Unknown"
    v = float(us_aqi)
    if v <= 50:   return "Good"
    if v <= 100:  return "Moderate"
    if v <= 150:  return "Unhealthy for Sensitive Groups"
    if v <= 200:  return "Unhealthy"
    if v <= 300:  return "Very Unhealthy"
    return "Hazardous"

def pack_tips(day: dict) -> List[str]:
    tips = []
    if (day.get("precip_probability", 0) or 0) >= 50 or (day.get("precip_mm", 0) or 0) >= 2:
        tips.append("Light rain jacket / compact umbrella")
    if (day.get("uv_index_max", 0) or 0) >= 7:
        tips.append("High-SPF sunscreen & hat")
    if (day.get("min_c", 999) or 999) < 8:
        tips.append("Warm layer for chilly evenings")
    if (day.get("wind_max_ms", 0) or 0) >= 10:
        tips.append("Windbreaker")
    return tips

def beach_outlook(max_wave_m: Optional[float]) -> str:
    if max_wave_m is None: return "No near-coast data"
    if max_wave_m < 0.5: return "Calm seas — great beach/swim conditions"
    if max_wave_m < 1.5: return "Moderate waves — suitable for most swimmers"
    if max_wave_m < 2.5: return "Rough — exercise caution"
    return "High surf — not ideal for swimming"

async def _get(client: httpx.AsyncClient, url: str, params: dict) -> dict:
    r = await client.get(url, params=params, headers=UA, timeout=30)
    if r.status_code >= 400:
        try:
            reason = r.json()
        except Exception:
            reason = r.text
        raise HTTPException(status_code=r.status_code, detail={"url": str(r.url), "error": reason})
    return r.json()

async def geocode_city(client: httpx.AsyncClient, city: str, count: int = 1, language: str = "en") -> dict:
    data = await _get(client, f"{GEOCODING_BASE}/search", {"name": city, "count": count, "language": language})
    results = data.get("results") or []
    if not results:
        raise HTTPException(status_code=404, detail=f"No geocoding match for city={city!r}")
    return results[0]

async def fetch_forecast(client: httpx.AsyncClient, lat: float, lon: float, tz: str, forecast_days: int) -> dict:
    params = {
        "latitude": lat, "longitude": lon, "timezone": tz, "timeformat": "unixtime",
        "forecast_days": max(1, min(forecast_days, 16)),
        "hourly": ",".join([
            "temperature_2m","weathercode",
            "precipitation_probability","precipitation",
            "wind_speed_10m","uv_index","is_day"
        ]),
        "daily": ",".join([
            "weathercode","temperature_2m_max","temperature_2m_min",
            "uv_index_max","precipitation_sum","precipitation_probability_max",
            "wind_speed_10m_max","wind_gusts_10m_max","sunrise","sunset"
        ]),
        "current": ",".join([
            "temperature_2m","relative_humidity_2m","wind_speed_10m",
            "precipitation","cloud_cover","weathercode","uv_index"
        ]),
    }
    return await _get(client, FORECAST_BASE, params)

async def fetch_air(client: httpx.AsyncClient, lat: float, lon: float, tz: str) -> dict:
    now = datetime.now(timezone.utc)
    params = {
        "latitude": lat, "longitude": lon, "timezone": tz, "timeformat": "unixtime",
        "hourly": ",".join(["pm2_5","pm10","us_aqi","european_aqi","uv_index"]),
        "current": ",".join(["us_aqi","pm2_5","pm10"]),
        "_ts": int(now.timestamp()),
    }
    return await _get(client, AIR_BASE, params)

async def fetch_marine(client: httpx.AsyncClient, lat: float, lon: float, tz: str, forecast_days: int) -> dict:
    now = datetime.now(timezone.utc)
    params = {
        "latitude": lat, "longitude": lon, "timezone": tz, "timeformat": "unixtime",
        "forecast_days": max(1, min(forecast_days, 16)),
        "hourly": "wave_height,sea_surface_temperature",
        "daily": "wave_height_max,sea_surface_temperature_max,sea_surface_temperature_min",
        "_ts": int(now.timestamp()),
    }
    return await _get(client, MARINE_BASE, params)

async def fetch_elev(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    now = datetime.now(timezone.utc)
    return await _get(client, ELEVATION_URL, {"latitude": lat, "longitude": lon, "_ts": int(now.timestamp())})

def summarize_forecast(raw: dict, days: int) -> dict:
    """Turn Open-Meteo forecast into human-friendly blocks."""
    current = raw.get("current", {}) or {}
    daily = raw.get("daily", {}) or {}
    d_time = daily.get("time") or []
    n = min(days, len(d_time))

    # current snapshot
    cur_desc = WCODE.get(current.get("weathercode"), "—")
    current_block = {
        "summary": cur_desc,
        "temp_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature", current.get("temperature_2m")),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_ms": current.get("wind_speed_10m"),
        "wind_text": wind_text(current.get("wind_speed_10m")),
        "uv_index": current.get("uv_index"),
        "precip_mm": current.get("precipitation"),
    }

    # per-day cards
    def dval(key, i, default=None):
        arr = daily.get(key); 
        return arr[i] if (arr and i < len(arr)) else default

    days_out: List[dict] = []
    for i in range(n):
        wcode = dval("weathercode", i)
        day = {
            "date": datetime.fromtimestamp(dval("time", i), tz=timezone.utc).astimezone().date().isoformat(),
            "summary": WCODE.get(wcode, "—"),
            "max_c": dval("temperature_2m_max", i),
            "min_c": dval("temperature_2m_min", i),
            "precip_probability": dval("precipitation_probability_max", i),
            "precip_mm": dval("precipitation_sum", i),
            "uv_index_max": dval("uv_index_max", i),
            "wind_max_ms": dval("wind_speed_10m_max", i),
            "wind_gust_ms": dval("wind_gusts_10m_max", i),
            "sunrise": datetime.fromtimestamp(dval("sunrise", i), tz=timezone.utc).astimezone().isoformat() if dval("sunrise", i) else None,
            "sunset": datetime.fromtimestamp(dval("sunset", i), tz=timezone.utc).astimezone().isoformat() if dval("sunset", i) else None,
        }
        day["wind_text"] = wind_text(day["wind_max_ms"])
        day["tips"] = pack_tips({
            "precip_probability": day["precip_probability"],
            "precip_mm": day["precip_mm"],
            "uv_index_max": day["uv_index_max"],
            "min_c": day["min_c"],
            "wind_max_ms": day["wind_max_ms"],
        })
        days_out.append(day)

    # quick travel hints
    advisories: List[str] = []
    if any((d.get("precip_probability") or 0) >= 60 for d in days_out):
        advisories.append("Expect some rainy periods — pack a light waterproof.")
    if any((d.get("uv_index_max") or 0) >= 7 for d in days_out):
        advisories.append("High UV on some days — sunscreen recommended.")
    if any((d.get("min_c") or 99) < 8 for d in days_out):
        advisories.append("Cool nights possible — bring a warm layer.")
    if any((d.get("wind_max_ms") or 0) >= 10 for d in days_out):
        advisories.append("Breezy days ahead — a windbreaker will help.")

    return {
        "current": current_block,
        "daily": days_out,
        "advisories": advisories,
    }

def summarize_air(raw: Optional[dict]) -> Optional[dict]:
    if not raw: return None
    # Prefer 'current' block; fallback to last hourly sample if needed
    cur = raw.get("current") or {}
    us_aqi = cur.get("us_aqi")
    pm25 = cur.get("pm2_5")
    pm10 = cur.get("pm10")
    cat = aqi_category(us_aqi)
    primary = None
    if pm25 is not None and pm10 is not None:
        primary = "PM2.5" if pm25 >= pm10 else "PM10"
    elif pm25 is not None:
        primary = "PM2.5"
    elif pm10 is not None:
        primary = "PM10"
    tips = []
    if us_aqi and us_aqi > 100:
        tips.append("If you’re sensitive to air pollution, limit prolonged outdoor activity.")
    return {
        "us_aqi": us_aqi,
        "category": cat,
        "primary_pollutant": primary,
        "pm2_5": pm25,
        "pm10": pm10,
        "tips": tips,
    }

def summarize_marine(raw: Optional[dict]) -> Optional[dict]:
    if not raw: return None
    daily = raw.get("daily") or {}
    times = daily.get("time") or []
    if not times: return None
    wh = daily.get("wave_height_max") or []
    sst_max = daily.get("sea_surface_temperature_max") or []
    sst_min = daily.get("sea_surface_temperature_min") or []
    out: List[dict] = []
    for i in range(min(5, len(times))):
        dt = datetime.fromtimestamp(times[i], tz=timezone.utc).astimezone().date().isoformat()
        waves = wh[i] if i < len(wh) else None
        out.append({
            "date": dt,
            "wave_height_max_m": waves,
            "sea_surface_temp_c_max": sst_max[i] if i < len(sst_max) else None,
            "sea_surface_temp_c_min": sst_min[i] if i < len(sst_min) else None,
            "beach_outlook": beach_outlook(waves),
        })
    return {"next_days": out}

@router.get("/weather")
async def weather(
    city: str = Query(..., description="City name, e.g., 'Barcelona'"),
    forecast_days: int = Query(7, ge=1, le=16, description="Number of forecast days (1–16)"),
    past_days: int = Query(0, ge=0, le=30, description="(Ignored in summary) kept for parity"),
    include_air: bool = Query(True, description="Include air quality summary"),
    include_marine: bool = Query(False, description="Include beach/marine summary"),
    include_elevation: bool = Query(False, description="Include elevation number"),
    language: str = Query("en", description="Geocoding language (ISO code)"),
) -> Dict[str, Any]:
    """
    Human-friendly weather for travelers:
    {
      meta: { city & match info },
      forecast: { current, daily[], advisories[] },
      air_quality?: { us_aqi, category, primary_pollutant, tips[] },
      marine?: { next_days[] },
      elevation_m?: number,
      errors: { block: reason }
    }
    """
    out: Dict[str, Any] = {"meta": {}, "forecast": None, "errors": {}}

    async with httpx.AsyncClient() as client:
        # 1) Geocode
        place = await geocode_city(client, city=city, count=1, language=language)
        lat, lon = place["latitude"], place["longitude"]
        tz = place.get("timezone", "auto")
        out["meta"] = {
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "city_query": city,
            "match": {
                "name": place.get("name"),
                "country": place.get("country"),
                "admin1": place.get("admin1"),
                "latitude": lat,
                "longitude": lon,
                "timezone": tz,
            },
        }

        # 2) Forecast (always) → summarized
        try:
            raw_fc = await fetch_forecast(client, lat, lon, tz, forecast_days)
            out["forecast"] = summarize_forecast(raw_fc, forecast_days)
        except HTTPException as e:
            out["errors"]["forecast"] = e.detail
        except Exception as e:
            out["errors"]["forecast"] = str(e)

        # 3) Air quality (optional) → summarized
        if include_air:
            try:
                raw_air = await fetch_air(client, lat, lon, tz)
                out["air_quality"] = summarize_air(raw_air)
            except HTTPException as e:
                out["errors"]["air_quality"] = e.detail
            except Exception as e:
                out["errors"]["air_quality"] = str(e)

        # 4) Marine (optional) → summarized
        if include_marine:
            try:
                raw_marine = await fetch_marine(client, lat, lon, tz, forecast_days)
                out["marine"] = summarize_marine(raw_marine)
            except HTTPException as e:
                out["errors"]["marine"] = e.detail
            except Exception as e:
                out["errors"]["marine"] = str(e)

        # 5) Elevation (optional, single number)
        if include_elevation:
            try:
                elev = await fetch_elev(client, lat, lon)
                # Open-Meteo elevation returns {"elevation":[...]} or {"elevation": x}
                elevation_m = None
                if isinstance(elev.get("elevation"), list) and elev["elevation"]:
                    elevation_m = elev["elevation"][0]
                elif isinstance(elev.get("elevation"), (int, float)):
                    elevation_m = elev["elevation"]
                out["elevation_m"] = elevation_m
            except HTTPException as e:
                out["errors"]["elevation"] = e.detail
            except Exception as e:
                out["errors"]["elevation"] = str(e)

    return out
