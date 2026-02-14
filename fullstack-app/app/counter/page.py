from typing import Any
from typing import Callable
from nestipy.web import (
    component,
    h,
    use_state,
    use_memo,
    use_callback,
    use_context,
    external_fn,
)
from app.layout import ThemeContext

use_app_store: Callable[[Callable[[Any], Any]], Any] = external_fn("../../store", "useAppStore", alias="useAppStore")


@component
def Page():
    theme: dict[str, str] = use_context(ThemeContext)
    count, set_count = use_state(0)
    shared_count: int = use_app_store(lambda state: state.sharedCount)
    inc_shared: Callable[[int], None] = use_app_store(lambda state: state.incShared)
    dec_shared: Callable[[int], None] = use_app_store(lambda state: state.decShared)

    def increment():
        set_count(count + 1)

    def decrement():
        set_count(count - 1)

    inc = use_callback(increment, deps=[count])
    dec = use_callback(decrement, deps=[count])

    def label():
        return f"Count: {count}"

    title = use_memo(label, deps=[count])

    if theme["theme"] == "dark":
        theme_name = "Dark"
    else:
        theme_name = "Light"

    if count % 2 == 0:
        parity = h.span("Even", class_name="pill")
    else:
        parity = h.span("Odd", class_name="pill pill-accent")

    return h.section(
        h.div(
            h.h2("Counter", class_name="page-title"),
            h.p(
                "Stateful hooks, memoized labels, and responsive controls.",
                class_name="page-subtitle",
            ),
            class_name="page-header",
        ),
        h.div(
            h.div(
                h.span("Current value", class_name="stat-label"),
                h.span(count, class_name="counter-display"),
                parity,
                class_name="counter-stack",
            ),
            h.div(
                h.button("-1", on_click=dec, class_name="btn"),
                h.button("+1", on_click=inc, class_name="btn btn-primary"),
                class_name="home-actions",
            ),
            h.p(title, class_name="card-subtitle"),
            class_name="card counter-card",
        ),
        h.div(
            h.div(
                h.span("Shared count", class_name="stat-label"),
                h.span(shared_count, class_name="counter-display"),
                class_name="counter-stack",
            ),
            h.div(
                h.button("-1", on_click=dec_shared, class_name="btn"),
                h.button("+1", on_click=inc_shared, class_name="btn btn-outline"),
                class_name="home-actions",
            ),
            class_name="card counter-card",
        ),
        h.div(
            h.span("Theme"),
            h.span(theme_name, class_name="stat-value"),
            class_name="stat-card",
        ),
        class_name="page",
    )