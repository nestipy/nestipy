from nestipy.web import (
    component,
    h,
    use_state,
    use_effect,
    use_memo,
    use_callback,
    use_context,
    external,
    external_fn,
    new_,
)
from app.layout import ThemeContext

Link = external("react-router-dom", "Link")
create_actions = external("../actions.client", "createActions", alias="createActions")
ApiClient = external("../api/client", "ApiClient")
use_app_store = external_fn("../store", "useAppStore", alias="useAppStore")


@component
def Page():
    theme: dict[str, str] = use_context(ThemeContext)
    shared_count = use_app_store(lambda state: state.sharedCount)
    inc_shared = use_app_store(lambda state: state.incShared)
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

    if ping == "Loading...":
        ping_status = "Connecting to API..."
    else:
        ping_status = f"API ping: {ping}"

    if theme["theme"] == "dark":
        theme_name = "Dark"
    else:
        theme_name = "Light"

    features = []
    for item in [
        {
            "title": "Python-first UI",
            "desc": "Write components in Python. Compile to TSX for Vite.",
        },
        {
            "title": "Typed Actions",
            "desc": "Call backend providers from the browser with type safety.",
        },
        {
            "title": "Instant Feedback",
            "desc": "Dev server + compiler keep your UI hot and fast.",
        },
    ]:
        features.append(
            h.div(
                h.h3(item["title"], class_name="feature-title"),
                h.p(item["desc"], class_name="feature-desc"),
                class_name="card feature-card",
            )
        )
   
    stats = []
    for item in [
        {"label": "Theme", "value": theme_name},
        {"label": "Shared", "value": f"#{shared_count}"},
        {"label": "Action", "value": "Live" if message != "Loading..." else "Booting"},
        {"label": "API", "value": "Ready" if ping != "Loading..." else "Syncing"},
    ]:
        stats.append(
            h.div(
                h.span(item["label"], class_name="stat-label"),
                h.span(item["value"], class_name="stat-value"),
                class_name="stat-card",
            )
        )

    return h.section(
        h.div(
            h.div(
                h.span("Fullstack starter", class_name="pill"),
                h.span("Nestipy + React + Vite", class_name="pill pill-accent"),
                class_name="pill-row",
            ),
            h.h1("Ship Python UI with modern tooling.", class_name="hero-title"),
            h.p(
                "Nestipy Web compiles Python components to React, keeps actions typed, and gives you a single fullstack workflow.",
                class_name="hero-subtitle",
            ),
            h.div(
                Link("Explore Counter", to="/counter", class_name="btn btn-primary"),
                Link("Open API Playground", to="/api-call", class_name="btn btn-outline"),
                class_name="hero-actions",
            ),
            class_name="hero",
        ),
        h.div(
            h.a(
                h.img(src="/nestipy.png", alt="Nestipy logo", class_name="logo nestipy"),
                href="https://nestipy.vercel.app",
                target="_blank",
                rel="noreferrer",
                class_name="logo-link",
            ),
            h.a(
                h.img(src="/react.svg", alt="React logo", class_name="logo react"),
                href="https://react.dev",
                target="_blank",
                rel="noreferrer",
                class_name="logo-link",
            ),
            h.a(
                h.img(src="/vite.svg", alt="Vite logo", class_name="logo vite"),
                href="https://vitejs.dev",
                target="_blank",
                rel="noreferrer",
                class_name="logo-link",
            ),
            class_name="logo-row",
        ),
        h.p("Click the logos to learn more.", class_name="logo-caption"),
        h.div(
            h.div(
                h.p(action_label, class_name="card-title"),
                h.p(ping_status, class_name="card-subtitle"),
                class_name="card-content",
            ),
            h.div(
                h.button("Reload Action", on_click=reload_action, class_name="btn btn-primary"),
                h.button("Reload API", on_click=reload_ping, class_name="btn"),
                h.button("Inc Shared", on_click=inc_shared, class_name="btn btn-outline"),
                class_name="home-actions",
            ),
            class_name="card status-card",
        ),
        h.div(features, class_name="feature-grid gap-4"),
        h.div(stats, class_name="stat-grid gap-4"),
        class_name="home space-y-8",
    )