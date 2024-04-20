from abc import ABC, abstractmethod


class AbstractFastAPIComponentProvider(ABC):
    """Provider interface for registering FastAPI app components."""

    @staticmethod
    @abstractmethod
    def register(app):
        """Register FastAPI app components.

        Args:
            app (FastAPI): FastAPI app instance.

        Raises:
            NotImplementedError: Method not implemented.
        """
        raise NotImplementedError
