import inspect
import re


class Utils:
    @classmethod
    def is_handler(cls, member):
        return inspect.isfunction(member) and hasattr(member, "handler__")

    @classmethod
    def string_to_url_path(cls, string):
        # Remove leading and trailing slashes for consistency.
        string = string.strip("/")
        # Replace invalid characters with underscores.
        valid_chars = r"[^a-zA-Z0-9\-_]"
        string = re.sub(valid_chars, '_', string)
        return '/' + string

    @classmethod
    def match_route(cls, route_pattern, url):
        pattern = re.compile(re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", route_pattern))
        match = pattern.match(url)
        return match is not None
