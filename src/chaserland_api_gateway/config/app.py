import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NAME: str = "chaserz98.com"
    ENV: str = "prod"
    DEBUG: bool = False

    BASE_PATH: str = str(Path(os.path.abspath(__file__)).parents[2])

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    ALLOWED_ORIGINS: list[str] = ["https://chaserz98.com", "https://www.chaserz98.com"]

    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


app_settings = Settings()
