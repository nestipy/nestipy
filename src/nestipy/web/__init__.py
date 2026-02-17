"""Nestipy Web - Python-to-React frontend tooling (Vite target)."""

from .config import WebConfig
from .compiler import compile_app, build_routes, CompilerError
from .ui import (
    Context,
    StoreHook,
    StoreSelector,
    component,
    h,
    external,
    external_fn,
    js_import,
    js,
    new_,
    props,
    Fragment,
    Slot,
    use_state,
    use_effect,
    use_effect_async,
    use_memo,
    use_callback,
    use_context,
    use_ref,
    create_context,
)
from .actions import (
    ActionsModule,
    ActionsOption,
    action,
    UseActionGuards,
    ActionPermissions,
    ActionAuth,
    ActionGuard,
    ActionContext,
    OriginActionGuard,
    CsrfActionGuard,
    ActionSignatureGuard,
    ActionPermissionGuard,
    ActionNonceCache,
)
from .actions_client import (
    build_action_specs,
    build_actions_schema,
    generate_actions_client_code,
    generate_actions_client_code_from_schema,
    codegen_actions_from_url,
    write_actions_client_file,
    generate_actions_types_code,
    generate_actions_types_code_from_schema,
    codegen_actions_types_from_url,
    write_actions_types_file,
)
from .client_types import (
    generate_client_types_code,
    codegen_client_types_from_url,
    write_client_types_file,
)
from .ssr import (
    SSRRenderer,
    SSRRenderError,
    create_ssr_renderer,
    env_ssr_enabled,
    env_ssr_runtime,
    resolve_ssr_entry,
)

__all__ = [
    "WebConfig",
    "compile_app",
    "build_routes",
    "CompilerError",
    "component",
    "h",
    "external",
    "external_fn",
    "js_import",
    "js",
    "new_",
    "props",
    "Fragment",
    "Slot",
    "Context",
    "StoreHook",
    "StoreSelector",
    "use_state",
    "use_effect",
    "use_effect_async",
    "use_memo",
    "use_callback",
    "use_context",
    "use_ref",
    "create_context",
    "ActionsModule",
    "ActionsOption",
    "action",
    "UseActionGuards",
    "ActionPermissions",
    "ActionAuth",
    "ActionGuard",
    "ActionContext",
    "OriginActionGuard",
    "CsrfActionGuard",
    "ActionSignatureGuard",
    "ActionPermissionGuard",
    "ActionNonceCache",
    "build_action_specs",
    "build_actions_schema",
    "generate_actions_client_code",
    "generate_actions_client_code_from_schema",
    "generate_actions_types_code",
    "generate_actions_types_code_from_schema",
    "codegen_actions_from_url",
    "codegen_actions_types_from_url",
    "write_actions_client_file",
    "write_actions_types_file",
    "generate_client_types_code",
    "codegen_client_types_from_url",
    "write_client_types_file",
    "SSRRenderer",
    "SSRRenderError",
    "create_ssr_renderer",
    "env_ssr_enabled",
    "env_ssr_runtime",
    "resolve_ssr_entry",
]


def codegen_client(*args, **kwargs):
    """Proxy to the router client generator."""
    from .client import codegen_client as _codegen_client

    return _codegen_client(*args, **kwargs)


def codegen_client_from_url(*args, **kwargs):
    """Proxy to the router client generator using a spec URL."""
    from .client import codegen_client_from_url as _codegen_client_from_url

    return _codegen_client_from_url(*args, **kwargs)


__all__.extend(["codegen_client", "codegen_client_from_url"])
