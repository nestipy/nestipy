from typing import Type, List, Optional

from pydantic import BaseModel, Field

from nestipy.dynamic_module import ConfigurableModuleBuilder


class RouteItem(BaseModel):
    path: str
    module: Type
    children: Optional[List["RouteItem"]] = Field(
        default_factory=lambda: [], alias="children"
    )


ConfigurableClassBuilder, ROUTER_CONFIG = (
    ConfigurableModuleBuilder[list[RouteItem]]().set_method("_register").build()
)
