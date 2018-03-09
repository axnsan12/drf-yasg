from django.utils import timezone
from rest_framework import serializers

from .models import Todo, TodoAnother, TodoYetAnother


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
