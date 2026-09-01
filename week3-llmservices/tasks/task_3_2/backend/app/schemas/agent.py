from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

class ActivityRequest(BaseModel):
    activity: str = Field(
        min_length=1,
        description=(
            "The activity the user is asking about."
        ),
    )

    location: str | None = None
    target_time: datetime | None = None
    requires_weather: bool

class ActivityRiskProfile(BaseModel):
    activity: str

    wind_penalty_weight: float = Field(
        ge = 0,
    )

    rain_penalty_weight: float = Field(
        ge = 0,
    )

    temperature_penalty_weight: float = Field(
        ge = 0,
    )

class WeatherData(BaseModel):
    location: str
    latitude: float
    longitude: float
    target_time: datetime
    temperature_c: float
    wind_speed_kmh: float

    rain_probability: float = Field(
        ge=0,
        le=100,
    )

class ActivityScore(BaseModel):
    score: float = Field(
        ge = 0,
        le = 100,
    )

    status: Literal[
        "excellent",
        "good",
        "degraded",
        "unsafe",
    ]

    hazards: list[str]

    deductions: dict[str, float]