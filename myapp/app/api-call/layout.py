from nestipy.web import component, h, Slot


@component
def Layout():
    return h.section(
        h.div(
            h.span("Workspace", class_name="pill"),
            h.h3("Typed Client Playground", class_name="panel-title"),
            h.p(
                "This nested layout scopes tooling for /api-call routes.",
                class_name="panel-subtitle",
            ),
            class_name="panel-header",
        ),
        h.div(h(Slot), class_name="panel-body"),
        class_name="panel panel-plain",
    )