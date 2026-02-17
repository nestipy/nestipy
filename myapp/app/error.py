from nestipy.web import component, h, external, external_fn, js

Link = external("react-router-dom", "Link")
use_route_error = external_fn("react-router-dom", "useRouteError", alias="useRouteError")
is_route_error_response = external_fn(
    "react-router-dom", "isRouteErrorResponse", alias="isRouteErrorResponse"
)


@component
def Error():
    error = use_route_error()
    status = js("isRouteErrorResponse(error) ? error.status : 500")
    title = js("isRouteErrorResponse(error) ? error.statusText : 'Unexpected error'")
    message = js(
        "error?.message ?? 'Something went wrong while rendering this page.'"
    )
    details = js("error?.stack ?? ''")

    return h.section(
        h.div(
            h.div(
                h.span(status, class_name="error-minimal-code"),
                h.div(class_name="error-minimal-divider"),
                h.div(
                    h.h1(title, class_name="error-minimal-title"),
                    h.p(message, class_name="error-minimal-message"),
                    class_name="error-minimal-text",
                ),
                class_name="error-minimal-row",
            ),
            h.div(
                h.h2("Details", class_name="error-details-title"),
                h.pre(details, class_name="error-details-body"),
                class_name="error-details",
            ),
            h.div(
                Link("Back to home", to="/", class_name="btn btn-primary"),
                class_name="error-minimal-actions",
            ),
            class_name="error-minimal-content",
        ),
        class_name="error-minimal",
    )