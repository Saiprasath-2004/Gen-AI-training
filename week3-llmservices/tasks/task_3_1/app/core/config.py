from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Weather Activity Advisor"
    app_version: str = "0.1.0"

    openrouter_api_key: SecretStr

    openrouter_url: str = (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    primary_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.0

    request_timeout: float = 30.0
    max_iterations: int = 5
    max_retry_attempts: int = 3
    weather_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()