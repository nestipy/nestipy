import os
from typing import Annotated

from dotenv import dotenv_values

from nestipy.common.decorator import Injectable
from nestipy.ioc import Inject
from .config_builder import CONFIG_OPTION, ConfigOption


@Injectable()
class ConfigService:
    options: Annotated[ConfigOption, Inject(CONFIG_OPTION)]
    env: dict = []

    def __init__(self):
        if self.options.ignore_env_file:
            self.env = dict(os.environ)
        else:
            env_directory = os.path.join(os.getcwd(), self.options.folder, '.env')
            self.env = dotenv_values(env_directory)
            if len(self.options.load) > 0:
                for load in self.options.load:
                    if callable(load):
                        self.env = {**self.env, **dict(load())}

    def get(self, key: str):
        return self.env.get(key)
