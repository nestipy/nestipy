
class MiddlewareConsumer:

    def __init__(self, compiler):
        self.compiler = compiler

    def apply_for_route(self, path, middleware):
        self.compiler.apply_middleware_to_path(path, [middleware])

    def apply_for_controller(self, ctrl, middleware):
        self.compiler.apply_middleware_to_ctrl(ctrl, [middleware])
