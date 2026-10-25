"""Call GetHomeGraph and read every home of the account.

The generated `StructuresServiceStub.GetHomeGraph` returns `GetHomeGraphResponse`,
which merges all homes into one. These helpers make the same call and return
`HomeGraph`, or the raw response to parse as either message.
"""

import grpc

from ghome_foyer_api.api_pb2 import GetHomeGraphRequest, HomeGraph

GET_HOME_GRAPH = "/google.internal.home.foyer.v1.StructuresService/GetHomeGraph"


def get_home_graph_bytes(
    channel: grpc.Channel,
    request: GetHomeGraphRequest | None = None,
    *,
    timeout: float | None = None,
) -> bytes:
    """Return the raw GetHomeGraph response.

    Parse it with `HomeGraph.FromString`, `GetHomeGraphResponse.FromString` or
    both. Raises `grpc.RpcError` if the call fails.
    """
    call: grpc.UnaryUnaryMultiCallable[GetHomeGraphRequest, bytes] = (
        channel.unary_unary(
            GET_HOME_GRAPH,
            request_serializer=GetHomeGraphRequest.SerializeToString,
            response_deserializer=None,
        )
    )
    return call(request or GetHomeGraphRequest(), timeout=timeout)


def get_home_graph(
    channel: grpc.Channel,
    request: GetHomeGraphRequest | None = None,
    *,
    timeout: float | None = None,
) -> HomeGraph:
    """Return the GetHomeGraph response with one entry per home.

    Raises `grpc.RpcError` if the call fails.
    """
    return HomeGraph.FromString(get_home_graph_bytes(channel, request, timeout=timeout))
