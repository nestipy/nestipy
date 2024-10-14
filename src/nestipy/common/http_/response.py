import mimetypes
import os
from typing import Union, TYPE_CHECKING, AsyncIterator, Callable

import aiofiles
import ujson as json

from nestipy.common.exception.http import HttpException
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus

if TYPE_CHECKING:
    from nestipy.common.template import TemplateEngine


class Response:
    _status_code: int = 200
    _headers: set[tuple[str, str]] = set()
    _cookies: set[tuple[str, str]] = set()
    _content: Union[bytes, None]

    def __init__(self, template_engine: Union["TemplateEngine", None] = None) -> None:
        self._headers = set()
        self._status_code = 200
        self._content = None
        self._stream_content = None
        self.template_engine = template_engine

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
        """
        Set status code
        Args:
            status_code(int): Status code

        Returns:
            response(Response): An instance of response
        """
        self._status_code = status_code
        return self

    def header(self, name: str, value: str) -> "Response":
        """
        Add header
        Args:
            name(str): Header name
            value (str): Header value

        Returns:
            response(Response): An instance of response
        """
        self._headers = set(
            [(k, v) for k, v in self._headers if k.lower() != name.lower]
        )
        self._headers.add((name, value))
        return self

    def cookie(self, name: str, value: str) -> "Response":
        """
        Add cookie
        Args:
            name(str): Cookie name
            value (str): Cookie value

        Returns:
            response(Response): An instance of response
        """
        self._cookies = set(
            [(k, v) for k, v in self._cookies if k.lower() != name.lower]
        )
        self._cookies.add((name, value))
        return self

    async def send(self, content: str, status_code: int = 200) -> "Response":
        """
        Send text
        Args:
            content(str): Text to send
            status_code(int): Status code

        Returns:
            response(Response): An instance of response
        """
        await self.status(status_code)._write(content.encode())
        return self

    async def html(self, content: str, status_code: Union[int, None] = None):
        """
        Render html
        Args:
            content(str): The html string content
            status_code(int):  Status code

        Returns:
            response(Response): An instance of response
        """
        self.header("Content-Type", "text/html")
        self.header("max-age", "0")
        if status_code is not None:
            self.status(status_code)
        await self._write(content.encode())
        return self

    async def redirect(self, url: str, status_code: int = 302) -> "Response":
        """
        Redirect response
        Args:
            url(str): The url in witch the request will be redirected
            status_code(int): Status code of response. default 302

        Returns:
            response(Response): An instance of response
        """
        self.status(status_code)
        self.header("Location", url)
        await self._write(b"")
        return self

    async def json(
        self, content: dict, status_code: Union[int, None] = None
    ) -> "Response":
        """
        Send json
        Args:
            content(dict): The json value to send
            status_code(int): Status code of response

        Returns:
             response(Response): An instance of response
        """
        if status_code is not None:
            self.status(status_code)
        self.header("Content-Type", "application/json")
        await self._write(json.dumps(content).encode("utf-8"))
        return self

    async def download(self, file_path: str, attachment: bool = True) -> "Response":
        """
        Download file
        Args:
            file_path(str): The path of the file to download
            attachment(bool): Setup if file will be downloaded as attachment
        Returns:
                response(Response): An instance of response
        """
        if not os.path.isfile(file_path):
            self.status(404)
            await self._write(b"File not found")
            return self
        file_name = os.path.basename(file_path)
        mimetype, _ = mimetypes.guess_type(file_name)
        self.header("Content-Type", mimetype or "application/octet-stream")
        self.header(
            "Content-Disposition",
            f"{'attachment; ' if attachment else ''}filename={file_name}",
        )
        async with aiofiles.open(file_path, "rb") as file:
            content = await file.read()
            self.header("Content-Length", str(len(content)))
            await self._write(content)
        return self

    async def stream(self, callback: Callable[[], AsyncIterator[Union[bytes, str]]]):
        """
        Stream content
        Args:
            callback(Callable[[], AsyncIterator[Union[bytes, str]]]):  An callback that render ans async iterator
        Returns:
            response(Response):Response instance
        """
        self._stream_content = callback
        return self

    async def stream_file(self, file_path: str, chunk_size: int = 4096) -> "Response":
        """
        Stream file
        Args:
            file_path(str): The path of file to stream
            chunk_size(int): Chunk size of every stream item
        Returns:
            response(Response): Response instance

        """
        if not os.path.isfile(file_path):
            self.status(404)
            await self._write(b"File not found")
            return self

        async def _get_stream() -> AsyncIterator[bytes]:
            async with aiofiles.open(file_path, "rb") as file:
                chunk: bytes = await file.read(chunk_size)
                # no benefit because we don't send response directly
                while chunk:
                    yield chunk
                    chunk = await file.read(chunk_size)

        return await self.stream(_get_stream)

    async def render(self, template: str, context=None):
        """
        Render template if template engine was configured.
        Args:
            template(str): the template name
            context (dict | None): context value to pass to template

        Returns:

        """
        if context is None:
            context = {}
        if self.template_engine is not None:
            content = self.template_engine.render(template, context)
            await self.html(content)
        else:
            raise HttpException(
                HttpStatus.BAD_GATEWAY,
                HttpStatusMessages.BAD_GATEWAY,
                "Template engine not configured",
            )
        return self

    def content_type(self) -> str:
        for key, value in self._headers:
            if str(key).lower() == "content-type":
                return value
        return "text/plain"

    def status_code(self) -> int:
        return self._status_code

    def content(self) -> Union[bytes, None]:
        return self._content

    def headers(self) -> set[tuple[str, str]]:
        return self._headers

    def cookies(self) -> set[tuple[str, str]]:
        return self._cookies

    def is_stream(self) -> bool:
        return self._stream_content is not None

    async def get_stream(self) -> AsyncIterator[bytes]:
        if self._stream_content is not None:
            yield self._stream_content()
