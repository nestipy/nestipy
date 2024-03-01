import inspect


class HookCompiler:
    def __init__(self, compiler):
        self.compiler = compiler

    def extract_hook_in_module(self, hook, module):
        if hasattr(module, hook) and inspect.ismethod(getattr(module, hook)):
            hook__ = getattr(module, hook)
            hooks = []
            if hook in self.compiler.hooks.keys():
                hooks = self.compiler.hooks[hook]
            hooks.append(hook__)
            self.compiler.hooks[hook] = hooks

    def extract_hooks_in_module(self, module):
        self.extract_hook_in_module("on_startup", module)
        self.extract_hook_in_module("on_shutdown", module)
