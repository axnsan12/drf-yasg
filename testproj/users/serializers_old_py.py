from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method


class MethodFieldExampleSerializer(serializers.Serializer):
    """
    Fallback implementation of SerializerMethodField type hinting for Python < 3.5
    """

    hinted_number = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a number")

    non_hinted_number = serializers.SerializerMethodField(
        help_text="No hint on the method, so this is expected to fallback to string")

    # `->` syntax isn't supported, instead decorate with a serializer that returns the same type
    # (a bit of a hack, but means we get the same output)
    @swagger_serializer_method(serializer_class=serializers.FloatField)
    def get_hinted_number(self, obj):
        return 1.0

    def get_non_hinted_number(self, obj):
        return 1.0
