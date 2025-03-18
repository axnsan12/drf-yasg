from __future__ import annotations

from rest_framework import generics, serializers


class GenericSerializer[T](serializers.Serializer):
    value = serializers.SerializerMethodField()

    def get_value(self, instance: T) -> str:
        return repr(instance)


class RetrieveView[T](generics.RetrieveAPIView):
    serializer_class = GenericSerializer[T]
