from nestipy.web import (
    component,
    h,
    use_state,
    use_effect,
    use_memo,
    use_callback,
    use_context,
    external,
    new_,
)
from app.layout import ThemeContext

Link = external("react-router-dom", "Link")
create_actions = external("../actions.client", "createActions", alias="createActions")
ApiClient = external("../api/client", "ApiClient")


@component
def Page():
    theme = use_context(ThemeContext)
    message, set_message = use_state("Loading...")
    ping, set_ping = use_state("Loading...")

    actions = create_actions()
    api = new_(ApiClient, {"baseUrl": ""})

    def on_action(result):
        set_message(result.ok and result.data or "Error")

    def on_ping(value):
        set_ping(value)

    def load_action():
        actions.AppActions.hello({"name": "Nestipy"}).then(on_action)

    def load_ping():
        api.ping().then(on_ping)

    reload_action = use_callback(load_action, deps=[])
    reload_ping = use_callback(load_ping, deps=[])

    def label():
        return f"Action says: {message}"

    action_label = use_memo(label, deps=[message])
    use_effect(load_action, deps=[])
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
                to=item["to"],
                key=item["to"],
                class_name="nav-link",
            )
        )

    if ping == "Loading...":
        ping_status = "Loading API ping..."
    else:
        ping_status = f"API ping: {ping}"

    return h.section(
        h.div(
            h.img(
                src="/nestipy.png",
                alt="Nestipy logo",
                class_name="logo nestipy",
            ),
            h.img(
                src="/react.svg",
                alt="React logo",
                class_name="logo react",
            ),
            h.img(
                src="/vite.svg",
                alt="Vite logo",
                class_name="logo vite",
            ),
            class_name="logo-row",
        ),
        h.h1("Nestipy Web + React + Vite", class_name="home-title"),
        h.p(
            "Build fullstack apps with Python-first UI, typed actions, and fast HMR.",
            class_name="home-subtitle",
        ),
        h.div(
            h.button(
                "Reload Action",
                on_click=reload_action,
                class_name="btn btn-primary",
            ),
            h.button(
                "Reload API",
                on_click=reload_ping,
                class_name="btn",
            ),
            class_name="home-actions",
        ),
        h.div(
            h.p(action_label, class_name="text-sm"),
            h.p(ping_status, class_name="text-xs text-slate-400"),
            h.p(
                f"Theme: {theme['theme']}",
                class_name="text-xs text-slate-500",
            ),
            class_name="home-card",
        ),
        h.nav(links, class_name="home-nav"),
        class_name="home",
    )