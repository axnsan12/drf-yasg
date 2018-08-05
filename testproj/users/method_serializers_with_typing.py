import datetime
import typing
import uuid

from rest_framework import serializers


class Unknown(object):
    pass


class MethodFieldExampleSerializer(serializers.Serializer):
    """
    Implementation of SerializerMethodField using type hinting for Python >= 3.5
    """

    hinted_number = serializers.SerializerMethodField(
        help_text="the type hint on the method should determine this to be a number")

    def get_hinted_number(self, obj) -> float:
        return 1.0

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
