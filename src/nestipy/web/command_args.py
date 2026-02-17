from __future__ import annotations

from typing import Iterable


def parse_args(args: Iterable[str]) -> dict[str, str | bool]:
    """Parse Nestipy web CLI arguments into a simple dict."""
    parsed: dict[str, str | bool] = {}
    args_list = list(args)
    i = 0
    while i < len(args_list):
        arg = args_list[i]
        if arg in {"--app", "--app-dir"} and i + 1 < len(args_list):
            parsed["app_dir"] = args_list[i + 1]
            i += 1
        elif arg in {"--out", "--out-dir"} and i + 1 < len(args_list):
            parsed["out_dir"] = args_list[i + 1]
            i += 1
        elif arg == "--clean":
            parsed["clean"] = True
        elif arg == "--watch":
            parsed["watch"] = True
        elif arg == "--vite":
            parsed["vite"] = True
        elif arg == "--install":
            parsed["install"] = True
        elif arg == "--backend" and i + 1 < len(args_list):
            parsed["backend"] = args_list[i + 1]
            i += 1
        elif arg == "--backend-cwd" and i + 1 < len(args_list):
            parsed["backend_cwd"] = args_list[i + 1]
            i += 1
        elif arg == "--proxy" and i + 1 < len(args_list):
            parsed["proxy"] = args_list[i + 1]
            i += 1
        elif arg == "--proxy-paths" and i + 1 < len(args_list):
            parsed["proxy_paths"] = args_list[i + 1]
            i += 1
        elif arg == "--router-spec" and i + 1 < len(args_list):
            parsed["router_spec"] = args_list[i + 1]
            i += 1
        elif arg == "--router-output" and i + 1 < len(args_list):
            parsed["router_output"] = args_list[i + 1]
            i += 1
        elif arg == "--no-build":
            parsed["no_build"] = True
        elif arg in {"--dev", "-D"}:
            parsed["dev"] = True
        elif arg == "--peer":
            parsed["peer"] = True
        elif arg == "--actions":
            parsed["actions"] = True
        elif arg == "--actions-output" and i + 1 < len(args_list):
            parsed["actions_output"] = args_list[i + 1]
            i += 1
        elif arg == "--actions-endpoint" and i + 1 < len(args_list):
            parsed["actions_endpoint"] = args_list[i + 1]
            i += 1
        elif arg == "--actions-watch" and i + 1 < len(args_list):
            parsed["actions_watch"] = args_list[i + 1]
            i += 1
        elif arg == "--ssr":
            parsed["ssr"] = True
        elif arg == "--ssr-entry" and i + 1 < len(args_list):
            parsed["ssr_entry"] = args_list[i + 1]
            i += 1
        elif arg == "--ssr-out-dir" and i + 1 < len(args_list):
            parsed["ssr_out_dir"] = args_list[i + 1]
            i += 1
        elif arg == "--ssr-runtime" and i + 1 < len(args_list):
            parsed["ssr_runtime"] = args_list[i + 1]
            i += 1
        elif arg == "--target" and i + 1 < len(args_list):
            parsed["target"] = args_list[i + 1]
            i += 1
        elif arg == "--spec" and i + 1 < len(args_list):
            parsed["spec"] = args_list[i + 1]
            i += 1
        elif arg == "--output" and i + 1 < len(args_list):
            parsed["output"] = args_list[i + 1]
            i += 1
        elif arg == "--lang" and i + 1 < len(args_list):
            parsed["lang"] = args_list[i + 1]
            i += 1
        elif arg == "--class" and i + 1 < len(args_list):
            parsed["class_name"] = args_list[i + 1]
            i += 1
        elif arg == "--prefix" and i + 1 < len(args_list):
            parsed["prefix"] = args_list[i + 1]
            i += 1
        i += 1
    return parsed


def collect_packages(args: Iterable[str]) -> list[str]:
    """Extract non-flag arguments as package specs."""
    args_list = list(args)
    packages: list[str] = []
    skip_next = False
    flags_with_values = {
        "--app",
        "--app-dir",
        "--out",
        "--out-dir",
        "--backend",
        "--backend-cwd",
        "--proxy",
        "--proxy-paths",
        "--actions-output",
        "--actions-endpoint",
        "--actions-watch",
        "--ssr-entry",
        "--ssr-out-dir",
        "--ssr-runtime",
        "--target",
        "--spec",
        "--output",
        "--lang",
        "--class",
        "--prefix",
    }
    flags_bool = {
        "--clean",
        "--watch",
        "--vite",
        "--install",
        "--no-build",
        "--actions",
        "--ssr",
        "--dev",
        "-D",
        "--peer",
    }
    for arg in args_list:
        if skip_next:
            skip_next = False
            continue
        if arg in flags_with_values:
            skip_next = True
            continue
        if arg in flags_bool:
            continue
        if arg.startswith("--"):
            continue
        packages.append(arg)
    return packages
