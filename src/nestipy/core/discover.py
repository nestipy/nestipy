from typing import Type

from nestipy.common import Injectable
from nestipy.common.utils import uniq_list


@Injectable()
class DiscoverService:
    _modules = []
    _providers = []
    _controllers = []

    def get_all_controller(self) -> list[Type]:
        return uniq_list(self._controllers)

    def get_all_module(self) -> list:
        return uniq_list(self._modules)

    def get_all_provider(self) -> list[Type]:
        return uniq_list(self._providers)

    def add_controller(self, *ctrl: object):
        self._controllers += list(ctrl)

    def add_provider(self, *services: object):
        self._providers += list(services)

    def add_module(self, *module_ref: object):
        self._modules += list(module_ref)
