from nestipy.web import (
    component,
    h,
    use_state,
    use_effect,
    use_context,
    external,
    external_fn,
    new_,
)
from app.layout import ThemeContext

ApiClient = external("../../api/client", "ApiClient")
use_app_store = external_fn("../../store", "useAppStore", alias="useAppStore")


@component
def Page():
    theme = use_context(ThemeContext)
    status, set_status = use_state("Waiting...")
    shared_count = use_app_store(lambda state: state.sharedCount)
    inc_shared = use_app_store(lambda state: state.incShared)

    api = new_(ApiClient, {"baseUrl": ""})

    def load_ping():
        api.ping().then(lambda value: set_status(f"API ping: {value}"))

    use_effect(load_ping, deps=[])

    return h.section(
        h.div(
            h.h2("API Playground", class_name="page-title"),
            h.p(
                "Ping the backend using the generated typed client.",
                class_name="page-subtitle",
            ),
            class_name="page-header",
        ),
        h.div(
            h.p(status, class_name="card-title"),
            h.button("Reload API", on_click=load_ping, class_name="btn"),
            class_name="card api-card",
        ),
        h.div(
            h.span("Shared count", class_name="stat-label"),
            h.span(shared_count, class_name="stat-value"),
            h.button("Inc Shared", on_click=inc_shared, class_name="btn btn-outline"),
            class_name="stat-card",
        ),
        h.p(
            f"Theme: {theme['theme']}",
            class_name="card-subtitle",
        ),
        class_name="page",
    )