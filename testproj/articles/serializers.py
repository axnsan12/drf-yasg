from rest_framework import serializers

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    references = serializers.DictField(
        help_text="this is a really bad example",
        child=serializers.URLField(help_text="but i needed to test these 2 fields somehow"),
        read_only=True,
    )
    uuid = serializers.UUIDField(help_text="should articles have UUIDs?", read_only=True)
    cover_name = serializers.FileField(use_url=False, source='cover', read_only=True)

    class Meta:
        model = Article
        fields = ('title', 'body', 'slug', 'date_created', 'date_modified',
                  'references', 'uuid', 'cover', 'cover_name')
        read_only_fields = ('date_created', 'date_modified',
                            'references', 'uuid', 'cover_name')
        lookup_field = 'slug'
        extra_kwargs = {'body': {'help_text': 'body serializer help_text'}}


class ImageUploadSerializer(serializers.Serializer):
    what_am_i_doing = serializers.RegexField(regex=r"^69$", help_text="test")
    image_styles = serializers.ListSerializer(
        child=serializers.ChoiceField(choices=['wide', 'tall', 'thumb', 'social']),
        help_text="Parameter with Items"
    )
    upload = serializers.ImageField(help_text="image serializer help_text")
