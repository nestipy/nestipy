from typing import Union, Any

from nestipy.metadata import NestipyContextProperty


class NestipyContextContainer:
    _instance: Union["NestipyContextContainer", None] = None
    _request = None
    _response = None
    _query_params = {}
    _params = {}
    _session = {}
    _headers = {}
    _body = {}
    _args = {}
    _files = {}
    _execution_context = None
    _websocket_sever = None
    _socket_sid = None
    _socket_data = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NestipyContextContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def set_value(cls, key: NestipyContextProperty, value: object):
        self = cls.get_instance()
        setattr(self, key.value, value)

    @classmethod
    def get_value(cls, key: NestipyContextProperty) -> Union[Any, None]:
        self = cls.get_instance()
        return getattr(self, key.value, None)

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return NestipyContextContainer(*args, **kwargs)

    def destroy(self):
        self._request = None
        self._response = None
        self._query_params = {}
        self._params = {}
        self._session = {}
        self._headers = {}
        self._body = {}
        self._args = {}
        self._execution_context = None
        self._websocket_sever = None
        self._instance = None
