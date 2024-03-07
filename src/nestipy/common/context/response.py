import json


class Response:
    def __init__(self, send):
        self.send = send
        self.headers = {}

    async def send_json(self, content, status_code=200):
        await self.send_response("json", content, status_code)

    async def send_text(self, content, status_code=200):
        await self.send_response("text", content, status_code)

    async def render_html(self, content, status_code=200):
        await self.send_response("html", content, status_code)

    async def download_file(self, file_stream, filename, status_code=200):
        await self.send_response("download", {"file_stream": file_stream, "filename": filename}, status_code)

    async def send_response(self, content_type, content, status_code=200):
        if content_type == "json":
            await self.send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"application/json")] + [(key.encode(), str(value).encode()) for
                                                                       key, value in self.headers.items()]
            })
            await self.send({
                "type": "http.response.body",
                "body": json.dumps(content).encode()
            })
        elif content_type == "text":
            await self.send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"text/plain")] + [(key.encode(), str(value).encode()) for key, value in
                                                                 self.headers.items()]
            })
            await self.send({
                "type": "http.response.body",
                "body": content.encode()
            })
        elif content_type == "html":
            await self.send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"text/html")] + [(key.encode(), str(value).encode()) for key, value in
                                                                self.headers.items()]
            })
            await self.send({
                "type": "http.response.body",
                "body": content.encode()
            })
        elif content_type == "download":
            file_stream = content["file_stream"]
            filename = content["filename"]
            await self.send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"application/octet-stream"),
                            (b"content-disposition", f"attachment; filename={filename}".encode())] + [
                               (key.encode(), str(value).encode()) for key, value in self.headers.items()]
            })
            while True:
                chunk = file_stream.read(65536)  # Read in chunks
                if not chunk:
                    break
                await self.send({
                    "type": "http.response.body",
                    "body": chunk
                })
            file_stream.close()  # Close the file stream after sending
