from nestipy.web import component, h

@component
def Page():
    return h.div(
        h.h1("Nestipy Web"),
        h.p("Edit app/page.py to get started"),
        h.a("User", href="/user"),
        class_name="p-8 space-y-2",
    )
