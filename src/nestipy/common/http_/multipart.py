from __future__ import annotations

import re
from urllib.parse import parse_qsl as _parse_qsl

__all__ = ("parse_content_header",)

_token = r"([\w!#$%&'*+\-.^_`|~]+)"  # noqa: S105
_quoted = r'"([^"]*)"'
_param = re.compile(rf";\s*{_token}=(?:{_token}|{_quoted})", re.ASCII)
_firefox_quote_escape = re.compile(r'\\"(?!; |\s*$)')


def parse_qsl(qs: bytes, separator: str) -> list[tuple[str, str]]:
    return _parse_qsl(qs.decode("utf-8"), keep_blank_values=True, separator=separator)


def parse_content_header(value: str) -> tuple[str, dict[str, str]]:
    value = _firefox_quote_escape.sub("%22", value)
    pos = value.find(";")
    if pos == -1:
        options: dict[str, str] = {}
    else:
        options = {
            m.group(1).lower(): m.group(2) or m.group(3).replace("%22", '"')
            for m in _param.finditer(value[pos:])
        }
        value = value[:pos]
    return value.strip().lower(), options
