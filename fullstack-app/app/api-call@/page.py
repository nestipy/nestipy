from nestipy.web import (
    component,
    h,
    use_state,
    use_effect,
    use_context,
    external,
    new_,
)
from app.layout import ThemeContext

Link = external("react-router-dom", "Link")
ApiClient = external("../../api/client", "ApiClient")


@component
def Page():
    theme = use_context(ThemeContext)
    status, set_status = use_state("Waiting...")

    api = new_(ApiClient, {"baseUrl": ""})

    def load_ping():
        api.ping().then(lambda value: set_status(f"API ping: {value}"))

    use_effect(load_ping, deps=[])

    links = []
    for item in [
        {"label": "Home", "to": "/"},
        {"label": "Counter", "to": "/counter"},
        {"label": "API", "to": "/api-call"},
    ]:
        links.append(
            Link(
                item["label"],
                key=item["to"],
                to=item["to"],
                class_name="nav-link",
            )
        )

    return h.section(
        h.nav(links, class_name="home-nav"),
        h.div(
            h.h2("API Playground", class_name="text-2xl font-semibold text-slate-100"),
            h.p(
                "Ping the backend using the generated typed client.",
                class_name="text-sm text-slate-400",
            ),
            class_name="space-y-2 text-center",
        ),
        h.div(
            h.p(status, class_name="text-base text-slate-200"),
            h.button(
                "Reload API",
                on_click=load_ping,
                class_name="btn",
            ),
            class_name="home-card",
        ),
        h.p(
            f"Theme: {theme['theme']}",
            class_name="text-xs text-slate-500",
        ),
        class_name="page",
    )