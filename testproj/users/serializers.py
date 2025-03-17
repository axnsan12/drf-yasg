import typing  # noqa: F401

from django.contrib.auth.models import User
from rest_framework import serializers

from drf_yasg.utils import swagger_serializer_method
from snippets.models import Snippet

from .method_serializers import MethodFieldExampleSerializer


class OtherStuffSerializer(serializers.Serializer):
    foo = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    article_slugs = serializers.SlugRelatedField(read_only=True, slug_field='slug', many=True, source='articles')
    last_connected_ip = serializers.IPAddressField(help_text="i'm out of ideas", protocol='ipv4', read_only=True)
    last_connected_at = serializers.DateField(help_text="really?", read_only=True)

    other_stuff = serializers.SerializerMethodField(
        help_text="the decorator should determine the serializer class for this")

    hint_example = MethodFieldExampleSerializer()

    @swagger_serializer_method(serializer_or_field=OtherStuffSerializer)
    def get_other_stuff(self, obj):
        """
        method_field that uses a serializer internally.

        By using the decorator, we can tell drf-yasg how to represent this in Swagger
        :param obj:
        :return:
        """
        return OtherStuffSerializer().data

    help_text_example_1 = serializers.SerializerMethodField(
        help_text="help text on field is set, so this should appear in swagger"
    )

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField(
        help_text="decorated instance help_text shouldn't appear in swagger because field has priority"))
    def get_help_text_example_1(self):
        """
        method docstring shouldn't appear in swagger because field has priority
        :return:
        """
        return 1

    help_text_example_2 = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField(
        help_text="instance help_text is set, so should appear in swagger"))
    def get_help_text_example_2(self):
        """
        method docstring shouldn't appear in swagger because decorator has priority
        :return:
        """
        return 1

    help_text_example_3 = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField())
    def get_help_text_example_3(self):
        """
        docstring is set so should appear in swagger as fallback
        :return:
        """
        return 1

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'articles', 'snippets',
                  'last_connected_ip', 'last_connected_at', 'article_slugs', 'other_stuff', 'hint_example',
                  'help_text_example_1', 'help_text_example_2', 'help_text_example_3')

        ref_name = "UserSerializer"


class UserListQuerySerializer(serializers.Serializer):
    username = serializers.CharField(help_text="this field is generated from a query_serializer", required=False)
    is_staff = serializers.BooleanField(help_text="this one too!", required=False)
    styles = serializers.MultipleChoiceField(help_text="and this one is fancy!", choices=('a', 'b', 'c', 'd'))
