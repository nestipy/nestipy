from typing import Optional, Type, cast, Any

from nestipy.ioc.dependency import create_type_annotated
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.metadata import CtxDepKey

_ALL_ARGS_TOKEN = "__all_args__"


def _graphql_args_callback(
    _name: str,
    token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    args: dict = (
        cast(Any, _request_context.execution_context).switch_to_graphql().get_args()
    )
    if token in (None, _ALL_ARGS_TOKEN):
        return {k: v for k, v in args.items() if k not in ("root", "info")}
    if token:
        return args.get(token)
    return args


def _graphql_parent_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    args: dict = (
        cast(Any, _request_context.execution_context).switch_to_graphql().get_args()
    )
    return args.get("root")


def _graphql_context_callback(
    _name: str,
    _token: Optional[str],
    _type_ref: Type,
    _request_context: RequestContextContainer,
):
    return (
        cast(Any, _request_context.execution_context).switch_to_graphql().get_context()
    )


def Args(token: Optional[str] = None):
    actual_token = _ALL_ARGS_TOKEN if token is None else token
    return create_type_annotated(_graphql_args_callback, CtxDepKey.Args)(actual_token)
Context = create_type_annotated(_graphql_context_callback, CtxDepKey.Context)
def Parent():
    return create_type_annotated(_graphql_parent_callback, CtxDepKey.Args)("root")

__all__ = ["Args", "Context", "Parent"]
