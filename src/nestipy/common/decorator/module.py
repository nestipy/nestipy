class Module:
    def __init__(self, controllers=None, providers=None, imports=None, exports=None, is_global=False):
        self.controllers = controllers
        self.providers = providers
        self.imports = imports
        self.exports = exports
        self.is_global = is_global

    def __call__(self, cls):
        class_providers = []

        if hasattr(cls, 'providers'):
            class_providers = cls.providers
        class_attrs = {
            "controllers": self.controllers or [],
            "providers": class_providers + (self.providers or []) ,
            "imports": self.imports or [],
            "exports": self.exports or [],
            "is_module__": True,
            "is_global__": self.is_global,
        }
        for key, value in class_attrs.items():
            setattr(cls, key, value)
        return cls
