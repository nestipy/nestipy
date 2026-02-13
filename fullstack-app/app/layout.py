from nestipy.web import component, h, Slot, use_state, use_callback, create_context, external

Link = external("react-router-dom", "Link")

ThemeContext = create_context({"theme": "light", "toggle": None})


@component
def Layout():
    theme, set_theme = use_state("light")

    def toggle_theme():
        set_theme("dark" if theme == "light" else "light")

    toggle_handler = use_callback(toggle_theme, deps=[theme])

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
        theme_label = "Dark mode"
    else:
        shell_class = "app-shell theme-light"
        toggle_label = "Switch to dark"
        theme_label = "Light mode"

    return h(
        ThemeContext.Provider,
        h.div(
            h.header(
                h.div(
                    h.div(
                        h.span("Nestipy", class_name="brand-name"),
                        h.span("Web", class_name="brand-pill"),
                        class_name="brand",
                    ),
                    h.p(
                        "Python-first UI and typed APIs.",
                        class_name="brand-subtitle",
                    ),
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
                        theme_label,
                        class_name="theme-label",
                    ),
                    class_name="header-actions",
                ),
                class_name="topbar",
            ),
            h.main(h(Slot), class_name="container"),
            h.footer(
                h.span("Nestipy Web"),
                h.span("•"),
                h.span("Fullstack scaffold"),
                class_name="footer",
            ),
            class_name=shell_class,
        ),
        value={"theme": theme, "toggle": toggle_handler},
    )