import enum


class NestipyContextProperty(enum.Enum):
    request: str = "_request"
    response: str = "_response"
    query_params: str = "_query_params"
    params: str = "_params"
    session: str = "_session"
    cookies: str = "_cookies"
    body: str = "_body"
    headers: str = "_headers"
    args: str = "_args"
    files: str = "_files"
    execution_context: str = "_execution_context"
    io_server: str = "_websocket_sever"
    io_client: str = "_socket_sid"
    io_data: str = "_socket_data"
