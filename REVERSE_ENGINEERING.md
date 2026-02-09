Below is a reverse-engineered view of the framework’s app lifecycle, metadata flow, DI/container mechanics, and request lifecycle based on the current codebase.

**App Lifecycle Graph (Full, Ordered Details, Vertical)**  
```mermaid
flowchart TB
    %% Keep labels short and stacked to force vertical layout
    subgraph DECORATORS["Decorator time"]
        direction TB
        D1["@Injectable<br/>register provider"]
        D2["@Controller<br/>register controller + route meta"]
        D3["@Module<br/>register module meta + class"]
        D4["@Route/@Get/@Post<br/>method meta"]
        D5["SetMetadata<br/>custom meta"]
    end

    D1 --> C0["Container<br/>services + singleton classes"]
    D2 --> C0
    D3 --> M0["Reflect meta<br/>on module"]
    D4 --> M1["Reflect meta<br/>on handlers"]
    D5 --> M2["Reflect meta<br/>on classes/methods"]

    A["NestipyFactory.create(AppModule)"] --> A1["setup log levels"]
    A1 --> A2{"generic type is<br/>BlackSheepApplication?"}
    A2 -->|yes| A3["load adapter<br/>BlackSheep -> FastAPI"]
    A2 -->|no| A4["use config.adapter<br/>or FastAPI"]
    A3 --> B
    A4 --> B

    B["NestipyApplication.__init__"] --> B1["HttpAdapter set"]
    B --> B2["GraphqlAdapter set"]
    B --> B3["RouterProxy created"]
    B --> B4["MiddlewareContainer get"]
    B --> B5["InstanceLoader created"]
    B --> B6["BackgroundTasks created"]
    B --> B7["process_config<br/>cors + debug"]
    B --> B8["register startup/shutdown<br/>callbacks on adapter"]

    B --> C["init(root_module)"]
    C --> C1["set root module"]
    C --> C2["add core providers<br/>ModuleProviderDict"]
    C2 --> C3["ModuleProviderDict<br/>add singleton by token"]
    C2 --> C4["update ModuleMetadata.Providers"]
    C4 --> C5["_set_metadata()"]
    C5 --> C6["ProviderMetadataCreator<br/>ClassMetadata"]
    C5 --> C7["ControllerMetadataCreator<br/>ClassMetadata"]
    C5 --> C8["ModuleMetadataCreator<br/>ClassMetadata + globals"]
    C8 --> C9["DynamicModule expand<br/>container add singleton"]

    F["ASGI app __call__"] --> G{"lifespan scope?"}
    G -->|yes| H["ready -> setup"]
    G -->|no| RQ["adapter handles request"]

    H --> H0{"already ready?"}
    H0 -->|yes| HEND["return"]
    H0 -->|no| H1["get modules<br/>imports + dynamic + root"]
    H1 --> H2["InstanceLoader.create_instances"]

    subgraph INST["InstanceLoader.create_instances"]
        direction TB
        I1["skip if already instantiated"]
        I2["create providers<br/>ModuleMetadata.Providers"]
        I3["create controllers<br/>ModuleMetadata.Controllers"]
        I4["create module instance"]
        I5["NestipyModule.configure<br/>+ module.on_startup"]
        I6["OnInit.on_startup"]
        I7["DiscoverService track all"]
        I8["GraphqlModule instance saved"]
        I9["recurse ModuleMetadata.Imports"]
        I10["create Interceptor/Guard/<br/>Middleware/ExceptionFilter<br/>disable_scope"]
    end

    H2 --> I1 --> I2 --> I3 --> I4 --> I5 --> I6 --> I7 --> I8 --> I9 --> I10

    subgraph DI["NestipyContainer.get resolution"]
        direction TB
        DAI1["check singleton or ModuleProviderDict"]
        DAI2["resolve properties<br/>__annotations__"]
        DAI3["context deps<br/>RequestContextContainer"]
        DAI4["scope check<br/>ClassMetadata providers"]
        DAI5["resolve __init__ or handler args"]
        DAI6["cache singleton if needed"]
    end

    I2 --> DAI1 --> DAI2 --> DAI3 --> DAI4 --> DAI5 --> DAI6

    H --> H9["RouterProxy.apply_routes"]
    H9 --> H10["RouteExplorer reads meta"]
    H9 --> H11["register routes on adapter"]
    H9 --> H12["build OpenAPI paths/schemas"]

    H --> H13{"GraphQL module exists?"}
    H13 -->|yes| H14["GraphqlProxy.apply_resolvers"]
    H --> H15{"IO adapter set?"}
    H15 -->|yes| H16["IoSocketProxy.apply_routes"]
    H --> H17{"OpenAPI handler registered?"}
    H17 -->|yes| H18["call openapi handler"]

    H --> H19["HttpAdapter.start"]
    H19 --> H20["set _ready true"]
    H19 --> H21["startup: BackgroundTasks.run"]

    H --> H22["finally: register devtools static"]
    H22 --> H23["register not-found route"]

    P["Shutdown signal"] --> Q["adapter on_shutdown callback"]
    Q --> R["NestipyApplication._destroy"]
    R --> S["BackgroundTasks.shutdown"]
    R --> T["InstanceLoader.destroy<br/>OnDestroy + module.on_shutdown"]
```

**App Lifecycle Order (Step-by-Step)**  
1. Import modules; decorators register providers/controllers/modules in `NestipyContainer` and write metadata to `Reflect`.
2. Call `NestipyFactory.create(AppModule)` -> setup log levels.
3. Choose adapter: if `__generic_type__ == BlackSheepApplication`, attempt BlackSheep then FastAPI; else use `config.adapter` or FastAPI.
4. `NestipyApplication.__init__` builds adapters, router proxy, middleware container, instance loader, background tasks, and config flags.
5. `NestipyApplication.init(AppModule)` adds core providers via `ModuleProviderDict` and compiles metadata with `_set_metadata`.
6. ASGI server calls app; on lifespan, `ready()` triggers `setup()` unless already ready.
7. `setup()` gathers modules via `_get_modules` (imports + dynamic modules + root).
8. `InstanceLoader.create_instances` recursively creates providers/controllers/modules via `NestipyContainer.get`.
9. Each `NestipyContainer.get` resolves singleton cache, then property injection, then constructor/method args.
10. Contextual params (Req/Res/Query/Param/etc) are resolved via `RequestContextContainer` callbacks.
11. `NestipyModule.configure` runs and can register middleware via `MiddlewareConsumer`; `OnInit` hooks run.
12. DiscoverService tracks providers/controllers/modules; GraphQL module instance is captured if present.
13. After recursion, interceptors/guards/middleware/exception filters are instantiated with `disable_scope=True`.
14. Build routes via `RouterProxy.apply_routes` -> `RouteExplorer` -> adapter route registration and OpenAPI docs.
15. Apply GraphQL resolvers and WebSocket routes if enabled.
16. Call OpenAPI registration hook if present.
17. Start HTTP adapter, mark app ready, run background tasks.
18. Always register devtools static assets and a not‑found handler route.
19. On shutdown, stop background tasks and invoke `OnDestroy` and `module.on_shutdown`.

**Entry Point**
- `NestipyFactory.create(AppModule)` constructs `NestipyApplication` and calls `init` to register root providers and build metadata.
  File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/nestipy_factory.py`
- The returned `NestipyApplication` is ASGI-callable; on lifespan it calls `ready()` and `setup()`.
  File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/nestipy_application.py`

**How Metadata Is Built and Read**
- Decorators write metadata using `Reflect.set_metadata`:
  - `@Module` writes `imports/providers/controllers/exports/global` and marks `_is_module_`.
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/common/decorator/class_.py`
  - `@Controller` writes controller path.
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/common/decorator/class_.py`
  - `@Route` / `@Get` / etc. write method path/method.
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/common/decorator/method.py`
- `NestipyApplication._set_metadata()` triggers metadata creators to attach `ClassMetadata` on providers/controllers/modules for DI scoping:
  - `ProviderMetadataCreator` and `ControllerMetadataCreator` add `ClassMetadata` to each provider/controller.
  - `ModuleMetadataCreator` ensures modules get `ClassMetadata` for module-scoped lookups and merges global providers.
    Files:
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/meta/metadata_creator.py`
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/meta/provider_metadata_creator.py`
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/meta/controller_metadata_creator.py`
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/meta/module_metadata_creator.py`
- Metadata storage/retrieval lives in `Reflect` (simple dict on `__reflect__metadata__`).
  File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/metadata/reflect.py`

**How Instances Are Created, Stored, and Resolved**
- `InstanceLoader.create_instances(modules)` iterates modules, creates providers and controllers via `NestipyContainer.get()`, and calls module hooks.
  File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/instance_loader.py`
- Registration:
  - `@Injectable` registers providers into the container (singleton by default, transient for request/transient).
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/common/decorator/class_.py`
  - `@Controller` registers controllers as singleton services.
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/common/decorator/class_.py`
  - `ModuleProviderDict` registers custom providers and stores itself in singleton instances keyed by token.
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/provider.py`
- Resolution algorithm (`NestipyContainer.get`):
  1. If singleton instance exists, return it.
  2. `_resolve_property` reads `__annotations__` on the class and resolves each annotation.
  3. `_resolve_method` resolves `__init__` args or a controller method’s args.
  File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/container.py`
- Property injection rules:
  - Uses typing annotations. If type is `Annotated[T, Inject()]` or other `TypeAnnotated`, it can resolve context values (Request, Response, Query, etc.).
    Files:
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/dependency.py`
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/helper.py`
  - Contextual values are pulled from `RequestContextContainer.execution_context` (set per request).
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/context_container.py`
- Scope:
  - Request scope currently maps to transient (`add_transient`) and is not a distinct cache.
    File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/common/decorator/class_.py`
  - Updated: Request scope now uses `contextvars` with a per-request cache in `RequestContextContainer`.
    Files:
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/context_container.py`
    `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/container.py`

**Startup/Shutdown Hooks**
- `OnInit.on_startup` and `OnDestroy.on_shutdown` are called for providers/controllers as appropriate.
  Files:
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/on_init.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/on_destroy.py`
- `NestipyModule.configure(consumer)` runs during instance creation and can register middleware via `MiddlewareConsumer`.
  Files:
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/dynamic_module/module/interface.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/dynamic_module/module/consumer.py`

**Request Lifecycle Graph**
```mermaid
flowchart TD
    A["HttpAdapter receives request"] --> B["RouterProxy.create_request_handler"]
    B --> C["ExecutionContext created"]
    C --> D["RequestContextContainer.set_execution_context"]
    D --> E["MiddlewareExecutor.execute()"]
    E --> F["GuardProcessor.process()"]
    F -->|unauthorized| X["HttpException -> ExceptionFilterHandler"]
    F --> G["RequestInterceptor.intercept()"]
    G --> H["Container.get(controller, method_name)"]
    H --> I["Resolve method params via DI + context annotations"]
    I --> J["Controller method executes"]
    J --> K["TemplateRendererProcessor (optional)"]
    K --> L["Ensure response (json/text/Response)"]
    L --> M["Response sent"]

    X --> N["ExceptionFilterHandler.catch()"]
    N --> M

    M --> Z["RequestContextContainer.destroy()"]
```

**Request Lifecycle Details**
- Execution context is created per request and stored in a singleton `RequestContextContainer`, allowing `@Req`, `@Res`, `@Query`, etc. to resolve.
  Files:
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/router/router_proxy.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/context/execution_context.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/ioc/context_container.py`
- Order of processing: middleware -> guards -> pipes -> interceptors -> handler -> template rendering -> response -> exception filters.
  Files:
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/middleware/executor.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/guards/processor.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/pipes/processor.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/interceptor/processor.py`
  `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/exception/processor.py`

**“When stop”**
- App shutdown calls `NestipyApplication._destroy()` via the adapter shutdown hook; it stops background tasks and calls `InstanceLoader.destroy()` to invoke `OnDestroy` on providers/controllers and `on_shutdown` on modules.
  File: `/Users/tsiresymila/Development/Python/nestipy/src/nestipy/core/nestipy_application.py`
