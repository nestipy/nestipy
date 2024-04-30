import dataclasses
from base64 import b64decode, b64encode
from typing import Type, Union, Literal

import itsdangerous
import ujson
from itsdangerous.exc import BadSignature

from nestipy.common.decorator import Injectable
from nestipy.common.http_ import Request, Response
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.types_ import NextFn


@dataclasses.dataclass
class SessionOption:
    secret_key: str = ''
    session_cookie: str = "session"
    max_age: Union[int, None] = 14 * 24 * 60 * 60
    path: str = "/"
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False
    domain: Union[str, None] = None


def session(option: SessionOption = SessionOption()) -> Type:
    @Injectable()
    class SessionMiddleware(NestipyMiddleware):

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
                    req.session = ujson.loads(b64decode(un_sign_data))
                    initial_session_was_empty = False
                except BadSignature:
                    req.session = {}
            else:
                req.session = {}
            result = await next_fn()
            cookie_max_age = f"Max-Age={option.max_age}; " if option.max_age else ""
            header_value = ", ".join([
                f"{key}={value}; path={option.path}; {cookie_max_age}{security_flags}"
                for (key, value) in res.cookies()
            ])
            if header_value:
                header_value += ", "
            if req.session:
                data = b64encode(ujson.dumps(req.session).encode("utf-8"))
                sign_data = signer.sign(data)
                header_value += "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                    session_cookie=option.session_cookie,
                    data=sign_data.decode("utf-8"),
                    path=option.path,
                    max_age=f"Max-Age={option.max_age}; " if option.max_age else "",
                    security_flags=security_flags,
                )
                res.header('Set-Cookie', header_value)
            elif initial_session_was_empty:
                header_value += "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                    session_cookie=option.session_cookie,
                    data="null",
                    path=option.path,
                    expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                    security_flags=security_flags,
                )
                res.header("Set-Cookie", header_value)

            return result

    return SessionMiddleware
