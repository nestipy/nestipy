from nestipy.web import component, h, Slot

@component
def Layout():
    return h.div(
        h.header("Nestipy Web", class_name="text-xl font-semibold"),
        h(Slot),
        class_name="min-h-screen bg-slate-950 text-white p-8 space-y-6",
    )
