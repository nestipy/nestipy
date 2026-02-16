from nestipy.web import component, h, external

Link = external("react-router-dom", "Link")


@component
def NotFound():
    return h.section(
        h.div(
            h.div(
                h.span("404", class_name="error-minimal-code"),
                h.div(class_name="error-minimal-divider"),
                h.div(
                    h.h1(
                        "This page could not be found.",
                        class_name="error-minimal-title",
                    ),
                    h.p(
                        "The route you requested doesn’t exist yet. Check your navigation or update routes.",
                        class_name="error-minimal-message",
                    ),
                    class_name="error-minimal-text",
                ),
                class_name="error-minimal-row",
            ),
            h.div(
                Link("Back to home", to="/", class_name="error-minimal-link"),
                class_name="error-minimal-actions",
            ),
            class_name="error-minimal-content",
        ),
        class_name="error-minimal",
    )