import json
import uuid
from dataclasses import is_dataclass
from typing import Any, Optional, Type

from pydantic import BaseModel

from .interface import PipeTransform, PipeArgumentMetadata


class ParseIntPipe(PipeTransform):
    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> int:
        if value is None:
            raise ValueError("Value is required")
        try:
            return int(value)
        except Exception as exc:
            raise ValueError(f"Cannot parse int from '{value}'") from exc


class ParseFloatPipe(PipeTransform):
    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> float:
        if value is None:
            raise ValueError("Value is required")
        try:
            return float(value)
        except Exception as exc:
            raise ValueError(f"Cannot parse float from '{value}'") from exc


class ParseBoolPipe(PipeTransform):
    TRUE_VALUES = {"true", "1", "yes", "y", "on"}
    FALSE_VALUES = {"false", "0", "no", "n", "off"}

    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            raise ValueError("Value is required")
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in self.TRUE_VALUES:
                return True
            if normalized in self.FALSE_VALUES:
                return False
        raise ValueError(f"Cannot parse bool from '{value}'")


class ParseUUIDPipe(PipeTransform):
    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        if value is None:
            raise ValueError("Value is required")
        try:
            return uuid.UUID(str(value))
        except Exception as exc:
            raise ValueError(f"Cannot parse UUID from '{value}'") from exc


class ParseJsonPipe(PipeTransform):
    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> Any:
        if value is None:
            raise ValueError("Value is required")
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, (bytes, bytearray)):
            value = value.decode()
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as exc:
                raise ValueError("Cannot parse JSON") from exc
        return value


class DefaultValuePipe(PipeTransform):
    def __init__(self, default: Any):
        self.default = default

    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> Any:
        if value is None:
            return self.default
        return value


class ValidationPipe(PipeTransform):
    def __init__(self, metatype: Optional[Type] = None):
        self.metatype = metatype

    async def transform(self, value: Any, metadata: PipeArgumentMetadata) -> Any:
        if value is None:
            return value
        metatype = self.metatype or metadata.metatype
        if metatype is None:
            return value
        if not isinstance(metatype, type):
            return value
        if isinstance(value, metatype):
            return value
        if is_dataclass(metatype):
            if isinstance(value, dict):
                return metatype(**value)
            return metatype(value)
        if issubclass(metatype, BaseModel):
            if isinstance(value, dict):
                return metatype(**value)
            return metatype.model_validate(value)
        if metatype is bool:
            return await ParseBoolPipe().transform(value, metadata)
        try:
            return metatype(value)
        except Exception:
            return value
