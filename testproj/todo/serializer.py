from collections import OrderedDict

from django.utils import timezone
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import Todo, TodoAnother, TodoTree, TodoYetAnother


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('title', 'a_hidden_field',)

    a_hidden_field = serializers.HiddenField(default=timezone.now)


class TodoAnotherSerializer(serializers.ModelSerializer):
    todo = TodoSerializer()

    class Meta:
        model = TodoAnother
        fields = ('title', 'todo')


class TodoYetAnotherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoYetAnother
        fields = ('title', 'todo')
        depth = 2
        swagger_schema_fields = {
            'example': OrderedDict([
                ('title', 'parent'),
                ('todo', OrderedDict([
                    ('title', 'child'),
                    ('todo', None),
                ])),
            ])
        }


class TodoTreeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(child=RecursiveField(), source='children.all')

    class Meta:
        model = TodoTree
        fields = ('id', 'title', 'children')


class TodoRecursiveSerializer(serializers.ModelSerializer):
    parent = RecursiveField(read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=TodoTree.objects.all(), pk_field=serializers.IntegerField(),
                                                   write_only=True, allow_null=True, required=False, default=None,
                                                   source='parent')

    class Meta:
        model = TodoTree
        fields = ('id', 'title', 'parent', 'parent_id')
