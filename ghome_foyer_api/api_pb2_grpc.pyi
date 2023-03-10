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
from abc import (
    ABCMeta,
    abstractmethod,
)
from collections.abc import (
    Iterator,
)
from ghome_foyer_api.api_pb2 import (
    GetAssistantDeviceSettingsRequest,
    GetAssistantDeviceSettingsResponse,
    GetAssistantRoutinesRequest,
    GetAssistantRoutinesResponse,
    GetHomeGraphRequest,
    GetHomeGraphResponse,
    UpdateAssistantDeviceSettingsRequest,
    UpdateAssistantDeviceSettingsResponse,
)
from grpc import (
    Channel,
    Server,
    ServicerContext,
    UnaryStreamMultiCallable,
    UnaryUnaryMultiCallable,
)

class HomeControlServiceStub:
    """Home Control Service"""

    def __init__(self, channel: Channel) -> None: ...
    GetAssistantRoutines: UnaryStreamMultiCallable[
        GetAssistantRoutinesRequest,
        GetAssistantRoutinesResponse,
    ]

class HomeControlServiceServicer(metaclass=ABCMeta):
    """Home Control Service"""

    @abstractmethod
    def GetAssistantRoutines(
        self,
        request: GetAssistantRoutinesRequest,
        context: ServicerContext,
    ) -> Iterator[GetAssistantRoutinesResponse]: ...

def add_HomeControlServiceServicer_to_server(servicer: HomeControlServiceServicer, server: Server) -> None: ...

class StructuresServiceStub:
    """Structure Service"""

    def __init__(self, channel: Channel) -> None: ...
    GetHomeGraph: UnaryUnaryMultiCallable[
        GetHomeGraphRequest,
        GetHomeGraphResponse,
    ]

class StructuresServiceServicer(metaclass=ABCMeta):
    """Structure Service"""

    @abstractmethod
    def GetHomeGraph(
        self,
        request: GetHomeGraphRequest,
        context: ServicerContext,
    ) -> GetHomeGraphResponse: ...

def add_StructuresServiceServicer_to_server(servicer: StructuresServiceServicer, server: Server) -> None: ...

class HomeDevicesServiceStub:
    """Home Devices Service"""

    def __init__(self, channel: Channel) -> None: ...
    GetAssistantDeviceSettings: UnaryStreamMultiCallable[
        GetAssistantDeviceSettingsRequest,
        GetAssistantDeviceSettingsResponse,
    ]
    UpdateAssistantDeviceSettings: UnaryStreamMultiCallable[
        UpdateAssistantDeviceSettingsRequest,
        UpdateAssistantDeviceSettingsResponse,
    ]

class HomeDevicesServiceServicer(metaclass=ABCMeta):
    """Home Devices Service"""

    @abstractmethod
    def GetAssistantDeviceSettings(
        self,
        request: GetAssistantDeviceSettingsRequest,
        context: ServicerContext,
    ) -> Iterator[GetAssistantDeviceSettingsResponse]: ...
    @abstractmethod
    def UpdateAssistantDeviceSettings(
        self,
        request: UpdateAssistantDeviceSettingsRequest,
        context: ServicerContext,
    ) -> Iterator[UpdateAssistantDeviceSettingsResponse]: ...

def add_HomeDevicesServiceServicer_to_server(servicer: HomeDevicesServiceServicer, server: Server) -> None: ...
