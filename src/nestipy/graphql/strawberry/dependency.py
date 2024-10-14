from typing import Optional, Type

from nestipy.ioc.dependency import create_type_annotated
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.metadata import CtxDepKey


def args_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    args: dict = _request_context.execution_context.switch_to_graphql().get_args()
    return args.get(_token or _name)


def Root():
    return create_type_annotated(args_callback, CtxDepKey.Args)("root")


def Info():
    return create_type_annotated(args_callback, CtxDepKey.Args)("info")
