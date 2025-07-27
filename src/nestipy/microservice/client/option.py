import asyncio
import enum
import logging
from dataclasses import dataclass, field
from ssl import SSLContext, TLSVersion
from typing import Union, Optional, Mapping, Literal, Iterable, List

import paho.mqtt.client as mqtt
from aio_pika.abc import SSLOptions, ExchangeType
from aiomqtt import ProtocolVersion, Will, Message, TLSParameters, ProxySettings
from aiomqtt.types import SocketOption, WebSocketHeaders
from aiormq.abc import TimeoutType
from nats.aio.client import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_RECONNECT_TIME_WAIT,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_PING_INTERVAL,
    DEFAULT_MAX_OUTSTANDING_PINGS,
    DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
    DEFAULT_DRAIN_TIMEOUT,
    Credentials,
    DEFAULT_INBOX_PREFIX,
    DEFAULT_PENDING_SIZE,
)
from paho.mqtt.properties import Properties
from pamqp.common import FieldTable, Arguments
from redis import ConnectionPool, CredentialProvider
from redis.asyncio.retry import Retry
from redis.utils import get_lib_version


class Transport(enum.Enum):
    TCP = "TCP"
    REDIS = "REDIS"
    MQTT = "MQTT"
    NATS = "NATS"
    RABBITMQ = "RABBITMQ"
    GRPC = "GRPC"
    CUSTOM = "CUSTOM"


@dataclass
class TCPClientOption:
    host: str = field(default="localhost")
    port: int = field(default=1333)
    start_server: bool = field(default=True)
    verbose: bool = field(default=True)


@dataclass
class GrpcClientOption:
    host: str = field(default="localhost")
    port: int = field(default=50051)
    verbose: bool = field(default=True)


@dataclass
class RedisClientOption:
    host: str = field(default="127.0.0.1")
    port: int = field(default=6379)
    db: Union[str, int] = 0
    password: Optional[str] = None
    socket_timeout: Optional[float] = None
    socket_connect_timeout: Optional[float] = None
    socket_keepalive: Optional[bool] = None
    socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None
    connection_pool: Optional[ConnectionPool] = None
    unix_socket_path: Optional[str] = None
    encoding: str = "utf-8"
    encoding_errors: str = "strict"
    decode_responses: bool = True
    retry_on_timeout: bool = False
    retry_on_error: Optional[list] = None
    ssl: bool = False
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_ca_data: Optional[str] = None
    ssl_check_hostname: bool = False
    ssl_min_version: Optional[TLSVersion] = (None,)
    ssl_ciphers: Optional[str] = None
    max_connections: Optional[int] = None
    single_connection_client: bool = False
    health_check_interval: int = 0
    client_name: Optional[str] = None
    lib_name: Optional[str] = "redis-py"
    lib_version: Optional[str] = get_lib_version()
    username: Optional[str] = None
    retry: Optional[Retry] = None
    auto_close_connection_pool: Optional[bool] = None
    redis_connect_func = None
    credential_provider: Optional[CredentialProvider] = None
    protocol: Optional[int] = 2


@dataclass
class MqttClientOption:
    hostname: str = field(default="localhost")
    port: int = field(default=1883)
    username: Optional[str] = None
    password: Optional[str] = None
    logger: Optional[logging.Logger] = None
    identifier: Optional[str] = None
    queue_type: type[asyncio.Queue[Message]] | None = None
    protocol: Optional[ProtocolVersion] = None
    will: Optional[Will] = None
    clean_session: Optional[bool] = None
    transport: Literal["tcp", "websockets", "unix"] = "tcp"
    timeout: Optional[float] = None
    keepalive: int = 60
    bind_address: str = ""
    bind_port: int = 0
    clean_start: mqtt.CleanStartOption = mqtt.MQTT_CLEAN_START_FIRST_ONLY
    max_queued_incoming_messages: Optional[int] = None
    max_queued_outgoing_messages: Optional[int] = None
    max_inflight_messages: Optional[int] = None
    max_concurrent_outgoing_calls: Optional[int] = None
    properties: Optional[Properties] = None
    tls_context: Optional[mqtt.ssl.SSLContext] = None
    tls_params: Optional[TLSParameters] = None
    tls_insecure: Optional[bool] = None
    proxy: Optional[ProxySettings] = None
    socket_options: Optional[Iterable[SocketOption]] = None
    websocket_path: Optional[str] = None
    websocket_headers: Union[WebSocketHeaders, None] = None


@dataclass
class NatsClientOption:
    servers: Union[str, List[str]] = field(
        default_factory=lambda: ["nats://localhost:4222"]
    )
    name: Optional[str] = None
    pedantic: bool = False
    verbose: bool = False
    allow_reconnect: bool = True
    connect_timeout: int = DEFAULT_CONNECT_TIMEOUT
    reconnect_time_wait: int = DEFAULT_RECONNECT_TIME_WAIT
    max_reconnect_attempts: int = DEFAULT_MAX_RECONNECT_ATTEMPTS
    ping_interval: int = DEFAULT_PING_INTERVAL
    max_outstanding_pings: int = DEFAULT_MAX_OUTSTANDING_PINGS
    dont_randomize: bool = False
    flusher_queue_size: int = DEFAULT_MAX_FLUSHER_QUEUE_SIZE
    no_echo: bool = False
    tls: Optional[SSLContext] = None
    tls_hostname: Optional[str] = None
    tls_handshake_first: bool = False
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    drain_timeout: int = DEFAULT_DRAIN_TIMEOUT
    user_credentials: Optional[Credentials] = None
    nkeys_seed: Optional[str] = None
    nkeys_seed_str: Optional[str] = None
    inbox_prefix: Union[str, bytes] = DEFAULT_INBOX_PREFIX
    pending_size: int = DEFAULT_PENDING_SIZE
    flush_timeout: Optional[float] = None


@dataclass
class RabbitMQQueueOption:
    name: str = None
    type: Union[ExchangeType, str] = ExchangeType.FANOUT
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False
    passive: bool = False
    arguments: Arguments = None
    timeout: TimeoutType = None
    robust: bool = True


@dataclass
class RabbitMQClientOption:
    host: str = field(default="localhost")
    port: int = field(default=1883)
    login: str = field(default="guest")
    password: str = field(default="guest")
    virtualhost: str = field(default="/")
    ssl: bool = field(default=False)
    loop: Optional[asyncio.AbstractEventLoop] = None
    ssl_options: Optional[SSLOptions] = None
    ssl_context: Optional[SSLContext] = None
    timeout: TimeoutType = None
    client_properties: Optional[FieldTable] = None
    queue_option: RabbitMQQueueOption = field(
        default_factory=lambda: RabbitMQQueueOption()
    )
