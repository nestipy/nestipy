import pytest

from dataclasses import dataclass

from nestipy.common.pipes import ValidationPipe
from nestipy.common.pipes import PipeArgumentMetadata


@dataclass
class Cat:
    name: str


@pytest.mark.asyncio
async def test_validation_pipe_whitelist_transform():
    pipe = ValidationPipe(whitelist=True, transform=True)
    value = {"name": "milo", "extra": "ignore"}
    result = await pipe.transform(value, PipeArgumentMetadata(metatype=Cat))
    assert isinstance(result, Cat)
    assert result.name == "milo"


@pytest.mark.asyncio
async def test_validation_pipe_whitelist_forbid():
    pipe = ValidationPipe(whitelist=True, forbid_non_whitelisted=True)
    value = {"name": "milo", "extra": "no"}
    with pytest.raises(ValueError):
        await pipe.transform(value, PipeArgumentMetadata(metatype=Cat))


@pytest.mark.asyncio
async def test_validation_pipe_no_transform():
    pipe = ValidationPipe(whitelist=True, transform=False)
    value = {"name": "milo", "extra": "ignore"}
    result = await pipe.transform(value, PipeArgumentMetadata(metatype=Cat))
    assert isinstance(result, dict)
    assert result == {"name": "milo"}
