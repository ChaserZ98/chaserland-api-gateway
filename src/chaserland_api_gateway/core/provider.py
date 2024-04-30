from abc import ABC, abstractmethod

from fastapi import FastAPI


class AbstractFastAPIComponentProvider(ABC):
    """Provider interface for registering FastAPI app components."""

    @abstractmethod
    def register(self, app: FastAPI):
        """Register FastAPI app components.

        Args:
            app (FastAPI): FastAPI app instance.

        Raises:
            NotImplementedError: Method not implemented.
        """
        raise NotImplementedError
