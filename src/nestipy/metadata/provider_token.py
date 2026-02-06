from dataclasses import dataclass
from typing import Union

@dataclass
class ProviderToken:
    """
    Represents a token used for custom providers when a string is used instead of a class type.
    """
    key: Union[str, None] = None
