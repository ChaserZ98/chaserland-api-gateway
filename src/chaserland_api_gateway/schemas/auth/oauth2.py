from enum import Enum

from pydantic import BaseModel


class OAuthProviderEnum(str, Enum):
    github = "github"


class OAuthUserRequest(BaseModel):
    provider: OAuthProviderEnum
    code: str
