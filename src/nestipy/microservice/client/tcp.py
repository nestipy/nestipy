import asyncio
import typing
from typing import AsyncIterator, Optional

from rich.style import Style

from .base import ClientProxy, MicroserviceOption
from .option import TCPClientOption

__SPLIT__ = "__SPLIT__"

from nestipy.common.logger import console


class TCPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 1333, verbose: bool = True):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.subscribers: dict[str, list[asyncio.StreamWriter]] = {}

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        try:
            while True:
                # Read data from client
                data = await reader.readline()
                if not data:
                    break

                command, topic, *message = (
                    data.decode("utf-8").strip().split(__SPLIT__, 2)
                )
                message = message[0] if message else ""
                if command == "SUBSCRIBE":
                    await self.subscribe(topic, writer)
                elif command == "PUBLISH":
                    await self.publish(topic, message)

        except Exception as e:
            if self.verbose:
                console.print(
                    f"ERROR:     {e}",
                    style=Style(color="red", bold=True),
                )
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            finally:
                pass

    async def subscribe(self, topic: str, writer: asyncio.StreamWriter):
        """Add a subscriber to a topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(writer)
        if self.verbose:
            console.print(
                f"INFO:     Client subscribed to {topic}",
                style=Style(color="green", bold=True),
            )

    async def publish(self, topic: str, message: str):
        """Broadcast a message to all subscribers of a topic."""
        if topic in self.subscribers:
            for sub in self.subscribers[topic]:
                try:
                    sub.write(f"[{topic}]{__SPLIT__}{message}\n".encode("utf-8"))
                    await sub.drain()
                except Exception as e:
                    self.subscribers[topic].remove(sub)
        if self.verbose:
            console.print(
                f"INFO:     Published to {topic}: {message}",
                style=Style(color="green", bold=True),
            )

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        if self.verbose:
            console.print(
                f"INFO:     Server started on {':'.join(addr)}...",
                style=Style(color="green", bold=True),
            )
        async with server:
            await server.serve_forever()


class TCPClientProxy(ClientProxy):
    def __init__(self, option: MicroserviceOption):
        super().__init__(option)
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._response_cache = {}
        self._config = typing.cast(
            TCPClientOption, self.option.option or TCPClientOption()
        )
        self.server: Optional[TCPServer] = (
            TCPServer(
                host=self._config.host,
                port=self._config.port,
                verbose=self._config.verbose,
            )
            if self._config.start_server
            else None
        )
        self.server_task: Optional[asyncio.Task] = None

    async def before_start(self):
        """Run before starting the microservice server listener"""
        if self.server is not None:
            self.server_task = asyncio.get_running_loop().create_task(
                self.server.start(), name="tcp_server"
            )
            await asyncio.sleep(1)

    async def before_close(self):
        """Run before stopping the microservice server listener"""
        if self.server_task:
            self.server_task.cancel()

    async def connect(self):
        """Establish a TCP connection."""
        if not self.writer:
            self.reader, self.writer = await asyncio.open_connection(
                self._config.host, self._config.port
            )

    async def slave(self) -> "TCPClientProxy":
        """Return a new instance for slave connection."""
        return TCPClientProxy(self.option)

    async def _publish(self, topic: str, data: str):
        """Publish a message to the specified topic."""
        await self.connect()
        self.writer.write(
            f"PUBLISH{__SPLIT__}{topic}{__SPLIT__}{data}\n".encode("utf-8")
        )
        await self.writer.drain()

    async def subscribe(self, topic: str):
        """Subscribe to a topic."""
        await self.connect()
        self.writer.write(f"SUBSCRIBE{__SPLIT__}{topic}\n".encode("utf-8"))
        await self.writer.drain()

    async def unsubscribe(self, topic: str):
        """Unsubscribe from a topic."""
        await self.connect()
        self.writer.write(f"UNSUBSCRIBE{__SPLIT__}{topic}\n".encode("utf-8"))
        await self.writer.drain()

    async def send_response(self, topic: str, data: str):
        """Send a response to a topic."""
        await self._publish(topic, data)

    async def listen(self) -> AsyncIterator[str]:
        """Listen for incoming messages."""
        while True:
            data = await self.reader.readline()
            if data:
                yield data.decode("utf-8").strip().split(__SPLIT__)[-1]

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        """Listen for a response on a given topic."""
        await self.subscribe(from_topic)
        try:
            while True:
                data = await self.reader.readline()
                if data:
                    message = data.decode("utf-8").strip()
                    key = f"[{from_topic}]{__SPLIT__}"
                    if message.startswith(key):
                        return message[len(key) :]
                await asyncio.sleep(0.01)
        finally:
            await self.unsubscribe(from_topic)

    async def close(self):
        """Close the connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None
