from nestipy.common.decorator import Module

from .guard_service import GuardService


@Module(
    providers=[GuardService],
    exports=[GuardService],
)
class GuardModule:
    ...
