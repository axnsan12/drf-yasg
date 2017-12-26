from .base import (
    BaseInspector, ViewInspector, FilterInspector, PaginatorInspector,
    FieldInspector, SerializerInspector, NotHandled
)
from .field import (
    InlineSerializerInspector, ReferencingSerializerInspector, RelatedFieldInspector, SimpleFieldInspector,
    FileFieldInspector, ChoiceFieldInspector, DictFieldInspector, StringDefaultFieldInspector,
    CamelCaseJSONFilter
)
from .query import (
    CoreAPICompatInspector, DjangoRestResponsePagination
)
from .view import SwaggerAutoSchema
from ..app_settings import swagger_settings

# these settings must be accesed only after definig/importing all the classes in this module to avoid ImportErrors
ViewInspector.field_inspectors = swagger_settings.DEFAULT_FIELD_INSPECTORS
ViewInspector.filter_inspectors = swagger_settings.DEFAULT_FILTER_INSPECTORS
ViewInspector.paginator_inspectors = swagger_settings.DEFAULT_PAGINATOR_INSPECTORS

__all__ = [
    # base inspectors
    'BaseInspector', 'FilterInspector', 'PaginatorInspector', 'FieldInspector', 'SerializerInspector', 'ViewInspector',

    # filter and pagination inspectors
    'CoreAPICompatInspector', 'DjangoRestResponsePagination',

    # field inspectors
    'InlineSerializerInspector', 'ReferencingSerializerInspector', 'RelatedFieldInspector', 'SimpleFieldInspector',
    'FileFieldInspector', 'ChoiceFieldInspector', 'DictFieldInspector', 'StringDefaultFieldInspector',
    'CamelCaseJSONFilter',

    # view inspectors
    'SwaggerAutoSchema',

    # module constants
    'NotHandled',
]
