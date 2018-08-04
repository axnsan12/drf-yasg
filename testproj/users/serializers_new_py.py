from rest_framework import serializers


class MethodFieldExampleSerializer(serializers.Serializer):
    """
  Implementation of SerializerMethodField using type hinting for Python >= 3.5
    """

    hinted_number = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a number")

    non_hinted_number = serializers.SerializerMethodField(
        help_text="No hint on the method, so this is expected to fallback to string")

    def get_hinted_number(self, obj) -> float:
        return 1.0

    def get_non_hinted_number(self, obj):
        return 1.0
