from typing import TYPE_CHECKING

from rest_framework import serializers

from drf_yasg import openapi
from drf_yasg.inspectors.field import SerializerMethodFieldInspector
from drf_yasg.openapi import ReferenceResolver

if TYPE_CHECKING:
    from uuid import UUID


def test_missing_runtime_annotations():
    class UserSerializer(serializers.Serializer):
        uuid = serializers.SerializerMethodField()

        def get_uuid(self, obj) -> "UUID":
            return obj.uuid

    field = UserSerializer().fields["uuid"]
    components = ReferenceResolver("definitions", "parameters", force_init=True)

    inspector = SerializerMethodFieldInspector(
        view=None,
        path="/",
        method="GET",
        components=components,
        request=None,
        field_inspectors=[],
    )

    inspector.field_to_swagger_object(field, openapi.Schema, True)
