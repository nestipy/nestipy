class ModuleMetadata:
    """
    Constant keys used for storing and retrieving module metadata using the Reflect system.
    """
    Imports: str = "imports"
    Exports: str = "exports"
    Providers: str = "providers"
    Controllers: str = "controllers"
    Global: str = "_global_"
    Root: str = "_root_"
    Module: str = "_is_module_"
