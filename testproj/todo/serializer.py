from rest_framework import serializers

from .models import Todo, TodoAnother, TodoYetAnother


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('title',)


class TodoAnotherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoAnother
        fields = ('title','todo')
        depth = 2


class TodoYetAnotherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoYetAnother
        fields = ('title','todo')
        depth = 2
