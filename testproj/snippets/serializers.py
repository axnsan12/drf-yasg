from rest_framework.status import HTTP_400_BAD_REQUEST

from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class LanguageSerializer(serializers.Serializer):
    name = serializers.ChoiceField(
        choices=LANGUAGE_CHOICES, default='python', help_text='The name of the programming language')


class ExampleProjectsSerializer(serializers.Serializer):
    project_name = serializers.CharField(help_text='Name of the project')
    github_repo = serializers.CharField(required=True, help_text='Github repository of the project')


class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})
    linenos = serializers.BooleanField(required=False)
    language = LanguageSerializer()
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
    lines = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, allow_null=True, required=False)
    example_projects = serializers.ListSerializer(child=ExampleProjectsSerializer())

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
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
