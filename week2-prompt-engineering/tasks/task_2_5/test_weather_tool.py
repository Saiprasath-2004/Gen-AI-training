from datetime import datetime

from weather_tool import fetch_weather

def main() -> None:

    weather = fetch_weather(
        location="Chennai",
        target_time=datetime(
            2026,
            8,
            21,
            6,
        ),
    )

    print("=" * 60)
    print("WEATHER TOOL TEST")
    print("=" * 60)

    print(f"Location: {weather.location}")
    print(f"Latitude: {weather.latitude}")
    print(f"Longitude: {weather.longitude}")
    print(f"Target time: {weather.target_time}")
    print(f"Temperature: {weather.temperature_c} °C")
    print(f"Wind: {weather.wind_speed_kmh} km/h")
    print(
        f"Rain probability: "
        f"{weather.rain_probability}%"
    )


if __name__ == "__main__":
    main()