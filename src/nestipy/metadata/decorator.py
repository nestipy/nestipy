from typing import Any, Union

from .reflect import Reflect


class SetMetadata:
    def __init__(
        self, key: str, data: Any, as_list: bool = False, as_dict: bool = False
    ):
        self.key = key
        self.data = data
        self.as_list = as_list
        self.as_dict = as_dict
        pass

    def __call__(self, cls):
        default = [] if self.as_list else {} if self.as_dict else None
        meta: Union[list, dict] = Reflect.get_metadata(cls, self.key, default)
        if self.as_list:
            meta = meta + self.data
        elif self.as_dict:
            meta.update(self.data)
        else:
            meta = self.data
        Reflect.set_metadata(cls, self.key, meta)
        return cls
