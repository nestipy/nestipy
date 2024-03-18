def singleton(get_aware=lambda scope, receive: id(scope)):
    instances = {}

    def decorator(cls):
        def get_instance(*args, **kwargs):
            scope_id = get_aware(*args, **kwargs)

            if scope_id not in instances:
                instances[scope_id] = cls(*args, **kwargs)
            return instances[scope_id]

        return get_instance

    return decorator
