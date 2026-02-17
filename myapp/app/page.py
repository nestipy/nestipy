from __future__ import annotations



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
        api.AppController.ping().then(on_ping)

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

    if theme["theme"] == "dark":
        toggle_label = "Switch to light"
    else:
        toggle_label = "Switch to dark"

    toggle_handler = theme["toggle"]
    if toggle_handler:
        toggle_button = h.button(
            toggle_label,
            on_click=toggle_handler,
            class_name="ghost-btn",
        )
    else:
        toggle_button = h.span(theme_name, class_name="theme-chip")

    link_cards = []
    for item in [
        {
            "title": "Docs",
            "desc": "Find in-depth guides for the Nestipy stack.",
            "href": "https://nestipy.vercel.app",
            "external": True,
        },
        {
            "title": "Counter",
            "desc": "Explore hooks and shared state updates.",
            "href": "/counter",
        },
        {
            "title": "API Playground",
            "desc": "Call typed HTTP clients from Python UI.",
            "href": "/api-call",
        },
        {
            "title": "Actions",
            "desc": "Trigger typed RPC actions instantly.",
            "href": "/action-call",
        },
    ]:
        card = h.div(
            h.h3(f"{item['title']} →", class_name="link-title"),
            h.p(item["desc"], class_name="link-desc"),
            class_name="link-card",
        )
        if "external" in item and item["external"]:
            link_cards.append(
                h.a(
                    card,
                    href=item["href"],
                    target="_blank",
                    rel="noreferrer",
                    class_name="link-card-wrap",
                    key=item["title"],
                )
            )
        else:
            link_cards.append(
                Link(
                    card,
                    to=item["href"],
                    class_name="link-card-wrap",
                    key=item["title"],
                )
            )

    return h.section(
        h.div(
            h.span("Get started by editing app/page.py", class_name="start-pill"),
            h.div(
                h.button(toggle_button, class_name="btn-ghost"),
                class_name="center-right flex flex-col gap-2",
            ),
            class_name="flex flex-row gap-8 ",
        ),
        h.div(
            h.div(
                h.img(src="/nestipy.png", alt="Nestipy", class_name="hero-logo", width="100", height="100"),
                h.h1("Nestipy", class_name="hero-logo"),
                h.p(
                    "Full-stack Python framework with typed actions and React UI.",
                    class_name="hero-sub",
                ),
                class_name="hero-center",
            ),
            class_name="hero-wrap",
        ),
        h.div(
            h.div(
                h.span("Action", class_name="status-label"),
                h.span(action_label, class_name="status-value"),
                class_name="status-item",
            ),
            h.div(
                h.span("API", class_name="status-label"),
                h.span(ping_status, class_name="status-value"),
                class_name="status-item",
            ),
            class_name="status-row",
        ),
        h.div(
            h.button("Reload Action", on_click=reload_action, class_name="btn-ghost"),
            h.button("Reload API", on_click=reload_ping, class_name="btn-ghost"),
            h.button("Inc Shared", on_click=inc_shared, class_name="btn-ghost"),
            class_name="status-actions",
        ),
        h.div(link_cards, class_name="link-grid"),
        class_name="home-next",
    )