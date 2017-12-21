from django.contrib.auth import get_user_model
from rest_framework import serializers

from snippets.models import Snippet


class UserSerializerrr(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    last_connected_ip = serializers.IPAddressField(help_text="i'm out of ideas", protocol='ipv4', read_only=True)
    last_connected_at = serializers.DateField(help_text="really?", read_only=True)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
        help_text='Default to logged in user if not specified at creation time.',
    )

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'snippets', 'last_connected_ip', 'last_connected_at', 'owner')


class UserListQuerySerializer(serializers.Serializer):
    username = serializers.CharField(help_text="this field is generated from a query_serializer")
    is_staff = serializers.BooleanField(help_text="this one too!")
