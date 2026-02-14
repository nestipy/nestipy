from nestipy.web import component, h, Slot, external
from app.state import ThemeContext, use_app_store

Link = external("react-router-dom", "Link")


@component
def Layout():
    theme = use_app_store(lambda state: state.theme)
    toggle_handler = use_app_store(lambda state: state.toggleTheme)
    shared_count = use_app_store(lambda state: state.sharedCount)

    nav_links = []
    for item in [
        {"label": "Home", "to": "/"},
        {"label": "Counter", "to": "/counter"},
        {"label": "API", "to": "/api-call"},
    ]:
        nav_links.append(
            Link(
                item["label"],
                to=item["to"],
                key=item["to"],
                class_name="nav-link",
            )
        )

    if theme == "dark":
        shell_class = "app-shell theme-dark"
        toggle_label = "Switch to light"
        theme_label = "Dark"
    else:
        shell_class = "app-shell theme-light"
        toggle_label = "Switch to dark"
        theme_label = "Light"

    return h(
        ThemeContext.Provider,
        h.div(
            h.header(
                h.div(
                    h.div(
                        h.span("Nestipy", class_name="brand-name"),
                        h.span("Fullstack", class_name="brand-pill"),
                        class_name="brand",
                    ),
                    h.p("Python UI + typed APIs", class_name="brand-subtitle"),
                    class_name="brand-block",
                ),
                h.nav(nav_links, class_name="nav"),
                h.div(
                    h.button(
                        toggle_label,
                        on_click=toggle_handler,
                        class_name="btn btn-ghost",
                    ),
                    h.span(
                        f"Shared {shared_count}",
                        class_name="shared-pill",
                    ),
                    h.span(
                        theme_label,
                        class_name="theme-label",
                    ),
                    class_name="header-actions",
                ),
                class_name="topbar",
            ),
            h.main(h(Slot), class_name="container"),
            h.footer(
                h.span("Nestipy"),
                h.span("•"),
                h.span("Web scaffold"),
                class_name="footer",
            ),
            class_name=shell_class,
        ),
        value={"theme": theme, "toggle": toggle_handler},
    )