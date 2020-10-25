import datetime
import decimal
import uuid

from rest_framework import serializers


class Unknown(object):
    pass


class MethodFieldExampleSerializer(serializers.Serializer):
    """
    Implementation of SerializerMethodField using type hinting for Python >= 3.5
    """

    hinted_bool = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a bool")

    def get_hinted_bool(self, obj) -> bool:
        return True

    hinted_int = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be an integer")

    def get_hinted_int(self, obj) -> int:
        return 1

    hinted_float = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a number")

    def get_hinted_float(self, obj) -> float:
        return 1.0

    hinted_decimal = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a decimal")

    def get_hinted_decimal(self, obj) -> decimal.Decimal:
        return decimal.Decimal(1)

    hinted_datetime = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a datetime")

    def get_hinted_datetime(self, obj) -> datetime.datetime:
        return datetime.datetime.now()

    hinted_date = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a date")

    def get_hinted_date(self, obj) -> datetime.date:
        return datetime.date.today()

    hinted_uuid = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a uuid")

    def get_hinted_uuid(self, obj) -> uuid.UUID:
        return uuid.uuid4()

    hinted_unknown = serializers.SerializerMethodField(
        help_text="type hint is unknown, so is expected to fallback to string")

    def get_hinted_unknown(self, obj) -> Unknown:
        return Unknown()

    non_hinted_number = serializers.SerializerMethodField(
        help_text="No hint on the method, so this is expected to fallback to string")

    def get_non_hinted_number(self, obj):
        return 1.0
