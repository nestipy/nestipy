import inspect
from snakecase import convert


def Injectable(_name: str = None):
    def wrapper(cls):
        setattr(cls, 'injectable__', True)
        setattr(cls, 'injectable__name__', convert(cls.__name__))
        if _name is not None:
            setattr(cls, 'token__', _name)
        return cls

    return wrapper
