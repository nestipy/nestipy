from typing import Optional, Any


class Inject:
    def __init__(self, cls, default: Optional = None):
        if not isinstance(cls, str) and not hasattr(cls, "injectable__"):
            raise Exception(f"{cls.__name__} is not injectable")
        setattr(self, 'default', default)
        setattr(self, 'dependency', cls)
