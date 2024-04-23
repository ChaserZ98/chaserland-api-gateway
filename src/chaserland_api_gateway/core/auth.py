from abc import ABC, abstractmethod
from typing import Annotated

from chaserland_common.jwt import JWTBearer
from fastapi import HTTPException, Security
from fastapi.security import (
    APIKeyCookie,
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes,
)

from ..config.jwt import jwt_settings


class AuthChecker(ABC):
    def __init__(
        self,
        public_key: str = jwt_settings.PUBLIC_KEY.get_secret_value(),
        algorithm: str = jwt_settings.ALGORITHM,
        mode: str = jwt_settings.MODE,
    ):
        self.public_key = public_key
        self.algorithm = algorithm
        self.mode = mode

    def parse_token(self, bearer_token: JWTBearer) -> dict:
        """parse token and return payload and scopes, raise HTTPException 401 if token cannot be verified

        Args:
            bearer_token (JWTBearer): token to parse

        Raises:
            HTTPException: 401 - Invalid token

        Returns:
            dict: payload after parsing token
        """

        if not bearer_token.verify(self.public_key, self.algorithm, self.mode):
            raise HTTPException(status_code=401, detail="Invalid token")
        payload = bearer_token.to_jwt().payload
        return payload


class CookieAuthChecker(AuthChecker):
    async def __call__(
        self,
        token: Annotated[
            str | None,
            Security(
                APIKeyCookie(
                    scheme_name="Bearer scheme",
                    description="Bearer token",
                    name="CHASERLAND_SESSION",
                )
            ),
        ],
    ):
        bearer_token = JWTBearer(access_token=token, token_type="bearer")
        payload = self.parse_token(bearer_token)
        return payload


class TokenAuthChecker(AuthChecker):
    async def __call__(
        self,
        token: Annotated[
            HTTPAuthorizationCredentials,
            Security(
                HTTPBearer(scheme_name="Bearer scheme", description="Bearer token"),
            ),
        ],
    ):
        bearer_token = JWTBearer(access_token=token.credentials, token_type="bearer")
        payload = self.parse_token(bearer_token)
        return payload


class ScopeChecker(AuthChecker):
    @abstractmethod
    async def __call__(self, scopes: SecurityScopes, token):
        pass

    def check_scopes(
        self, required_scopes: SecurityScopes, token_scopes: list[str]
    ) -> None:
        """raise HTTPException if not enough permissions, otherwise return None

        Args:
            required_scopes (SecurityScopes): required scopes from route
            token_scopes (list[str]): list of scopes from token

        Raises:
            HTTPException: 403 - Not enough permissions
        """
        for scope in required_scopes.scopes:
            if scope not in token_scopes:
                raise HTTPException(status_code=403, detail="Not enough permissions")


class CookieScopeChecker(ScopeChecker):
    async def __call__(
        self,
        scopes: SecurityScopes,
        token: Annotated[
            str | None,
            Security(
                APIKeyCookie(
                    scheme_name="Bearer scheme",
                    description="Bearer token",
                    name="CHASERLAND_SESSION",
                )
            ),
        ],
    ):
        bearer_token = JWTBearer(access_token=token, token_type="bearer")
        payload = self.parse_token(bearer_token)
        token_scopes = payload.get("scopes", [])
        self.check_scopes(scopes, token_scopes)
        return payload


class TokenScopeChecker(ScopeChecker):
    async def __call__(
        self,
        scopes: SecurityScopes,
        token: Annotated[
            HTTPAuthorizationCredentials,
            Security(
                HTTPBearer(scheme_name="Bearer scheme", description="Bearer token"),
            ),
        ],
    ):
        bearer_token = JWTBearer(access_token=token.credentials, token_type="bearer")
        payload = self.parse_token(bearer_token)
        token_scopes = payload.get("scopes", [])
        self.check_scopes(scopes, token_scopes)
        return payload
