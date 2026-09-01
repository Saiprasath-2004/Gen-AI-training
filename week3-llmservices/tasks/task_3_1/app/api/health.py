from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("")
async def  health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/config")
async def config_check(
    settings: Settings = Depends(get_settings),
) -> dict[str, str| int| float] :

    return{
        "app_name": settings.app_name,
        "model": settings.primary_model,
        "temperature": settings.temperature,
        "request_timeout": settings.request_timeout,
        "max_iterations": settings.max_iterations,
        "weather_timeout": settings.weather_timeout,
    }