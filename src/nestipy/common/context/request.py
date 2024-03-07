import asyncio


class Request:
    def __init__(self, scope, receive):
        self.scope = scope
        self.original_receive = receive
        self.method = getattr(scope, 'method', None)
        self.path = scope["path"]
        self.user = None
        self.query_params = scope["query_string"]
        self.headers = {key.decode(): value.decode() for key, value in scope["headers"]}
        self.body = None
        self._receive, self._receive_copy = asyncio.Queue(), asyncio.Queue()
        # asyncio.create_task(self._fill_receive_copy())
        # asyncio.create_task(self._parse_body())

    async def _fill_receive_copy(self):
        while True:
            message = await self.original_receive()
            if message['type'] == 'http.disconnect':
                await self._receive.put(message)
                await self._receive_copy.put(message)
                break
            await self._receive.put(message)
            await self._receive_copy.put(message)

    async def receive(self):
        return await self._receive.get()

    async def receive_copy(self):
        return await self._receive_copy.get()

    async def read_body(self):
        if self.body is None:
            body_chunks = []
            while True:
                message = await self.receive()
                message_type = message["type"]
                if message_type == "http.request":
                    body_chunks.append(message.get("body", b""))
                elif message_type == "http.disconnect":
                    break
            self.body = b"".join(body_chunks).decode()

    async def _parse_body(self):
        if self.method in {"POST", "PUT", "PATCH"}:
            await self.read_body()

    async def json(self):
        if self.body is None:
            await self.read_body()
        import json
        return json.loads(self.body)
