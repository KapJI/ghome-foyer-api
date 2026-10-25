"""Tests for the GetHomeGraph helpers, against an in-process gRPC server."""

from concurrent import futures
import unittest

import grpc

from ghome_foyer_api.api_pb2 import GetHomeGraphRequest, GetHomeGraphResponse
from ghome_foyer_api.home_graph import get_home_graph, get_home_graph_bytes


class HomeGraphTest(unittest.TestCase):
    """Two homes on the wire, as Google sends them for an account with two homes."""

    def setUp(self) -> None:
        """Serve GetHomeGraph, recording each request it receives."""
        # Concatenated messages read as one with two field 2 entries
        first = GetHomeGraphResponse()
        first.home.home_name = "Home"
        first.home.devices.add(device_name="Kitchen speaker")
        second = GetHomeGraphResponse()
        second.home.home_name = "Test home"
        self.response = first.SerializeToString() + second.SerializeToString()
        self.requests: list[GetHomeGraphRequest] = []

        def handle(request: bytes, context: grpc.ServicerContext) -> bytes:
            self.requests.append(GetHomeGraphRequest.FromString(request))
            return self.response

        handler = grpc.method_handlers_generic_handler(
            "google.internal.home.foyer.v1.StructuresService",
            {"GetHomeGraph": grpc.unary_unary_rpc_method_handler(handle)},
        )
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        self.server.add_generic_rpc_handlers((handler,))
        port = self.server.add_insecure_port("127.0.0.1:0")
        self.server.start()
        self.channel = grpc.insecure_channel(f"127.0.0.1:{port}")

    def tearDown(self) -> None:
        """Stop the server."""
        self.channel.close()
        self.server.stop(None)

    def test_get_home_graph_keeps_homes_apart(self) -> None:
        """Each home keeps its own name and devices, unlike GetHomeGraphResponse."""
        home_graph = get_home_graph(self.channel, timeout=5)
        homes = [(home.home_name, len(home.devices)) for home in home_graph.homes]
        self.assertEqual(homes, [("Home", 1), ("Test home", 0)])

    def test_get_home_graph_bytes_sends_request(self) -> None:
        """The request reaches the server and the response comes back unparsed."""
        request = GetHomeGraphRequest(string1="hash")
        raw = get_home_graph_bytes(self.channel, request, timeout=5)
        self.assertEqual(raw, self.response)
        self.assertEqual([r.string1 for r in self.requests], ["hash"])


if __name__ == "__main__":
    unittest.main()
