"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
This file contains the following services:

HomeControlService
  - GetAssistantRoutines

StructuresService
  - GetHomeGraph

HomeDevicesService
  - GetAssistantDeviceSettings
"""

import abc
import collections.abc
import ghome_foyer_api.api_pb2
import grpc
import grpc.aio
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore[misc, type-arg]
    ...

class HomeControlServiceStub:
    """Home Control Service"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    GetAssistantRoutines: grpc.UnaryStreamMultiCallable[
        ghome_foyer_api.api_pb2.GetAssistantRoutinesRequest,
        ghome_foyer_api.api_pb2.GetAssistantRoutinesResponse,
    ]

class HomeControlServiceAsyncStub:
    """Home Control Service"""

    GetAssistantRoutines: grpc.aio.UnaryStreamMultiCallable[
        ghome_foyer_api.api_pb2.GetAssistantRoutinesRequest,
        ghome_foyer_api.api_pb2.GetAssistantRoutinesResponse,
    ]

class HomeControlServiceServicer(metaclass=abc.ABCMeta):
    """Home Control Service"""

    @abc.abstractmethod
    def GetAssistantRoutines(
        self,
        request: ghome_foyer_api.api_pb2.GetAssistantRoutinesRequest,
        context: _ServicerContext,
    ) -> typing.Union[collections.abc.Iterator[ghome_foyer_api.api_pb2.GetAssistantRoutinesResponse], collections.abc.AsyncIterator[ghome_foyer_api.api_pb2.GetAssistantRoutinesResponse]]: ...

def add_HomeControlServiceServicer_to_server(servicer: HomeControlServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...

class StructuresServiceStub:
    """Structure Service"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    GetHomeGraph: grpc.UnaryUnaryMultiCallable[
        ghome_foyer_api.api_pb2.GetHomeGraphRequest,
        ghome_foyer_api.api_pb2.GetHomeGraphResponse,
    ]

class StructuresServiceAsyncStub:
    """Structure Service"""

    GetHomeGraph: grpc.aio.UnaryUnaryMultiCallable[
        ghome_foyer_api.api_pb2.GetHomeGraphRequest,
        ghome_foyer_api.api_pb2.GetHomeGraphResponse,
    ]

class StructuresServiceServicer(metaclass=abc.ABCMeta):
    """Structure Service"""

    @abc.abstractmethod
    def GetHomeGraph(
        self,
        request: ghome_foyer_api.api_pb2.GetHomeGraphRequest,
        context: _ServicerContext,
    ) -> typing.Union[ghome_foyer_api.api_pb2.GetHomeGraphResponse, collections.abc.Awaitable[ghome_foyer_api.api_pb2.GetHomeGraphResponse]]: ...

def add_StructuresServiceServicer_to_server(servicer: StructuresServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...

class HomeDevicesServiceStub:
    """Home Devices Service"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    GetAssistantDeviceSettings: grpc.UnaryStreamMultiCallable[
        ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsRequest,
        ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsResponse,
    ]

    UpdateAssistantDeviceSettings: grpc.UnaryStreamMultiCallable[
        ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsRequest,
        ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsResponse,
    ]

class HomeDevicesServiceAsyncStub:
    """Home Devices Service"""

    GetAssistantDeviceSettings: grpc.aio.UnaryStreamMultiCallable[
        ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsRequest,
        ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsResponse,
    ]

    UpdateAssistantDeviceSettings: grpc.aio.UnaryStreamMultiCallable[
        ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsRequest,
        ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsResponse,
    ]

class HomeDevicesServiceServicer(metaclass=abc.ABCMeta):
    """Home Devices Service"""

    @abc.abstractmethod
    def GetAssistantDeviceSettings(
        self,
        request: ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsRequest,
        context: _ServicerContext,
    ) -> typing.Union[collections.abc.Iterator[ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsResponse], collections.abc.AsyncIterator[ghome_foyer_api.api_pb2.GetAssistantDeviceSettingsResponse]]: ...

    @abc.abstractmethod
    def UpdateAssistantDeviceSettings(
        self,
        request: ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsRequest,
        context: _ServicerContext,
    ) -> typing.Union[collections.abc.Iterator[ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsResponse], collections.abc.AsyncIterator[ghome_foyer_api.api_pb2.UpdateAssistantDeviceSettingsResponse]]: ...

def add_HomeDevicesServiceServicer_to_server(servicer: HomeDevicesServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...
