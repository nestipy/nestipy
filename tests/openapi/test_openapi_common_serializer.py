from dataclasses import dataclass
from enum import Enum

from nestipy.openapi.openapi_docs.common import (
    normalize_key,
    normalize_dict_factory,
    Serializer,
)
from nestipy.openapi.openapi_docs.v3 import Reference


class Color(Enum):
    RED = "red"


@dataclass
class Sample:
    ref: str
    value: str


def test_normalize_key():
    assert normalize_key("example_key") == "exampleKey"
    assert normalize_key(Color.RED) == "red"


def test_normalize_dict_factory_handles_ref():
    data = normalize_dict_factory([("ref", "#/components/schemas/Test"), ("value", 1)])
    assert data["$ref"] == "#/components/schemas/Test"
    assert data["value"] == 1


def test_serializer_to_obj_and_json():
    serializer = Serializer()
    ref = Reference(ref="#/components/schemas/Test")
    obj = serializer.to_obj(ref)
    assert obj == {"$ref": "#/components/schemas/Test"}
    json_str = serializer.to_json(ref)
    assert "components" in json_str
