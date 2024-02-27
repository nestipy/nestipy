from dataclasses import dataclass
from typing import Optional, Any, Callable


@dataclass
class ModuleProvider:
    provide: Optional[Any] = None
    use_value: Optional[Any] = None
    use_factory: Optional[Callable[[Any], Any]] = None
    inject: Optional[list[Any]] = None
