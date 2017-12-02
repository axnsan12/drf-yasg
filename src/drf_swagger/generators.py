from rest_framework.schemas import SchemaGenerator as _SchemaGenerator

from . import openapi


class OpenAPISchemaGenerator(_SchemaGenerator):
    def __init__(self, info, version, url=None, patterns=None, urlconf=None):
        super(OpenAPISchemaGenerator, self).__init__(info.title, url, info.description, patterns, urlconf)
        self.info = info
        self.version = version

    def get_schema(self, request=None, public=False):
        document = super(OpenAPISchemaGenerator, self).get_schema(request, public)
        swagger = openapi.Swagger.from_coreapi(document, self.info, self.version)
        return swagger
