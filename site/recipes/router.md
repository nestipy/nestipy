**Router-Module** is only for HTTP-based applications.

In an HTTP application, such as a REST API, the route path for a handler is constructed by combining the (optional) prefix specified in the controller (using the `@Controller` decorator) with any path defined in the method's decorator (e.g., `@Get('users')`). Additionally, a global prefix can be set to apply to all routes in the application.

In certain scenarios, it may be useful to define a prefix at the module level, which applies to all controllers within that module. For instance, consider a REST application that exposes multiple endpoints related to a specific feature, such as a "Dashboard." Instead of repeating the `/dashboard` prefix in each controller, you can leverage a utility module, like `RouterModule`, as demonstrated below:

```python

from nestipy.common import Module
from nestipy.router import RouterModule, RouteItem


@Module(
    imports=[
        AdminModule,
        DashboardModule,
        MetricsModule,
        RouterModule.register([
            RouteItem(
                path='admin',
                module=AdminModule,
                children=[
                    RouteItem(
                        path='dashboard',
                        module=DashboardModule,
                    ),
                    RouteItem(
                        path='metrics',
                        module=MetricsModule,
                    )
                ]
            )
        ])
    ],
)
class AppModule:
    pass
```
In the example above, every controller registered within the `DashboardModule` will automatically inherit the additional `/admin/dashboard` prefix. This is because the module recursively concatenates paths from parent to child. Similarly, controllers defined inside the `MetricsModule` will include the module-level prefix `/admin/metrics` in their routes.  

