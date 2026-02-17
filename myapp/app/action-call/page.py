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

create_actions = external_fn("../../actions.client", "createActions", alias="createActions")


@component
def Page():
    theme: "ThemeContextValue" = use_context(ThemeContext)
    status, set_status = use_state("Waiting...")
    shared_count = use_app_store(lambda state: state.sharedCount)
    inc_shared = use_app_store(lambda state: state.incShared)

    actions = create_actions()

    def load_ping():
        actions.AppActions.hello({"name": "Nestipy"}).then(lambda value: set_status(f"Action ping: {value.ok and value.data or value.error}"))

    use_effect(load_ping, deps=[])

    return h.section(
        h.div(
            h.span("Action call", class_name="pill pill-accent"),
            h.h2("Action playground", class_name="page-title"),
            h.p(
                "Call the backend through the generated actions and keep responses typed.",
                class_name="page-subtitle",
            ),
            class_name="page-header",
        ),
        h.div(
            h.span("Latest response", class_name="simple-label"),
            h.p(status, class_name="simple-status"),
            h.button("Reload Action", on_click=load_ping, class_name="btn btn-primary"),
            class_name="simple-panel",
        ),
        h.div(
            h.span("Shared count", class_name="simple-label"), 
            h.span(shared_count, class_name="simple-value"),
            h.button("Inc Shared", on_click=inc_shared, class_name="btn btn-outline"),
            class_name="simple-panel",
        ),
        h.p(
            f"Theme: {theme['theme']}",
            class_name="simple-note",
        ),
        class_name="page page-centered",
    )