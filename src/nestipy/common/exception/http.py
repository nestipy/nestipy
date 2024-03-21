from typing import Union


class HttpException(Exception):
    def __init__(self, status_code: int, message: str = None, details: Union[dict, str] = None):
        self.status_code = status_code
        self.message = message
        self.details = details

    def __str__(self):
        return f"{self.status_code} - {self.message} - {self.details}"
