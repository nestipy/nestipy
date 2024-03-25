import enum


class NestipyContainerKey(enum.Enum):
    request: str = '_request'
    response: str = '_response'
    query_params: str = '_query_params'
    params: str = '_params'
    session: str = '_session'
    body: str = '_body'
    headers: str = '_headers'
    args: str = '_args'
    files: str = '_files'
    execution_context: str = '_execution_context'
    websocket_server: str = '_websocket_sever'
