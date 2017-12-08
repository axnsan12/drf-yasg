from collections import defaultdict, OrderedDict

import django.db.models
import uritemplate
from coreapi.compat import force_text
from rest_framework.schemas.generators import SchemaGenerator
from rest_framework.schemas.inspectors import get_pk_description

from drf_swagger.inspectors import SwaggerAutoSchema
from . import openapi


class OpenAPISchemaGenerator(object):
    """
    This class iterates over all registered API endpoints and returns an appropriate OpenAPI 2.0 compliant schema.
    Method implementations shamelessly stolen and adapted from rest_framework SchemaGenerator.
    """

    def __init__(self, info, version, url=None, patterns=None, urlconf=None):
        self._gen = SchemaGenerator(info.title, url, info.get('description', ''), patterns, urlconf)
        self.info = info
        self.version = version
        self.endpoints = None
        self.url = url

    def get_schema(self, request=None, public=False):
        """Generate an openapi.Swagger representing the API schema."""
        if self.endpoints is None:
            inspector = self._gen.endpoint_inspector_cls(self._gen.patterns, self._gen.urlconf)
            self.endpoints = inspector.get_api_endpoints()

        self.clean_endpoints(None if public else request)
        paths = self.get_paths()

        url = self._gen.url
        if not url and request is not None:
            url = request.build_absolute_uri()

        return openapi.Swagger(
            info=self.info, paths=paths,
            _url=url, _version=self.version,
        )

    def create_view(self, callback, method, request):
        view = self._gen.create_view(callback, method, request)
        overrides = getattr(callback, 'swagger_auto_schema', None)
        if overrides is not None:
            # decorated function based view
            for method, _ in overrides.items():
                view_method = getattr(view, method, None)
                if view_method is not None:
                    setattr(view_method.__func__, 'swagger_auto_schema', overrides)
        return view

    def clean_endpoints(self, request):
        """Generate {path: (view_class, [(method, view)]) given (path, method, callback)."""
        view_paths = defaultdict(list)
        view_cls = {}
        for path, method, callback in self.endpoints:
            view = self.create_view(callback, method, request)
            path = self._gen.coerce_path(path, method, view)
            view_paths[path].append((method, view))
            view_cls[path] = callback.cls
        self.endpoints = {path: (view_cls[path], methods) for path, methods in view_paths.items()}

    def get_operation_keys(self, subpath, method, view):
        """
        Return a list of keys that should be used to layout a link within
        the schema document.

        /users/                   ("users", "list"), ("users", "create")
        /users/{pk}/              ("users", "read"), ("users", "update"), ("users", "delete")
        /users/enabled/           ("users", "enabled")  # custom viewset list action
        /users/{pk}/star/         ("users", "star")     # custom viewset detail action
        /users/{pk}/groups/       ("users", "groups", "list"), ("users", "groups", "create")
        /users/{pk}/groups/{pk}/  ("users", "groups", "read"), ("users", "groups", "update")
        """
        return self._gen.get_keys(subpath, method, view)

    def get_paths(self):
        if not self.endpoints:
            return []
        prefix = self._gen.determine_path_prefix(self.endpoints.keys())
        paths = OrderedDict()

        default_schema_cls = SwaggerAutoSchema
        for path, (view_cls, methods) in sorted(self.endpoints.items()):
            path_parameters = self.get_path_parameters(path, view_cls)
            operations = {}
            for method, view in methods:
                if not self._gen.has_view_permissions(path, method, view):
                    continue

                operation_keys = self.get_operation_keys(path[len(prefix):], method, view)
                overrides = self.get_overrides(view, method)
                auto_schema_cls = overrides.get('auto_schema', default_schema_cls)
                schema = auto_schema_cls(view, path, method, overrides)
                operations[method.lower()] = schema.get_operation(operation_keys)

            paths[path] = openapi.PathItem(parameters=path_parameters, **operations)

        return openapi.Paths(paths=paths)

    def get_overrides(self, view, method):
        method = method.lower()
        action = getattr(view, 'action', method)
        action_method = getattr(view, action, None)
        overrides = getattr(action_method, 'swagger_auto_schema', {})
        if method in overrides:
            overrides = overrides[method]

        return overrides

    def get_path_parameters(self, path, view_cls):
        """Return a list of Parameter instances corresponding to any templated path variables.

        :param str path: templated request path
        :param type view_cls: the view class associated with the path
        :return list[openapi.Parameter]: path parameters
        """
        parameters = []
        model = getattr(getattr(view_cls, 'queryset', None), 'model', None)

        for variable in uritemplate.variables(path):
            pattern = None
            type = openapi.TYPE_STRING
            description = None
            if model is not None:
                # Attempt to infer a field description if possible.
                try:
                    model_field = model._meta.get_field(variable)
                except Exception:
                    model_field = None

                if model_field is not None and model_field.help_text:
                    description = force_text(model_field.help_text)
                elif model_field is not None and model_field.primary_key:
                    description = get_pk_description(model, model_field)

                if hasattr(view_cls, 'lookup_value_regex') and getattr(view_cls, 'lookup_field', None) == variable:
                    pattern = view_cls.lookup_value_regex
                elif isinstance(model_field, django.db.models.AutoField):
                    type = openapi.TYPE_INTEGER

            field = openapi.Parameter(
                name=variable,
                required=True,
                in_=openapi.IN_PATH,
                type=type,
                pattern=pattern,
                description=description,
            )
            parameters.append(field)

        return parameters
