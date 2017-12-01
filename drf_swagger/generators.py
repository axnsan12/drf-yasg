from rest_framework.schemas.generators import distribute_links, SchemaGenerator

from . import openapi


class OpenAPISchemaGenerator(object):
    def __init__(self, info, version, url=None, patterns=None, urlconf=None):
        self._gen = SchemaGenerator(info.title, url, info.description, patterns, urlconf)
        self.info = info
        self.version = version
        self.endpoints = None

    def get_schema(self, request=None, public=False):
        """Generate an openapi.Swagger representing the API schema.

        Shamelessly stolen from rest_framework SchemaGenerator."""
        if self.endpoints is None:
            inspector = self._gen.endpoint_inspector_cls(self._gen.patterns, self._gen.urlconf)
            self.endpoints = inspector.get_api_endpoints()

        # Generate (path, method, view) given (path, method, callback)
        view_endpoints = []
        for path, method, callback in self.endpoints:
            view = self._gen.create_view(callback, method, request)
            path = self._gen.coerce_path(path, method, view)
            view_endpoints.append((path, method, view))
        self.endpoints = view_endpoints

        paths = self.get_paths()

        url = self._gen.url
        if not url and request is not None:
            url = request.build_absolute_uri()

        # distribute_links(links)
        return openapi.Swagger(
            info=self.info, paths=paths,
            _url=url, _version=self.version,
        )

    def get_paths(self):
        if not self.endpoints:
            return []
        prefix = self._gen.determine_path_prefix(ve[0] for ve in self.endpoints)
        operations = []
        for path, method, view in self.endpoints:
            if not self._gen.has_view_permissions(path, method, view):
                continue
            # link = view.schema.get_link(path, method, base_url=self.url)
            operations.append((path, method))

        return {}




