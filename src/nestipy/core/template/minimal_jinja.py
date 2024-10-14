import os
from typing import Any

from minijinja import Environment

from nestipy.common.template import TemplateEngine


class MinimalJinjaTemplateEngine(TemplateEngine):
    env: Environment

    def __init__(self, template_dir: str):
        super().__init__(template_dir)
        self.env = Environment(loader=self.loader)

    def loader(self, name):
        segments = []
        for segment in name.split("/"):
            if "\\" in segment or segment in (".", ".."):
                return None
            segments.append(segment)
        try:
            path = os.path.join(self.template_dir, *segments)
            with open(path) as f:
                content = f.read()
                return content
        except (IOError, OSError):
            pass

    def render(self, template: str, context: dict) -> str:
        return self.env.render_template(template, **context)

    def render_str(self, string: str, context: dict) -> str:
        return self.env.render_str(string, **context)

    def get_env(self) -> Any:
        return self.env
