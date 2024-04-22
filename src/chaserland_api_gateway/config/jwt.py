from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    PRIVATE_KEY: SecretStr = SecretStr("")
    PUBLIC_KEY: SecretStr = SecretStr("")
    ALGORITHM: str = ""
    MODE: str = ""

    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


jwt_settings = JWTSettings()
