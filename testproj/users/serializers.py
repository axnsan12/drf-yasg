from django.contrib.auth.models import User
from rest_framework import serializers

from drf_yasg.utils import swagger_serializer_method
from snippets.models import Snippet

try:
    import typing
    from .method_serializers_with_typing import MethodFieldExampleSerializer
except ImportError:
    from .method_serializers_without_typing import MethodFieldExampleSerializer


class OtherStuffSerializer(serializers.Serializer):
    foo = serializers.CharField()


class UserSerializerrr(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    article_slugs = serializers.SlugRelatedField(read_only=True, slug_field='slug', many=True, source='articles')
    last_connected_ip = serializers.IPAddressField(help_text="i'm out of ideas", protocol='ipv4', read_only=True)
    last_connected_at = serializers.DateField(help_text="really?", read_only=True)

    other_stuff = serializers.SerializerMethodField(
        help_text="the decorator should determine the serializer class for this")

    hint_example = MethodFieldExampleSerializer()

    @swagger_serializer_method(serializer=OtherStuffSerializer)
    def get_other_stuff(self, obj):
        """
        method_field that uses a serializer internally.

        By using the decorator, we can tell drf-yasg how to represent this in Swagger
        :param obj:
        :return:
        """
        return OtherStuffSerializer().data

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'articles', 'snippets',
                  'last_connected_ip', 'last_connected_at', 'article_slugs', 'other_stuff', 'hint_example')


class UserListQuerySerializer(serializers.Serializer):
    username = serializers.CharField(help_text="this field is generated from a query_serializer", required=False)
    is_staff = serializers.BooleanField(help_text="this one too!", required=False)
