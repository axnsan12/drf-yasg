from rest_framework import serializers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


def test_missing_runtime_annotations():
    class UserSerializer(serializers.Serializer):
        uuid = serializers.SerializerMethodField()

        def get_uuid(self, obj) -> UUID:
            return obj.uuid

    typing.get_type_hints(UserSerializer().get_uuid)