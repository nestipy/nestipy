from .openapi_docs.v3 import Info, OpenAPI, Components, SecurityScheme, HTTPSecurity


class DocumentBuilder:
    _info: dict = {"title": "Nestipy", "description": "", "version": "1.0"}
    _security_schemes: dict = {}
    _schemas: dict = {}
    _instance: "DocumentBuilder" = None

    @classmethod
    def get_instance(cls):
        return DocumentBuilder()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DocumentBuilder, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set_title(self, title: str):
        self._info["title"] = title
        return self

    def set_description(self, description: str):
        self._info["description"] = description
        return self

    def set_version(self, version: str):
        self._info["version"] = version
        return self

    def add_basic_auth(self):
        self._security_schemes["basicAuth"] = HTTPSecurity(
            scheme="basic",
        )
        return self

    def add_bearer_auth(self):
        self._security_schemes["bearer"] = HTTPSecurity(
            scheme="bearer",
        )
        return self

    def add_security(self, name, security: SecurityScheme):
        self._security_schemes[name] = security
        return self

    def build(self):
        return OpenAPI(
            info=Info(**self._info),
            components=Components(
                security_schemes=self._security_schemes, schemas=self._schemas
            ),
        )
