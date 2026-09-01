from datetime import datetime

from schemas import (
    ActivityRiskProfile,
    WeatherData,
)
from scoring_tool import calculate_activity_score


def main() -> None:

    weather = WeatherData(
        location="Chennai",
        latitude=13.08784,
        longitude=80.27847,
        target_time=datetime(
            2026,
            8,
            21,
            6,
        ),
        temperature_c=25.9,
        wind_speed_kmh=10.2,
        rain_probability=10,
    )

    risk_profile = ActivityRiskProfile(
        activity="cricket",
        wind_penalty_weight=1.0,
        rain_penalty_weight=2.5,
        temperature_penalty_weight=1.0,
    )

    result = calculate_activity_score(
        weather=weather,
        risk_profile=risk_profile,
    )

    print("=" * 60)
    print("SCORING TOOL TEST")
    print("=" * 60)

    print(f"Score: {result.score}")
    print(f"Status: {result.status}")
    print(f"Hazards: {result.hazards}")
    print(f"Deductions: {result.deductions}")


if __name__ == "__main__":
    main()