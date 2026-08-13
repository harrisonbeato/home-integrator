from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    hikvision_host: str
    hikvision_username: str
    hikvision_password: str

    telegram_bot_token: str
    telegram_chat_id: str

    telegram_send_all_events: bool = True
    telegram_event_types: str = "human,person"

    hikvision_channels: str = ""

    database_path: str = "/data/home_integrator.db"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def event_types(self) -> set[str]:
        return {
            item.strip().lower()
            for item in self.telegram_event_types.split(",")
            if item.strip()
        }

    @property
    def channels(self) -> set[int]:
        return {
            int(item.strip())
            for item in self.hikvision_channels.split(",")
            if item.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
