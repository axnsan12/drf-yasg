import pytest
from django.urls import path
from django.utils.decorators import method_decorator
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from drf_yasg import openapi
from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.utils import swagger_auto_schema


def test_no_form_parameters_with_non_form_parsers():
    # see https://github.com/axnsan12/drf-yasg/issues/270
    # test that manual form parameters for views that haven't set
    # all their parsers classes to form parsers are not allowed
    # even when the request body is empty

    @method_decorator(name='post', decorator=swagger_auto_schema(
        operation_description="Logins a user and returns a token",
        manual_parameters=[
            openapi.Parameter(
                "username",
                openapi.IN_FORM,
                required=True,
                type=openapi.TYPE_STRING,
                description="Valid username or email for authentication"
            ),
        ]
    ))
    class CustomObtainAuthToken(ObtainAuthToken):
        throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES

    urlpatterns = [
        path('token/', CustomObtainAuthToken.as_view()),
    ]

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        patterns=urlpatterns
    )

    with pytest.raises(SwaggerGenerationError):
        generator.get_schema(None, True)
