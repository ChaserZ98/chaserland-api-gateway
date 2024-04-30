import logging.config

from fastapi import FastAPI

from ..config.log import log_settings
from ..core.provider import AbstractFastAPIComponentProvider


class LogProvider(AbstractFastAPIComponentProvider):
    def register(self, app: FastAPI):
        logging.config.dictConfig(log_settings.FASTAPI_LOG_CONFIG)
