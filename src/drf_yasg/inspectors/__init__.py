import inspect
import logging
from collections import OrderedDict

import coreschema
from django.utils.encoding import force_text
from rest_framework import serializers
from rest_framework.pagination import CursorPagination, PageNumberPagination, LimitOffsetPagination
from rest_framework.utils import json, encoders
from rest_framework.viewsets import GenericViewSet

from .. import openapi
from ..app_settings import swagger_settings
from ..utils import is_list_view

#: Sentinel value that inspectors must return to signal that they do not know how to handle an object
NotHandled = object()

logger = logging.getLogger(__name__)


def force_serializer_instance(serializer):
    """Force `serializer` into a ``Serializer`` instance. If it is not a ``Serializer`` class or instance, raises
    an assertion error.

    :param serializer: serializer class or instance
    :return: serializer instance
    """
    if inspect.isclass(serializer):
        assert issubclass(serializer, serializers.BaseSerializer), "Serializer required, not %s" % serializer.__name__
        return serializer()

    assert isinstance(serializer, serializers.BaseSerializer), \
        "Serializer class or instance required, not %s" % type(serializer).__name__
    return serializer


class BaseInspector(object):
    def __init__(self, view, path, method, components, request):
        """
        :param view: the view associated with this endpoint
        :param str path: the path component of the operation URL
        :param str method: the http method of the operation
        :param openapi.ReferenceResolver components: referenceable components
        :param Request request: the request made against the schema view; can be None
        """
        self.view = view
        self.path = path
        self.method = method
        self.components = components
        self.request = request

    def probe_inspectors(self, inspectors, method_name, obj, initkwargs=None, **kwargs):
        """Probe a list of inspectors with a given object. The first inspector in the list to return a value that
        is not :data:`.NotHandled` wins.

        :param list[type[BaseInspector]] inspectors: list of inspectors to probe
        :param str method_name: name of the target method on the inspector
        :param obj: first argument to inspector method
        :param dict initkwargs: extra kwargs for instantiating inspector class
        :param kwargs: additional arguments to inspector method
        :return: the return value of the winning inspector, or ``None`` if no inspector handled the object
        """
        initkwargs = initkwargs or {}

        for inspector in inspectors:
            assert hasattr(inspector, method_name), inspector.__name__ + " must implement " + method_name
            assert inspect.isclass(inspector), "inspector must be a class, not an object"
            assert issubclass(inspector, BaseInspector), "inspector must subclass of BaseInspector"

            inspector = inspector(self.view, self.path, self.method, self.components, self.request, **initkwargs)
            method = getattr(inspector, method_name)
            result = method(obj, **kwargs)
            if result is not NotHandled:
                return result

        logger.warning("%s ignored because no inspector in %s handled it (operation: %s)", obj, inspectors, method_name)
        return None  # pragma: no cover


class PaginatorInspector(BaseInspector):
    """Base inspector for paginators.

    Responisble for determining extra query parameters and response structure added by given paginators.
    """

    def get_paginator_parameters(self, paginator):
        """Get the pagination parameters for a single paginator **instance**.

        Should return :data:`.NotHandled` if this inspector does not know how to handle the given `paginator`.

        :param BasePagination paginator: the paginator
        :rtype: list[openapi.Parameter]
        """
        return NotHandled

    def get_paginated_response(self, paginator, response_schema):
        """Add appropriate paging fields to a response :class:`.Schema`.

        Should return :data:`.NotHandled` if this inspector does not know how to handle the given `paginator`.

        :param BasePagination paginator: the paginator
        :param openapi.Schema response_schema: the response schema that must be paged.
        :rtype: openapi.Schema
        """
        return NotHandled


class FilterInspector(BaseInspector):
    """Base inspector for filter backends.

    Responsible for determining extra query parameters added by given filter backends.
    """

    def get_filter_parameters(self, filter_backend):
        """Get the filter parameters for a single filter backend **instance**.

        Should return :data:`.NotHandled` if this inspector does not know how to handle the given `filter_backend`.

        :param BaseFilterBackend filter_backend: the filter backend
        :rtype: list[openapi.Parameter]
        """
        return NotHandled


class CoreAPICompatInspector(PaginatorInspector, FilterInspector):
    """Converts ``coreapi.Field``\ s to :class:`.openapi.Parameter`\ s for filters and paginators that implement a
    ``get_schema_fields`` method.
    """

    def get_paginator_parameters(self, paginator):
        fields = []
        if hasattr(paginator, 'get_schema_fields'):
            fields = paginator.get_schema_fields(self.view)

        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_filter_parameters(self, filter_backend):
        fields = []
        if hasattr(filter_backend, 'get_schema_fields'):
            fields = filter_backend.get_schema_fields(self.view)
        return [self.coreapi_field_to_parameter(field) for field in fields]

    def coreapi_field_to_parameter(self, field):
        """Convert an instance of `coreapi.Field` to a swagger :class:`.Parameter` object.

        :param coreapi.Field field:
        :rtype: openapi.Parameter
        """
        location_to_in = {
            'query': openapi.IN_QUERY,
            'path': openapi.IN_PATH,
            'form': openapi.IN_FORM,
            'body': openapi.IN_FORM,
        }
        coreapi_types = {
            coreschema.Integer: openapi.TYPE_INTEGER,
            coreschema.Number: openapi.TYPE_NUMBER,
            coreschema.String: openapi.TYPE_STRING,
            coreschema.Boolean: openapi.TYPE_BOOLEAN,
        }
        return openapi.Parameter(
            name=field.name,
            in_=location_to_in[field.location],
            type=coreapi_types.get(type(field.schema), openapi.TYPE_STRING),
            required=field.required,
            description=field.schema.description,
        )


class DjangoRestResponsePagination(PaginatorInspector):
    """Provides response schema pagination warpping for django-rest-framework's LimitOffsetPagination,
    PageNumberPagination and CursorPagination
    """

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        if isinstance(paginator, (LimitOffsetPagination, PageNumberPagination, CursorPagination)):
            has_count = not isinstance(paginator, CursorPagination)
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('count', openapi.Schema(type=openapi.TYPE_INTEGER) if has_count else None),
                    ('next', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI)),
                    ('previous', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI)),
                    ('results', response_schema),
                )),
                required=['count', 'results']
            )

        return paged_schema


class FieldInspector(BaseInspector):
    """Base inspector for serializers and serializer fields. """

    def __init__(self, view, path, method, components, request, field_inspectors):
        super(FieldInspector, self).__init__(view, path, method, components, request)
        self.field_inspectors = field_inspectors

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        """Convert a drf Serializer or Field instance into a Swagger object.

        Should return :data:`.NotHandled` if this inspector does not know how to handle the given `field`.

        :param rest_framework.serializers.Field field: the source field
        :param type[openapi.SwaggerDict] swagger_object_type: should be one of Schema, Parameter, Items
        :param bool use_references: if False, forces all objects to be declared inline
           instead of by referencing other components
        :param kwargs: extra attributes for constructing the object;
           if swagger_object_type is Parameter, ``name`` and ``in_`` should be provided
        :return: the swagger object
        :rtype: openapi.Parameter,openapi.Items,openapi.Schema,openapi.SchemaRef
        """
        return NotHandled

    def probe_field_inspectors(self, field, swagger_object_type, use_references, **kwargs):
        """Helper method for recursively probing `field_inspectors` to handle a given field.

        All arguments are the same as :meth:`.field_to_swagger_object`.

        :rtype: openapi.Parameter,openapi.Items,openapi.Schema,openapi.SchemaRef
        """
        return self.probe_inspectors(
            self.field_inspectors, 'field_to_swagger_object', field, {'field_inspectors': self.field_inspectors},
            swagger_object_type=swagger_object_type, use_references=use_references, **kwargs
        )

    def _get_partial_types(self, field, swagger_object_type, use_references, **kwargs):
        """Helper method to extract generic information from a field and return a partial constructor for the
        appropriate openapi object. The return value is a tuple consisting of:

        All arguments are the same as :meth:`.field_to_swagger_object`.

        * a function for constructing objects of `swagger_object_type`; its prototype is: ::

            def SwaggerType(existing_object=None, **instance_kwargs):

          This function creates an instance of `swagger_object_type`, passing the following attributes to its init,
          in order of precedence:

            - arguments specified by the ``kwargs`` parameter of :meth:`._get_partial_types`
            - ``instance_kwargs`` passed to the constructor function
            - ``title``, ``description``, ``required``, ``default`` and ``read_only`` inferred from the field,
              where appropriate

          If ``existing_object`` is not ``None``, it is updated instead of creating a new object.

        * a type that should be used for child objects if `field` is of an array type. This can currently have two
          values:

            - :class:`.Schema` if `swagger_object_type` is :class:`.Schema`
            - :class:`.Items` if `swagger_object_type` is  :class:`.Parameter` or :class:`.Items`

        :rtype: tuple[callable,(type[openapi.Schema],type[openapi.Items])]
        """
        assert swagger_object_type in (openapi.Schema, openapi.Parameter, openapi.Items)
        assert not isinstance(field, openapi.SwaggerDict), "passed field is already a SwaggerDict object"
        title = force_text(field.label) if field.label else None
        title = title if swagger_object_type == openapi.Schema else None  # only Schema has title
        title = None
        description = force_text(field.help_text) if field.help_text else None
        description = description if swagger_object_type != openapi.Items else None  # Items has no description either

        def SwaggerType(existing_object=None, **instance_kwargs):
            if 'required' not in instance_kwargs and swagger_object_type == openapi.Parameter:
                instance_kwargs['required'] = field.required

            if 'default' not in instance_kwargs and swagger_object_type != openapi.Items:
                default = getattr(field, 'default', serializers.empty)
                if default is not serializers.empty:
                    if callable(default):
                        try:
                            if hasattr(default, 'set_context'):
                                default.set_context(field)
                            default = default()
                        except Exception:  # pragma: no cover
                            logger.warning("default for %s is callable but it raised an exception when "
                                           "called; 'default' field will not be added to schema", field, exc_info=True)
                            default = None

                    if default is not None:
                        try:
                            default = field.to_representation(default)
                            # JSON roundtrip ensures that the value is valid JSON;
                            # for example, sets get transformed into lists
                            default = json.loads(json.dumps(default, cls=encoders.JSONEncoder))
                        except Exception:  # pragma: no cover
                            logger.warning("'default' on schema for %s will not be set because "
                                           "to_representation raised an exception", field, exc_info=True)
                            default = None

                    if default is not None:
                        instance_kwargs['default'] = default

            if 'read_only' not in instance_kwargs and swagger_object_type == openapi.Schema:
                if field.read_only:
                    instance_kwargs['read_only'] = True

            instance_kwargs.setdefault('title', title)
            instance_kwargs.setdefault('description', description)
            instance_kwargs.update(kwargs)

            if existing_object is not None:
                assert isinstance(existing_object, swagger_object_type)
                for attr, val in instance_kwargs.items():
                    setattr(existing_object, attr, val)
                return existing_object

            return swagger_object_type(**instance_kwargs)

        # arrays in Schema have Schema elements, arrays in Parameter and Items have Items elements
        child_swagger_type = openapi.Schema if swagger_object_type == openapi.Schema else openapi.Items
        return SwaggerType, child_swagger_type


class SerializerInspector(FieldInspector):
    def get_schema(self, serializer):
        """Convert a DRF Serializer instance to an :class:`.openapi.Schema`.

        Should return :data:`.NotHandled` if this inspector does not know how to handle the given `serializer`.

        :param serializers.BaseSerializer serializer: the ``Serializer`` instance
        :rtype: openapi.Schema
        """
        return NotHandled

    def get_request_parameters(self, serializer, in_):
        """Convert a DRF serializer into a list of :class:`.Parameter`\ s.

        Should return :data:`.NotHandled` if this inspector does not know how to handle the given `serializer`.

        :param serializers.BaseSerializer serializer: the ``Serializer`` instance
        :param str in_: the location of the parameters, one of the `openapi.IN_*` constants
        :rtype: list[openapi.Parameter]
        """
        return NotHandled


from .field import (
    InlineSerializerInspector, ReferencingSerializerInspector, RelatedFieldInspector, SimpleFieldInspector,
    FileFieldInspector, ChoiceFieldInspector, DictFieldInspector, StringDefaultFieldInspector
)


class ViewInspector(BaseInspector):
    body_methods = ('PUT', 'PATCH', 'POST')  #: methods allowed to have a request body

    # real values set at the bottom to prevent import loops
    field_inspectors = []  #:
    filter_inspectors = []  #:
    paginator_inspectors = []  #:

    def __init__(self, view, path, method, components, request, overrides):
        """
        Inspector class responsible for providing :class:`.Operation` definitions given a view, path and method.

        :param dict overrides: manual overrides as passed to :func:`@swagger_auto_schema <.swagger_auto_schema>`
        """
        super(ViewInspector, self).__init__(view, path, method, components, request)
        self.overrides = overrides
        self._prepend_inspector_overrides('field_inspectors')
        self._prepend_inspector_overrides('filter_inspectors')
        self._prepend_inspector_overrides('paginator_inspectors')

    def _prepend_inspector_overrides(self, inspectors):
        extra_inspectors = self.overrides.get(inspectors, None)
        if extra_inspectors:
            default_inspectors = [insp for insp in getattr(self, inspectors) if insp not in extra_inspectors]
            setattr(self, inspectors, extra_inspectors + default_inspectors)

    def get_operation(self, operation_keys):
        """Get an :class:`.Operation` for the given API endpoint (path, method).
        This includes query, body parameters and response schemas.

        :param tuple[str] operation_keys: an array of keys describing the hierarchical layout of this view in the API;
          e.g. ``('snippets', 'list')``, ``('snippets', 'retrieve')``, etc.
        :rtype: openapi.Operation
        """
        raise NotImplementedError("ViewInspector must implement get_operation()!")

    # methods below provided as default implementations for probing inspectors

    def should_filter(self):
        """Determine whether filter backend parameters should be included for this request.

        :rtype: bool
        """
        if not getattr(self.view, 'filter_backends', None):
            return False

        if self.method.lower() not in ["get", "delete"]:
            return False

        if not isinstance(self.view, GenericViewSet):
            return True

        return is_list_view(self.path, self.method, self.view)

    def get_filter_parameters(self):
        """Return the parameters added to the view by its filter backends.

        :rtype: list[openapi.Parameter]
        """
        if not self.should_filter():
            return []

        fields = []
        for filter_backend in self.view.filter_backends:
            fields += self.probe_inspectors(self.filter_inspectors, 'get_filter_parameters', filter_backend()) or []

        return fields

    def should_page(self):
        """Determine whether paging parameters and structure should be added to this operation's request and response.

        :rtype: bool
        """
        if not hasattr(self.view, 'paginator'):
            return False

        if self.view.paginator is None:
            return False

        if self.method.lower() != 'get':
            return False

        return is_list_view(self.path, self.method, self.view)

    def get_pagination_parameters(self):
        """Return the parameters added to the view by its paginator.

        :rtype: list[openapi.Parameter]
        """
        if not self.should_page():
            return []

        return self.probe_inspectors(self.paginator_inspectors, 'get_paginator_parameters', self.view.paginator) or []

    def serializer_to_schema(self, serializer):
        """Convert a serializer to an OpenAPI :class:`.Schema`.

        :param serializers.BaseSerializer serializer: the ``Serializer`` instance
        :returns: the converted :class:`.Schema`, or ``None`` in case of an unknown serializer
        :rtype: openapi.Schema,openapi.SchemaRef,None
        """
        return self.probe_inspectors(
            self.field_inspectors, 'get_schema', serializer, {'field_inspectors': self.field_inspectors}
        )

    def serializer_to_parameters(self, serializer, in_):
        """Convert a serializer to a possibly empty list of :class:`.Parameter`\ s.

        :param serializers.BaseSerializer serializer: the ``Serializer`` instance
        :param str in_: the location of the parameters, one of the `openapi.IN_*` constants
        :rtype: list[openapi.Parameter]
        """
        return self.probe_inspectors(
            self.field_inspectors, 'get_request_parameters', serializer, {'field_inspectors': self.field_inspectors},
            in_=in_
        ) or []

    def get_paginated_response(self, response_schema):
        """Add appropriate paging fields to a response :class:`.Schema`.

        :param openapi.Schema response_schema: the response schema that must be paged.
        :returns: the paginated response class:`.Schema`, or ``None`` in case of an unknown pagination scheme
        :rtype: openapi.Schema
        """
        return self.probe_inspectors(self.paginator_inspectors, 'get_paginated_response',
                                     self.view.paginator, response_schema=response_schema)


ViewInspector.field_inspectors = swagger_settings.DEFAULT_FIELD_INSPECTORS
ViewInspector.filter_inspectors = swagger_settings.DEFAULT_FILTER_INSPECTORS
ViewInspector.paginator_inspectors = swagger_settings.DEFAULT_PAGINATOR_INSPECTORS

from . import view

SwaggerAutoSchema = view.SwaggerAutoSchema

__all__ = [
    'BaseInspector', 'FilterInspector', 'PaginatorInspector', 'FieldInspector', 'SerializerInspector', 'ViewInspector',
    'CoreAPICompatInspector', 'DjangoRestResponsePagination',
    'InlineSerializerInspector', 'ReferencingSerializerInspector',
    'RelatedFieldInspector', 'SimpleFieldInspector', 'FileFieldInspector', 'ChoiceFieldInspector', 'DictFieldInspector',
    'StringDefaultFieldInspector', 'SwaggerAutoSchema',
]
