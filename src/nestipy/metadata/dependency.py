class CtxDepKey:
    Service: str = "service"
    Request: str = "request"
    Response: str = "response"
    Session: str = "session"
    Sessions: str = "sessions"
    Cookie: str = "cookie"
    Cookies: str = "cookies"
    Header: str = "header"
    Headers: str = "headers"
    Query: str = "query"
    Queries: str = "queries"
    Body: str = "body"
    Params: str = "params"
    Param: str = "param"
    Args: str = "args"
    Arg: str = "arg"
    Context: str = "execution_context"
    Files: str = "files"
    WebSocketClient: str = "io_client"
    SocketData: str = "io_data"

    @classmethod
    def to_list(cls) -> list:
        return [
            cls.Service,
            cls.Request,
            cls.Param,
            cls.Response,
            cls.Session,
            cls.Queries,
            cls.Query,
            cls.Body,
            cls.Params,
            cls.Args,
            cls.Arg,
            cls.WebSocketClient,
            cls.Cookie,
            cls.Files,
            cls.Cookies,
            cls.Context,
            cls.Sessions,
            cls.SocketData,
            cls.Header,
            cls.Headers,
        ]
