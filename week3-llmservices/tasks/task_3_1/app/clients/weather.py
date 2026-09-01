from datetime import datetime

import httpx

from app.core.config import Settings
from app.core.retry import retry_async
from app.exceptions import ExternalServiceError
from app.schemas.agent import WeatherData

class WeatherClient:

    GEOCODING_URL = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    FORECAST_URL = (
        "https://api.open-meteo.com/v1/forecast"
    )

    def __init__(
            self,
            settings: Settings,
            http_client: httpx.AsyncClient,
        ) -> None:
    
            self._settings = settings
            self._http_client = http_client


    async def geocode_location(
        self,
        location: str,
    ) -> tuple[float, float, str]:

        async def make_request() -> httpx.Response:
            response = await self._http_client.get(
                self.GEOCODING_URL,
                params={
                    "name": location,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
                timeout=self._settings.weather_timeout,
            )

            response.raise_for_status()

            return response


        try:
            response = await retry_async(
                make_request,
                max_attempts=self._settings.max_retry_attempts,
            )

        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                "Weather geocoding request timed out."
            ) from exc

        except httpx.NetworkError as exc:
            raise ExternalServiceError(
                "Weather geocoding service could not be reached."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                "Weather geocoding service returned an unsuccessful HTTP status.",
                status_code=exc.response.status_code,
            ) from exc

        data = response.json()
        results = data.get("results")

        if not results:
            raise ValueError(
                 f"location not found: {location}"
            )

        result = results[0]

        return (
            result["latitude"],
            result["longitude"],
            result["name"],
        )

    async def fetch_weather(
        self,
        location: str,
        target_time: datetime,
    ) -> WeatherData:

        (
            latitude,
            longitude,
            resolved_location
        ) = await self.geocode_location(location)

        async def make_request() -> httpx.Response:
            response = await self._http_client.get(
                self.FORECAST_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": (
                        "temperature_2m,"
                        "precipitation_probability,"
                        "wind_speed_10m"
                    ),
                    "forecast_days": 7,
                    "timezone": "auto",
                },
                timeout=self._settings.weather_timeout
            )

            response.raise_for_status()

            return response


        try:
            response = await retry_async(
                make_request,
                max_attempts=self._settings.max_retry_attempts,
            )

        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                "Weather forecast request timed out."
            ) from exc

        except httpx.NetworkError as exc:
            raise ExternalServiceError(
                "Weather forecast service could not be reached."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                "Weather forecast service returned an unsuccessful HTTP status.",
                status_code=exc.response.status_code,
            ) from exc

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

        target_time_string = target_hour.strftime(
            "%Y-%m-%dT%H:%M"
        )

        times = hourly.get("time", [])

        if target_time_string not in times:
            raise ValueError(
                f"No forecast available for "
                f"{target_time_string}"
            )

        index = times.index(target_time_string)

        temperature = hourly.get(
            "temperature_2m",
            [],
        )

        rain_probabilites = hourly.get(
            "precipitation_probability",
            [],
        )

        wind_speed = hourly.get(
            "wind_speed_10m",
            [],
        )

        try:

            temperature = temperature[index]
            rain_probability = rain_probabilites[index]
            wind_speed = wind_speed[index]

        except IndexError as exc:
            raise ValueError(
                "Whether API returned incomplete hourly  data"
            ) from exc

        return WeatherData(
            location = resolved_location,
            latitude = latitude,
            longitude = longitude,
            target_time = target_hour,
            temperature_c = temperature,
            wind_speed_kmh = wind_speed,
            rain_probability = rain_probability,
        )
