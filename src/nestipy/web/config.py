from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(slots=True)
class WebConfig:
    app_dir: str = "app"
    out_dir: str = "web"
    target: str = "vite"
    src_dir: str = "src"
    pages_dir: str = "pages"
    clean: bool = False

    def resolve_app_dir(self, root: str | None = None) -> Path:
        base = Path(root or os.getcwd())
        return (base / self.app_dir).resolve()

    def resolve_out_dir(self, root: str | None = None) -> Path:
        base = Path(root or os.getcwd())
        return (base / self.out_dir).resolve()

    def resolve_src_dir(self, root: str | None = None) -> Path:
        return self.resolve_out_dir(root) / self.src_dir

    def resolve_pages_dir(self, root: str | None = None) -> Path:
        return self.resolve_src_dir(root) / self.pages_dir


__all__ = ["WebConfig"]
