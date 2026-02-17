from __future__ import annotations

from nestipy.router.spec import RouterSpec, RouteParamSpec, RouteSpec
from nestipy.web.client_types import generate_client_types_code


def test_generate_client_types_code() -> None:
    spec = RouterSpec(
        prefix="",
        routes=[
            RouteSpec(
                path="/users/{user_id}",
                methods=["GET"],
                controller="UserController",
                handler="get_user",
                operation_id="UserController.get_user",
                params=[
                    RouteParamSpec(
                        name="user_id",
                        source="path",
                        type=int,
                        required=True,
                    )
                ],
                return_type=str,
            )
        ],
    )
    code = generate_client_types_code(spec)
    assert "class UserControllerApi" in code
    assert "def get_user" in code
    assert "class ApiClient" in code
