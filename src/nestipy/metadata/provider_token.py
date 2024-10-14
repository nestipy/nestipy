from dataclasses import dataclass
from typing import Union


@dataclass
class ProviderToken:
    key: Union[str, None] = None
