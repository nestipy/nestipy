import os
import shutil

from minijinja import Environment


class TemplateGenerator:
    env: Environment

    def __init__(self):
        self.env = Environment(
            loader=self.loader
        )
        self.env.add_filter('capitalize', str.capitalize)
        self.env.add_filter('lower', str.lower)

    @classmethod
    def loader(cls, name):
        segments = []
        for segment in name.split("/"):
            if "\\" in segment or segment in (".", ".."):
                return None
            segments.append(segment)
        try:
            path = os.path.join(os.path.dirname(__file__), 'views', *segments)
            with open(path) as f:
                content = f.read()
                return content
        except (IOError, OSError):
            pass

    def render_template(self, template, **kwargs):
        return self.env.render_template(template, **kwargs)

    @classmethod
    def copy_project(cls, destination):
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'project'), destination)
