import logging.config

from fastapi import FastAPI

from ..config.log import log_settings
from ..core.provider import AbstractFastAPIComponentProvider


class LogProvider(AbstractFastAPIComponentProvider):
    @staticmethod
    def register(app: FastAPI):
        logging.config.dictConfig(log_settings.FASTAPI_LOG_CONFIG)
