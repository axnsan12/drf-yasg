from django.contrib.auth.models import User
from rest_framework import serializers

from snippets.models import Snippet


class UserSerializerrr(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    article_slugs = serializers.SlugRelatedField(read_only=True, slug_field='slug', many=True, source='articles')
    last_connected_ip = serializers.IPAddressField(help_text="i'm out of ideas", protocol='ipv4', read_only=True)
    last_connected_at = serializers.DateField(help_text="really?", read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'articles', 'snippets',
                  'last_connected_ip', 'last_connected_at', 'article_slugs')


class UserListQuerySerializer(serializers.Serializer):
    username = serializers.CharField(help_text="this field is generated from a query_serializer", required=False)
    is_staff = serializers.BooleanField(help_text="this one too!", required=False)
