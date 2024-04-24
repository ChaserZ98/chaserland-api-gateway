from abc import ABCMeta, abstractmethod
from collections.abc import AsyncIterator, Callable, Iterable
from typing import Any
from uuid import uuid4

import grpc


class AsyncClientInterceptor(
    grpc.aio.UnaryUnaryClientInterceptor,
    grpc.aio.UnaryStreamClientInterceptor,
    grpc.aio.StreamUnaryClientInterceptor,
    grpc.aio.StreamStreamClientInterceptor,
    metaclass=ABCMeta,
):
    @abstractmethod
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        client_call_details: grpc.aio.ClientCallDetails,
    ) -> Any:
        raise NotImplementedError

    async def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request: Any,
    ):
        return await self.intercept(
            _async_swap_args(continuation), request, client_call_details
        )

    async def intercept_unary_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request: Any,
    ):
        return await self.intercept(
            _async_swap_args(continuation), request, client_call_details
        )

    async def intercept_stream_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: Iterable[Any] | AsyncIterator[Any],
    ):
        return await self.intercept(
            _async_swap_args(continuation), request_iterator, client_call_details
        )

    async def intercept_stream_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: Iterable[Any] | AsyncIterator[Any],
    ):
        return await self.intercept(
            _async_swap_args(continuation), request_iterator, client_call_details
        )


def _async_swap_args(fn: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
    async def new_fun(x, y):
        return await fn(y, x)

    return new_fun


class AsyncClientMetadataInterceptor(AsyncClientInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        client_call_details: grpc.aio.ClientCallDetails,
    ) -> Any:
        if "rpc-id" in client_call_details.metadata:
            client_call_details.metadata.delete_all("rpc-id")
        client_call_details.metadata["rpc-id"] = str(uuid4())
        response_or_iterator = method(request_or_iterator, client_call_details)
        if hasattr(response_or_iterator, "__aiter__"):
            return response_or_iterator
        return await response_or_iterator
