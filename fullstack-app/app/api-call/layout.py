from nestipy.web import component, h, Slot


@component
def Layout():
    return h.section(
        h.div(
            h.p("API Workspace", class_name="text-xs uppercase tracking-[0.3em] text-slate-500"),
            h.h3("Typed Client Playground", class_name="text-xl font-semibold text-slate-100"),
            h.p(
                "This section has its own nested layout.",
                class_name="text-sm text-slate-400",
            ),
            class_name="space-y-2",
        ),
        h.div(h(Slot), class_name="mt-6"),
        class_name="rounded-3xl border border-slate-800 bg-slate-900/40 p-6",
    )