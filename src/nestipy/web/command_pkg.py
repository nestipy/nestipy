from __future__ import annotations

import json
import subprocess
from typing import Iterable

from nestipy.web.config import WebConfig

from .command_args import collect_packages, parse_args
from .command_shell import run_command_capture, select_package_manager, web_build_log_mode, web_log


def install(args: Iterable[str]) -> None:
    """Install frontend dependencies using the detected package manager."""
    parsed = parse_args(args)
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
    )
    if not (config.resolve_out_dir() / "package.json").exists():
        from nestipy.web.compiler import ensure_vite_files

        ensure_vite_files(config)
    install_deps(config)


def add(args: Iterable[str]) -> None:
    """Add frontend dependencies to the Vite project."""
    parsed = parse_args(args)
    packages = collect_packages(args)
    if not packages:
        raise RuntimeError("Provide at least one package to add.")
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
    )
    out_dir = config.resolve_out_dir()
    if not (out_dir / "package.json").exists():
        from nestipy.web.compiler import ensure_vite_files

        ensure_vite_files(config)
    if parsed.get("peer"):
        add_peer_dependencies(out_dir, packages)
        install_deps(config)
        return

    manager = select_package_manager(out_dir)
    if manager == "pnpm":
        cmd = ["pnpm", "add"]
        if parsed.get("dev"):
            cmd.append("-D")
    elif manager == "yarn":
        cmd = ["yarn", "add"]
        if parsed.get("dev"):
            cmd.append("--dev")
    else:
        cmd = ["npm", "install"]
        if parsed.get("dev"):
            cmd.append("-D")
    cmd.extend(packages)
    subprocess.run(cmd, cwd=str(out_dir), check=False)


def install_deps(config: WebConfig) -> None:
    """Install frontend dependencies with the selected package manager."""
    out_dir = config.resolve_out_dir()
    manager = select_package_manager(out_dir)
    web_log(f"Install: running {manager} install")
    if manager == "pnpm":
        cmd = ["pnpm", "install"]
    elif manager == "yarn":
        cmd = ["yarn", "install"]
    else:
        cmd = ["npm", "install"]
    rc, lines = run_command_capture(cmd, str(out_dir))
    mode = web_build_log_mode()
    if mode != "silent":
        added_line = next((l for l in lines if "added " in l and "package" in l), None)
        audited_line = next((l for l in lines if "audited " in l), None)
        vuln_line = next((l for l in lines if "vulnerabilities" in l), None)
        summary_parts = [p for p in (added_line, audited_line, vuln_line) if p]
        if summary_parts:
            web_log(f"Install: {' | '.join(summary_parts)}")
        else:
            web_log("Install: complete")
    if rc != 0:
        raise RuntimeError("Dependency install failed.")


def add_peer_dependencies(out_dir, packages: list[str]) -> None:
    """Add peerDependencies entries to the package.json."""
    package_json = out_dir / "package.json"
    if not package_json.exists():
        raise RuntimeError("package.json not found in web output directory.")
    data = json.loads(package_json.read_text(encoding="utf-8"))
    peers = data.setdefault("peerDependencies", {})
    for spec in packages:
        name, version = split_package_spec(spec)
        peers[name] = version
    package_json.write_text(json.dumps(data, indent=2), encoding="utf-8")


def split_package_spec(spec: str) -> tuple[str, str]:
    """Split a package spec into name and version (defaults to latest)."""
    if spec.startswith("@"):
        if "@" in spec[1:]:
            name, version = spec.rsplit("@", 1)
            return name, version or "latest"
        return spec, "latest"
    if "@" in spec:
        name, version = spec.split("@", 1)
        return name, version or "latest"
    return spec, "latest"
