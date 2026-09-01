from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ActivityRequest(BaseModel):
    """
    Structured interpretation of the user's request.

    """

    activity: str = Field(
        min_length=1,
        description=(
            "The activity the user is asking about. "
            "This must remain free-form so the system can "
            "support activities that were not known when "
            "the application was developed."
        ),
    )

    location: str | None = Field(
        default=None,
        description=(
            "Location relevant to the request. "
            "Use null if no location is provided."
        ),
    )

    target_time: datetime | None = Field(
        default=None,
        description=(
            "Specific date and time relevant to the weather "
            "request. Use null when the request concerns "
            "current conditions or no specific time is given."
        ),
    )

    requires_weather: bool = Field(
        description=(
            "Whether weather information is required to "
            "answer the user's request."
        ),
    )


class ActivityRiskProfile(BaseModel):
    """
    Risk parameters selected by the LLM after receiving
    the actual weather conditions.
    """

    activity: str

    wind_penalty_weight: float = Field(
        ge=0,
        description=(
            "How strongly wind conditions should affect "
            "this activity."
        ),
    )

    rain_penalty_weight: float = Field(
        ge=0,
        description=(
            "How strongly rain probability should affect "
            "this activity."
        ),
    )

    temperature_penalty_weight: float = Field(
        ge=0,
        description=(
            "How strongly temperature should affect "
            "this activity."
        ),
    )


class WeatherData(BaseModel):
    """
    Normalized weather information returned by the
    deterministic weather tool.
    """

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
    """
    Deterministic result produced by the scoring tool.
    """

    score: float = Field(
        ge=0,
        le=100,
    )

    status: Literal[
        "excellent",
        "good",
        "degraded",
        "unsafe",
    ]

    hazards: list[str]

    deductions: dict[str, float]