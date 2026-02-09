from nestipy.commander.commander import NestipyCommander
from nestipy.dynamic_module import DynamicModule
from nestipy.metadata import ModuleMetadata, Reflect


class ModuleA:
    pass


class ModuleB:
    pass


def test_get_modules_includes_dynamic_modules():
    dynamic = DynamicModule(module=ModuleB)
    Reflect.set_metadata(ModuleA, ModuleMetadata.Imports, [dynamic])

    modules = NestipyCommander._get_modules(ModuleA)

    assert ModuleA in modules
    assert ModuleB in modules
