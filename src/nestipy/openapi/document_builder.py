from typing import Optional
from .openapi_docs.v3 import Info, OpenAPI, Components, SecurityScheme, HTTPSecurity


class DocumentBuilder:
    """
    Utility class for building OpenAPI documentation.
    Uses a singleton pattern to maintain the documentation state.
    """

    _info: dict = {"title": "Nestipy", "description": "", "version": "1.0"}
    _security_schemes: dict = {}
    _schemas: dict = {}
    _instance: Optional["DocumentBuilder"] = None

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of DocumentBuilder.
        :return: DocumentBuilder instance.
        """
        return DocumentBuilder()

    def __new__(cls, *args, **kwargs):
        """
        Ensure singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_title(self, title: str):
        """
        Set the title of the API.
        :param title: API title.
        :return: Self for chaining.
        """
        self._info["title"] = title
        return self

    def set_description(self, description: str):
        """
        Set the description of the API.
        :param description: API description.
        :return: Self for chaining.
        """
        self._info["description"] = description
        return self

    def set_version(self, version: str):
        """
        Set the version of the API.
        :param version: API version.
        :return: Self for chaining.
        """
        self._info["version"] = version
        return self

    def add_basic_auth(self):
        """
        Add Basic Authentication to the security schemes.
        :return: Self for chaining.
        """
        self._security_schemes["basicAuth"] = HTTPSecurity(
            scheme="basic",
        )
        return self

    def add_bearer_auth(self):
        """
        Add Bearer Authentication (JWT) to the security schemes.
        :return: Self for chaining.
        """
        self._security_schemes["bearer"] = HTTPSecurity(
            scheme="bearer",
        )
        return self

    def add_security(self, name, security: SecurityScheme):
        """
        Add a custom security scheme.
        :param name: Name of the security scheme.
        :param security: SecurityScheme instance.
        :return: Self for chaining.
        """
        self._security_schemes[name] = security
        return self

    def build(self):
        """
        Build the final OpenAPI document.
        :return: OpenAPI document object.
        """
        return OpenAPI(
            info=Info(**self._info),
            components=Components(
                security_schemes=self._security_schemes, schemas=self._schemas
            ),
        )
