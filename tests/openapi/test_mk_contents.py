import os
from datetime import datetime

from nestipy.openapi.openapi_docs.mk.contents import (
    JSONContentWriter,
    FormContentWriter,
    OADJSONEncoder,
)


def test_json_content_writer():
    writer = JSONContentWriter()
    assert writer.handle_content_type("application/json") is True
    content = writer.write({"a": 1})
    assert '"a"' in content


def test_form_content_writer():
    writer = FormContentWriter()
    assert writer.handle_content_type("x-www-form-urlencoded") is True
    assert writer.handle_content_type("application/x-www-form-urlencoded") is False
    assert writer.handle_content_type("multipart/form-data") is False
    assert writer.write({"a": "b"}) == "a=b"


def test_oad_json_encoder_datetime_format(monkeypatch):
    dt = datetime(2020, 1, 2, 3, 4, 5)
    monkeypatch.setenv("OPENAPI_DATETIME_FORMAT", "%Y/%m/%d")
    enc = OADJSONEncoder()
    assert enc.default(dt) == "2020/01/02"
    os.environ.pop("OPENAPI_DATETIME_FORMAT", None)
    assert "2020-01-02" in enc.default(dt)
