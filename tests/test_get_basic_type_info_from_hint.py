import sys
import uuid
from typing import Dict, List, Optional, Set, Union

import pytest

from drf_yasg import openapi
from drf_yasg.inspectors.field import get_basic_type_info_from_hint

resolutions = [
    (
        bool,
        {
            "type": openapi.TYPE_BOOLEAN,
            "format": None,
        },
    ),
    (
        int,
        {
            "type": openapi.TYPE_INTEGER,
            "format": None,
        },
    ),
    (
        str,
        {
            "type": openapi.TYPE_STRING,
            "format": None,
        },
    ),
    (
        list,
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_STRING),
        },
    ),
    (
        list[bool],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_BOOLEAN),
        },
    ),
    (
        List,
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_STRING),
        },
    ),
    (
        List[bool],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_BOOLEAN),
        },
    ),
    (
        List[int],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_INTEGER),
        },
    ),
    (
        List[str],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_STRING),
        },
    ),
    (
        Set[int],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_INTEGER),
        },
    ),
    (
        dict,
        {
            "type": openapi.TYPE_OBJECT,
            "format": None,
        },
    ),
    (
        dict[int, int],
        {
            "type": openapi.TYPE_OBJECT,
            "format": None,
        },
    ),
    (
        Dict[int, int],
        {
            "type": openapi.TYPE_OBJECT,
            "format": None,
        },
    ),
    (
        Optional[bool],
        {
            "type": openapi.TYPE_BOOLEAN,
            "format": None,
            "x-nullable": True,
        },
    ),
    (
        Optional[List[int]],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_INTEGER),
            "x-nullable": True,
        },
    ),
    (
        Union[List[int], type(None)],
        {
            "type": openapi.TYPE_ARRAY,
            "items": openapi.Items(openapi.TYPE_INTEGER),
            "x-nullable": True,
        },
    ),
    (
        Union[int, float],
        None,
    ),
    (
        uuid.UUID,
        {
            "type": openapi.TYPE_STRING,
            "format": openapi.FORMAT_UUID,
        },
    ),
    (
        None,
        None,
    ),
    (
        "SomeType",
        None,
    ),
    (
        type("SomeType", (object,), {}),
        None,
    ),
]

if sys.version_info >= (3, 10):
    resolutions.extend(
        [
            (
                bool | None,
                {
                    "type": openapi.TYPE_BOOLEAN,
                    "format": None,
                    "x-nullable": True,
                },
            ),
            (
                list[int] | None,
                {
                    "type": openapi.TYPE_ARRAY,
                    "items": openapi.Items(openapi.TYPE_INTEGER),
                    "x-nullable": True,
                },
            ),
            (
                int | float,
                None,
            ),
        ]
    )


@pytest.mark.parametrize("hint_class, expected_swagger_type_info", resolutions)
def test_get_basic_type_info_from_hint(hint_class, expected_swagger_type_info):
    type_info = get_basic_type_info_from_hint(hint_class)
    assert type_info == expected_swagger_type_info
