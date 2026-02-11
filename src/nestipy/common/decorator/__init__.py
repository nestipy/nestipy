from typing import Callable, Type, Union, Any

from .class_ import Module, Controller, Injectable, Scope
from .method import Route, Get, Post, Patch, Put, Delete, Version, Cache


def apply_decorators(*callback: Callable[[Union[Type | Callable]], Any]):
    def decorator(cls: Union[Type | Callable]):
        for deco in callback:
            cls = deco(cls)
        return cls

    return decorator


__all__ = [
    "Module",
    "Controller",
    "Injectable",
    "Scope",
    "Route",
    "Get",
    "Post",
    "Put",
    "Patch",
    "Delete",
    "Version",
    "Cache",
    "apply_decorators",
]
