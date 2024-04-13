## Nice to know

1. [x] A dynamic module must be decorated with `@Module()` and must extends `DynamicModule`
2. [x] Inside Dynamic module, we can access ioc container by `self.get_container()` and this container , inside property `instances` we can access to any instance of ModuleProvider or Service that we have declared in any Module.
3. [x] `on_startup`, and `on_shutdown` hooks are available in any Module(Dynamic or Not)
4. [x] We can define a provider by using `ModuleProvider` instance instead of create a service in Module.
5. [x] All provider declared in `AppModule` are declared as Global Provider
6. [x] Module is is compiled by its priority order of declaration in imports
