from nestipy.core.utils import Utils


def Controller(path: str = '/', **kwargs):
    def wrapper(cls):
        class_attrs = {
            "kwargs__": kwargs,
            "controller__": True,
            "path": Utils.string_to_url_path(path)
        }
        for key, value in class_attrs.items():
            setattr(cls, key, value)

        return cls

    return wrapper
