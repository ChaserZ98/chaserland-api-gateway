from datetime import datetime, timezone

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    version: str = None
    time: datetime = datetime.now(timezone.utc)
