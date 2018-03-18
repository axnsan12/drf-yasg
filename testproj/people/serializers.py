from rest_framework import serializers

from .models import Identity, Person


class IdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Identity
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    identity = IdentitySerializer()

    class Meta:
        model = Person
        fields = '__all__'

    def create(self, validated_data):
        identity = Identity(**validated_data['identity'])
        identity.save()
        validated_data['identity'] = identity
        return super().create(validated_data)
