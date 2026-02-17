from __future__ import annotations



from typing import TYPE_CHECKING

from nestipy.web import (
    component,
    h,
    use_state,
    use_callback,
)
from app.store import use_app_store


@component
def Page():
    count, set_count = use_state(0)
    shared_count = use_app_store(lambda state: state.sharedCount)
    inc_shared = use_app_store(lambda state: state.incShared)
    dec_shared = use_app_store(lambda state: state.decShared)

    def increment():
        set_count(count + 1)

    def decrement():
        set_count(count - 1)

    inc = use_callback(increment, deps=[count])
    dec = use_callback(decrement, deps=[count])

    def label():
        return f"Count: {count}"


    return h.section(
        h.div(
            h.span("Interactive demo", class_name="pill"),
            h.h2("Counter lab", class_name="page-title"),
            h.p(
                "Stateful hooks, memoized labels, and shared store updates in one place.",
                class_name="page-subtitle",
            ),
            class_name="page-header",
        ),
        h.div(
            h.div(
                h.span("Local count", class_name="simple-label"),
                h.span(count, class_name="counter-display"),             
                h.div(
                    h.button("-1", on_click=dec, class_name="btn btn-outline"),
                    h.button("+1", on_click=inc, class_name="btn btn-primary"),
                    class_name="home-actions",
                ),
                class_name="simple-panel",
            ),
            h.div(
                h.span("Shared count", class_name="simple-label"),
                h.span(shared_count, class_name="counter-display"),
                h.div(
                    h.button("-1", on_click=dec_shared, class_name="btn"),
                    h.button("+1", on_click=inc_shared, class_name="btn btn-outline"),
                    class_name="home-actions",
                ),
                class_name="simple-panel",
            ),
            class_name="simple-grid",
        ),
        class_name="page page-centered",
    )