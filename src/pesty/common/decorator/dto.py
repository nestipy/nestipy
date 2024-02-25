from litestar.dto import DTOConfig, DataclassDTO
import inspect


def Dto():
    def wrapper(cls):
        class_attrs = {
            "config_module": DTOConfig(experimental_codegen_backend=True),
            "__module__": cls.__module__
        }
        for name, value in inspect.getmembers(cls):
            if not name.startswith('__'):
                class_attrs[name] = value

        return type(cls.__name__, (DataclassDTO[cls],) + cls.__bases__, {**class_attrs})

    return wrapper
