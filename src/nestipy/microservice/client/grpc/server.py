import asyncio
from typing import Any

import grpc
from rich.style import Style

import nestipy.microservice.client.grpc.microservice_pb2 as pb2
import nestipy.microservice.client.grpc.microservice_pb2_grpc as pb2_grpc
from nestipy.common.logger import console


class GrpcServer(pb2_grpc.GrpcServicer):
    def __init__(self, verbose: bool = True):
        self.subscriptions: dict[str, Any] = {}
        self.verbose: bool = verbose

    async def Subscribe(self, request, context):
        topic = request.topic
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(context)
        if self.verbose:
            console.print(
                f"INFO:     Client subscribed to {topic}",
                style=Style(color="green", bold=True),
            )
        try:
            while True:
                await asyncio.sleep(0.01)
        except grpc.aio.AioRpcError as e:
            if self.verbose:
                console.print(
                    f"ERROR:     Subscription error  {e}",
                    style=Style(color="red", bold=True),
                )
            if topic in self.subscriptions and context in self.subscriptions[topic]:
                self.subscriptions[topic].remove(context)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]

    async def Unsubscribe(self, request, context):
        topic = request.topic
        if topic in self.subscriptions and context in self.subscriptions[topic]:
            self.subscriptions[topic].remove(context)
            if self.verbose:
                console.print(
                    f"INFO:     Client unsubscribe to {topic}",
                    style=Style(color="green", bold=True),
                )
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
        return pb2.Empty()

    async def SendData(self, request, context):
        topic = request.topic
        if self.verbose:
            console.print(
                f"INFO:     Client send data  to {topic}",
                style=Style(color="green", bold=True),
            )
        if topic in self.subscriptions:
            for client_context in self.subscriptions[topic]:
                try:
                    await client_context.write(
                        pb2.DataResponse(topic=topic, data=request.data)
                    )
                except grpc.aio.AioRpcError as e:
                    if self.verbose:
                        console.print(
                            f"ERROR:     Sending data error  {e}",
                            style=Style(color="red", bold=True),
                        )
                    self.subscriptions[topic].remove(client_context)
                    if not self.subscriptions[topic]:
                        del self.subscriptions[topic]
        return pb2.Empty()

    async def serve(self, port: int = 50051) -> None:
        """Start the server."""
        server = grpc.aio.server()
        pb2_grpc.add_GrpcServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{port}")
        console.print(
            f"INFO:     Grcp server running on port {port}.",
            style=Style(color="green", bold=True),
        )
        await server.start()
        await server.wait_for_termination()
