from nestipy.openapi.openapi_docs.mk.common import (
    is_reference,
    is_object_schema,
    is_array_schema,
    get_ref_type_name,
)


def test_is_reference():
    assert is_reference({"$ref": "#/components/schemas/Foo"}) is True
    assert is_reference({"ref": "no"}) is False
    assert is_reference("not-dict") is False


def test_is_object_schema():
    assert is_object_schema({"type": "object", "properties": {"a": {}}}) is True
    assert is_object_schema({"type": "object"}) is False
    assert is_object_schema({"type": "array", "items": {}}) is False


def test_is_array_schema():
    assert is_array_schema({"type": "array", "items": {"type": "string"}}) is True
    assert is_array_schema({"type": "array"}) is False
    assert is_array_schema({"type": "object", "properties": {}}) is False


def test_get_ref_type_name():
    assert get_ref_type_name("#/components/schemas/Foo") == "Foo"
    assert get_ref_type_name({"$ref": "#/components/schemas/Bar"}) == "Bar"
