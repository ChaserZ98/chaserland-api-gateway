import asyncio
from contextlib import AbstractAsyncContextManager

import grpc
from chaserland_grpc_proto.protos.user.user_pb2 import OAuthLoginRequest
from chaserland_grpc_proto.protos.user.user_pb2_grpc import UserStub

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

    async def oauth_login(self, request: OAuthLoginRequest, timeout: float = 5):
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
