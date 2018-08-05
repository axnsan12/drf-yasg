import datetime
import uuid

from rest_framework import serializers

from drf_yasg.utils import swagger_serializer_method


class Unknown(object):
    pass


class MethodFieldExampleSerializer(serializers.Serializer):
    """
    Fallback implementation of SerializerMethodField type hinting for Python < 3.5

    `->` syntax isn't supported, instead decorate with a serializer that returns the same type
    a bit of a hack, but it provides a cross-check between hinting and decorator functionality.
    """

    hinted_number = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a number")

    @swagger_serializer_method(serializer_class=serializers.FloatField)
    def get_hinted_number(self, obj):
        return 1.0

    hinted_datetime = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a datetime")

    @swagger_serializer_method(serializer_class=serializers.DateTimeField)
    def get_hinted_datetime(self, obj):
        return datetime.datetime.now()

    hinted_date = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a date")

    @swagger_serializer_method(serializer_class=serializers.DateField)
    def get_hinted_date(self, obj):
        return datetime.date.today()

    hinted_uuid = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a uuid")

    @swagger_serializer_method(serializer_class=serializers.UUIDField)
    def get_hinted_uuid(self, obj):
        return uuid.uuid4()

    hinted_unknown = serializers.SerializerMethodField(
        help_text="type hint is unknown, so is expected to fallback to string")

    def get_hinted_unknown(self, obj):
        return Unknown()

    non_hinted_number = serializers.SerializerMethodField(
        help_text="No hint on the method, so this is expected to fallback to string")

    def get_non_hinted_number(self, obj):
        return 1.0
