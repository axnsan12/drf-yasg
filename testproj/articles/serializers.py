from rest_framework import serializers

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'body', 'slug', 'date_created', 'date_modified')
        read_only_fields = ('date_created', 'date_modified')
        lookup_field = 'slug'
        extra_kwargs = {'body': {'help_text': 'body serializer help_text'}}


class ImageUploadSerializer(serializers.Serializer):
    upload = serializers.ImageField(help_text="image serializer help_text")
