from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from articles.models import Article, ArticleGroup


class ArticleSerializer(serializers.ModelSerializer):
    references = serializers.DictField(
        help_text=_("this is a really bad example"),
        child=serializers.URLField(help_text="but i needed to test these 2 fields somehow"),
        read_only=True,
    )
    uuid = serializers.UUIDField(help_text="should articles have UUIDs?", read_only=True)
    cover_name = serializers.FileField(use_url=False, source='cover', required=True)
    group = serializers.SlugRelatedField(slug_field='uuid', queryset=ArticleGroup.objects.all())
    original_group = serializers.SlugRelatedField(slug_field='uuid', read_only=True)

    class Meta:
        model = Article
        fields = ('title', 'author', 'body', 'slug', 'date_created', 'date_modified', 'read_only_nullable',
                  'references', 'uuid', 'cover', 'cover_name', 'article_type', 'group', 'original_group', )
        read_only_fields = ('date_created', 'date_modified', 'references', 'uuid', 'cover_name', 'read_only_nullable')
        lookup_field = 'slug'
        extra_kwargs = {
            'body': {'help_text': 'body serializer help_text'},
            'author': {
                'default': serializers.CurrentUserDefault(),
                'help_text': _("The ID of the user that created this article; if none is provided, "
                               "defaults to the currently logged in user.")
            },
            'read_only_nullable': {'allow_null': True},
        }


class ImageUploadSerializer(serializers.Serializer):
    image_id = serializers.UUIDField(read_only=True)
    what_am_i_doing = serializers.RegexField(
        regex=r"^69$",
        help_text="test",
        default="69",
        allow_null=True
    )
    image_styles = serializers.ListSerializer(
        child=serializers.ChoiceField(choices=['wide', 'tall', 'thumb', 'social']),
        help_text="Parameter with Items"
    )
    upload = serializers.ImageField(help_text="image serializer help_text")
