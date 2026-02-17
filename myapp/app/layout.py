from nestipy.web import component, h, Slot
from app.store import ThemeContext, use_app_store


@component
def Layout():
    theme = use_app_store(lambda state: state.theme)
    toggle_handler = use_app_store(lambda state: state.toggleTheme)

    if theme == "dark":
        shell_class = "app-shell theme-dark"
    else:
        shell_class = "app-shell theme-light"

    return h(
        ThemeContext.Provider,
        h.div(
            h.main(h(Slot), class_name="page-shell"),
            class_name=shell_class,
        ),
        value={"theme": theme, "toggle": toggle_handler},
    )