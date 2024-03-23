import os
from typing import Union

import aiofiles
import ujson as json


class Response:
    _status_code: int = 200
    _headers: set[tuple[str, str]] = set()
    _content: Union[bytes, None]

    def __init__(self) -> None:
        self._headers = set()
        self._status_code = 200
        self._content = None

    async def _start(self) -> None:
        # await self._send({
        #     "type": "http.response.start",
        #     "status": self._status_code,
        #     "headers": list(self._headers),
        # })
        pass

    async def _write(self, content: bytes) -> None:
        # await self._start()
        # await self._send({
        #     "type": "http.response.body",
        #     "body": content,
        #     "more_body": False,
        # })
        self._content = content

    def status(self, status_code: int) -> "Response":
        self._status_code = status_code
        return self

    def header(self, name: str, value: str) -> "Response":
        self._headers = set([(k, v) for k, v in self._headers if k.lower() != name.lower])
        self._headers.add((name, value))
        return self

    async def send(self, content: str, status_code: int = 200) -> "Response":
        await self.status(status_code)._write(content.encode())
        return self

    async def html(self, content: str, status_code: int = None):
        self.header("Content-Type", "text/html")
        self.header('max-age', '0')
        if status_code is not None:
            self.status(status_code)
        await self._write(content.encode())
        return self

    async def redirect(self, url: str, status_code: int = 302) -> "Response":
        self.status(status_code)
        self.header("Location", url)
        await self._write(b"")
        return self

    async def json(self, content: dict, status_code: int = None) -> "Response":
        if status_code is not None:
            self.status(status_code)
        self.header("Content-Type", "application/json")
        await self._write(json.dumps(content).encode("utf-8"))
        return self

    async def download(self, file_path: str, file_name: str, attachment: bool = True) -> "Response":
        if not os.path.isfile(file_path):
            self.status(404)
            await self._write(b"File not found")
            return self

        self.header("Content-Disposition", f"{'attachment; ' if attachment else ''}filename={file_name}")
        async with aiofiles.open(file_path, "rb") as file:
            content = await file.read()
            self.header("Content-Length", str(len(content)))
            await self._write(content)
        return self

    async def stream_file(self, file_path: str, chunk_size: 4096) -> "Response":
        if not os.path.isfile(file_path):
            self.status(404)
            await self._write(b"File not found")
            return self
        async with aiofiles.open(file_path, "rb") as file:
            chunk: bytes = await file.read(chunk_size)
            while chunk:
                await self._write(chunk)
                chunk: bytes = await file.read(chunk_size)

        return self

    def content_type(self) -> str:
        for key, value in self._headers:
            if str(key).lower() == 'content-type':
                return value
        return 'text/plain'
