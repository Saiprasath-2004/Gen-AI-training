from app.schemas.agent import(
    ActivityRiskProfile,
    ActivityScore,
    WeatherData,
)

def calculate_activity_score(
    weather: WeatherData,
    risk_profile: ActivityRiskProfile,
) -> ActivityScore:

    score = 100.0

    hazards: list[str] = []
    deductions: dict[str, float] = {}

    wind_deduction = 0.0

    if weather.wind_speed_kmh > 30:
        excess_wind = (
            weather.wind_speed_kmh - 30
        )

        wind_deduction = (
            excess_wind
            * risk_profile.wind_penalty_weight
        )

        hazards.append(
            f"Strong wind: "
            f"{weather.wind_speed_kmh:.1f} km/h"
        )

    rain_deduction = 0.0

    if weather.rain_probability > 30:

        excess_rain = (
            weather.rain_probability - 30
        )

        rain_deduction = (
            excess_rain
            * risk_profile.rain_penalty_weight 
            / 2
        )

        hazards.append(
            f"Rain Probability: "
            f"{weather.rain_probability:.0f}%"
        )

    temperature_deduction = 0.0

    if weather.temperature_c < 10:
        temperature_deduction = (
            (10 - weather.temperature_c)
            * risk_profile.temperature_penalty_weight
        )

        hazards.append(
            f"Low temperature: "
            f"{weather.temperature_c:.1f} °C"
        )

    elif weather.temperature_c > 35:
        temperature_deduction = (
            (weather.temperature_c - 35)
            * risk_profile.temperature_penalty_weight
        )

        hazards.append(
            f"High temperature: "
            f"{weather.temperature_c:.1f} °C"
        )

    if wind_deduction > 0 :
        deductions["wind"] = round(
            wind_deduction,
            2,
        )

    if rain_deduction > 0 :
            deductions["rain"] = round(
                rain_deduction,
                2,
            )

    if temperature_deduction > 0 :
            deductions["temperature"] = round(
                temperature_deduction,
                2,
            )

    score -= (
        wind_deduction
        + rain_deduction
        + temperature_deduction
    )

    score = max(
        0.0,
        min(100.0, score)
    )

    if score >= 90:
        status = "excellent"
    elif score >= 75:
        status = "good"
    elif score >= 50:
        status = "degraded"
    else:
        status = "unsafe"

    return ActivityScore(
        score= round(score,2),
        status=status,
        hazards=hazards,
        deductions=deductions,
    )