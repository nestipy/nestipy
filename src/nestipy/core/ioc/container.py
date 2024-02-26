import inspect

from ...common.decorator.inject import Inject


class NestipyContainer:
    def __init__(self):
        self.dependencies = {}
        self.instances = {}

    def register(self, cls, token: str = None):
        if cls in self.dependencies:
            return
        if token is not None:
            self.dependencies[token] = cls
            return
        params = inspect.getmembers(cls, predicate=lambda member: isinstance(member, Inject))
        dependencies = {param[0]: param[1] for param in params}
        self.dependencies[cls] = dependencies

    def resolve_method(self, method, token):
        if token not in self.dependencies:
            self.register(method, token)
        if token in self.instances:
            return self.instances[token]
        instance = method()
        self.instances[token] = instance
        return instance

    def resolve_class_property_inject(self, cls, module, exist=None):
        dependency_resolved = []
        if exist is not None:
            dependency_resolved = []
        if cls not in self.dependencies:
            self.register(cls)
        if cls in self.instances:
            return self.instances[cls]

        providers_imports = self.get_module_exported_providers(module)
        deps = self.dependencies[cls].items()
        if len(deps) > 0:
            dependency_resolved.append(cls)
        for name, dep in deps:
            dependency_cls = dep.dependency
            if dependency_cls in dependency_resolved:
                raise Exception(f"Circular dependency found for {cls.__name__}.")

            if hasattr(module, 'provider_instances__') and dependency_cls in getattr(module,
                                                                                     'provider_instances__').keys():
                provider_instances__ = getattr(module, 'provider_instances__')
                dep_resolved = provider_instances__[dependency_cls]
                setattr(cls, name, dep_resolved)
            elif isinstance(dependency_cls, str):
                lambda_function = self.find_method_by_token(dependency_cls, providers_imports.keys())
                if lambda_function is not None:
                    dep_resolved = self.resolve_method(lambda_function, dependency_cls)
                    setattr(cls, name, dep_resolved)
                else:
                    setattr(cls, name, dep.default)
            else:
                if dependency_cls not in providers_imports.keys():
                    return setattr(cls, name, dep.default)
                dep_resolved = self.resolve(dependency_cls, providers_imports[dependency_cls], dependency_resolved)
                setattr(cls, name, dep_resolved)

    def resolve(self, cls, module, exist=None):
        self.resolve_class_property_inject(cls, module, exist)
        instance = cls()
        self.instances[cls] = instance
        return instance

    @classmethod
    def get_module_exported_providers(cls, module):
        providers = {}
        imports = [m for m in module.imports if m is not None]
        for m in imports:
            for p in m.exports:
                if hasattr(p, 'injectable__'):
                    providers[p] = m
        for p in module.providers:
            if hasattr(p, 'injectable__'):
                providers[p] = module
        return providers

    @classmethod
    def find_method_by_token(cls, token, imports):
        for p in imports:
            if hasattr(p, 'token__') and p.token__ == token:
                return p

        return None
