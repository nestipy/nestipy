"""CLI command body for ``nestipy run client:gen``."""

from __future__ import annotations

from typing import Optional

from nestipy.commander.style import echo

from . import generate_client, generate_client_from_url


def _parse(args: tuple) -> dict:
    parsed: dict[str, Optional[str]] = {
        "output": None,
        "class_name": "ApiClient",
        "prefix": "",
        "spec": None,
    }
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in {"--output", "-o"} and i + 1 < len(args):
            parsed["output"] = args[i + 1]
            i += 1
        elif arg in {"--class", "--name"} and i + 1 < len(args):
            parsed["class_name"] = args[i + 1]
            i += 1
        elif arg == "--prefix" and i + 1 < len(args):
            parsed["prefix"] = args[i + 1]
            i += 1
        elif arg in {"--spec", "--url"} and i + 1 < len(args):
            parsed["spec"] = args[i + 1]
            i += 1
        i += 1
    return parsed


def run_client_gen(modules: list[type], args: tuple) -> None:
    """Generate a typed TypeScript client from controllers or a router-spec URL.

    Usage::

        nestipy run client:gen --output clients/api_client.ts [--class ApiClient]
                               [--prefix /api] [--spec http://127.0.0.1:8000/_router/spec]
    """
    parsed = _parse(args)
    output = parsed["output"]
    if not output:
        echo.error("Missing --output for client:gen")
        return

    class_name = parsed["class_name"] or "ApiClient"
    spec_url = parsed["spec"]
    if spec_url:
        generate_client_from_url(spec_url, output, class_name=class_name)
    else:
        generate_client(modules, output, class_name=class_name, prefix=parsed["prefix"] or "")
    echo.info(f"TypeScript client written to {output}")
