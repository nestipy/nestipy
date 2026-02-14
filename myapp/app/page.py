from __future__ import annotations

__ssr__ = True

from typing import TYPE_CHECKING

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
)
from app.state import ThemeContext, use_app_store

if TYPE_CHECKING:
    from app.state import ThemeContextValue

Link = external("react-router-dom", "Link")
create_actions = external_fn("../actions.client", "createActions", alias="createActions")
create_api_client = external_fn("../api/client", "createApiClient", alias="createApiClient")


@component
def Page():
    theme: "ThemeContextValue" = use_context(ThemeContext)
    shared_count = use_app_store(lambda state: state.sharedCount)
    inc_shared = use_app_store(lambda state: state.incShared)
    message, set_message = use_state("Loading...")
    ping, set_ping = use_state("Loading...")

    actions = create_actions()
    api = create_api_client()

    def on_action(result):
        set_message(result.ok and result.data or "Error")

    def on_ping(value):
        set_ping(value)

    def load_action():
        actions.AppActions.hello({"name": "Nestipy"}).then(on_action)

    def load_ping():
        api.App.ping().then(on_ping)

    reload_action = use_callback(load_action, deps=[])
    reload_ping = use_callback(load_ping, deps=[])

    action_label = use_memo(lambda: f"Action says: {message}", deps=[message])
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
            "title": "Python-first components",
            "desc": "Compose UI in Python and compile to TSX for Vite.",
        },
        {
            "title": "Typed actions + API",
            "desc": "Generate clients for providers and HTTP routes automatically.",
        },
        {
            "title": "Instant feedback loop",
            "desc": "Hot reload + schema regen keeps the stack synchronized.",
        },
    ]:
        features.append(
            h.div(
                h.h3(item["title"], class_name="feature-title"),
                h.p(item["desc"], class_name="feature-desc"),
                class_name="card feature-card",
                key=item["title"],
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
                key=item["label"],
            )
        )

    return h.section(
        h.div(
            h.div(
                h.span("Fullstack starter", class_name="pill"),
                h.span("Nestipy + React + Vite", class_name="pill pill-accent"),
                class_name="pill-row",
            ),
            h.h1("Build modern web experiences in Python.", class_name="hero-title"),
            h.p(
                "Nestipy Web turns Python UI into React, ships typed actions and API clients, and keeps everything hot in Vite.",
                class_name="hero-subtitle",
            ),
            h.div(
                Link("View Counter", to="/counter", class_name="btn btn-primary"),
                Link("API Playground", to="/api-call", class_name="btn btn-outline"),
                class_name="hero-actions",
            ),
            class_name="hero-card",
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
        h.div(stats, class_name="stat-grid"),
        h.div(features, class_name="feature-grid"),
        class_name="home",
    )