from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Type


@dataclass
class PipeArgumentMetadata:
    type: Optional[str] = None
    metatype: Optional[Type] = None
    data: Optional[str] = None


class PipeTransform(ABC):
    @abstractmethod
    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> Any:
        """
        Args:
            value (Any): Raw value
            metadata (PipeArgumentMetadata): Argument metadata
        """
        pass
