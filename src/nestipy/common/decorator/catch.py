class Catch:
    def __init__(self, handler):
        self.handler = handler

    def __call__(self, cls):
        error_handlers = getattr(cls, 'error_handler__', [])
        error_handlers = error_handlers + (self.handler if isinstance(self.handler, list) else [self.handler])
        setattr(cls, 'error_handler__', error_handlers)
        return cls
