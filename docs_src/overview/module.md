# Modules

A module is a class annotated with a `@Module()` decorator. The `@Module()` decorator provides metadata that **Nestipy** makes use of to organize the application structure.

Every Nestipy application has at least one module, a **root module**. The root module is the starting point Nestipy uses to build the **application graph**—the internal data structure Nestipy uses to resolve module and provider relationships and dependencies.

## Basic Module

The `@Module()` decorator takes a single object whose properties describe the module:

| Property | Description |
| :--- | :--- |
| `providers` | The providers that will be instantiated by the Nestipy injector and that may be shared at least across this module. |
| `controllers` | The set of controllers defined in this module which have to be instantiated. |
| `imports` | The list of imported modules that export the providers which are required in this module. |
| `exports` | The subset of `providers` that are provided by this module and should be available in other modules which import this module. |

```python
from nestipy.common import Module
from .cats_controller import CatsController
from .cats_service import CatsService

@Module(
    controllers=[CatsController],
    providers=[CatsService],
)
class CatsModule:
    pass
```

### Encapsulation
In Nestipy, modules **encapsulate** providers by default. This means that it's impossible to inject providers that are neither directly part of the current module nor exported from the imported modules. Thus, you may consider the exported providers from a module as the module's public interface, or API.

## Feature Modules

A **Feature Module** simply organizes code relevant to a specific feature, keeping code organized and establishing clear boundaries. This helps you manage complexity and develop with SOLID principles as the application and/or team size grows.

For example, a `CatsModule` might contain all logic related to cats, including its own service and controller.

## Shared Modules

In Nestipy, modules are **singletons** by default, and thus you can share the same instance of any provider between multiple modules effortlessly.

Every module is automatically a **Shared Module**. Once created it can be reused by any module. Imagine that we want to share an instance of the `CatsService` between several other modules. In order to do that, we first need to **export** the `CatsService` provider by adding it to the module's `exports` array.

```python
@Module(
    controllers=[CatsController],
    providers=[CatsService],
    exports=[CatsService],
)
class CatsModule:
    pass
```

Now any module that imports the `CatsModule` has access to the `CatsService` and will share the same instance with all other modules which import it as well.

## Global Modules

If you have a set of providers which should be available everywhere (e.g., helpers, database connections, etc.), you can make a module **global** with the `@Global()` decorator.

```python
from nestipy.common import Module, Global

@Global()
@Module(
    providers=[ConfigService],
    exports=[ConfigService],
)
class ConfigModule:
    pass
```

::: warning
Making everything global is not a good design decision. Global modules should be used sparingly to reduce the amount of boilerplate needed to import the same module in many places.
:::

## Dynamic Modules

The Nestipy module system includes a powerful feature called **Dynamic Modules**. This feature enables you to create customizable modules that can register and configure providers dynamically.

Dynamic modules are commonly used for tasks like configuration management, database connections, and third-party integrations where you need to pass options to the module at runtime.

---

**Next Up:** Learn about the request lifecycle and how to intercept traffic in the [Middlewares](/overview/middleware) section.
