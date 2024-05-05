from datetime import datetime, timezone
from typing import Annotated

from chaserland_api_gateway.config.app import app_settings
from chaserland_api_gateway.schemas.auth import oauth2 as schemas
from chaserland_api_gateway.services.user import UserServiceClient, get_user_stub
from chaserland_common.jwt import JWTBearer
from chaserland_grpc_proto.protos.user.user_pb2 import (
    OAuthLoginRequest,
    OAuthProvider,
)
from fastapi import APIRouter, Body, Depends, HTTPException, Response

router = APIRouter(prefix="/oauth2", tags=["oauth2"])


@router.post(
    "",
    response_model=JWTBearer,
    summary="Request ChaserLand access token",
)
async def request_access_token(
    response: Response,
    body: Annotated[schemas.OAuthUserRequest, Body(...)],
    user_stub: Annotated[UserServiceClient, Depends(get_user_stub)],
):
    if body.provider not in schemas.OAuthProviderEnum:
        raise HTTPException(
            status_code=400, detail=f"Invalid provider: {body.provider}"
        )
    token = await user_stub.oauth_login(
        OAuthLoginRequest(
            provider=OAuthProvider.Value(
                f"OAUTH_PROVIDER_{body.provider.value.upper()}"
            ),
            code=body.code,
        )
    )
    token = JWTBearer(token_type=token.token_type, access_token=token.access_token)
    jwt = token.to_jwt()
    response.set_cookie(
        key="CHASERLAND_SESSION",
        value=token.access_token,
        path="/",
        httponly=True,
        samesite="Lax",
        secure=app_settings.ENV == "prod",
        expires=datetime.fromtimestamp(
            jwt.payload["iat"] + jwt.payload["exp"]
        ).astimezone(tz=timezone.utc),
    )
    response.set_cookie(
        key="logged_in",
        value="true",
        path="/",
        samesite="Lax",
        httponly=True,
        secure=app_settings.ENV == "prod",
    )
    return token
