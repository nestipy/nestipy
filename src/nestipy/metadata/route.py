class RouteKey:
    """
    Constant keys used for storing and retrieving route metadata on controller methods.
    """

    path: str = "_path_"
    kwargs: str = "_kwargs_"
    method: str = "_request_method_"
    version: str = "_version_"
    cache: str = "_cache_"
