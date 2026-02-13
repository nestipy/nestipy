from nestipy.web import component, h, Slot, use_state, use_callback, create_context

ThemeContext = create_context({"theme": "dark", "toggle": None})


@component
def Layout():
    theme, set_theme = use_state("dark")

    def toggle_theme():
        set_theme("light" if theme == "dark" else "dark")

    toggle_handler = use_callback(toggle_theme, deps=[theme])
    return h(
        ThemeContext.Provider,
        h.div(
            h.header(
                h.div(
                    h.span(
                        "Nestipy Web",
                        class_name="text-xs uppercase tracking-[0.35em] text-slate-400",
                    ),
                    h.span("Python-first UI", class_name="text-xs text-slate-500"),
                    class_name="flex items-center gap-3",
                ),
                h.button(
                    f"Switch to {'light' if theme == 'dark' else 'dark'} mode",
                    on_click=toggle_handler,
                    class_name=(
                        "rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 "
                        "text-xs font-semibold text-slate-200 hover:bg-slate-800"
                    ),
                ),
                class_name=(
                    "flex items-center justify-between gap-4 border-b border-slate-900 "
                    "px-6 py-4"
                ),
            ),
            h.main(h(Slot), class_name="flex-1 px-6"),
            class_name="min-h-screen flex flex-col",
        ),
        value={"theme": theme, "toggle": toggle_handler},
    )