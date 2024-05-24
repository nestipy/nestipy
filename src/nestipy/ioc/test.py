from typing import get_args, Type, ForwardRef

from nestipy.ioc import RequestContextContainer
from nestipy.ioc.dependency import create_type_annotated


def callback(req: RequestContextContainer):
    return req.get_instance()


Injector = create_type_annotated('injector', callback)


def test(type_checking: Injector[dict]):
    print(get_args(type_checking))


if __name__ == '__main__':
    test(dict())
