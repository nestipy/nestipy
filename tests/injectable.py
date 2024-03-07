import inspect
import functools


class Injectable:
    _registry = {}
    _instances = {}
    _being_resolved = set()

    def __init__(self, key=None):
        self.key = key

    def __call__(self, obj):
        if inspect.isclass(obj):
            self._registry[obj.__name__] = obj
            return obj
        elif inspect.isfunction(obj):
            if self.key:
                self._registry[self.key] = obj
                return obj
            else:
                raise ValueError("Key must be specified for function registration")
        else:
            raise ValueError("Unsupported type for Injectable")

    @classmethod
    def resolve_dependencies(cls):
        for name, obj in cls._registry.items():
            if inspect.isclass(obj):
                cls._instances[name] = cls._resolve(obj)

        # Resolve functions after all classes are resolved
        for name, obj in cls._registry.items():
            if inspect.isfunction(obj):
                cls._instances[name] = cls.resolve(obj)

    @classmethod
    def resolve(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dependencies = cls._resolve_dependencies(func)
            return func(**dependencies)

        return wrapper

    @classmethod
    def _resolve(cls, obj):
        if inspect.isclass(obj):
            if obj.__name__ in cls._being_resolved:
                raise RuntimeError("Circular dependency detected.")
            cls._being_resolved.add(obj.__name__)

            instance = cls._instantiate(obj)
            cls._being_resolved.remove(obj.__name__)
            return instance
        else:
            return obj

    @classmethod
    def _resolve_dependencies(cls, func):
        dependencies = {}
        signature = inspect.signature(func)
        for param_name, param in signature.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                dependency_cls_name = param.annotation
                if dependency_cls_name not in cls._instances:
                    dependencies[param.name] = cls._resolve(cls.resolve(param.annotation))
                else:
                    dependencies[param.name] = cls._instances[dependency_cls_name]
        return dependencies

    @classmethod
    def _instantiate(cls, obj):
        init_method = getattr(obj, "__init__", None)
        if init_method:
            init_signature = inspect.signature(init_method)
            init_params = list(init_signature.parameters.values())[1:]  # Exclude 'self' parameter
            dependencies = {}
            for param in init_params:
                if param.annotation != inspect.Parameter.empty:
                    dependency_cls_name = param.annotation
                    if dependency_cls_name not in cls._instances:
                        dependencies[param.name] = cls._resolve(cls.resolve(param.annotation))
                    else:
                        dependencies[param.name] = cls._instances[dependency_cls_name]
            instance = obj(**dependencies)
        else:
            instance = obj()
        return instance


def inject(obj):
    return Injectable._instances.get(obj)


def external_dependency(cls):
    cls.__external_dependency__ = True
    return cls


@Injectable(key="some_function")
def some_function(dependency: 'AnotherDependency'):
    return dependency.some_dependency.value


@Injectable()
class SomeDependency:
    def __init__(self):
        self.value = "Hello, world!"


@Injectable()
class AnotherDependency:
    def __init__(self, some_dependency: SomeDependency):
        self.some_dependency = some_dependency


# Register Injectable services and resolve dependencies
Injectable.resolve_dependencies()

# Example usage with class
service_instance = inject("SomeDependency")
print(service_instance.value)  # Output: Hello, world!

# Example usage with function
result = inject("some_function")()
print(result)  # Output: Hello, world!
