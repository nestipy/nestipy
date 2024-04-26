from __future__ import annotations

import re
from collections import defaultdict
from email.utils import decode_rfc2231
from functools import lru_cache
from typing import Any
from urllib.parse import unquote, parse_qsl as _parse_qsl

from .upload_file import UploadFile

__all__ = ("parse_body", "parse_content_header", "parse_multipart_form", "parse_url_encoded_form_data")

_token = r"([\w!#$%&'*+\-.^_`|~]+)"  # noqa: S105
_quoted = r'"([^"]*)"'
_param = re.compile(rf";\s*{_token}=(?:{_token}|{_quoted})", re.ASCII)
_firefox_quote_escape = re.compile(r'\\"(?!; |\s*$)')


def parse_qsl(qs: bytes, separator: str) -> list[tuple[str, str]]:
    return _parse_qsl(qs.decode("latin-1"), keep_blank_values=True, separator=separator)


@lru_cache(1024)
def parse_url_encoded_form_data(encoded_data: bytes) -> dict[str, str | list[str]]:
    """Parse an url encoded form data dict.

    Args:
        encoded_data: The encoded byte string.

    Returns:
        A parsed dict.
    """
    decoded_dict: defaultdict[str, list[str]] = defaultdict(list)
    for k, v in parse_qsl(encoded_data, separator="&"):
        decoded_dict[k].append(v)
    return {k: v if len(v) > 1 else v[0] for k, v in decoded_dict.items()}


def parse_content_header(value: str) -> tuple[str, dict[str, str]]:
    value = _firefox_quote_escape.sub("%22", value)
    pos = value.find(";")
    if pos == -1:
        options: dict[str, str] = {}
    else:
        options = {
            m.group(1).lower(): m.group(2) or m.group(3).replace("%22", '"') for m in _param.finditer(value[pos:])
        }
        value = value[:pos]
    return value.strip().lower(), options


def parse_body(body: bytes, boundary: bytes, multipart_form_part_limit: int) -> list[bytes]:
    if not (body and boundary):
        return []

    form_parts = body.split(boundary, multipart_form_part_limit + 3)[1:-1]

    if len(form_parts) > multipart_form_part_limit:
        raise Exception(
            f"number of multipart components exceeds the allowed limit of {multipart_form_part_limit}, "
            f"this potentially indicates a DoS attack"
        )

    return form_parts


def parse_multipart_form(
        body: bytes,
        boundary: bytes,
        multipart_form_part_limit: int = 1000,
        type_decoders: Any | None = None,
) -> dict[str, Any]:
    fields: defaultdict[str, list[Any]] = defaultdict(list)

    for form_part in parse_body(body=body, boundary=boundary, multipart_form_part_limit=multipart_form_part_limit):
        file_name = None
        content_type = "text/plain"
        content_charset = "utf-8"
        field_name = None
        line_index = 2
        line_end_index = 0
        headers: list[tuple[str, str]] = []

        while line_end_index != -1:
            line_end_index = form_part.find(b"\r\n", line_index)
            form_line = form_part[line_index:line_end_index].decode("utf-8")

            if not form_line:
                break

            line_index = line_end_index + 2
            colon_index = form_line.index(":")
            current_idx = colon_index + 2
            form_header_field = form_line[:colon_index].lower()
            form_header_value, form_parameters = parse_content_header(form_line[current_idx:])

            if form_header_field == "content-disposition":
                field_name = form_parameters.get("name")
                file_name = form_parameters.get("filename")

                if file_name is None and (filename_with_asterisk := form_parameters.get("filename*")):
                    encoding, _, value = decode_rfc2231(filename_with_asterisk)
                    file_name = unquote(value, encoding=encoding or content_charset)

            elif form_header_field == "content-type":
                content_type = form_header_value
                content_charset = form_parameters.get("charset", "utf-8")
            headers.append((form_header_field, form_header_value))

        if field_name:
            post_data = form_part[line_index:-4].lstrip(b"\r\n")
            if file_name:
                form_file = UploadFile(
                    content_type=content_type, filename=file_name, file_data=post_data, headers=dict(headers)
                )
                fields[field_name].append(form_file)
            elif post_data:
                fields[field_name].append(post_data.decode(content_charset))
            else:
                fields[field_name].append(None)

    return {k: v if len(v) > 1 else v[0] for k, v in fields.items()}
