from __future__ import annotations

from typing import TYPE_CHECKING

from nestipy.web import (
    component,
    h,
    use_state,
    use_effect,
    use_context,
    external,
    external_fn,
)
from app.state import ThemeContext, use_app_store

if TYPE_CHECKING:
    from app.state import ThemeContextValue

create_api_client = external_fn("../../api/client", "createApiClient", alias="createApiClient")


@component
def Page():
    theme: "ThemeContextValue" = use_context(ThemeContext)
    status, set_status = use_state("Waiting...")
    shared_count = use_app_store(lambda state: state.sharedCount)
    inc_shared = use_app_store(lambda state: state.incShared)

    api = create_api_client()

    def load_ping():
        api.AppController.ping().then(lambda value: set_status(f"API ping: {value}"))

    use_effect(load_ping, deps=[])

    return h.section(
        h.div(
            h.span("Typed client", class_name="pill pill-accent"),
            h.h2("API playground", class_name="page-title"),
            h.p(
                "Call the backend through the generated client and keep responses typed.",
                class_name="page-subtitle",
            ),
            class_name="page-header",
        ),
        h.div(
            h.p(status, class_name="card-title"),
            h.button("Reload API", on_click=load_ping, class_name="btn btn-primary"),
            class_name="card api-card",
        ),
        h.div(
            h.div(
                h.span("Shared count", class_name="stat-label"),
                h.span(shared_count, class_name="stat-value"),
                class_name="stat-card",
            ),
            h.button("Inc Shared", on_click=inc_shared, class_name="btn btn-outline"),
            class_name="stat-row",
        ),
        h.p(
            f"Theme: {theme['theme']}",
            class_name="card-subtitle",
        ),
        class_name="page",
    )
