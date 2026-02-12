from nestipy.web import component, h

@component
def Page():
    return h.div(
        h.h1("Nestipy Web user page"),
        h.p("Edit app/user/page.py to get started"),
        class_name="p-8 space-y-2",
    )
