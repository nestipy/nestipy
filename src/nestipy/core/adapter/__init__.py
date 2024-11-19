from .http_adapter import HttpAdapter

try:
    from .blacksheep_adapter import BlackSheepAdapter
except ImportError:
    BlackSheepAdapter = None

from .fastapi_adapter import FastApiAdapter

# Dynamically build the __all__ list
__all__ = ["HttpAdapter"]
if BlackSheepAdapter:
    __all__.append("BlackSheepAdapter")
if FastApiAdapter:
    __all__.append("FastApiAdapter")
