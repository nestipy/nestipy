class CtxDepKey:
    Service: str = 'service'
    Request: str = 'request'
    Response: str = 'response'
    Session: str = 'session'
    Query: str = 'query'
    Body: str = 'body'
    Params: str = 'params'
    Args: str = 'args'
    Context: str = 'execution_context'
    Files: str = 'files'
    SocketClient: str = 'io_client'
    SocketData: str = 'io_data'

    @classmethod
    def to_list(cls) -> list:
        return [
            cls.Service, cls.Request,
            cls.Response, cls.Session,
            cls.Query, cls.Body,
            cls.Params, cls.Args,
            cls.SocketClient,
            cls.Files,
            cls.Context,
        ]
