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

    return h.section(
        h.div(
            h.span(status, class_name="error-code"),
            h.h1(title, class_name="error-title"),
            h.p(message, class_name="error-message"),
            Link("Back home", to="/", class_name="btn btn-primary"),
            class_name="error-card",
        ),
        class_name="error-page",
    )