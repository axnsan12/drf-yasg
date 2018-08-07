import datetime
import decimal
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

    hinted_bool = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a bool")

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField)
    def get_hinted_bool(self, obj):
        return True

    hinted_int = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be an integer")

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_hinted_int(self, obj):
        return 1

    hinted_float = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a number")

    @swagger_serializer_method(serializer_or_field=serializers.FloatField)
    def get_hinted_float(self, obj):
        return 1.0

    hinted_decimal = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a decimal")

    # note that in this case an instance is required since DecimalField has required arguments
    @swagger_serializer_method(serializer_or_field=serializers.DecimalField(max_digits=6, decimal_places=4))
    def get_hinted_decimal(self, obj):
        return decimal.Decimal(1)

    hinted_datetime = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a datetime")

    @swagger_serializer_method(serializer_or_field=serializers.DateTimeField)
    def get_hinted_datetime(self, obj):
        return datetime.datetime.now()

    hinted_date = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a date")

    @swagger_serializer_method(serializer_or_field=serializers.DateField)
    def get_hinted_date(self, obj):
        return datetime.date.today()

    hinted_uuid = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a uuid")

    @swagger_serializer_method(serializer_or_field=serializers.UUIDField)
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
