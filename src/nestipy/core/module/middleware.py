from dataclasses import dataclass
from typing import Callable


@dataclass
class MiddlewareDict:
    path: str
    middleware: Callable


class MiddlewareConsumer:

    def __init__(self, compiler):
        self.compiler = compiler

    def apply_for_route(self, module, path, middleware):
        self.compiler.apply_middleware_to_path(module, path, [middleware])

    def apply_for_controller(self, module, ctrl, middleware):
        self.compiler.apply_middleware_to_ctrl(module, ctrl, [middleware])
