from abc import ABC, abstractmethod
from typing import Any

import ujson


class Serializer(ABC):
    @abstractmethod
    async def serialize(self, data: Any) -> str:
        pass

    @abstractmethod
    async def deserialize(self, data: str) -> Any:
        pass


class JSONSerializer(Serializer):
    async def serialize(self, data: Any) -> str:
        return ujson.dumps(data)

    async def deserialize(self, data: str) -> Any:
        return ujson.loads(data)
