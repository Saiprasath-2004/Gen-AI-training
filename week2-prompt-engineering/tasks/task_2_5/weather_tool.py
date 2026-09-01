from datetime import datetime

import httpx

from schemas  import WeatherData

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 10.0

def geocode_location(location: str) -> tuple[float, float, str]:
    """
        Convert a human-readable location into latitude and longitude.

        Returns:
            latitude
            longitude
            resolved location name
    """

    response = httpx.get(
        GEOCODING_URL,
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("results")

    if not results:
        raise ValueError(
            f"location not found: {location}"
        )

    result = results[0]

    return(
        result["latitude"],
        result["longitude"],
        result["name"],
    )

def fetch_weather(
    location: str,
    target_time: datetime,
) -> WeatherData:
    """
        Fetch weather conditions for a specific location and time.

        This function is deterministic from the application's
        perspective: it retrieves facts from the external
        weather service and does not involve an LLM.
    """

    latitude, longitude, resolved_location = (
        geocode_location(location)
    )

    response = httpx.get(
        FORECAST_URL,
        params={
            "latitude" : latitude,
            "longitude" : longitude,
            "hourly" : (
                "temperature_2m",
                "precipitation_probability",
                "wind_speed_10m"
            ),
            "forecast_days": 7,
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    hourly = data.get("hourly")

    if not hourly:
        raise ValueError(
            "Weather API returned no hourly forecast data"
        )

    target_hour = target_time.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    times = hourly.get("time", [])

    target_time_string = target_hour.strftime(
        "%Y-%m-%dT%H:%M"
    )

    if target_time_string not in times:
        raise ValueError(
            f"No forecast available for {target_time_string}"
        )

    index = times.index(target_time_string)

    temperatures = hourly.get(
        "temperature_2m",
        [],
    )

    rain_probabilities = hourly.get(
        "precipitation_probability",
        [],
    )

    wind_speeds = hourly.get(
        "wind_speed_10m",
        [],
    )

    try:

        temperature =temperatures[index]
        rain_probability = rain_probabilities[index]
        wind_speed = wind_speeds[index]

    except IndexError as exc:
        raise ValueError(
            "Weather API Returned incomplete hourly data"
        ) from exc

    return WeatherData(
        location=resolved_location,
        latitude=latitude,
        longitude=longitude,
        target_time=target_hour,
        temperature_c=temperature,
        wind_speed_kmh=wind_speed,
        rain_probability=rain_probability,
    )