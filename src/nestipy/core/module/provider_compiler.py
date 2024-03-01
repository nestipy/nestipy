import inspect

from nestipy.common.decorator.injectable import Injectable
from nestipy.core.module.provider import ModuleProvider


class ProviderCompiler:
    def __init__(self, compiler):
        self.compiler = compiler

    async def compile(self, module, init=False):
        self.compiler.remove_module_none_imported(module)
        # Resolve instance of all module provider
        await self.resolve_providers_of_module(module)
        imports = getattr(module, 'imports')
        global_module = []
        global_providers = []
        if init:
            ins_m = module()
            self.compiler.module_resolved[module.__name__] = ins_m
            self.compiler.hook_compiler.extract_hooks_in_module(ins_m)
            global_providers = self.extract_provider(module)
            old_global_module = [m for m in imports if
                                 hasattr(m, "is_global__") and m.is_global__]
            for index, gb_module in enumerate(old_global_module):
                # set global providers for  all
                setattr(gb_module, 'providers', global_providers + getattr(gb_module, 'providers'))
                self.compiler.modify_module_imports(gb_module, old_global_module[0:index + 1])
                await self.compile(gb_module)
                global_module.append(gb_module)

        imported_modules = [m for m in imports if
                            m not in global_module and m.__name__ not in self.compiler.module_resolved.keys()]
        for module_import in imported_modules:
            # set global providers for  all
            setattr(module_import, 'providers', global_providers + getattr(module_import, 'providers'))
            self.compiler.modify_module_imports(module_import, global_module)
            await self.compile(module_import)
            instance = module_import()
            self.compiler.module_resolved[module_import.__name__] = instance
            self.compiler.hook_compiler.extract_hooks_in_module(instance)

    async def resolve_providers_of_module(self, module):
        await self.recreate_async_provider(module)
        await self.recreate_module_provider(module)
        providers = self.extract_provider(module)
        for p in providers:
            is_middleware = hasattr(p, 'middleware__')
            if inspect.isclass(p):
                # put instance of provider inside container
                instance = self.compiler.container.resolve(p, module)
                self.compiler.put_module_provider_instance(module, p, instance, is_middleware=is_middleware)
            else:
                # put value identified by token  inside container
                token = p.token__
                instance = self.compiler.container.resolve_method(p, token=token)
                self.compiler.put_module_provider_instance(module, token, instance, is_middleware=is_middleware)

        await self.compiler.resolve_controllers_of_module(module)
        self.compiler.middleware_compiler.extract_middleware_of_module(module)

    async def recreate_async_provider(self, module):
        if hasattr(module, 'module_provider__'):
            provider: ModuleProvider = getattr(module, 'module_provider__')
            if provider.provide:
                if provider.use_value is not None:
                    setattr(module, "providers",
                            [Injectable(provider.provide)(lambda: provider.use_value)] + module.providers)
                    return
                if provider.use_factory:
                    inject = self.filter_async_provider_inject(module.imports, provider.inject)
                    value = await self.resolve_use_factory(use_factory=provider.use_factory, inject=inject)
                    setattr(module, "providers", [Injectable(provider.provide)(lambda: value)] + module.providers)
                    return

    async def recreate_module_provider(self, module):
        providers = getattr(module, 'providers')
        instance_of_module_provider = [p for p in providers if isinstance(p, ModuleProvider)]
        module_provider_injectable = self.extract_provider(module)
        for p in instance_of_module_provider:
            if p.provide is None:
                pass
            if p.use_value is not None:
                module_provider_injectable = [Injectable(p.provide)(lambda: p.use_value)] + module_provider_injectable
                continue
            if p.use_factory is not None:
                value = await self.resolve_use_factory(use_factory=p.use_factory, inject=module_provider_injectable)
                module_provider_injectable = [Injectable(p.provide)(lambda: value)] + module_provider_injectable
                continue
        setattr(module, 'providers', module_provider_injectable)

    @classmethod
    def extract_provider(cls, module):
        return [p for p in module.providers if hasattr(p, 'injectable__')]

    @classmethod
    def extract_exported_provider(cls, module):
        return [p for p in module.providers if hasattr(p, 'injectable__')]

    def filter_async_provider_inject(self, modules: list, inject: list):
        providers = []
        for module in modules:
            providers = providers + self.extract_exported_provider(module)
        return [p for p in inject if p in providers]

    async def resolve_use_factory(self, use_factory, inject=None):
        if inject is None:
            inject = []
        factory_signature = inspect.signature(use_factory).parameters
        factory_dependencies = {}
        for param_name, param in factory_signature.items():
            if param.annotation in inject:
                dep_value = self.compiler.container.instances.get(param.annotation)
                factory_dependencies[param_name] = dep_value
        if inspect.iscoroutinefunction(use_factory):
            return await use_factory(**factory_dependencies)
        return use_factory(**factory_dependencies)
