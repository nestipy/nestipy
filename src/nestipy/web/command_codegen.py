from __future__ import annotations

import hashlib
import json
import os
import traceback
import urllib.error
import urllib.request
from typing import Iterable, Type

from nestipy.common.logger import logger
from nestipy.web.actions_client import (
    codegen_actions_from_url,
    generate_actions_client_code_from_schema,
    write_actions_client_file,
)
from nestipy.web.client import codegen_client, codegen_client_from_url
from nestipy.web.config import WebConfig

from .command_args import parse_args


def codegen(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Generate an API client from a router spec or modules."""
    parsed = parse_args(args)
    output = parsed.get("output")
    if not output:
        raise RuntimeError("Missing --output for web:codegen")

    language = str(parsed.get("lang", "python"))
    class_name = str(parsed.get("class_name", "ApiClient"))
    prefix = str(parsed.get("prefix", ""))

    spec_url = parsed.get("spec")
    if spec_url:
        codegen_client_from_url(str(spec_url), str(output), language=language, class_name=class_name)
        return

    if modules is None:
        raise RuntimeError("Modules are required to generate client without --spec")

    codegen_client(modules, str(output), language=language, class_name=class_name, prefix=prefix)


def codegen_actions(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Generate an actions client from modules or a schema URL."""
    parsed = parse_args(args)
    spec_url = parsed.get("spec")
    if modules is None:
        if spec_url:
            output = parsed.get("actions_output") or parsed.get("output")
            if not output:
                output = "web/src/actions.client.ts"
            codegen_actions_from_url(str(spec_url), str(output))
            return
        raise RuntimeError("Modules are required to generate actions client")
    output = parsed.get("actions_output") or parsed.get("output")
    if not output:
        output = "web/src/actions.client.ts"
    endpoint = str(parsed.get("actions_endpoint", "/_actions"))
    write_actions_client_file(modules, str(output), endpoint=endpoint)


def maybe_codegen_client(parsed: dict[str, str | bool], config: WebConfig) -> None:
    """Generate a router client if a spec URL is configured."""
    spec_url = parsed.get("spec")
    if not spec_url:
        return
    language = str(parsed.get("lang", "ts"))
    output = parsed.get("output")
    if not output:
        default_path = config.resolve_src_dir() / "api" / "client.ts"
        output = str(default_path)
    class_name = str(parsed.get("class_name", "ApiClient"))
    codegen_client_from_url(str(spec_url), str(output), language=language, class_name=class_name)


def maybe_codegen_actions(
    parsed: dict[str, str | bool], config: WebConfig, modules: list[Type] | None
) -> None:
    """Generate an actions client if requested via CLI flags."""
    if not parsed.get("actions"):
        return
    spec_url = parsed.get("spec")
    output = parsed.get("actions_output")
    if not output:
        output = str(config.resolve_src_dir() / "actions.client.ts")
    if modules is None:
        if spec_url:
            codegen_actions_from_url(str(spec_url), str(output))
        return
    endpoint = str(parsed.get("actions_endpoint", "/_actions"))
    write_actions_client_file(modules, str(output), endpoint=endpoint)


def maybe_codegen_actions_schema(
    url: str,
    output: str,
    last_hash: str | None,
    last_etag: str | None,
) -> tuple[str | None, str | None]:
    """Fetch the action schema and update the client file if it changed."""
    headers: dict[str, str] = {}
    if last_etag:
        headers["If-None-Match"] = last_etag
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            etag = response.headers.get("ETag")
            schema = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return last_hash, last_etag
        return last_hash, last_etag
    except Exception:
        return last_hash, last_etag
    code = generate_actions_client_code_from_schema(schema)
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    if digest == last_hash:
        return last_hash, last_etag
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)
    logger.info("[WEB] Actions client updated")
    return digest, (etag or last_etag)


def hash_file(path: str) -> str | None:
    """Hash a file's content for change detection."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def maybe_codegen_router_spec(
    url: str,
    output: str,
    last_hash: str | None,
) -> str | None:
    """Fetch the router spec and update the client file if it changed."""
    try:
        codegen_client_from_url(url, output, language="ts", class_name="ApiClient")
    except Exception:
        logger.exception("[WEB] router client generation failed")
        if not logger.isEnabledFor(20):
            traceback.print_exc()
        return last_hash
    digest = hash_file(output)
    if digest and digest != last_hash:
        logger.info("[WEB] API client updated")
    return digest or last_hash
