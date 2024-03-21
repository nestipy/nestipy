from typing import Any, Union

from .reflect import Reflect


class SetMetadata:
    def __init__(self, key: str, data: Any, as_list: bool = False, as_dict: bool = False):
        self.key = key
        self.data = data
        self.as_list = as_list
        self.as_dict = as_dict
        pass

    def __call__(self, cls):
        default = [] if self.as_list else {}
        meta: Union[list, dict] = Reflect.get_metadata(cls, self.key, default)
        if self.as_list:
            meta = meta + self.data
        else:
            meta.update(self.data)

        # if self.key in meta.keys():
        #
        #         data: Union[list[Any], Any] = meta[self.key]
        #         if isinstance(data, list):
        #             data += self.data
        #         else:
        #             data = data + self.data
        #         meta[self.key] = data
        #     if self.as_dict:
        #         data: dict = meta[self.key]
        #         data.update(self.data)
        #         meta[self.key] = data
        # else:
        #     meta[self.key] = self.data
        Reflect.set_metadata(cls, self.key, meta)
        return cls
