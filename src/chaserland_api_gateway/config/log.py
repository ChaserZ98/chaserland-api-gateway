import os

from chaserland_common.logger import ColorFormatter
from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import app_settings


class LogSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_DIRECTORY: str = "logs"
    LOG_PATH: str = os.path.join(os.path.dirname(app_settings.BASE_PATH), LOG_DIRECTORY)

    model_config = SettingsConfigDict(
        env_prefix="APP_LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def LOG_FORMATTERS(self) -> dict:
        return {
            "generic": {
                "style": "{",
                "format": "[{asctime}] [{process:^5d}] [{name:^18s}] [{levelname:^8s}] {message:s}",
                "datefmt": "%Y-%m-%d %H:%M:%S %Z",
                "class": "logging.Formatter",
            },
            "color_console": {
                "style": "{",
                "format": "[{asctime}] [{process:^5d}] [{name:^22s}] [{levelname:^20s}] {message:s}",
                "datefmt": "%Y-%m-%d %H:%M:%S %Z",
                "()": ColorFormatter,
            },
        }

    @property
    def LOG_HANDLERS(self) -> dict:
        return {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": "ext://sys.stdout",
            },
            "color_console": {
                "class": "logging.StreamHandler",
                "formatter": "color_console",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "generic",
                "filename": os.path.join(self.LOG_PATH, "access.log"),
                "maxBytes": 1024 * 1024 * 100,  # 100MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "generic",
                "filename": os.path.join(self.LOG_PATH, "error.log"),
                "maxBytes": 1024 * 1024 * 100,  # 100MB
                "backupCount": 5,
            },
        }

    @property
    def UVICORN_LOG_CONFIG(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": self.LOG_FORMATTERS,
            "handlers": self.LOG_HANDLERS,
            "loggers": {
                "uvicorn": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["error_file"],
                    "propagate": True,
                    "qualname": "uvicorn",
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": [],
                    "propagate": False,
                    "qualname": "uvicorn.access",
                },
                "uvicorn.error": {
                    "level": self.LOG_LEVEL,
                    "handlers": [],
                    "propagate": True,
                    "qualname": "uvicorn.error",
                },
            },
        }

    @property
    def FASTAPI_LOG_CONFIG(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "root": {"level": "INFO", "handlers": ["color_console"]},
            "loggers": {
                "fastapi": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["error_file"],
                    "propagate": True,
                    "qualname": "fastapi",
                },
                "fastapi.access": {
                    "level": "INFO",
                    "handlers": ["file"],
                    "propagate": False,
                    "qualname": "fastapi.access",
                },
                "apscheduler": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["error_file"],
                    "propagate": True,
                    "qualname": "apscheduler",
                },
            },
            "handlers": self.LOG_HANDLERS,
            "formatters": self.LOG_FORMATTERS,
        }


log_settings = LogSettings()
