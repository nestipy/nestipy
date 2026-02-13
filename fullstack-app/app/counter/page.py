from nestipy.web import (
    component,
    h,
    use_state,
    use_memo,
    use_callback,
    use_context,
    external,
)
from app.layout import ThemeContext

Link = external("react-router-dom", "Link")


@component
def Page():
    theme = use_context(ThemeContext)
    count, set_count = use_state(0)

    def increment():
        set_count(count + 1)

    def decrement():
        set_count(count - 1)

    inc = use_callback(increment, deps=[count])
    dec = use_callback(decrement, deps=[count])

    def label():
        return f"Count: {count}"

    title = use_memo(label, deps=[count])

    links = []
    for item in [
        {"label": "Home", "to": "/"},
        {"label": "Counter", "to": "/counter"},
        {"label": "API", "to": "/api-call"},
    ]:
        links.append(
            Link(
                item["label"],
                to=item["to"],
                key=item["to"],
                class_name="nav-link",
            )
        )

    if count % 2 == 0:
        parity = h.span("Even", class_name="text-xs text-emerald-400")
    else:
        parity = h.span("Odd", class_name="text-xs text-amber-400")

    return h.section(
        h.nav(links, class_name="home-nav"),
        h.div(
            h.h2("Counter", class_name="text-2xl font-semibold text-slate-100"),
            h.p(
                "Use hooks to keep state and memoize values.",
                class_name="text-sm text-slate-400",
            ),
            class_name="space-y-2 text-center",
        ),
        h.div(
            h.p(title, class_name="text-base text-slate-200"),
            parity,
            h.div(
                h.button(
                    "+1",
                    on_click=inc,
                    class_name="btn btn-primary",
                ),
                h.button(
                    "-1",
                    on_click=dec,
                    class_name="btn",
                ),
                class_name="home-actions",
            ),
            class_name="home-card",
        ),
        h.p(
            f"Theme: {theme['theme']}",
            class_name="text-xs text-slate-500",
        ),
        class_name="page",
    )