import dataclasses
import inspect
from abc import ABC, abstractmethod
from base64 import b64decode, b64encode
from typing import Type, Union, Literal, Any, Callable
from uuid import uuid4

import itsdangerous
import ujson
from itsdangerous.exc import BadSignature

from nestipy.common.decorator import Injectable
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.types_ import NextFn


class SessionStore(ABC):
    def __init__(self):
        self.store = {}

    @abstractmethod
    def get(self, session_id: str) -> dict:
        raise NotImplemented("Must implement")

    @abstractmethod
    def set(self, session_id: str, session_data: Any) -> None:
        raise NotImplemented("Must implement")

    @abstractmethod
    def delete(self, session_id: str) -> None:
        raise NotImplemented("Must implement")


class InMemoryStore(SessionStore):
    def __init__(self):
        super().__init__()

    def get(self, session_id: str) -> dict:
        return self.store.get(session_id, {})

    def set(self, session_id: str, session_data: Any) -> None:
        self.store[session_id] = session_data

    def delete(self, session_id: str) -> None:
        if session_id in self.store:
            del self.store[session_id]


@dataclasses.dataclass
class SessionCookieOption:
    secret_key: str = ""
    session_cookie: str = "cookie-session"
    max_age: Union[int, None] = 60 * 60
    path: str = "/"
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False
    domain: Union[str, None] = None


def cookie_session(option: SessionCookieOption = SessionCookieOption()) -> Type:
    @Injectable()
    class CookieSessionMiddleware(NestipyMiddleware):
        async def use(self, req: Request, res: Response, next_fn: NextFn):
            initial_session_was_empty = True
            signer = itsdangerous.TimestampSigner(str(option.secret_key))
            security_flags = "httponly; samesite=" + option.same_site
            if option.https_only:
                security_flags += "; secure"
            if option.domain is not None:
                security_flags += f"; domain={option.domain}"
            if option.session_cookie in req.cookies:
                data = req.cookies[option.session_cookie].encode("utf-8")
                try:
                    un_sign_data = signer.unsign(data, max_age=option.max_age)
                    req.session = {**req.session, **ujson.loads(b64decode(un_sign_data))}
                    initial_session_was_empty = False
                except BadSignature:
                    pass
            try:
                result = await next_fn()
            finally:
                cookie_max_age = f"Max-Age={option.max_age}; " if option.max_age else ""
                header_value = ", ".join(
                    [
                        f"{key}={value}; path={option.path}; {cookie_max_age}{security_flags}"
                        for (key, value) in res.cookies()
                    ]
                )
                if header_value:
                    header_value += ", "
                if req.session:
                    data = b64encode(ujson.dumps(req.session).encode("utf-8"))
                    sign_data = signer.sign(data)
                    header_value += "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                        # noqa E501
                        session_cookie=option.session_cookie,
                        data=sign_data.decode("utf-8"),
                        path=option.path,
                        max_age=f"Max-Age={option.max_age}; " if option.max_age else "",
                        security_flags=security_flags,
                    )
                    res.header("Set-Cookie", header_value)
                elif initial_session_was_empty:
                    header_value += "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(
                        # noqa E501
                        session_cookie=option.session_cookie,
                        data="null",
                        path=option.path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=security_flags,
                    )
                    res.header("Set-Cookie", header_value)

            return result

    return CookieSessionMiddleware


@dataclasses.dataclass
class SessionOption:
    secret_key: str = ""
    session_key: str = "session"
    max_age: Union[int, None] = 60 * 60
    path: str = "/"
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False
    domain: Union[str, None] = None
    store: SessionStore = InMemoryStore()


async def call(callback: Callable, *args, **kwargs):
    if inspect.iscoroutinefunction(callback):
        return await callback(*args, **kwargs)
    else:
        return callback(*args, **kwargs)


def session(option: SessionOption = SessionOption()):
    @Injectable()
    class SessionMiddleware(NestipyMiddleware):
        async def use(self, req: "Request", res: "Response", next_fn: "NextFn"):
            initial_session_was_empty = True
            security_flags = "httponly; samesite=" + option.same_site
            if option.https_only:
                security_flags += "; secure"
            if option.domain is not None:
                security_flags += f"; domain={option.domain}"

            session_id = req.cookies.get(option.session_key)

            if session_id and session_id in option.store.store:
                sessions = await call(option.store.get, session_id)
                req.session = {**req.session, **sessions}
                initial_session_was_empty = False
            else:
                session_id = str(uuid4())
            try:
                result = await next_fn()
            finally:
                cookie_max_age = f"Max-Age={option.max_age}; " if option.max_age else ""
                header_value = ", ".join(
                    [
                        f"{key}={value}; path={option.path}; {cookie_max_age}{security_flags}"
                        for (key, value) in res.cookies()
                    ]
                )
                if header_value:
                    header_value += ", "

                await call(option.store.set, session_id, req.session)
                if req.session:
                    header_value += "{session_key}={data}; path={path}; {max_age}{security_flags}".format(
                        session_key=option.session_key,
                        data=session_id,
                        path=option.path,
                        max_age=f"Max-Age={option.max_age}; " if option.max_age else "",
                        security_flags=security_flags,
                    )
                    res.header("Set-Cookie", header_value)
                elif initial_session_was_empty:
                    header_value += "{session_key}={data}; path={path}; {expires}{security_flags}".format(
                        session_key=option.session_key,
                        data="null",
                        path=option.path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=security_flags,
                    )
                    res.header("Set-Cookie", header_value)

            return result

    return SessionMiddleware
