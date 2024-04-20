from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    DRIVER: str = "redis"
    HOST: SecretStr = SecretStr("")
    PORT: str = "6379"
    PASSWORD: SecretStr = SecretStr("")

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def REDIS_URL(self) -> SecretStr:
        return SecretStr(
            f"{self.DRIVER}://:{self.PASSWORD.get_secret_value()}@{self.HOST.get_secret_value()}:{self.PORT}"
        )


redis_settings = RedisSettings()
