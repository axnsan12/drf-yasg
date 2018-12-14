import uuid
from typing import Dict, List, Union, Set

import pytest

from drf_yasg import openapi
from drf_yasg.inspectors.field import get_basic_type_info_from_hint


@pytest.mark.parametrize('hint_class, expected_swagger_type_info', [
    (int, {'type': openapi.TYPE_INTEGER, 'format': None}),
    (str, {'type': openapi.TYPE_STRING, 'format': None}),
    (bool, {'type': openapi.TYPE_BOOLEAN, 'format': None}),
    (dict, {'type': openapi.TYPE_OBJECT, 'format': None}),
    (Dict[int, int], {'type': openapi.TYPE_OBJECT, 'format': None}),
    (uuid.UUID, {'type': openapi.TYPE_STRING, 'format': openapi.FORMAT_UUID}),
    (List[int], {'type': openapi.TYPE_ARRAY, 'items': openapi.Items(openapi.TYPE_INTEGER)}),
    (List[str], {'type': openapi.TYPE_ARRAY, 'items': openapi.Items(openapi.TYPE_STRING)}),
    (List[bool], {'type': openapi.TYPE_ARRAY, 'items': openapi.Items(openapi.TYPE_BOOLEAN)}),
    (Set[int], {'type': openapi.TYPE_ARRAY, 'items': openapi.Items(openapi.TYPE_INTEGER)}),
    (Union[List[int], type(None)], {'type': openapi.TYPE_ARRAY, 'items': openapi.Items(openapi.TYPE_INTEGER)}),
    # Following cases are for stability reasons here. It's not 100% correct, but it should work somehow and not crash.
    (Union[int, bool], {'type': openapi.TYPE_INTEGER, 'format': None}),
    (List, {'type': openapi.TYPE_ARRAY, 'items': openapi.Items(openapi.TYPE_STRING)}),
])
def test_get_basic_type_info_from_hint(hint_class, expected_swagger_type_info):
    type_info = get_basic_type_info_from_hint(hint_class)
    assert type_info == expected_swagger_type_info
