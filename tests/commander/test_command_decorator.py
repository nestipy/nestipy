from nestipy.commander.decorator import Command
from nestipy.commander.meta import CommanderMeta
from nestipy.common.constant import NESTIPY_SCOPE_ATTR
from nestipy.metadata import Reflector


def test_command_decorator_sets_metadata():
    def handler():
        return "ok"

    decorated = Command("hello", "desc")(handler)
    meta = Reflector.get_metadata(decorated, CommanderMeta.Meta, None)

    assert meta is not None
    assert meta.get("name") == "hello"
    assert meta.get("description") == "desc"
    # Injectable should mark the handler with scope metadata
    assert getattr(decorated, NESTIPY_SCOPE_ATTR, None) is not None
