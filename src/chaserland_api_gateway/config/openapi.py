from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAPISettings(BaseSettings):
    FAVICON_URL: str = ""
    LICENSE_NAME: str = ""
    LICENSE_URL: str = ""
    CONTACT_NAME: str = ""
    CONTACT_URL: str = ""
    CONTACT_EMAIL: str = ""

    model_config = SettingsConfigDict(
        env_prefix="OPENAPI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def CONTACT(self) -> dict:
        return {
            "name": self.CONTACT_NAME,
            "url": self.CONTACT_URL,
            "email": self.CONTACT_EMAIL,
        }

    @property
    def LICENSE_INFO(self) -> dict:
        return {
            "name": self.LICENSE_NAME,
            "url": self.LICENSE_URL,
        }


openapi_settings = OpenAPISettings()
