from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinValueValidator
from rest_framework import serializers

from snippets.models import LANGUAGE_CHOICES, STYLE_CHOICES, Snippet, SnippetViewer


class LanguageSerializer(serializers.Serializer):
    name = serializers.ChoiceField(
        choices=LANGUAGE_CHOICES, default='python', help_text='The name of the programming language')
    read_only_nullable = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        ref_name = None


class ExampleProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(label='project name custom title', help_text='Name of the project')
    github_repo = serializers.CharField(required=True, help_text='Github repository of the project')

    class Meta:
        ref_name = 'Project'


class UnixTimestampField(serializers.DateTimeField):
    def to_representation(self, value):
        """ Return epoch time for a datetime object or ``None``"""
        from django.utils.dateformat import format
        try:
            return int(format(value, 'U'))
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        import datetime
        return datetime.datetime.fromtimestamp(int(value))

    class Meta:
        swagger_schema_fields = {
            'format': 'integer',
            'title': 'Client date time suu',
            'description': 'Date time in unix timestamp format',
        }


class SnippetSerializer(serializers.Serializer):
    """SnippetSerializer classdoc

    create: docstring for create from serializer classdoc
    """
    id = serializers.IntegerField(read_only=True, help_text="id serializer help text")
    created = UnixTimestampField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
        help_text="The ID of the user that created this snippet; if none is provided, "
                  "defaults to the currently logged in user."
    )
    owner_as_string = serializers.PrimaryKeyRelatedField(
        help_text="The ID of the user that created this snippet.",
        pk_field=serializers.CharField(help_text="this help text should not show up"),
        read_only=True,
        source='owner',
    )
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})
    tags = serializers.ListField(child=serializers.CharField(min_length=2), min_length=3, max_length=15)
    linenos = serializers.BooleanField(required=False)
    language = LanguageSerializer(help_text="Sample help text for language")
    styles = serializers.MultipleChoiceField(choices=STYLE_CHOICES, default=['solarized-dark'])
    lines = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, allow_null=True, required=False)
    example_projects = serializers.ListSerializer(child=ExampleProjectSerializer(), read_only=True,
                                                  validators=[MaxLengthValidator(100)])
    difficulty_factor = serializers.FloatField(help_text="this is here just to test FloatField",
                                               read_only=True, default=lambda: 6.9)
    rate_as_string = serializers.DecimalField(max_digits=6, decimal_places=3, default=Decimal('0.0'),
                                              validators=[MinValueValidator(Decimal('0.0'))])
    rate = serializers.DecimalField(max_digits=6, decimal_places=3, default=Decimal('0.0'), coerce_to_string=False,
                                    validators=[MinValueValidator(Decimal('0.0'))])

    nullable_secondary_language = LanguageSerializer(allow_null=True)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        del validated_data['styles']
        del validated_data['lines']
        del validated_data['difficulty_factor']
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance


class SnippetViewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnippetViewer
        fields = '__all__'
