from nestipy.web import component, h


@component
def NotFound():
    return h.section(
        h.h1("Page not found", class_name="text-3xl font-semibold text-slate-100"),
        h.p(
            "This route does not exist yet. We'll add nested notfound handling soon.",
            class_name="text-sm text-slate-400",
        ),
        class_name="home",
    )