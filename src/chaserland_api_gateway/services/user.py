import asyncio
from contextlib import AbstractAsyncContextManager

import grpc
from chaserland_grpc_proto.protos.user.user_pb2 import (
    OAuthLoginRequest,
    OAuthLoginResponse,
)
from chaserland_grpc_proto.protos.user.user_pb2_grpc import UserStub
from fastapi import Request

from ..config.grpc import ServiceSettings
from ..utils.interceptor import (
    AsyncClientInterceptor,
    AsyncClientMetadataInterceptor,
)

user_service_settings = ServiceSettings(_env_prefix="GRPC_USER_SERVICE_")


class UserServiceClient:
    def __init__(self, channel: grpc.aio.Channel):
        self.channel = channel
        self.stub = UserStub(self.channel)

    async def wait_for_ready(self, timeout: float = 5):
        await asyncio.wait_for(self.channel.wait_for_ready(), timeout=timeout)

    async def oauth_login(
        self, request: OAuthLoginRequest, timeout: float = 5
    ) -> OAuthLoginResponse:
        return await self.stub.oauth_login(request, timeout=timeout)


class UserService(AbstractAsyncContextManager[UserServiceClient]):
    def __init__(
        self,
        address: str = user_service_settings.ADDRESS,
        grace_time: float = user_service_settings.GRACE_TIME,
        interceptors: list[AsyncClientInterceptor] | None = [
            AsyncClientMetadataInterceptor(),
        ],
    ):
        self.address = address
        self.grace_time = grace_time
        self.interceptors = interceptors

    async def __aenter__(self) -> UserServiceClient:
        self.channel = grpc.aio.insecure_channel(
            self.address, interceptors=self.interceptors
        )
        self.stub = UserServiceClient(self.channel)
        return self.stub

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool | None:
        await self.channel.close(grace=self.grace_time)


def get_user_stub(request: Request) -> UserServiceClient:
    if not hasattr(request.state, "user_stub"):
        raise AttributeError("Request state does not have a 'user_stub' attribute.")
    user_stub = request.state.user_stub
    if not isinstance(user_stub, UserServiceClient):
        raise TypeError(
            f"User stub is not an instance of UserServiceClient. Got: {type(user_stub)}."
        )
    return user_stub
