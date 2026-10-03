from decimal import Decimal

import pytest
from rest_framework import serializers

from drf_yasg import openapi
from drf_yasg.inspectors.field import get_basic_type_info


@pytest.mark.parametrize(
    "coerce_to_string, expected_type, expected_format",
    [
        # Default: rendered as a string, so no numeric format is attached.
        # ``decimal`` is not a valid OpenAPI format.
        (True, openapi.TYPE_STRING, None),
        # decimal_as_float path: rendered as a number with a spec-valid format.
        (False, openapi.TYPE_NUMBER, openapi.FORMAT_DOUBLE),
    ],
)
def test_decimal_field_format(coerce_to_string, expected_type, expected_format):
    field = serializers.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=Decimal("0.0"),
        coerce_to_string=coerce_to_string,
    )

    type_info = get_basic_type_info(field)

    assert type_info["type"] == expected_type
    assert type_info.get("format") == expected_format
