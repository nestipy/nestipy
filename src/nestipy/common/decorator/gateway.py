from snakecase import convert


def Gateway(_name: str = None):
    def wrapper(cls):
        setattr(cls, 'injectable__', True)
        setattr(cls, 'gateway__', True)
        setattr(cls, 'injectable__name__', convert(cls.__name__))
        if _name is not None:
            setattr(cls, 'token__', _name)
        return cls

    return wrapper


def SubscribeMessage(event: str):
    def wrapper(cls):
        setattr(cls, 'gateway__handler__', True)
        setattr(cls, 'gateway__handler__event__', event)
        return cls

    return wrapper


GATEWAY_SERVER = 'GATEWAY_SERVER'

