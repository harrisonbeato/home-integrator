from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    hikvision_username: str
    hikvision_password: str
    hikvision_cameras: str

    telegram_bot_token: str
    telegram_chat_id: str

    database_path: str = "/data/home_integrator.db"
    log_level: str = "INFO"
    allowed_target_types: str = "human,vehicle"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cameras(self) -> list[str]:
        return [
            camera.strip()
            for camera in self.hikvision_cameras.split(",")
            if camera.strip()
        ]

    @property
    def target_types(self) -> set[str]:
        return {
            target.strip().lower()
            for target in self.allowed_target_types.split(",")
            if target.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()