from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    NAME: str = "gRPC service"

    HOST: str = "localhost"
    PORT: int = 8080

    GRACE_TIME: float = 5.0

    model_config = SettingsConfigDict(
        env_prefix="GRPC_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def ADDRESS(self) -> str:
        return f"{self.HOST}:{self.PORT}"
