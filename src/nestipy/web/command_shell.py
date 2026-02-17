from __future__ import annotations

import os
import subprocess
from pathlib import Path

from nestipy.common.logger import logger


def web_build_log_mode() -> str:
    mode = os.getenv("NESTIPY_WEB_BUILD_LOG", "summary").strip().lower()
    if mode not in {"summary", "verbose", "silent"}:
        mode = "summary"
    return mode


def web_log(message: str) -> None:
    if logger.isEnabledFor(20):
        logger.info("[WEB] %s", message)
    else:
        print(f"[NESTIPY] INFO [WEB] {message}")


def run_command_capture(cmd: list[str], cwd: str) -> tuple[int, list[str]]:
    lines: list[str] = []
    process = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    assert process.stdout is not None
    for raw in process.stdout:
        line = raw.rstrip("\n")
        if line:
            lines.append(line)
        if web_build_log_mode() == "verbose":
            web_log(line)
    return process.wait(), lines


def summarize_build_lines(lines: list[str]) -> None:
    mode = web_build_log_mode()
    if mode == "silent":
        return
    for line in lines:
        text = line.strip()
        lower = text.lower()
        if text.startswith("dist/") or text.startswith("web/dist/"):
            web_log(text)
        elif "building" in lower and "vite" in lower:
            web_log(text)
        elif "modules transformed" in lower:
            web_log(text)
        elif "built in" in lower:
            web_log(text)


def log_build_failure(lines: list[str], tail: int = 200) -> None:
    """Emit useful error context from build output."""
    if not lines:
        web_log("Build failed with no output.")
        return
    lower_lines = [line for line in lines if "error" in line.lower() or "failed" in line.lower()]
    if lower_lines:
        web_log("Build errors:")
        for line in lower_lines[-tail:]:
            web_log(line)
        return
    web_log("Build failed. Last output:")
    for line in lines[-tail:]:
        web_log(line)


def select_package_manager(out_dir: Path) -> str:
    """Choose a package manager based on existing lockfiles."""
    if (out_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (out_dir / "yarn.lock").exists():
        return "yarn"
    return "npm"
